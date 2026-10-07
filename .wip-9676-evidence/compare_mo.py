"""Validate and compare paired #9676 artifacts; no enum arrays are compared.

Usage: compare_mo.py OUTDIR --years 2026 2025
Artifacts may be flattened into OUTDIR from the six uploaded microsim jobs.
Write each available paired year's JSON; incomplete annual TANF is explicit
and causes a nonzero exit after the durable monthly results are reported.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

CORE = "3.32.15"
SHA256 = "6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84"
SCENARIOS = ("unmodified", "marked", "marked_no_assets")


def stats(before, after, weights, tolerance=0.0001):
    before = np.asarray(before, dtype=float)
    after = np.asarray(after, dtype=float)
    weights = np.asarray(weights, dtype=float)
    assert before.shape == after.shape == weights.shape
    assert np.isfinite(before).all() and np.isfinite(after).all()
    delta = after - before
    changed = np.abs(delta) > tolerance
    total = float(np.dot(before, weights))
    change = float(np.dot(delta, weights))
    return {
        "main_sum": total,
        "branch_sum": float(np.dot(after, weights)),
        "change": change,
        "percent_change": 100 * change / total if total else None,
        "records_changed": int(changed.sum()),
        "weighted_changed": float(weights[changed].sum()),
        "records_up": int((delta > tolerance).sum()),
        "records_down": int((delta < -tolerance).sum()),
        "sum_up": float(np.dot(delta[delta > tolerance], weights[delta > tolerance])),
        "sum_down": float(
            np.dot(delta[delta < -tolerance], weights[delta < -tolerance])
        ),
        "max_absolute_record_change": float(np.abs(delta).max(initial=0)),
    }


def failure_counts(income, resources, selected, weights):
    income = np.asarray(income, dtype=bool)
    resources = np.asarray(resources, dtype=bool)
    result = {}
    for name, mask in (
        ("income_only", ~income & resources),
        ("resources_only", income & ~resources),
        ("both_income_and_resources", ~income & ~resources),
        ("neither", income & resources),
    ):
        mask &= selected
        result[name] = {
            "records": int(mask.sum()),
            "weighted": float(weights[mask].sum()),
        }
    return result


def compare(out, scenario, year):
    tags = [f"{code}_{scenario}_{year}" for code in ("main", "branch")]
    metadata = [json.loads((out / f"{tag}_meta.json").read_text()) for tag in tags]
    for code, meta in zip(("main", "branch"), metadata):
        assert meta["code"] == code
        assert meta["scenario"] == scenario
        assert meta["year"] == year
        assert meta["policyengine_core"] == CORE
        assert meta["dataset_actual_sha256"] == SHA256
        assert meta["dataset_expected_sha256"] == SHA256
        assert meta["months_complete"] == 12, meta
    for key in (
        "dataset_uri",
        "python",
        "n_person_full",
        "n_spm_full",
        "n_person_mo",
        "n_spm_mo",
        "marked_person_ids",
        "bank_assets_zeroed",
    ):
        assert metadata[0][key] == metadata[1][key], (key, metadata)
    persons = [pd.read_pickle(out / f"{tag}_person.pkl") for tag in tags]
    units = [pd.read_pickle(out / f"{tag}_spm.pkl") for tag in tags]
    for key in (
        "person_id",
        "household_id",
        "spm_unit_id",
        "tax_unit_id",
        "marked",
        f"person_weight_{year}",
        f"mo_tanf_is_non_parent_caretaker_{year}",
        f"bank_account_assets_{year}",
    ):
        np.testing.assert_array_equal(persons[0][key], persons[1][key], err_msg=key)
    for key in (
        "spm_unit_id",
        f"spm_weight_{year}",
        f"takes_up_tanf_if_eligible_{year}",
    ):
        np.testing.assert_array_equal(units[0][key], units[1][key], err_msg=key)
    wp = persons[0][f"person_weight_{year}"].to_numpy()
    ws = units[0][f"spm_weight_{year}"].to_numpy()
    assert persons[0]["person_id"].is_unique and units[0]["spm_unit_id"].is_unique
    assert np.isfinite(wp).all() and np.isfinite(ws).all()
    assert (wp >= 0).all() and (ws >= 0).all()
    a, b = units
    pa, pb = persons
    result = {
        "metadata": metadata,
        "monthly": {},
        "person_diagnostics": {},
        "unit_diagnostics": {},
    }
    for key in pa.columns.intersection(pb.columns):
        if key.endswith((f"_{year}",)) or f"_{year}_" in key:
            if pd.api.types.is_numeric_dtype(pa[key]):
                result["person_diagnostics"][key] = stats(pa[key], pb[key], wp)
    for key in a.columns.intersection(b.columns):
        if key.endswith((f"_{year}",)) or f"_{year}_" in key:
            if pd.api.types.is_numeric_dtype(a[key]):
                result["unit_diagnostics"][key] = stats(a[key], b[key], ws)

    affected_ids = set()
    for month in range(1, 13):
        suffix = f"{year}_{month:02d}"
        membership = f"mo_tanf_is_assistance_unit_member_{suffix}"
        added = (~pa[membership].to_numpy(dtype=bool)) & pb[membership].to_numpy(
            dtype=bool
        )
        removed = pa[membership].to_numpy(dtype=bool) & (
            ~pb[membership].to_numpy(dtype=bool)
        )
        changed_ids = pa.loc[added | removed, "spm_unit_id"].to_numpy()
        affected_ids.update(changed_ids.tolist())
        selected = np.isin(a["spm_unit_id"], changed_ids)
        payment = f"mo_tanf_{suffix}"
        income = f"mo_tanf_income_eligible_{suffix}"
        resources = f"mo_tanf_resources_eligible_{suffix}"
        result["monthly"][f"{month:02d}"] = {
            "entitlement": stats(a[payment], b[payment], ws),
            "members_added": {
                "records": int(added.sum()),
                "weighted": float(wp[added].sum()),
            },
            "members_removed": {
                "records": int(removed.sum()),
                "weighted": float(wp[removed].sum()),
            },
            "units_with_membership_change": int(selected.sum()),
            "failures_among_membership_changed_units": {
                "main": failure_counts(a[income], a[resources], selected, ws),
                "branch": failure_counts(b[income], b[resources], selected, ws),
            },
            "new_income_failures": int(
                (
                    selected
                    & a[income].to_numpy(dtype=bool)
                    & ~b[income].to_numpy(dtype=bool)
                ).sum()
            ),
            "new_resource_failures": int(
                (
                    selected
                    & a[resources].to_numpy(dtype=bool)
                    & ~b[resources].to_numpy(dtype=bool)
                ).sum()
            ),
        }

    entitlement = f"mo_tanf_annual_{year}"
    result["annual_entitlement"] = stats(a[entitlement], b[entitlement], ws)
    result["annual_mo_entitlement_with_takeup"] = stats(
        a[f"mo_tanf_annual_takeup_{year}"], b[f"mo_tanf_annual_takeup_{year}"], ws
    )
    actual_tanf = f"tanf_{year}"
    annual_complete = (
        actual_tanf in a
        and actual_tanf in b
        and all(
            meta["status"] == "complete" and "tanf_all_states_weighted_sum" in meta
            for meta in metadata
        )
    )
    if annual_complete:
        result["annual_actual_tanf"] = stats(a[actual_tanf], b[actual_tanf], ws)
        result["annual_actual_tanf_all_states_change"] = (
            metadata[1]["tanf_all_states_weighted_sum"]
            - metadata[0]["tanf_all_states_weighted_sum"]
        )
    else:
        result["annual_actual_tanf"] = {
            "incomplete": True,
            "errors": [m.get("annual_tanf_error") for m in metadata],
        }

    delta = b[entitlement].to_numpy() - a[entitlement].to_numpy()
    weighted_delta = delta * ws
    order = np.argsort(-np.abs(weighted_delta))
    total_absolute = float(np.abs(weighted_delta).sum())
    result["two_largest_records_share_of_absolute_annual_change"] = (
        float(np.abs(weighted_delta[order[:2]]).sum() / total_absolute)
        if total_absolute
        else None
    )
    drivers = []
    selected = np.isin(a["spm_unit_id"], list(affected_ids)) | (np.abs(delta) > 0.0001)
    for i in order:
        if not selected[i]:
            continue
        record = {
            "spm_unit_id": int(a["spm_unit_id"].iloc[i]),
            "weight": float(ws[i]),
            "annual_main": float(a[entitlement].iloc[i]),
            "annual_branch": float(b[entitlement].iloc[i]),
            "annual_change_per_record": float(delta[i]),
            "annual_weighted_change": float(weighted_delta[i]),
            "takeup": bool(a[f"takes_up_tanf_if_eligible_{year}"].iloc[i]),
        }
        for code, frame in (("main", a), ("branch", b)):
            record[code] = {
                variable: float(frame[f"{variable}_{year}_01"].iloc[i])
                for variable in (
                    "mo_tanf_assistance_unit_size",
                    "mo_tanf_gross_earned_income",
                    "mo_tanf_gross_unearned_income",
                    "mo_tanf_countable_income",
                    "mo_tanf_countable_resources",
                    "mo_tanf_income_eligible",
                    "mo_tanf_resources_eligible",
                    "mo_tanf_non_parent_caretaker_included",
                )
            }
        drivers.append(record)
    result["membership_changed_or_payment_changed_records"] = drivers
    return result, annual_complete


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    parser.add_argument("--years", nargs="+", type=int, default=[2026, 2025])
    args = parser.parse_args()
    complete = True
    for year in args.years:
        reports = {}
        for scenario in SCENARIOS:
            try:
                report, annual_complete = compare(args.outdir, scenario, year)
                reports[scenario] = report
                complete &= annual_complete
            except FileNotFoundError as error:
                reports[scenario] = {"missing": str(error)}
                complete = False
        destination = args.outdir / f"compare_{year}.json"
        destination.write_text(json.dumps(reports, indent=2))
        print(destination, flush=True)
        for scenario, report in reports.items():
            print(
                scenario,
                json.dumps(
                    {
                        key: report.get(key)
                        for key in (
                            "annual_entitlement",
                            "annual_actual_tanf",
                            "two_largest_records_share_of_absolute_annual_change",
                            "missing",
                        )
                    }
                ),
                flush=True,
            )
    raise SystemExit(0 if complete else 1)
