"""Validate the exact two-comparison continuation and preserved source evidence.

Only stdlib validation executes here. Serialized artifact bytes are hashed,
never deserialized. The source run and controller run have separate identities.
"""

import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from validate_saved_evidence import Validator, require, read_json, validate_assertions

SOURCE_RUN = "37551528031"
MODEL = "e39bb2c4c248ac4699032d7053f7429213014e75"
FIXTURE_HASH = "0a01250de835a9e5067ac7f5e212fd8cb141b7a403262d6cc0e7cf9f97db2d96"
ORIGINAL_ERRORS = [
    "task main: main_new_member_yaml: unpermitted command failure 1",
    "task old_head: old_head_new_member_yaml: unpermitted command failure 4",
    "main_new_member_failures: preserved failure was not an assertion failure",
]
REPLACED = {
    "logs/main/summary.txt",
    "logs/main/main_new_member_yaml.log",
    "logs/main/main_new_member_yaml.time",
    "logs/main/main_new_member_failures.json",
    "logs/old_head/summary.txt",
    "logs/old_head/old_head_new_member_yaml.log",
    "logs/old_head/old_head_new_member_yaml.time",
}


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def args_for(path, metadata):
    return SimpleNamespace(
        evidence=path,
        run_metadata=metadata,
        run_id=SOURCE_RUN,
        expected_branch_sha=MODEL,
        years=[2026, 2025],
    )


def validate(root):
    original = root / "original-evidence"
    saved = root / "saved-evidence"
    continuation = root / "continuation"
    source_metadata = continuation / "source-run.json"
    before = Validator(args_for(original, source_metadata)).run()
    require(before["errors"] == ORIGINAL_ERRORS, "original failure set changed")
    require(
        before["known_name_case_wrapper_failure_only"],
        "source mutation wrapper provenance invalid",
    )
    for task, name in (
        ("main", "main_new_member_yaml"),
        ("old_head", "old_head_new_member_yaml"),
    ):
        log = (original / f"logs/{task}/{name}.log").read_text()
        require(
            "ImportPathMismatchError" in log and "conftest.py" in log,
            "original missing comparison is not the recorded import-path error",
        )
    manifest = read_json(continuation / "source-manifest.json")
    files = {
        str(path.relative_to(original)): path
        for path in original.rglob("*")
        if path.is_file()
    }
    require(set(files) == set(manifest), "source preservation manifest is incomplete")
    changed = set()
    for name, path in files.items():
        require(digest(path) == manifest[name], f"original evidence changed: {name}")
        target = saved / name
        require(target.is_file(), f"reused file missing: {name}")
        if digest(target) != manifest[name]:
            changed.add(name)
    require(changed == REPLACED, "missing or extra replacements in combined evidence")
    require(
        {str(path.relative_to(saved)) for path in saved.rglob("*") if path.is_file()}
        == set(files),
        "combined model/test artifact has unexpected extra files",
    )
    controller = read_json(continuation / "controller-run.json")
    planned = read_json(continuation / "controller.json")
    require(
        str(controller["databaseId"]) == planned["controller_run_id"],
        "controller run ID mismatch",
    )
    require(
        controller["headSha"] == planned["controller_sha"],
        "controller checkout mismatch",
    )
    require(
        controller["status"] == "in_progress",
        "cloud controller unexpectedly completed before validation",
    )
    require(
        planned["model_sha"] == MODEL and planned["source_run_id"] == SOURCE_RUN,
        "controller and tested model/source identities differ",
    )
    require(
        planned["phase"] == "two-missing-yaml-comparisons",
        "continuation ran an unrequested phase",
    )
    for task in ("main", "old_head"):
        receipt = read_json(continuation / f"{task}-receipt.json")
        require(receipt["code"] == task, "comparison receipt checkout label mismatch")
        require(
            receipt["controller_run_id"] == planned["controller_run_id"]
            and receipt["controller_sha"] == planned["controller_sha"],
            "comparison receipt controller mismatch",
        )
        require(
            receipt["runtime"] == read_json(original / f"logs/{task}/runtime.json"),
            "fresh comparison runtime differs from the original pinned runtime",
        )
        require(
            receipt["fixture_sha256"] == FIXTURE_HASH
            and receipt["collected"] == 16
            and receipt["wrapper_exit"] == 0,
            "comparison fixture/count/command failed",
        )
        require(
            "/member-fixtures/" in receipt["fixture"],
            "comparison did not use external fixture",
        )
        if task == "main":
            require(
                receipt["underlying_exit"] == 1
                and receipt["all_failures_are_call_assertions"],
                "main comparison lacks required assertions",
            )
            validate_assertions(receipt["failures"], "fresh main comparison")
            for target in (
                "mandatory dependent parent's income can eliminate",
                "same household with no income",
            ):
                validate_assertions(
                    receipt["failures"], "fresh main comparison", target
                )
        else:
            require(
                receipt["underlying_exit"] == 0
                and receipt["passed"] == 16
                and receipt["failures"] == [],
                "old head did not pass exactly 16 cases",
            )
    result = Validator(args_for(saved, source_metadata)).run()
    require(result["valid"], "combined evidence invalid: " + repr(result["errors"]))
    result.update(
        {
            "continuation_run": controller,
            "controller_completed": False,
            "controller_sha": planned["controller_sha"],
            "tested_model_sha": MODEL,
            "original_validation_errors": before["errors"],
            "replaced_files": sorted(changed),
            "preserved_source_files": len(files),
            "source_manifest_sha256": digest(continuation / "source-manifest.json"),
            "continuation_scope": "Only main and old-head YAML comparisons rerun; all other tests, households, mutation and microsimulation files reused byte-for-byte.",
            "limitations": [
                "The independent validator executes no model or tests; the continuation explicitly reruns only the two previously unusable YAML comparisons.",
                "All original microsimulation and completed test artifact bytes are preserved and hashed. Pickled arrays are not deserialized; paired identities, weights and intervention equality rely on the original successful comparator.",
                "Dataset bytes are not rehashed again. Recorded verified dataset digests are checked; the two fresh comparison receipts rehash their imported membership formulas and candidate fixture.",
                "The original source workflow remains failed; its two import-path errors are preserved, with separate new comparison receipts.",
                "The cloud validator verifies controller identity while it is active; completed-controller provenance must be independently checked after artifact download.",
                "Saved-evidence validation does not fix retained policy limitations or establish the normal PR CI result.",
            ],
        }
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(args.root)
    except Exception as error:
        result = {"valid": False, "errors": [str(error)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(
        json.dumps(
            {key: result.get(key) for key in ("valid", "errors", "continuation_scope")},
            indent=2,
        )
    )
    raise SystemExit(0 if result["valid"] else 1)
