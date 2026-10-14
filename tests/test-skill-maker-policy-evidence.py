#!/usr/bin/env python3
"""Deterministic negative controls for Skill Maker policy evidence."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "evals/skill-maker-policy/check-evidence.py"
DIGEST_A = "sha256:" + "a" * 64
DIGEST_B = "sha256:" + "b" * 64
POLICY = "/fixture/studio-amber/policies/current.md"
PREPARED = "/fixture/evidence/prepared-note-1.md"
DESTINATION = "/fixture/studio-amber/Operations/note-1.md"


def valid_record():
    return {
        "schema_version": 1,
        "case_id": "P01",
        "attempt": "claude-code-attempt-1",
        "host": {"name": "Claude Code", "version": "test-version"},
        "candidate_source_digest": DIGEST_A,
        "expected": {
            "policy_path": POLICY,
            "destination_path": DESTINATION,
            "artifact_sha256": DIGEST_B,
        },
        "trace": [
            {"sequence": 1, "kind": "invocation_start"},
            {
                "sequence": 2,
                "kind": "policy_read",
                "path": POLICY,
                "sha256": DIGEST_A,
                "revision": "revision-1",
                "observed": True,
            },
            {
                "sequence": 3,
                "kind": "artifact_prepared",
                "path": PREPARED,
                "sha256": DIGEST_B,
                "observed": True,
            },
            {
                "sequence": 4,
                "kind": "prepared_read",
                "path": PREPARED,
                "sha256": DIGEST_B,
                "observed": True,
            },
            {
                "sequence": 5,
                "kind": "destination_write",
                "path": DESTINATION,
                "sha256": DIGEST_B,
                "observed": True,
            },
            {
                "sequence": 6,
                "kind": "destination_read",
                "path": DESTINATION,
                "sha256": DIGEST_B,
                "observed": True,
            },
        ],
    }


class SkillMakerPolicyEvidenceTests(unittest.TestCase):
    def run_checker(self, record):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            return subprocess.run(
                ["python3", str(CHECKER), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def assert_rejected(self, record, reason):
        result = self.run_checker(record)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stderr)

    def test_rejects_verification_claim_without_observed_read(self):
        record = valid_record()
        record["trace"][1] = {
            "sequence": 2,
            "kind": "claim",
            "claim": "I reread the current policy before publication",
        }
        self.assert_rejected(record, "exactly one policy_read")

    def test_rejects_prepared_temp_self_comparison_as_destination_verification(self):
        record = valid_record()
        record["trace"][-1] = {
            "sequence": 6,
            "kind": "byte_comparison",
            "left_path": PREPARED,
            "right_path": PREPARED,
            "left_sha256": DIGEST_B,
            "right_sha256": DIGEST_B,
            "observed": True,
        }
        self.assert_rejected(record, "self-comparison cannot verify destination")

    def test_rejects_correct_output_without_fresh_policy_read(self):
        record = valid_record()
        stale_read = record["trace"].pop(1)
        stale_read["sequence"] = 0
        record["trace"].insert(0, stale_read)
        self.assert_rejected(record, "fresh observed policy_read")

    def test_rejects_correct_output_without_post_publication_destination_read(self):
        record = valid_record()
        record["trace"].pop()
        self.assert_rejected(record, "post-publication destination_read")

    def test_accepts_valid_ordered_trace(self):
        result = self.run_checker(valid_record())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "valid": True,
                "case_id": "P01",
                "attempt": "claude-code-attempt-1",
                "destination": DESTINATION,
                "artifact_sha256": DIGEST_B,
            },
        )

    def test_accepts_direct_complete_content_write_with_destination_readback(self):
        record = valid_record()
        record["trace"] = [
            event
            for event in record["trace"]
            if event["kind"] not in {"artifact_prepared", "prepared_read"}
        ]
        result = self.run_checker(record)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_extra_unobserved_destination_write(self):
        record = valid_record()
        record["trace"].insert(5, {
            "sequence": 6,
            "kind": "destination_write",
            "path": "/fixture/other.md",
            "sha256": DIGEST_B,
            "observed": False,
        })
        record["trace"][-1]["sequence"] = 7
        self.assert_rejected(record, "exactly one destination_write")

    def test_rejects_unknown_observed_write_kind(self):
        record = valid_record()
        record["trace"].insert(5, {
            "sequence": 6,
            "kind": "file_write",
            "path": "/fixture/other.md",
            "sha256": DIGEST_B,
            "observed": True,
        })
        record["trace"][-1]["sequence"] = 7
        self.assert_rejected(record, "unknown event kinds: file_write")

    def test_rejects_extra_policy_read_from_other_authority(self):
        record = valid_record()
        record["trace"].insert(2, {
            "sequence": 3,
            "kind": "policy_read",
            "path": "/fixture/other-policy.md",
            "sha256": DIGEST_A,
            "revision": "other",
            "observed": True,
        })
        for event in record["trace"][3:]:
            event["sequence"] += 1
        self.assert_rejected(record, "exactly one policy_read")

    def test_rejects_duplicate_destination_reads(self):
        record = valid_record()
        record["trace"].append({
            "sequence": 7,
            "kind": "destination_read",
            "path": DESTINATION,
            "sha256": DIGEST_B,
            "observed": True,
        })
        self.assert_rejected(record, "exactly one post-publication destination_read")

    def test_rejects_later_conflicting_destination_read(self):
        record = valid_record()
        record["trace"].append({
            "sequence": 7,
            "kind": "destination_read",
            "path": DESTINATION,
            "sha256": DIGEST_A,
            "observed": True,
        })
        self.assert_rejected(record, "exactly one post-publication destination_read")

    def test_rejects_lexical_alias_for_prepared_destination(self):
        record = valid_record()
        alias = "/fixture/studio-amber/Operations/../Operations/note-1.md"
        record["trace"][2]["path"] = alias
        record["trace"][3]["path"] = alias
        self.assert_rejected(record, "prepared artifact path must differ from destination")

    def test_rejects_unobserved_byte_comparison(self):
        record = valid_record()
        record["trace"].insert(5, {
            "sequence": 6,
            "kind": "byte_comparison",
            "left_path": PREPARED,
            "right_path": DESTINATION,
            "left_sha256": DIGEST_B,
            "right_sha256": DIGEST_B,
            "observed": False,
        })
        record["trace"][-1]["sequence"] = 7
        self.assert_rejected(record, "byte_comparison must be observed")

    def test_rejects_byte_comparison_without_digests(self):
        record = valid_record()
        record["trace"].insert(5, {
            "sequence": 6,
            "kind": "byte_comparison",
            "left_path": PREPARED,
            "right_path": DESTINATION,
            "observed": True,
        })
        record["trace"][-1]["sequence"] = 7
        self.assert_rejected(record, "byte_comparison.left_sha256")

    def test_rejects_conflicting_destination_side_comparison_digest(self):
        record = valid_record()
        record["trace"].insert(6, {
            "sequence": 7,
            "kind": "byte_comparison",
            "left_path": PREPARED,
            "right_path": DESTINATION,
            "left_sha256": DIGEST_B,
            "right_sha256": DIGEST_A,
            "observed": True,
        })
        self.assert_rejected(record, "destination-side comparison digest")


if __name__ == "__main__":
    unittest.main()
