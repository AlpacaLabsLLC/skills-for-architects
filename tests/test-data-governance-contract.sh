#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from copy import deepcopy
import hashlib
from pathlib import Path
import re

SOURCE_REVISION = "baacdacf25511d118b5a0c9e2999ba70dcb5b940"
SOURCE_POLICY_SHA256 = "f7fea15a95ef007775cf208c4068094fc7d7690ae039986ea3ccbb1d51407af9"
GOVERNED_SURFACES = {
    "plugin summary": Path("README.md"),
    "public data-governance projection": Path("docs/data-governance.md"),
    "release-delivery gate": Path("docs/release-delivery.md"),
    "architecture authority map": Path("docs/architecture.md"),
}
CONTRACT_TEST = Path("tests/test-data-governance-contract.sh")

for label, path in GOVERNED_SURFACES.items():
    assert path.is_file(), f"missing governed surface: {label}: {path}"
assert CONTRACT_TEST.is_file(), f"missing public contract test: {CONTRACT_TEST}"

surfaces = {
    label: path.read_text(encoding="utf-8")
    for label, path in GOVERNED_SURFACES.items()
}

required = {
    "plugin summary": (
        "The open-source plugin does not upload or store studio, project or module records on Arch Studio servers.",
        "Hosted record-holding modules use the separate boundaries in the [data-governance documentation](./docs/data-governance.md).",
    ),
    "public data-governance projection": (
        SOURCE_REVISION,
        SOURCE_POLICY_SHA256,
        "The accepted private source remains the policy owner",
        "The open-source plugin does not upload studio, project or module records to Arch Studio.",
        "## Hosted record-holding modules",
        "only when a signed-in firm requests an operation that saves to that module",
        "does not change how unrelated skills, modules or local records are handled",
        "project files, drawings, workbooks and other documents remain with the firm",
        "only members of the firm",
        "Turning a module off does not delete its records",
        "deletes canonical live records",
        "six-hour database recovery-history window",
        "up-to-60-second file-cache propagation limit",
        "not used for model training, general product improvement, corpus building or cross-firm analysis",
        "right to a full, portable export",
        "inference region is not pinned",
        "Legal-role classifications remain neutral and pending owner and legal approval",
        "does not silently fall back",
    ),
    "release-delivery gate": (
        "## Public data-promise projection gate",
        SOURCE_REVISION,
        SOURCE_POLICY_SHA256,
        "private source remains authoritative",
        "No projection may invent a second policy authority",
        "canonical live-record deletion",
        "six-hour database recovery history",
        "up-to-60-second file-cache propagation",
        "inference region is not pinned",
        "legal-role classifications remain neutral and pending owner and legal approval",
        "No firm enablement, merge, publication, release or deployment is authorized by this projection.",
    ),
    "architecture authority map": (
        "The local plugin does not upload those records to Arch Studio.",
        "Hosted record-holding modules use separately governed, firm-isolated storage",
        SOURCE_REVISION,
        SOURCE_POLICY_SHA256,
        "private source remains the policy owner",
    ),
}

private_identifier_sha256 = {
    "a8abe02471e0d8f5388bf4926bf0e420acafb181b2c9e77820094c20d3060fe5",
    "602d66a3bd18d60476af7681a98835ee6f44160bdfd97b8819af648deef78f0d",
    "61b6c0201fbddac40e0c62d6f7e90439ce3b21cc1c55c485f9ed9c937df310ff",
    "618484e2c549451830e2b2c19b498d90b4fc8d206174f13c43ed058e6470ee2f",
    "51b2233f27d991c69d6d99336a854591b57de538dcab7b97d7f4cf3f03a0e22e",
    "76977023b60464d2541bba6b4f54bc4f3ac0ecd722947b0ffd0567ac350e61f1",
    "7ddb0704314b289e7df028a91980144a09de964e2155c0b1d2b5263996c9bb7a",
}

forbidden_patterns = (
    (r"\b(?:the )?public projection (?:is|becomes|acts as) the policy owner\b", "authority transfer"),
    (r"\bthe open-source plugin (?:may|can|will) upload(?: and store)?\b", "local upload overclaim"),
    (r"\b(?:all|every) (?:backup |provider-managed )?cop(?:y|ies)\b", "all-copy claim"),
    (r"\b(?:fully|completely|immediately|permanently|irreversibly) (?:deleted|erased|removed)\b", "absolute deletion"),
    (r"\bdeleted from (?:all|every) (?:backup |provider-managed )?(?:copy|copies|location|locations)\b", "absolute deletion"),
    (r"\b(?:all data|records|files|backups) (?:is|are) (?:stored|kept|located) only in\b", "single-region storage claim"),
    (r"\binference region is pinned\b", "pinned inference-region claim"),
    (r"\b(?:ALPA|a provider|the provider) (?:is|acts as|serves as) (?:a |the )?(?:data )?(?:controller|processor|subprocessor)\b", "invented legal role"),
    (r"\b(?:are|is|may be|can be|will be) used (?:for|to) [^.\n]*(?:model training|(?:general )?product improvement|corpus building|cross-firm analysis)\b", "forbidden record use"),
    (r"\b(?:a hosted operation|the hosted module) (?:may|can|will) silently fall back\b", "silent fallback permission"),
    (r"\b[A-Z][A-Za-z0-9-]+ \(PostgreSQL\)", "private database-provider identifier"),
    (r"\b(?:aws|gcp|azure)-[a-z0-9-]+-\d\b", "private region identifier"),
)


def validate(candidate):
    for label, statements in required.items():
        text = candidate[label]
        for statement in statements:
            assert statement in text, f"{label}: missing: {statement}"

    policy = candidate["public data-governance projection"]
    delivery = candidate["release-delivery gate"]
    architecture = candidate["architecture authority map"]
    revision_occurrences = sum(text.count(SOURCE_REVISION) for text in (policy, delivery, architecture))
    digest_occurrences = sum(text.count(SOURCE_POLICY_SHA256) for text in (policy, delivery, architecture))
    assert revision_occurrences == 3, f"source revision occurrence drift: {revision_occurrences}"
    assert digest_occurrences == 3, f"source digest occurrence drift: {digest_occurrences}"

    joined = "\n".join(candidate.values())
    public_artifacts = joined + "\n" + CONTRACT_TEST.read_text(encoding="utf-8")
    words = re.findall(r"[A-Za-z0-9-]+", public_artifacts)
    for width in (1, 2, 3):
        for start in range(len(words) - width + 1):
            candidate_identifier = " ".join(words[start : start + width])
            digest = hashlib.sha256(candidate_identifier.encode("utf-8")).hexdigest()
            assert digest not in private_identifier_sha256, (
                f"private provider identifier exposed (sha256: {digest})"
            )
    for pattern, claim in forbidden_patterns:
        match = re.search(pattern, joined, re.IGNORECASE)
        assert match is None, f"{claim}: {match.group(0)}"


validate(surfaces)

mutations = {
    "source revision drift": ("public data-governance projection", SOURCE_REVISION, "0" * 40),
    "source digest drift": ("release-delivery gate", SOURCE_POLICY_SHA256, "0" * 64),
    "authority transfer": ("architecture authority map", "private source remains the policy owner", "private source remains the policy owner. The public projection is the policy owner"),
    "local upload overclaim": ("plugin summary", "The open-source plugin does not upload or store studio, project or module records on Arch Studio servers.", "The open-source plugin does not upload or store studio, project or module records on Arch Studio servers. The open-source plugin may upload and store records."),
    "all-copy deletion": ("public data-governance projection", "deletes canonical live records", "deletes canonical live records. All copies are deleted"),
    "pinned inference region": ("public data-governance projection", "inference region is not pinned", "inference region is not pinned. The inference region is pinned"),
    "invented legal role": ("public data-governance projection", "Legal-role classifications remain neutral and pending owner and legal approval", "Legal-role classifications remain neutral and pending owner and legal approval. ALPA acts as a data controller"),
    "forbidden product use": ("public data-governance projection", "not used for model training, general product improvement, corpus building or cross-firm analysis", "not used for model training, general product improvement, corpus building or cross-firm analysis. Records may be used for general product improvement"),
    "forbidden corpus use": ("public data-governance projection", "not used for model training, general product improvement, corpus building or cross-firm analysis", "not used for model training, general product improvement, corpus building or cross-firm analysis. Records may be used for corpus building"),
    "private provider identifier": ("release-delivery gate", "six-hour database recovery history", "six-hour database recovery history through PrivateCloud (PostgreSQL)"),
    "private region identifier": ("release-delivery gate", "up-to-60-second file-cache propagation", "up-to-60-second file-cache propagation in aws-private-central-9"),
    "silent fallback": ("public data-governance projection", "does not silently fall back", "does not silently fall back. A hosted operation may silently fall back"),
}
for name, (label, old, new) in mutations.items():
    mutated = deepcopy(surfaces)
    assert old in mutated[label], f"ineffective mutation setup: {name}"
    mutated[label] = mutated[label].replace(old, new, 1)
    try:
        validate(mutated)
    except AssertionError:
        pass
    else:
        raise AssertionError(f"mutation survived: {name}")
PY

printf '%s\n' '✓ public data-governance projection pins authority and rejects drift/overclaims'
