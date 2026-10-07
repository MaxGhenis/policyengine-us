"""Validate #9676 saved CI JSON/log evidence using only Python's stdlib.

No model imports, pickle reads, dataset reads, tests, or microsimulations.
The only permitted command failure is the original new_member_mutations
wrapper's case-sensitive name-check error, with independently checked saved
assertion evidence. Every other missing, failed, or incomplete phase fails.
"""

import argparse
import ast
import json
import math
import re
from pathlib import Path

MAIN = "5b1d5bdf47044607341d76f3c932ba2e7b74a060"
OLD_HEAD = "a6c44418afccac0270dcb9ea155338dac0c9a05d"
EVIDENCE_HEAD = "e39bb2c4c248ac4699032d7053f7429213014e75"
CORE = "3.32.15"
DATASET_URI = "hf://datasets/policyengine/populace-us/populace_us_2024.h5@populace-us-2024-spm-20260909"
DATASET_HASH = "6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84"
MARK_IDS = [182870, 327890, 327891, 1040115, 1040116, 1327890, 1327891]
SCENARIOS = ("unmodified", "marked", "marked_no_assets")
GUARD_YAML = "explicit parent flag requires a dependent child"
GUARD_PYTHON = "test_parent_flag_needs_a_dependent_child_in_the_persons_tax_unit"
NPCR_PYTHON = "test_non_parent_caretaker_identification_matches_independent_rule"
KNOWN_MESSAGE = (
    "intended detecting case missing: Explicit parent flag requires a dependent child"
)
TASKS = {
    "suites": (
        "runtime_identity",
        "mo_tanf_yaml",
        "property_suites",
        "explicit_source_roles",
        "input_definitions",
        "partner_contracts",
        "household_checks",
        "known_resource_defect",
    ),
    "mutations": (
        "runtime_identity",
        "new_member_mutations",
        "old_member_mutations",
        "new_property_mutations",
        "old_property_mutations",
    ),
    "main": (
        "runtime_identity",
        "main_new_member_yaml",
        "main_household_checks",
        "main_known_resource_defect",
    ),
    "old_head": (
        "runtime_identity",
        "old_head_new_member_yaml",
        "old_head_household_checks",
    ),
}
MUTATIONS = {
    "new_member_mutations": {"none": 0, "drop_has_dependent_child": 1},
    "old_member_mutations": {"none": 0, "drop_has_dependent_child": 0},
    "new_property_mutations": {
        "none": 0,
        "drop_has_dependent_child": 1,
        "npcr_never": 1,
    },
    "old_property_mutations": {
        "none": 0,
        "drop_has_dependent_child": 0,
        "npcr_never": 0,
    },
}
MONTHLY_UNITS = (
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
    "has_npcr",
)
MONTHLY_PERSONS = (
    "monthly_age",
    "mo_tanf_is_assistance_unit_member",
    "mo_tanf_dependent_child",
    "mo_tanf_non_parent_caretaker",
    "receives_ssi",
    "ssi",
    "tanf_gross_earned_income",
    "mo_unearned",
)


class InvalidEvidence(Exception):
    pass


def require(condition, message):
    if not condition:
        raise InvalidEvidence(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def close(a, b):
    return finite(a) and finite(b) and math.isclose(a, b, rel_tol=1e-10, abs_tol=0.02)


def read_text(path):
    require(path.is_file(), f"missing file: {path}")
    require(
        0 < path.stat().st_size < 25_000_000, f"empty or excessive text file: {path}"
    )
    return path.read_text()


def read_json(path):
    def reject_constant(value):
        raise InvalidEvidence(f"nonfinite JSON constant {value} in {path}")

    return json.loads(read_text(path), parse_constant=reject_constant)


def validate_assertions(records, label, target=None):
    require(
        isinstance(records, list) and bool(records), f"{label}: no recorded assertions"
    )
    for record in records:
        require(record.get("when") == "call", f"{label}: non-call failure")
        require(record.get("assertion") is True, f"{label}: non-assertion failure")
        require(
            record.get("exception") == "AssertionError",
            f"{label}: unexpected exception",
        )
        require(
            bool(record.get("nodeid")) and bool(record.get("test_name")),
            f"{label}: missing failure provenance",
        )
    if target:
        require(
            any(
                target.casefold() in record["test_name"].casefold()
                for record in records
            ),
            f"{label}: intended detecting case absent: {target}",
        )


def validate_stats(stats, label, maximum_records=None):
    require(
        isinstance(stats, dict) and not stats.get("incomplete"),
        f"{label}: incomplete statistics",
    )
    for key in (
        "main_sum",
        "branch_sum",
        "change",
        "weighted_changed",
        "sum_up",
        "sum_down",
        "max_absolute_record_change",
    ):
        require(finite(stats.get(key)), f"{label}: missing/nonfinite {key}")
    require(
        close(stats["branch_sum"] - stats["main_sum"], stats["change"]),
        f"{label}: inconsistent aggregate difference",
    )
    # The saved comparator omits per-record changes <= 0.0001 from these
    # two direction totals, while retaining them in aggregate change.
    require(
        stats["sum_up"] >= 0 and stats["sum_down"] <= 0,
        f"{label}: invalid directional totals",
    )
    for key in ("records_changed", "records_up", "records_down"):
        require(
            type(stats.get(key)) is int and stats[key] >= 0, f"{label}: invalid {key}"
        )
        if maximum_records is not None:
            require(stats[key] <= maximum_records, f"{label}: excessive {key}")
    require(
        stats["records_up"] + stats["records_down"] == stats["records_changed"],
        f"{label}: inconsistent changed record count",
    )
    require(
        stats["weighted_changed"] >= 0 and stats["max_absolute_record_change"] >= 0,
        f"{label}: negative magnitude",
    )


class Validator:
    def __init__(self, args):
        self.args = args
        self.root = args.evidence.resolve()
        self.errors = []
        self.validated = []
        self.known_wrapper_failure = False
        self.branch_sha = args.expected_branch_sha
        self.run_metadata = None
        self.runtime = {}
        self.metadata = {}
        self.mutation_provenance = {}
        self.impact_summary = {}

    def section(self, name, callback):
        try:
            callback()
            self.validated.append(name)
        except (
            InvalidEvidence,
            OSError,
            ValueError,
            KeyError,
            TypeError,
            IndexError,
        ) as error:
            self.errors.append(f"{name}: {error}")

    def source_run(self):
        if self.args.run_metadata:
            meta = read_json(self.args.run_metadata)
            require(
                str(meta["databaseId"]) == str(self.args.run_id),
                "source run ID mismatch",
            )
            require(meta["status"] == "completed", "source run is not completed")
            require(
                meta["conclusion"] in ("success", "failure"),
                "source run was cancelled, skipped, or timed out",
            )
            require(
                re.fullmatch(r"[0-9a-f]{40}", meta["headSha"]) is not None,
                "invalid source head SHA",
            )
            if self.branch_sha:
                require(
                    self.branch_sha == meta["headSha"],
                    "expected branch SHA differs from source run",
                )
            self.branch_sha = meta["headSha"]
            self.run_metadata = meta
        if self.branch_sha is None:
            self.branch_sha = read_json(self.root / "logs/suites/runtime.json")[
                "code_sha"
            ]
        require(
            re.fullmatch(r"[0-9a-f]{40}", self.branch_sha) is not None,
            "invalid evidence branch SHA",
        )

    def mutation(self, name):
        evidence = read_json(self.root / f"logs/mutations/{name}.json")
        expected = MUTATIONS[name]
        require(
            evidence["actual"] == expected and evidence["expected"] == expected,
            "mutation actual/expected maps differ from required maps",
        )
        require(
            all(type(value) is int for value in evidence["actual"].values()),
            "mutation exit codes are not integers",
        )
        require(
            set(evidence["failures"]) == set(expected),
            "missing/extra mutation failure lists",
        )
        for mutation, code in expected.items():
            records = evidence["failures"][mutation]
            if code == 0:
                require(
                    records == [], f"passing mutation {mutation} has failure records"
                )
            else:
                target = (
                    NPCR_PYTHON
                    if mutation == "npcr_never"
                    else GUARD_YAML
                    if name == "new_member_mutations"
                    else GUARD_PYTHON
                )
                validate_assertions(records, f"{name}/{mutation}", target)
        self.mutation_provenance[name] = evidence["failures"]

    def task(self, task):
        folder = self.root / "logs" / task
        lines = read_text(folder / "summary.txt").splitlines()
        expected_names = TASKS[task]
        results = []
        flags = []
        for line in lines:
            match = re.fullmatch(r"(\S+) actual=(\d+) expected=(\d+)", line)
            flag = re.fullmatch(r"Unexpected result flag: ([01])", line)
            require(
                match is not None or flag is not None,
                f"unexpected summary line: {line}",
            )
            if match:
                results.append((match[1], int(match[2]), int(match[3])))
            else:
                flags.append(int(flag[1]))
        require(
            tuple(name for name, _, _ in results) == expected_names,
            "missing, extra, reordered, or duplicated command results",
        )
        require(len(flags) == 1, "missing/duplicate task status flag")
        for name, actual, expected in results:
            require(expected == 0, f"unexpected required command code for {name}")
            log = read_text(folder / f"{name}.log")
            timing = read_text(folder / f"{name}.time")
            require(
                re.search(rf"Exit status: {actual}\s*$", timing, re.MULTILINE)
                is not None,
                f"{name}: timing exit differs from summary",
            )
            if actual != 0:
                require(
                    task == "mutations"
                    and name == "new_member_mutations"
                    and actual == 1,
                    f"{name}: unpermitted command failure {actual}",
                )
                require(
                    name in self.mutation_provenance,
                    "known wrapper failure has unvalidated mutation assertions",
                )
                error_lines = [
                    line
                    for line in log.splitlines()
                    if line.startswith("UNEXPECTED MUTATION RESULTS ")
                ]
                require(
                    len(error_lines) == 1,
                    "known wrapper failure lacks unique recorded reason",
                )
                reason = ast.literal_eval(
                    error_lines[0].removeprefix("UNEXPECTED MUTATION RESULTS ")
                )
                require(
                    reason == {"drop_has_dependent_child": KNOWN_MESSAGE},
                    "wrapper failed for an additional/different reason",
                )
                self.known_wrapper_failure = True
            if task == "suites" and name in ("mo_tanf_yaml", "partner_contracts"):
                count = re.search(r"Total test files: (\d+)", log)
                require(
                    count is not None and int(count[1]) > 0 and "Workers: 1" in log,
                    f"{name}: missing nonempty single-worker batch evidence",
                )
                batches = re.findall(
                    r"^\s*Batch \d+:.*\|\s*(passed|failed)\s*$", log, re.MULTILINE
                )
                require(
                    bool(batches) and all(state == "passed" for state in batches),
                    f"{name}: missing/failed batch results",
                )
            if task == "suites" and name in ("property_suites", "input_definitions"):
                require(
                    re.search(r"\b[1-9]\d* passed\b", log) is not None,
                    f"{name}: no nonempty pytest pass count",
                )
            if name == "explicit_source_roles":
                for test in (
                    "test_membership_matches_the_restated_rule",
                    NPCR_PYTHON,
                    "test_a_dependent_parent_member_excludes_the_non_parent_caretaker",
                    "test_unit_income_is_members_income",
                ):
                    require(
                        f"PASS {test} with explicit canonical source roles" in log,
                        f"missing source-role check: {test}",
                    )
            if name == "old_head_new_member_yaml":
                require(
                    re.search(r"\b16 passed\b", log) is not None,
                    "old-head comparison lacks all 16 member cases",
                )
        expected_flag = 1 if task == "mutations" and self.known_wrapper_failure else 0
        require(
            flags == [expected_flag],
            "task status does not match permitted command outcomes",
        )
        runtime = read_json(folder / "runtime.json")
        expected_sha = (
            MAIN
            if task == "main"
            else OLD_HEAD
            if task == "old_head"
            else self.branch_sha
        )
        require(
            runtime["code_sha"] == expected_sha,
            "runtime imported the wrong checkout SHA",
        )
        require(
            runtime["policyengine_core"] == CORE
            and runtime["python"].startswith("3.14."),
            "runtime core/Python version mismatch",
        )
        checkout = task if task in ("main", "old_head") else "wip"
        require(
            f"/{checkout}/policyengine_us/" in runtime["policyengine_us_file"],
            "runtime imported the wrong checkout path",
        )
        require(
            re.fullmatch(r"[0-9a-f]{64}", runtime["membership_formula_sha256"])
            is not None,
            "invalid formula hash",
        )
        self.runtime[task] = runtime

    def preserved_failure(self, task, name, targets):
        evidence = read_json(self.root / f"logs/{task}/{name}.json")
        require(
            evidence["actual_exit_code"] == 1
            and evidence["expected_assertion_failure"] is True,
            "preserved failure was not an assertion failure",
        )
        validate_assertions(evidence["failures"], name)
        for target in targets:
            validate_assertions(evidence["failures"], name, target)

    def household_checks(self, task, filename, label):
        evidence = read_json(self.root / f"logs/{task}/{filename}.json")
        require(evidence["label"] == label, "household comparison label mismatch")
        checkout = task if task in ("main", "old_head") else "wip"
        require(
            f"/{checkout}/policyengine_us/" in evidence["module"],
            "household comparison imported wrong checkout",
        )
        require(
            set(evidence["cases"])
            == {
                "regression_unmarked_grandparent",
                "regression_dependent_45_adult_child",
                "resource_fixture_a_excluded_grandparent_assets",
                "resource_fixture_b_included_npcr_spouse_assets",
                "income_loss_disability_14400",
                "income_loss_zero_income_pair",
            },
            "household comparison cases missing/extra",
        )
        for name, case in evidence["cases"].items():
            count = len(case["people"])
            require(
                count > 0 and len(set(case["people"])) == count,
                f"{name}: invalid people list",
            )
            for variable in ("member", "parent_flag", "npcr"):
                require(
                    len(case[variable]) == count
                    and all(type(value) is bool for value in case[variable]),
                    f"{name}: incomplete/nonboolean {variable}",
                )
            require(
                len(case["ssi"]) == count
                and all(finite(value) for value in case["ssi"]),
                f"{name}: invalid SSI diagnostic",
            )
            for variable in (
                "npcr_included",
                "size",
                "gross_unearned",
                "countable_income",
                "standard_of_need",
                "countable_resources",
                "resources_eligible",
                "mo_tanf",
            ):
                require(finite(case[variable]), f"{name}: missing/nonfinite {variable}")

    def impact(self, code, scenario, year):
        tag = f"{code}_{scenario}_{year}"
        meta = read_json(self.root / f"out/{tag}_meta.json")
        require(
            (meta["code"], meta["scenario"], meta["year"]) == (code, scenario, year),
            "artifact tag identity mismatch",
        )
        require(
            meta["code_sha"] == (MAIN if code == "main" else self.branch_sha),
            "impact checkout SHA mismatch",
        )
        require(
            meta["policyengine_core"] == CORE and meta["python"].startswith("3.14."),
            "impact core/Python mismatch",
        )
        require(meta["dataset_uri"] == DATASET_URI, "wrong default dataset URI")
        require(
            meta["dataset_actual_sha256"]
            == meta["dataset_expected_sha256"]
            == DATASET_HASH,
            "dataset digest mismatch",
        )
        require(
            meta["status"] == "complete" and meta["months_complete"] == 12,
            "monthly/annual impact is incomplete",
        )
        require(
            "annual_tanf_error" not in meta
            and finite(meta["tanf_all_states_weighted_sum"]),
            "missing/failed annual actual TANF",
        )
        require(
            meta["calculation_population"]
            == "full default dataset; saved frames contain Missouri only",
            "population scope mismatch",
        )
        for entity in ("person", "spm"):
            full, mo = meta[f"n_{entity}_full"], meta[f"n_{entity}_mo"]
            require(
                type(full) is int and type(mo) is int and 0 < mo <= full,
                "invalid entity counts",
            )
            frame = self.root / f"out/{tag}_{entity}.pkl"
            require(
                frame.is_file() and frame.stat().st_size > 0,
                "missing/empty saved frame",
            )
        require(
            meta["marked_person_ids"] == ([] if scenario == "unmodified" else MARK_IDS),
            "wrong intervention source IDs",
        )
        require(
            finite(meta["bank_assets_zeroed"]) and meta["bank_assets_zeroed"] >= 0,
            "invalid bank-asset sensitivity amount",
        )
        if scenario != "marked_no_assets":
            require(
                meta["bank_assets_zeroed"] == 0, "unexpected asset-zeroing intervention"
            )
        self.metadata[tag] = meta

    def comparison(self, year):
        report = read_json(self.root / f"out/compare_{year}.json")
        require(set(report) == set(SCENARIOS), "comparison is missing a scenario")
        for scenario, result in report.items():
            require("missing" not in result, "scenario comparison is missing artifacts")
            metas = [
                self.metadata[f"{code}_{scenario}_{year}"]
                for code in ("main", "branch")
            ]
            require(
                result["metadata"] == metas,
                "comparison metadata differs from validated source artifacts",
            )
            for key in (
                "python",
                "dataset_uri",
                "dataset_actual_sha256",
                "n_person_full",
                "n_spm_full",
                "n_person_mo",
                "n_spm_mo",
                "marked_person_ids",
                "bank_assets_zeroed",
            ):
                require(
                    metas[0][key] == metas[1][key], f"paired metadata differs: {key}"
                )
            for key in (
                "annual_entitlement",
                "annual_mo_entitlement_with_takeup",
                "annual_actual_tanf",
            ):
                validate_stats(
                    result[key], f"{scenario}/{year}/{key}", metas[0]["n_spm_mo"]
                )
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
                "person_weight",
            ):
                validate_stats(
                    result["person_diagnostics"][f"{variable}_{year}"],
                    f"{variable}/{year}",
                    metas[0]["n_person_mo"],
                )
            require(
                close(
                    result["annual_actual_tanf_all_states_change"],
                    metas[1]["tanf_all_states_weighted_sum"]
                    - metas[0]["tanf_all_states_weighted_sum"],
                ),
                "national TANF difference is inconsistent",
            )
            require(
                set(result["monthly"]) == {f"{m:02d}" for m in range(1, 13)},
                "comparison lacks all twelve months",
            )
            for month, monthly in result["monthly"].items():
                validate_stats(
                    monthly["entitlement"],
                    f"{scenario}/{year}/{month}/entitlement",
                    metas[0]["n_spm_mo"],
                )
                for variable in MONTHLY_UNITS:
                    validate_stats(
                        result["unit_diagnostics"][f"{variable}_{year}_{month}"],
                        f"{variable}/{year}/{month}",
                        metas[0]["n_spm_mo"],
                    )
                for variable in MONTHLY_PERSONS:
                    validate_stats(
                        result["person_diagnostics"][f"{variable}_{year}_{month}"],
                        f"{variable}/{year}/{month}",
                        metas[0]["n_person_mo"],
                    )
                changed_units = monthly["units_with_membership_change"]
                require(
                    type(changed_units) is int
                    and 0 <= changed_units <= metas[0]["n_spm_mo"],
                    "invalid changed-unit count",
                )
                for code in ("main", "branch"):
                    failures = monthly["failures_among_membership_changed_units"][code]
                    require(
                        set(failures)
                        == {
                            "income_only",
                            "resources_only",
                            "both_income_and_resources",
                            "neither",
                        },
                        "failure causes are not separated",
                    )
                    require(
                        sum(row["records"] for row in failures.values())
                        == changed_units,
                        "failure counts do not partition affected units",
                    )
                    require(
                        all(
                            type(row["records"]) is int
                            and row["records"] >= 0
                            and finite(row["weighted"])
                            and row["weighted"] >= 0
                            for row in failures.values()
                        ),
                        "invalid failure-cause counts",
                    )
                causes = monthly["failures_among_membership_changed_units"]
                require(
                    close(
                        sum(row["weighted"] for row in causes["main"].values()),
                        sum(row["weighted"] for row in causes["branch"].values()),
                    ),
                    "failure-cause weighted totals differ between paired codes",
                )
            for key in ("main_sum", "branch_sum", "change"):
                require(
                    close(
                        sum(
                            month["entitlement"][key]
                            for month in result["monthly"].values()
                        ),
                        result["annual_entitlement"][key],
                    ),
                    f"monthly {key} does not reconcile to annual",
                )
            share = result["two_largest_records_share_of_absolute_annual_change"]
            require(
                share is None or finite(share) and 0 <= share <= 1,
                "invalid two-record dominance statistic",
            )
            drivers = result["membership_changed_or_payment_changed_records"]
            require(
                isinstance(drivers, list)
                and len({row["spm_unit_id"] for row in drivers}) == len(drivers),
                "invalid/duplicate driver records",
            )
            for driver in drivers:
                require(
                    finite(driver["weight"])
                    and driver["weight"] >= 0
                    and type(driver["takeup"]) is bool,
                    "invalid driver weight/takeup",
                )
                require(
                    close(
                        driver["annual_branch"] - driver["annual_main"],
                        driver["annual_change_per_record"],
                    ),
                    "driver annual difference is inconsistent",
                )
                require(
                    close(
                        driver["weight"] * driver["annual_change_per_record"],
                        driver["annual_weighted_change"],
                    ),
                    "driver weighted change is inconsistent",
                )
                for code in ("main", "branch"):
                    require(
                        all(finite(value) for value in driver[code].values()),
                        "nonfinite driver diagnostic",
                    )
            self.impact_summary[f"{scenario}_{year}"] = {
                key: result[key]
                for key in (
                    "annual_entitlement",
                    "annual_actual_tanf",
                    "annual_actual_tanf_all_states_change",
                    "two_largest_records_share_of_absolute_annual_change",
                )
            }

    def final_status(self):
        tests = read_text(self.root / "logs/tests_status.txt").strip()
        require(
            tests == ("1" if self.known_wrapper_failure else "0"),
            "aggregate tests status contains an unpermitted failure",
        )
        require(
            read_text(self.root / "out/impact_status.txt").strip() == "0",
            "impact phase failed",
        )
        require(
            read_text(self.root / "out/compare_status.txt").strip() == "0",
            "comparison phase failed",
        )
        require(
            self.runtime["suites"] == self.runtime["mutations"],
            "branch test tasks imported different code",
        )
        if self.run_metadata:
            require(
                self.run_metadata["conclusion"]
                == ("failure" if self.known_wrapper_failure else "success"),
                "source conclusion is inconsistent with the only permitted wrapper failure",
            )

    def run(self):
        self.section("source-run provenance", self.source_run)
        for name in MUTATIONS:
            self.section(name, lambda name=name: self.mutation(name))
        for task in TASKS:
            self.section(f"task {task}", lambda task=task: self.task(task))
        for task, filename, label in (
            ("suites", "household_branch", "branch"),
            ("main", "household_main", "main"),
            ("old_head", "household_old_head", "old_head"),
        ):
            self.section(
                filename,
                lambda task=task, filename=filename, label=label: self.household_checks(
                    task, filename, label
                ),
            )
        resource = "excluded grandparent's separately owned assets do not count"
        for task, name, targets in (
            ("suites", "known_resource_defect", [resource]),
            ("main", "main_known_resource_defect", [resource]),
            (
                "main",
                "main_new_member_failures",
                [
                    "mandatory dependent parent's income can eliminate",
                    "same household with no income",
                ],
            ),
        ):
            self.section(
                name,
                lambda task=task, name=name, targets=targets: self.preserved_failure(
                    task, name, targets
                ),
            )
        for year in self.args.years:
            for scenario in SCENARIOS:
                for code in ("main", "branch"):
                    self.section(
                        f"impact {code}/{scenario}/{year}",
                        lambda code=code, scenario=scenario, year=year: self.impact(
                            code, scenario, year
                        ),
                    )
            self.section(
                f"paired comparison {year}", lambda year=year: self.comparison(year)
            )
        self.section("aggregate phase status", self.final_status)
        return {
            "valid": not self.errors,
            "source_run_id": str(self.args.run_id),
            "source_run": self.run_metadata,
            "evidence_branch_sha": self.branch_sha,
            "years_required": self.args.years,
            "known_name_case_wrapper_failure_only": self.known_wrapper_failure,
            "validated_sections": self.validated,
            "errors": self.errors,
            "mutation_assertion_provenance": self.mutation_provenance,
            "impacts": self.impact_summary,
            "limitations": [
                "No model, dataset, tests or microsimulations were rerun.",
                "Pickled arrays are not read; entity alignment, weights and intervention vector equality rely on the successfully generated paired comparison report.",
                "Dataset bytes and formula contents are not rehashed; recorded verified digests and source-run checkout identity are checked.",
                "Source-run provenance is independently checked only when --run-metadata is supplied.",
                "This validates saved evidence; it does not change the original workflow's conclusion or fix retained policy limitations.",
            ],
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "evidence", type=Path, help="downloaded artifact root containing logs/ and out/"
    )
    parser.add_argument("--run-id", default="37551528031")
    parser.add_argument("--run-metadata", type=Path)
    parser.add_argument("--expected-branch-sha", default=EVIDENCE_HEAD)
    parser.add_argument("--years", nargs="+", type=int, default=[2026, 2025])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = Validator(args).run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "valid",
                    "source_run_id",
                    "evidence_branch_sha",
                    "known_name_case_wrapper_failure_only",
                    "errors",
                )
            },
            indent=2,
        )
    )
    raise SystemExit(0 if result["valid"] else 1)
