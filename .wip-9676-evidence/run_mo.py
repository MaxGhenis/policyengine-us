"""Paired full-default-dataset Missouri TANF evidence for #9676.

Run from the tested checkout with its code first on PYTHONPATH:
    run_mo.py CODE OUTDIR SCENARIO --years 2026 [2025]

All entities in the certified default dataset remain in the simulation;
only saved diagnostic frames are filtered to Missouri. No subsampling,
weight rescaling, altered itemization, or structural overrides are used.
Each year's monthly diagnostics checkpoint before national annual TANF.
"""

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

EVIDENCE = Path(__file__).resolve().parent
DATASET_URI = "hf://datasets/policyengine/populace-us/populace_us_2024.h5@populace-us-2024-spm-20260909"
DATASET_SHA256 = "6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84"
START = time.time()


def log(out, message):
    # Linux reports KiB, macOS bytes.
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == "darwin" else rss * 1024
    line = f"[{time.time() - START:.1f}s peak_rss={rss_bytes / 1e9:.2f}GB] {message}"
    print(line, flush=True)
    with (out / "run_log.txt").open("a") as handle:
        handle.write(line + "\n")


def arr(sim, variable, period, **kwargs):
    return np.asarray(sim.calculate(variable, period, use_weights=False, **kwargs))


def digest(path):
    sha = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def save_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2))
    temporary.replace(path)


def save_frame(path, value):
    temporary = path.with_suffix(".tmp")
    pd.DataFrame(value).to_pickle(temporary)
    temporary.replace(path)


def run_year(code, out, scenario, year):
    import policyengine_us
    from policyengine_us import Microsimulation
    from policyengine_us.model_api import add
    from policyengine_us.system import (
        DEFAULT_DATASET,
        DEFAULT_DATASET_SHA256,
        _resolve_dataset_path,
    )

    tag = f"{code}_{scenario}_{year}"
    metadata_path = out / f"{tag}_meta.json"
    code_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    core = importlib.metadata.version("policyengine-core")
    assert core == "3.32.15", core
    assert DEFAULT_DATASET == DATASET_URI, DEFAULT_DATASET
    assert DEFAULT_DATASET_SHA256 == DATASET_SHA256, DEFAULT_DATASET_SHA256
    if os.environ.get("EXPECTED_CODE_SHA"):
        assert code_sha == os.environ["EXPECTED_CODE_SHA"]
    module = Path(policyengine_us.__file__).resolve()
    assert module.is_relative_to(Path.cwd().resolve()), module
    dataset_path = Path(_resolve_dataset_path(DEFAULT_DATASET)).resolve()
    dataset_hash = digest(dataset_path)
    assert dataset_hash == DATASET_SHA256, (dataset_path, dataset_hash)
    if metadata_path.exists():
        previous = json.loads(metadata_path.read_text())
        if previous.get("status") == "complete":
            assert previous["code_sha"] == code_sha
            assert previous["dataset_actual_sha256"] == dataset_hash
            assert previous["policyengine_core"] == core
            log(out, f"{tag}: completed matching checkpoint; skip")
            return

    metadata = {
        "code": code,
        "code_sha": code_sha,
        "scenario": scenario,
        "year": year,
        "policyengine_core": core,
        "policyengine_us_version": importlib.metadata.version("policyengine-us"),
        "python": platform.python_version(),
        "policyengine_us_file": str(module),
        "dataset_uri": DEFAULT_DATASET,
        "dataset_resolved_path": str(dataset_path),
        "dataset_expected_sha256": DATASET_SHA256,
        "dataset_actual_sha256": dataset_hash,
        "calculation_population": "full default dataset; saved frames contain Missouri only",
        "status": "started",
    }
    save_json(metadata_path, metadata)
    log(
        out, f"{tag}: verified dataset {dataset_hash}; building full default simulation"
    )
    build_start = time.time()
    sim = Microsimulation()
    metadata["build_seconds"] = time.time() - build_start
    pid = arr(sim, "person_id", year)
    ids = json.loads((EVIDENCE / "npcr_person_ids.json").read_text())
    assert len(ids) == 7 and len(set(ids)) == 7, ids
    mark = np.isin(pid, ids)
    assert int(mark.sum()) == len(ids), (int(mark.sum()), ids)
    metadata["marked_person_ids"] = ids if scenario != "unmodified" else []
    metadata["bank_assets_zeroed"] = 0.0
    if scenario in ("marked", "marked_no_assets"):
        # Retain all existing NPCR inputs, changing only the seven marks.
        baseline = np.array(
            arr(sim, "mo_tanf_is_non_parent_caretaker", year), dtype=bool
        )
        changed = baseline.copy()
        changed[mark] = True
        assert np.array_equal(changed[~mark], baseline[~mark])
        sim.set_input("mo_tanf_is_non_parent_caretaker", year, changed)
        metadata["baseline_npcr_true_count"] = int(baseline.sum())
        metadata["intervention_npcr_true_count"] = int(changed.sum())
        if scenario == "marked_no_assets":
            bank = np.array(arr(sim, "bank_account_assets", year), dtype=float)
            metadata["bank_assets_zeroed"] = float(bank[mark].sum())
            bank[mark] = 0
            # The historical sensitivity zeroes bank assets only.
            sim.set_input("bank_account_assets", year, bank)

    in_mo = arr(sim, "state_code", year, map_to="person", decode_enums=True) == "MO"
    in_mo_spm = np.asarray(
        sim.map_result(in_mo, "person", "spm_unit", how="any"), dtype=bool
    )
    assert np.all(in_mo[mark]), "all seven intervention people must be in Missouri"
    person = {
        "person_id": pid[in_mo],
        "household_id": arr(sim, "household_id", year, map_to="person")[in_mo],
        "spm_unit_id": arr(sim, "spm_unit_id", year, map_to="person")[in_mo],
        "tax_unit_id": arr(sim, "tax_unit_id", year, map_to="person")[in_mo],
        f"person_weight_{year}": np.asarray(sim.get_weights("age", year))[in_mo],
        "marked": mark[in_mo]
        if scenario != "unmodified"
        else np.zeros(int(in_mo.sum()), dtype=bool),
    }
    spm = {
        "spm_unit_id": arr(sim, "spm_unit_id", year)[in_mo_spm],
        f"spm_weight_{year}": np.asarray(sim.get_weights("mo_tanf", f"{year}-01"))[
            in_mo_spm
        ],
        f"takes_up_tanf_if_eligible_{year}": arr(
            sim, "takes_up_tanf_if_eligible", year
        )[in_mo_spm],
    }
    for variable in (
        "age",
        "own_children_in_household",
        "is_parent",
        "mo_tanf_is_parent_of_dependent_child",
        "mo_tanf_is_non_parent_caretaker",
        "is_tax_unit_head",
        "is_tax_unit_spouse",
        "is_tax_unit_dependent",
        "is_tax_unit_head_or_spouse",
        "is_in_secondary_school",
        "bank_account_assets",
    ):
        person[f"{variable}_{year}"] = arr(sim, variable, year)[in_mo]
    sources = list(
        sim.tax_benefit_system.parameters(
            f"{year}-01"
        ).gov.states.mo.dss.tanf.income.sources.unearned
    )
    metadata["unearned_sources"] = sources
    monthly_units = (
        "mo_tanf",
        "mo_tanf_eligible",
        "mo_tanf_assistance_unit_size",
        "mo_tanf_income_eligible",
        "mo_tanf_resources_eligible",
        "mo_tanf_non_parent_caretaker_included",
        "mo_tanf_standard_of_need",
        "mo_tanf_gross_earned_income",
        "mo_tanf_gross_unearned_income",
        "mo_tanf_countable_income",
        "mo_tanf_income_for_need_test",
        "mo_tanf_gross_income_eligible",
        "mo_tanf_standard_of_need_test",
        "mo_tanf_percentage_of_need_test",
        "mo_tanf_countable_resources",
    )
    annual_entitlement = np.zeros(int(in_mo_spm.sum()), dtype=float)
    for month in range(1, 13):
        period = f"{year}-{month:02d}"
        for variable in (
            "monthly_age",
            "mo_tanf_is_assistance_unit_member",
            "mo_tanf_dependent_child",
            "mo_tanf_non_parent_caretaker",
            "receives_ssi",
            "ssi",
            "tanf_gross_earned_income",
        ):
            person[f"{variable}_{year}_{month:02d}"] = arr(sim, variable, period)[in_mo]
        person[f"mo_unearned_{year}_{month:02d}"] = np.asarray(
            add(sim.person, period, sources)
        )[in_mo]
        for variable in monthly_units:
            spm[f"{variable}_{year}_{month:02d}"] = arr(sim, variable, period)[
                in_mo_spm
            ]
        spm[f"has_npcr_{year}_{month:02d}"] = np.asarray(
            sim.map_result(
                arr(sim, "mo_tanf_non_parent_caretaker", period),
                "person",
                "spm_unit",
                how="any",
            )
        )[in_mo_spm]
        annual_entitlement += spm[f"mo_tanf_{year}_{month:02d}"]
        # Each completed month is durable even if a later calculation fails.
        save_frame(out / f"{tag}_person.pkl", person)
        save_frame(out / f"{tag}_spm.pkl", spm)
        metadata["months_complete"] = month
        save_json(metadata_path, metadata)
        log(out, f"{tag}: month {month:02d} checkpointed")

    spm[f"mo_tanf_annual_{year}"] = annual_entitlement
    takeup = np.asarray(spm[f"takes_up_tanf_if_eligible_{year}"], dtype=bool)
    spm[f"mo_tanf_annual_takeup_{year}"] = annual_entitlement * takeup
    save_frame(out / f"{tag}_spm.pkl", spm)
    metadata["n_person_full"] = len(pid)
    metadata["n_spm_full"] = sim.populations["spm_unit"].count
    metadata["n_person_mo"] = int(in_mo.sum())
    metadata["n_spm_mo"] = int(in_mo_spm.sum())
    metadata["status"] = "monthly_complete"
    save_json(metadata_path, metadata)
    log(
        out,
        f"{tag}: monthly and annual entitlement saved; calculating annual national tanf",
    )
    try:
        # Keep the requested actual annual takeup-adjusted model output as
        # well as MO-only entitlement * takeup for diagnosing any divergence.
        annual_tanf = arr(sim, "tanf", year)
        spm[f"tanf_{year}"] = annual_tanf[in_mo_spm]
        metadata["tanf_all_states_weighted_sum"] = float(
            np.dot(annual_tanf, np.asarray(sim.get_weights("tanf", year)))
        )
        save_frame(out / f"{tag}_spm.pkl", spm)
        metadata["status"] = "complete"
    except Exception as error:
        metadata["annual_tanf_error"] = repr(error)
        save_json(metadata_path, metadata)
        raise
    metadata["elapsed_seconds"] = time.time() - START
    metadata["max_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )
    save_json(metadata_path, metadata)
    log(out, f"{tag}: complete")
    del sim
    gc.collect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("code", choices=("main", "branch"))
    parser.add_argument("outdir", type=Path)
    parser.add_argument(
        "scenario", choices=("unmodified", "marked", "marked_no_assets")
    )
    parser.add_argument("--years", nargs="+", type=int, default=[2026, 2025])
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    for requested_year in args.years:
        run_year(args.code, args.outdir, args.scenario, requested_year)
