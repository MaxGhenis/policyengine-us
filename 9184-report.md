# PR #9184 resume report

Feature head: `b24094b166c4f9410b74befec727d33541d48713`, already published on `PolicyEngine/policyengine-us:ltss-financial-eligibility`. This resume audited and reused the previous attempt's recovery and CI; it made no further model or partner-test changes. The PR remains open and was not merged.

## Recovery and fixes

- Reused `dd679e82a2` (complete backup tree), `afd7d0cb33` (main merge), `f6afddd041` (Delaware input contract and registry), and `b24094b166` (main merge through `6b80a8e447`). All were already pushed. The incomplete saved patch was not reapplied. A writable `merge-tree --write-tree` check of backup versus that main snapshot succeeded without conflicts (tree `2aced7e7d01ad3450d000b65a4f2bebe204c7c19`).
- Preserved all ten obsolete parameter deletions, canonical SSI-derived SIL/resource thresholds, and backup CSRA Cases 13–18 byte-for-byte. No additional implementation gap was found.
- January/June MMMNA uses the operative $2,643.75 federal minimum and $4,066.50 Texas maximum; July uses $2,705. Regression: financial `medicaid_ltss_mmmna.yaml:315`, `:361`. The suggested pre-July zero is inconsistent with the effective standards.
- Delaware's monthly Person Boolean `medicaid_ltss_income_disregards_already_applied` defaults false. True supplies final countable income and skips the second $20 deduction (`is_medicaid_ltss_income_eligible.py:64`). Ordered earned exclusions and community-spouse sole-$20 budgeting are documented. Regression `is_medicaid_ltss_income_eligible.yaml:606` expects `[true, false, false, true]` for final $2,485/$2,486, spousal $5,035, and raw unearned $2,505.
- Existing Delaware couple tests already cover a single $20 disregard, including exact $3,727.50/$3,747.50 boundaries (`income YAML:171`, `:291`).
- Preserved floor/half/cap resource boundaries and +$1 failures (`resource YAML:619` onward), sole-resource composite failure (`composite YAML:302`), and unsupported December 2025 (`:403`).
- Preserved independent statutory equity screening, negative-equity flooring, exception priority, invalid-share failure without an exception, CPI-U indexing/nearest-$1,000 rounding, and the 2028 ceiling without replacing the indexed minimum. The annual equity chassis divergence has separate follow-up [#9895](https://github.com/PolicyEngine/policyengine-us/issues/9895), referenced in `medicaid_ltss_home_equity_eligible.py:25`.
- Separate partial HHS/Healthcare registry entry covers TX/DE/WA, verified 2026 (`policyengine_us/programs.yaml:175`); existing Medicaid status remains complete.
- Pinned DSSM citations use the 73-page export and corrected section/page mappings; the Delaware resource notice points to page 2. WA's CSRA floor begins July 2025. Stock/rate units and canonical parameter reuse remain intact.
- Existing ABD categorization, disabled-waiver regression, Delaware hospital exclusion, bounded geography/service scope, and disclosed court/hearing, agricultural-equity, and WA excess-resource limitations remain intact.

The PR body was updated successfully with the detailed reviewer-response mapping, methodology choices, CI evidence, pending impact status, and file/line references. DTrim99's changes-requested review remains uncleared; the hub must request re-review.

## Verified tests

Reused Linux CI on the exact feature head, [Actions run 37504243982](https://github.com/PolicyEngine/policyengine-us/actions/runs/37504243982). All 30 check runs succeeded. Downloaded logs are in `.resume-evidence/`; these are CI results, not local reruns.

| Coverage | Passed |
|---|---:|
| Composite YAML | 10 |
| Income YAML | 13 |
| CSRA/resources YAML | 18 |
| Pathway YAML | 15 |
| Equity YAML | 14 |
| MMMNA YAML | 9 |
| SSI-derived SIL YAML | 2 |
| **Financial YAML total** | **81** |
| LTSS invariant/property tests | 18 |
| All HHS baseline YAML (includes Medicaid) | 1,250 |
| API partner contracts | 620 |

Partner coverage includes Amplifi 2025/2026, My Friend Ben 2025, Impactica 2025, and analytics healthcare. No partner failures appeared in these logs, and no partner expected outputs were edited. Registry integrity checks also passed in the Python job. Local `make format` passed during this resume (6,825 Python files unchanged; lint exit 0), using the prior venv with offline/no-sync settings. The Python 3.13 venv produced a compatibility warning against the checkout's Python 3.14 preference; no environment was changed. Invariant timing evidence includes 1.16 seconds shared-fixture setup and individual future-year calls around 0.06–0.23 seconds; no before/after benchmark or per-file peak-memory measurement was obtained.

The newly supplied regressions were not rerun against the old published head in this resume. Before/after execution evidence remains pending; the spec's earlier old-head observations are not relabeled as fresh runs.

## Impact and remaining work

Real default-dataset main/branch impact runs for **2026 and 2028 remain pending**. No empirical person/dollar comparison is claimed. The dependency audit expects exactly zero changes in `is_medicaid_eligible`, `medicaid`, `household_health_benefits`, `household_net_income`, and `household_net_income_including_health_benefits`, because existing consumers do not use the new screens. This expectation is unmeasured.

Branch-only monthly dataset summaries for January/June/July 2026 and January 2027/2028, and supplied-input sensitivity cohorts, also remain pending. The new variables are absent on main; no zero-valued main comparator was fabricated. Unsupported default setting/AU inputs fail closed, so these screens do not establish a national LTSS caseload estimate. The documented supplied-input examples imply pre-July allowance increases of about $2,644–$4,067/month without a composite eligibility effect, and future SSI/CPI growth bands may admit additional supplied applicants; national caseload size is unknown.

The mandatory host runner was attempted and exited 75: this sandbox denies `ps`, so `heavy_run.sh` cannot verify nice 0. Python independently reports the current process at nice 0, but that does not authorize bypassing the runner. The shared lock, hub output/report directories, and the assigned worktree's original Git metadata are outside the writable roots. No locked test/microsimulation was started. GitHub connectivity was intermittent; failed read operations were retried with backoff.

Git metadata used for this resume is isolated in `.resume-git/` within the assigned workspace, with read-only object reuse from the original repository. The caller's checkout, previous worktree, and repository metadata were not written. This report is retained in the assigned workspace because `~/reviews/us-hub/fixes/9184-report.md` is outside the writable roots.

## Methodology choices for Max

- **WA rounding:** retained the recommended federal arithmetic: $2,850.625 at January shelter $1,000 versus the state chart's rounded-input $2,850.
- **Standalone equity:** retained the independent statutory screen; composite eligibility applies the pathway gate.
- **Couple budgeting:** caller chooses the permitted unit; AU=2 supplies combined totals on each applicant, while community-spouse/AU=1 inputs are separately attributed.
- **Earned income:** retained the explicit final-countable-input flag; the statutory deduction order is preserved.

`axiom: needed` — no completed parity proof was found. No encoder run was initiated.

To finish: run old-head regressions and locked 2026/2028 impacts in an environment that can use the host runner and shared lock, add measured results to the PR body/report, complete Axiom follow-up, and obtain DTrim99 clearance. Do not merge as part of this job.
