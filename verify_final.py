#!/usr/bin/env python3
"""Verify the published Transformer audit without rerunning experiments."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_ORIGIN = (
    "https://github.com/MachineLearning-Nerd/"
    "icml26-transformer-holder-approximation"
)
EXPECTED_BRANCHES = {"main"}
EXPECTED_IDENTITY = (
    "MachineLearning-Nerd",
    "MachineLearning-Nerd@users.noreply.github.com",
)
EXPECTED_REPOSITORY = "MachineLearning-Nerd/icml26-transformer-holder-approximation"
EXPECTED_OVERALL_VERDICT = "PARTIAL_CLAIM_1_TOY_CLAIM_2_PINNED_ROUTE_FALSIFIED_CLAIMS_3_TO_4_UNVERIFIED"
EXPECTED_PUBLICATION_BOUNDARY = "PARTIAL_TOY_AND_ROUTE_FALSIFICATION_NO_FULL_REPRODUCTION"
CLAIM1_DIR = ROOT / "outputs/claim1_constructive_toy"
CLAIM2_DIR = ROOT / "outputs/claim2_l2_to_linf_counterexample"
ERRORS: list[str] = []


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(relative: str) -> object:
    try:
        return json.loads((ROOT / relative).read_text())
    except Exception as exc:
        ERRORS.append(f"{relative}: cannot parse JSON: {exc}")
        return {}


def verify_hash_manifest(relative: str, base: Path) -> None:
    path = ROOT / relative
    for line in path.read_text().splitlines():
        fields = line.split()
        require(len(fields) == 2, f"malformed hash row in {relative}: {line}")
        if len(fields) != 2:
            continue
        digest, name = fields
        target = ROOT / name
        if not target.is_file():
            target = base / name
        require(target.is_file(), f"missing hash input: {target}")
        if target.is_file():
            require(sha256(target) == digest, f"hash mismatch: {target}")


def close(actual: float, expected: float, label: str, tolerance: float = 1e-9) -> None:
    require(abs(actual - expected) <= tolerance, f"{label}: {actual} != {expected}")


def main() -> int:
    origin_result = run("git", "remote", "get-url", "origin")
    origin = origin_result.stdout.strip().removesuffix(".git").rstrip("/")
    require(origin == EXPECTED_ORIGIN, f"unexpected origin: {origin!r}")

    symref = run("git", "ls-remote", "--symref", "origin", "HEAD")
    require(
        "ref: refs/heads/main\tHEAD" in symref.stdout,
        "origin HEAD does not point to main",
    )

    heads = run("git", "ls-remote", "--heads", "origin")
    remote_branches = set()
    for line in heads.stdout.splitlines():
        fields = line.split("\t", 1)
        if len(fields) == 2 and fields[1].startswith("refs/heads/"):
            remote_branches.add(fields[1].removeprefix("refs/heads/"))
    require(remote_branches == EXPECTED_BRANCHES, f"remote branches: {sorted(remote_branches)}")
    require(
        not any(branch.startswith("orx/") for branch in remote_branches),
        "old orx branch remains on the remote",
    )

    local_heads = run(
        "git",
        "for-each-ref",
        "--format=%(refname:strip=2)",
        "refs/heads",
    )
    local_branches = set(filter(None, local_heads.stdout.splitlines()))
    require(
        local_branches <= EXPECTED_BRANCHES,
        f"unexpected local branches: {sorted(local_branches - EXPECTED_BRANCHES)}",
    )
    require(
        not run("git", "for-each-ref", "refs/original").stdout.strip(),
        "refs/original exists",
    )

    count_result = run("git", "rev-list", "--count", "--all")
    try:
        commit_count = int(count_result.stdout.strip())
    except ValueError:
        commit_count = 0
    require(commit_count >= 10, f"reachable commit count is only {commit_count}")

    identity_output = run(
        "git",
        "log",
        "--all",
        "--format=%an%x09%ae%x09%cn%x09%ce",
    ).stdout
    for line in filter(None, identity_output.splitlines()):
        fields = line.split("\t")
        require(len(fields) == 4, f"malformed identity row: {line}")
        if len(fields) == 4:
            author_name, author_email, committer_name, committer_email = fields
            require(
                (author_name, author_email) == EXPECTED_IDENTITY,
                f"non-canonical author identity: {line}",
            )
            require(
                (committer_name, committer_email) == EXPECTED_IDENTITY,
                f"non-canonical committer identity: {line}",
            )
    messages = run("git", "log", "--all", "--format=%B").stdout
    require(
        "Co-authored-by:" not in messages and "Co-Authored-By:" not in messages,
        "co-author trailer found in commit messages",
    )

    required_files = [
        "README.md",
        "STATUS.md",
        "branch-audit.md",
        "BRANCH_AUDIT.md",
        "CLAIM_EVIDENCE.md",
        "SOURCE_AUDIT.md",
        "ENVIRONMENT.md",
        "REPORT.md",
        "AUTHOR_THANK_YOU.md",
        "CITATION.cff",
        "claims.json",
        "reproduction_verdicts.json",
        "AUTONOMOUS_STATE.json",
        "EVIDENCE_MANIFEST.json",
        "verify_final.py",
        "contract/contract_manifest.json",
        "contract/live_claims.json",
        "evidence/source/SHA256SUMS",
        "evidence/source/arxiv_source.tar.gz",
        "evidence/source/arxiv.pdf",
        "evidence/claim1_attempt1/SHA256SUMS",
        "evidence/claim1_attempt1/result.json",
        "outputs/claim1_constructive_toy/SHA256SUMS",
        "outputs/claim1_constructive_toy/summary.json",
        "outputs/claim1_constructive_toy/audit.md",
        "outputs/claim2_l2_to_linf_counterexample/SHA256SUMS",
        "outputs/claim2_l2_to_linf_counterexample/result.json",
        "outputs/claim2_l2_to_linf_counterexample/run.log",
        "outputs/claim2_l2_to_linf_counterexample/stdout.log",
        "src/claim1_direct_cpu_audit.py",
        "src/claim1_constructive_transformer_toy.py",
        "src/claim2_l2_to_linf_counterexample.py",
    ]
    for relative in required_files:
        require((ROOT / relative).is_file(), f"missing required file: {relative}")

    manifest = load_json("EVIDENCE_MANIFEST.json")
    if isinstance(manifest, dict):
        require(
            manifest.get("branch_contract") == {
                "default": "main",
                "total": 1,
                "descriptive": 0,
                "old_prefix_absent": "orx/",
            },
            "branch contract mismatch",
        )
        require(
            manifest.get("repository") == EXPECTED_REPOSITORY
            and manifest.get("overall_verdict") == EXPECTED_OVERALL_VERDICT
            and manifest.get("publication_allowed") is False
            and manifest.get("publication_boundary") == EXPECTED_PUBLICATION_BOUNDARY
            and manifest.get("score_claim") is False
            and manifest.get("official_author_endorsement") is False,
            "manifest publication boundary mismatch",
        )
        require(
            manifest.get("attribution", {}).get("email") == EXPECTED_IDENTITY[1],
            "manifest attribution mismatch",
        )
        aggregates = manifest.get("aggregates", {})
        files = manifest.get("files", [])
    else:
        aggregates, files = {}, []
    for relative, expected in aggregates.items():
        path = ROOT / relative
        require(path.is_file(), f"missing aggregate input: {relative}")
        require(expected not in (None, "", "PENDING"), f"aggregate hash pending: {relative}")
        if path.is_file() and expected not in (None, "", "PENDING"):
            require(sha256(path) == expected, f"aggregate hash mismatch: {relative}")
    for row in files:
        relative = row.get("path", "")
        path = ROOT / relative
        expected = row.get("sha256")
        require(path.is_file(), f"manifest file missing: {relative}")
        require(expected not in (None, "", "PENDING"), f"manifest hash pending: {relative}")
        if path.is_file() and expected not in (None, "", "PENDING"):
            require(sha256(path) == expected, f"manifest hash mismatch: {relative}")

    claims = load_json("claims.json")
    expected_statuses = {
        1: "TOY_REDUCED_CONSTRUCTIVE_APPROXIMATION",
        2: "FALSIFIED_PINNED_L2_LINF_PROOF_ROUTE",
        3: "UNVERIFIED_NOT_STARTED",
        4: "UNVERIFIED_NOT_STARTED",
    }
    if isinstance(claims, dict):
        actual_claims = {item.get("id"): item for item in claims.get("claims", [])}
    else:
        actual_claims = {}
    require(set(actual_claims) == set(expected_statuses), "claims.json IDs mismatch")
    for claim_id, status in expected_statuses.items():
        require(
            actual_claims.get(claim_id, {}).get("status") == status,
            f"claims.json status mismatch for Claim {claim_id}",
        )
    reproduction = load_json("reproduction_verdicts.json")
    state = load_json("AUTONOMOUS_STATE.json")
    require(
        claims.get("repository") == EXPECTED_REPOSITORY
        and claims.get("overall_verdict") == EXPECTED_OVERALL_VERDICT
        and claims.get("publication_allowed") is False
        and claims.get("publication_boundary") == EXPECTED_PUBLICATION_BOUNDARY
        and claims.get("score_claim") is False
        and claims.get("official_author_endorsement") is False,
        "claims publication boundary mismatch",
    )
    require(
        reproduction.get("repository") == EXPECTED_REPOSITORY
        and reproduction.get("overall_verdict") == EXPECTED_OVERALL_VERDICT
        and reproduction.get("publication_allowed") is False
        and reproduction.get("publication_boundary") == EXPECTED_PUBLICATION_BOUNDARY
        and reproduction.get("score_claim") is False
        and reproduction.get("official_author_endorsement") is False
        and {
            str(row.get("id")).removeprefix("C"): row.get("status")
            for row in reproduction.get("claims", [])
        }
        == {
            "1": "TOY_REDUCED_CONSTRUCTIVE_APPROXIMATION",
            "2": "FALSIFIED_PINNED_L2_LINF_PROOF_ROUTE",
            "3": "UNVERIFIED_NOT_STARTED",
            "4": "UNVERIFIED_NOT_STARTED",
        },
        "reproduction verdict boundary mismatch",
    )
    require(
        state.get("github_repository") == "https://github.com/" + EXPECTED_REPOSITORY
        and state.get("phase") == "published_scoped_partial_audit"
        and state.get("publication_allowed") is False
        and state.get("overall_verdict") == EXPECTED_OVERALL_VERDICT
        and state.get("publication_boundary") == EXPECTED_PUBLICATION_BOUNDARY
        and state.get("score_claim") is False
        and state.get("official_author_endorsement") is False
        and state.get("live_verification", {}).get("branch_count") == 1
        and state.get("live_verification", {}).get("default_branch") == "main"
        and state.get("verified_reachable_commits") == 12,
        "state publication boundary mismatch",
    )
    require(
        state.get("attribution", {}).get("email") == EXPECTED_IDENTITY[1],
        "state attribution mismatch",
    )

    live_claims = load_json("contract/live_claims.json")
    require(
        isinstance(live_claims, list)
        and len(live_claims) == 4
        and all(item.get("status") == "unverified" for item in live_claims),
        "live claim contract changed unexpectedly",
    )

    verify_hash_manifest("evidence/source/SHA256SUMS", ROOT / "evidence/source")
    verify_hash_manifest(
        "evidence/claim1_attempt1/SHA256SUMS",
        ROOT / "evidence/claim1_attempt1",
    )
    verify_hash_manifest(
        "outputs/claim1_constructive_toy/SHA256SUMS",
        CLAIM1_DIR,
    )
    verify_hash_manifest(
        "outputs/claim2_l2_to_linf_counterexample/SHA256SUMS",
        CLAIM2_DIR,
    )

    summary = load_json("outputs/claim1_constructive_toy/summary.json")
    require(isinstance(summary, dict), "Claim 1 summary is not an object")
    if isinstance(summary, dict):
        require(summary.get("seeds") == [20260801, 20260802, 20260803, 20260804, 20260805], "Claim 1 seed set mismatch")
        require(summary.get("ntrain") == 4000 and summary.get("ntest") == 8000, "Claim 1 sample contract mismatch")
        require(summary.get("verdict") == "toy", "Claim 1 verdict mismatch")
        seed_meta = load_json("outputs/claim1_constructive_toy/meta_seed20260801.json")
        require(
            isinstance(seed_meta, dict) and seed_meta.get("device") == "local CPU",
            "Claim 1 device mismatch",
        )
        expected_widths = {
            "16": (0.3071274077396229, 0.4622693141212866),
            "64": (0.20026873953487978, 0.4713274960320265),
            "256": (0.09366697844408187, 0.4757207770524562),
        }
        width_summary = summary.get("width_summary", {})
        require(set(width_summary) == set(expected_widths), "Claim 1 width set mismatch")
        for width, (l2, control) in expected_widths.items():
            close(width_summary[width]["mean_l2"], l2, f"Claim 1 mean L2 {width}")
            close(width_summary[width]["mean_permuted_label_l2"], control, f"Claim 1 control L2 {width}")
            require(width_summary[width]["control_degrades_all_seeds"] is True, f"Claim 1 control failed at {width}")

    row_files = sorted(CLAIM1_DIR.glob("rows_seed*.csv"))
    require(len(row_files) == 5, "Claim 1 raw seed file count mismatch")
    row_count = 0
    for path in row_files:
        with path.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        require(len(rows) == 3, f"Claim 1 row count mismatch: {path.name}")
        row_count += len(rows)
        for row in rows:
            require(row["control_degrades"] == "True", f"Claim 1 control flag failed: {path.name}")
            require(float(row["permuted_label_l2_error"]) > float(row["l2_test_error"]), f"Claim 1 control ordering failed: {path.name}")
    require(row_count == 15, "Claim 1 total raw row count mismatch")

    result = load_json("outputs/claim2_l2_to_linf_counterexample/result.json")
    require(isinstance(result, dict), "Claim 2 result is not an object")
    if isinstance(result, dict):
        require(result.get("verdict") == "falsified", "Claim 2 verdict mismatch")
        rows = result.get("rows", [])
        require(len(rows) == 6, "Claim 2 width row count mismatch")
        for row in rows:
            width = float(row["width"])
            close(row["linf"], 1.0, f"Claim 2 Linfinity {width}")
            close(row["l2_analytic"], math.sqrt(2.0 * width / 3.0), f"Claim 2 analytic L2 {width}")
            require(row["abs_error"] < 2e-9, f"Claim 2 quadrature error too large at {width}")
        witness = result.get("concrete_witness", {})
        close(witness.get("width", 0.0), 0.0125, "Claim 2 witness width")
        close(witness.get("linf", 0.0), 1.0, "Claim 2 witness Linfinity")
        require(witness.get("l2_analytic", 1.0) < 0.1, "Claim 2 witness L2 is not below .1")

    for relative, markers in {
        "src/claim1_direct_cpu_audit.py": ("def upper_blocks", "d0>2", "expected_ratio"),
        "src/claim1_constructive_transformer_toy.py": ("def encode_attention", "permuted_label_l2_error", "widths"),
        "src/claim2_l2_to_linf_counterexample.py": ("def tent_l2_squared", "triangular", "l2_quadrature"),
    }.items():
        source = (ROOT / relative).read_text()
        for marker in markers:
            require(marker in source, f"producer marker missing: {relative}: {marker}")

    document_markers = {
        "README.md": (
            "PARTIAL_CLAIM_1_TOY_CLAIM_2_PINNED_ROUTE_FALSIFIED_CLAIMS_3_TO_4_UNVERIFIED",
            "reproduction_verdicts.json",
            "AUTONOMOUS_STATE.json",
            "publication_allowed=false",
            "score_claim=false",
            "official_author_endorsement=false",
        ),
        "STATUS.md": (
            "published_scoped_partial_audit",
            "PARTIAL_CLAIM_1_TOY_CLAIM_2_PINNED_ROUTE_FALSIFIED_CLAIMS_3_TO_4_UNVERIFIED",
            "reproduction_verdicts.json",
        ),
        "REPORT.md": (
            "PARTIAL_CLAIM_1_TOY_CLAIM_2_PINNED_ROUTE_FALSIFIED_CLAIMS_3_TO_4_UNVERIFIED",
            "publication_allowed=false",
            "official_author_endorsement=false",
        ),
    }
    for relative, markers in document_markers.items():
        document = (ROOT / relative).read_text()
        for marker in markers:
            require(marker in document, f"{relative} missing marker: {marker}")

    if ERRORS:
        print("FINAL_AUDIT=FAILED")
        for error in ERRORS:
            print(f"- {error}")
        return 1
    print(
        f"FINAL_AUDIT=VERIFIED branches={len(remote_branches)} "
        f"commits={commit_count} claim1=toy claim2=proof-route-falsified claims3-4=unverified"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
