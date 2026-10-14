#!/usr/bin/env python3
"""Validate ordered host evidence for Skill Maker policy publication.

This checker validates a normalized record made from an actual retained host trace. It
cannot establish that the normalized record is authentic or reconstruct missing trace.
"""

from __future__ import annotations

import json
from pathlib import Path
import posixpath
import re
import sys
from typing import Any


SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
EVENT_KINDS = {
    "invocation_start",
    "policy_read",
    "artifact_prepared",
    "prepared_read",
    "destination_write",
    "destination_read",
    "byte_comparison",
    "claim",
}


class EvidenceError(ValueError):
    """The supplied record does not establish the required observations."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def string(value: Any, field: str) -> str:
    require(isinstance(value, str) and bool(value), f"{field} must be a nonempty string")
    return value


def digest(value: Any, field: str) -> str:
    value = string(value, field)
    require(bool(SHA256.fullmatch(value)), f"{field} must be sha256:<64 lowercase hex>")
    return value


def normalized_path(value: Any, field: str) -> str:
    value = string(value, field)
    normalized = posixpath.normpath(value)
    require(normalized not in {"", "."}, f"{field} must identify a file path")
    return normalized


def validate(record: Any) -> dict[str, Any]:
    require(isinstance(record, dict), "evidence root must be an object")
    require(record.get("schema_version") == 1, "schema_version must equal 1")
    case_id = string(record.get("case_id"), "case_id")
    attempt = string(record.get("attempt"), "attempt")
    host = record.get("host")
    require(isinstance(host, dict), "host must be an object")
    string(host.get("name"), "host.name")
    string(host.get("version"), "host.version")
    digest(record.get("candidate_source_digest"), "candidate_source_digest")

    expected = record.get("expected")
    require(isinstance(expected, dict), "expected must be an object")
    policy_path = normalized_path(expected.get("policy_path"), "expected.policy_path")
    destination = normalized_path(expected.get("destination_path"), "expected.destination_path")
    artifact_digest = digest(expected.get("artifact_sha256"), "expected.artifact_sha256")
    require(policy_path != destination, "policy and destination paths must differ")

    trace = record.get("trace")
    require(isinstance(trace, list) and bool(trace), "trace must be a nonempty array")
    require(all(isinstance(event, dict) for event in trace), "every trace event must be an object")
    sequences = [event.get("sequence") for event in trace]
    require(
        all(isinstance(sequence, int) and not isinstance(sequence, bool) for sequence in sequences),
        "every trace sequence must be an integer",
    )
    require(sequences == sorted(set(sequences)), "trace sequences must be unique and strictly ordered")
    require(
        all(isinstance(event.get("kind"), str) and event["kind"] for event in trace),
        "every trace event must have a nonempty kind",
    )
    unknown_kinds = sorted({event["kind"] for event in trace} - EVENT_KINDS)
    require(not unknown_kinds, f"trace contains unknown event kinds: {', '.join(unknown_kinds)}")

    for event in trace:
        if event["kind"] == "byte_comparison":
            left = normalized_path(event.get("left_path"), "byte_comparison.left_path")
            right = normalized_path(event.get("right_path"), "byte_comparison.right_path")
            require(left != right, "self-comparison cannot verify destination")
            require(event.get("observed") is True, "byte_comparison must be observed")
            left_digest = digest(event.get("left_sha256"), "byte_comparison.left_sha256")
            right_digest = digest(event.get("right_sha256"), "byte_comparison.right_sha256")
            if left == destination:
                require(left_digest == artifact_digest,
                        "destination-side comparison digest must equal expected artifact digest")
            if right == destination:
                require(right_digest == artifact_digest,
                        "destination-side comparison digest must equal expected artifact digest")

    starts = [event for event in trace if event["kind"] == "invocation_start"]
    require(len(starts) == 1, "trace must contain exactly one invocation_start")
    start_sequence = starts[0]["sequence"]

    writes = [event for event in trace if event["kind"] == "destination_write"]
    require(len(writes) == 1, "trace must contain exactly one destination_write")
    write = writes[0]
    require(write.get("observed") is True, "destination_write must be observed")
    require(normalized_path(write.get("path"), "destination_write.path") == destination,
            "destination_write path must equal expected.destination_path")
    require(digest(write.get("sha256"), "destination_write.sha256") == artifact_digest,
            "destination_write digest must equal expected artifact digest")
    write_sequence = write["sequence"]
    require(write_sequence > start_sequence, "destination_write must follow invocation_start")

    policy_reads = [event for event in trace if event["kind"] == "policy_read"]
    require(len(policy_reads) == 1, "trace must contain exactly one policy_read")
    policy_read = policy_reads[0]
    require(policy_read.get("observed") is True, "policy_read must be observed")
    require(normalized_path(policy_read.get("path"), "policy_read.path") == policy_path,
            "policy_read path must equal expected.policy_path")
    require(start_sequence < policy_read["sequence"] < write_sequence,
            "fresh observed policy_read is required after invocation_start and before publication")
    digest(policy_read.get("sha256"), "policy_read.sha256")
    string(policy_read.get("revision"), "policy_read.revision")

    # Some hosts publish complete content directly and never create a separate
    # prepared file. If the trace does claim file-based preparation, prove that
    # preparation independently; it cannot stand in for destination readback.
    preparation_events = [
        event for event in trace if event["kind"] in {"artifact_prepared", "prepared_read"}
    ]
    if preparation_events:
        prepared = [event for event in trace if event["kind"] == "artifact_prepared"]
        require(len(prepared) == 1, "claimed preparation requires exactly one artifact_prepared")
        prepared_event = prepared[0]
        require(prepared_event.get("observed") is True, "artifact_prepared must be observed")
        prepared_path = normalized_path(prepared_event.get("path"), "artifact_prepared.path")
        require(prepared_path != destination, "prepared artifact path must differ from destination")
        require(digest(prepared_event.get("sha256"), "artifact_prepared.sha256") == artifact_digest,
                "artifact_prepared digest must equal expected artifact digest")
        require(
            policy_read["sequence"] < prepared_event["sequence"] < write_sequence,
            "artifact_prepared must follow the fresh policy read and precede publication",
        )

        prepared_reads = [event for event in trace if event["kind"] == "prepared_read"]
        require(len(prepared_reads) == 1,
                "claimed preparation requires exactly one prepared_read")
        prepared_read = prepared_reads[0]
        require(prepared_read.get("observed") is True, "prepared_read must be observed")
        require(normalized_path(prepared_read.get("path"), "prepared_read.path") == prepared_path,
                "prepared_read path must equal artifact_prepared.path")
        require(prepared_event["sequence"] < prepared_read["sequence"] < write_sequence,
                "prepared_read must follow artifact_prepared and precede publication")
        require(
            digest(prepared_read.get("sha256"), "prepared_read.sha256") == artifact_digest,
            "prepared_read digest must equal expected artifact digest",
        )

    destination_reads = [event for event in trace if event["kind"] == "destination_read"]
    require(len(destination_reads) == 1,
            "trace must contain exactly one post-publication destination_read")
    destination_read = destination_reads[0]
    require(destination_read.get("observed") is True, "destination_read must be observed")
    require(normalized_path(destination_read.get("path"), "destination_read.path") == destination,
            "destination_read path must equal expected.destination_path")
    require(destination_read["sequence"] > write_sequence,
            "post-publication destination_read of the exact destination is required")
    require(
        digest(destination_read.get("sha256"), "destination_read.sha256") == artifact_digest,
        "destination_read digest must equal expected artifact digest",
    )

    return {
        "valid": True,
        "case_id": case_id,
        "attempt": attempt,
        "destination": destination,
        "artifact_sha256": artifact_digest,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check-evidence.py EVIDENCE.json", file=sys.stderr)
        return 2
    try:
        record = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        result = validate(record)
    except (OSError, UnicodeError, json.JSONDecodeError, EvidenceError) as error:
        print(f"invalid evidence: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
