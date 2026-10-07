# #9676 fix-round evidence report

Recovered prior head: `aec34394e4`. Original reviewed PR head: `a6c44418af`. This audit read the C spec, saved current-head review, saved primary Missouri law/manual sources, previous job tail, prior worktree files, and `~/reviews/us-hub/fixes/9676-evidence`. No model, partner, or Git files were edited by the evidence auditor.

The prior implementation preserves main's #9741 NPCR `get_override_branch` helpers. The requested build retains the membership formula and explicit-input contract, with new tests and corrected documentation. There is no new policy or methodology choice needed within that scope. The school-enrolled 18-year-old grouping and relationship imputation remain declared interpretations/limits.

## Findings and resolution

| Finding | Recovered change or required disclosure | Evidence status |
|---|---|---|
| 1. Missing own-tax-unit dependent-child guard coverage | Two-tax-unit YAML case and dedicated Python property require `[true,true,false]`, size two, `$234.08628`. Removing `has_dependent_child` must produce a failure. | Member YAML: 16 passed. **[PENDING FRESH MUTATION RESULT]** |
| 2. Two undisclosed default regressions | Body gives both new zero-income overpayments, exact before/after membership and payments. Relationship-inference correction remains a separate follow-up. | Hand-computed and saved 2026-09-29 review; **[PENDING FRESH MAIN/BRANCH HOUSEHOLD RESULTS]** |
| 3. Excluded grandparent assets | Preserve the legal `$5,000` asset counterexample outside the passing suite. Prepared resource follow-up covers excluded-grandparent assets and INCLUDED NPCR spouse assets together; financially responsible nonmembers cannot all be excluded. | Existing failure supported by saved review and current Manual 10.11. **[PENDING FRESH RESOURCE HOUSEHOLD RESULTS]** |
| 4. Missing sensitivities and overstated cause | Body includes dated `−$20.46M` and `−$15.23M` historical sensitivities; income and resources are explained separately. | Historical 2026-09-29 report; **[PENDING FRESH PAIRED IMPACT]** |
| 5. School-enrolled 18-year-old grouping | YAML and property docstring label retained interpretation (i), size three. Formula commentary describes the grouping as one reading rather than settled law. Body explains minor-parent definition and alternative size-two readings. | Current Manual 4.3 and archived 0210.005.30; recovered code read |
| 6. Missing converse and dependent oracle | New property independently asserts the entire NPCR identification vector and existence condition. Membership still uses model inclusion; body/docstring narrow independence claims. Flag-off comparisons explicitly run current code. | Recovered property read; **[PENDING FRESH PROPERTY/MUTATION RESULT]** |
| 7. Vacuous final YAML case | Replaced with finding 1's meaningful two-tax-unit case. | Updated member YAML: 16 passed |
| 8. Wrong school variant and weighted-only accuracy | Saved rescore includes `none`, both weightings, false positives/negatives, distinct persons, and effective sample size. Body describes pointer agreement and hedges Census artifact explanation. | `rescore_none.json` and `.out` complete; direct HDF column metadata check complete |
| 9. January snapshot | Formula comment and input documentation identify annual January snapshot and limitation with monthly age changes. | Recovered variable read |
| 10. Adoption omitted | Input documentation and comment identify explicit `true` for adoptive parents outside 12–50 years. Age window is imputation, not law. | Recovered variable read |
| 11. Stale formula accuracy prose | Dataset-specific accuracy claim removed from formula; versioned rescore belongs in body. | Recovered variable read |
| 12. Explicit-input scope | Documentation/body say unspecified people become false for the supplied year, while other years may use the default. | Recovered variable read and saved core contract review |
| 13. Reversed conditional statistic | Body says 73% of parents in another tax unit from their child cohabit with the child's other parent. No inference that most cohabiting parents file separately. | Saved CPS ground-truth report §b: 903 of 1,245 parent records, 1.84M of 2.52M weighted |

## Completed evidence that can be reused

`tests/branch_member_yaml.txt` contains **16 passed** on the previous worktree. The output identifies the module path but does not record a Git SHA. It is evidence for the unchanged recovered member file, not proof of every check on a final composed head. Its pytest test phase took 141.27 seconds; the surrounding command wall time was inflated by severe host contention.

`tests/branch_properties_mutations.txt` is empty. No completed current-round property, mutation, partner, household-check, or paired microsimulation output exists in the evidence folder. The CI harness was prepared but, per the root's GitHub check, never pushed/run. No final `9676-report.md` or separate #9676 journal/progress file was found. The previous job tail confirms the 16-case YAML pass and unfinished evidence workflow.

`rescore_none.json` / `.out` are complete and can be reused. They use the saved Census ASEC 2023–2025 and Populace 2024 helpers and frames. The score is against `G`, resolved CPS parent pointers, rather than `G_legal`, the biological/adoptive-only subset; describe the result as parent-pointer agreement.

| Data and rule (`none`) | Selected | Precision weighted / unweighted | Recall weighted / unweighted | Selected effective n |
|---|---:|---:|---:|---:|
| Census pooled, own children only | 85 | 64.21% / 68.24% | 100% / 100% | 62.46 |
| Census pooled, age guard | 71 | 74.82% / 78.87% | 95.63% / 96.55% | 50.65 |
| Populace US, own children only | 74 | 95.17% / 94.59% | 100% / 100% | 22.39 |
| Populace US, age guard | 71 | 99.999993% / 95.77% | 99.999984% / 97.14% | 21.40 |
| Populace MO, either rule | 4 | 100% / 100% | 100% / 100% | 2.92 |

Guarded Populace has three false positives (weight 0.013188) and two false negatives (weight 0.031064). Missouri's four selected records represent three distinct persons. Pooled Census Missouri selects zero; its precision/recall are undefined. The Missouri evidence is thin.

Direct lightweight HDF metadata verification on 2026-10-06 read `person/table.dtype.names` from snapshot `9a814a3b3b53c0ecd6e1737b6ec862c31300ef6f/populace_us_2024.h5`: 318 person columns; `A_HSCOL`, `tax_unit_role_input`, and `own_children_in_household` present; `is_in_secondary_school` and `is_tax_unit_dependent` absent. The saved rescore's own `populace_stores` check searches HDF key names rather than column metadata and is insufficient alone; the direct verification resolves this.

## Required regression disclosures

| Zero-income household | Main | PR | Legal unit |
|---|---|---|---|
| Unmarked grandparent 55, dependent mother 20, child 3 | Grandparent and child, size two, `$234.08628` | All three, size three, `$292.08996` | Mother and child, size two |
| Head 40/child 10, dependent adult 45 whose own child is 20 | Head and child, size two, `$234.08628` | Adds adult 45, size three, `$292.08996` | Head and child, size two |

Each is a new `$58.00368/month`, `$696.04416/year` default overpayment. Child counts and age windows cannot resolve either relationship.

The added income-loss YAML uses `$14,400 / 12 = $1,200`, above size-four need `$990`, so grant zero; main pays the three children `$292.08996`. Its zero-income pair pays size-four `$341.8074`, a gain of `$49.71744/month`. These are hand-computed model-convention expectations; payment rounding remains outside scope.

## Historical impact and fresh verification

The saved 2026-09-29 study used core 3.32.8, branch `0771d2c498`, the default Populace tag `populace-us-2024-spm-20260909`, and dataset SHA-256 `6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84`. Its unmodified comparison turned the parent flag off on branch code. Its marked sensitivities also executed actual pre-branch code `10e3f989ba`. The former is not a pre-PR execution.

| Historical 2026 scenario | Annual entitlement delta | January delta | Takeup delta |
|---|---:|---:|---:|
| Unmodified | `$0` | `$0` | `$0` |
| Seven grandparents marked | `−$20,456,424` (−15.7%) | `−$1,704,702` | `$0` |
| Marked and grandparents' bank assets zeroed | `−$15,230,525` (−9.5%) | `−$1,269,211` | `$0` |

The unmodified study added four members, 22,417.5 weighted, without changing entitlement or takeup in any month. All four affected units failed income tests and three failed resources. Once marked, SPM 17211 (weight 5,836) loses the children's `$292.09/month` because their mother's disability income exceeds need. Zeroing excluded-grandparent assets lets SPM 1017211 (weight 8,759) gain `$49.72/month`. These two records dominate the totals. SPM 76134 continues to fail on another parent's income and resources; grandparents' income alone cannot explain all failures.

Fresh paired current-main/final-branch 2025 and 2026 results, all twelve months, same core and dataset, interventions on both codes: **[PENDING FRESH IMPACT TABLE, PROVENANCE, AND ARTIFACTS]**.

Final targeted suite, unchanged partner contract, old-head/main comparison, and mutation counts: **[PENDING FRESH CI/TEST TABLE AND ARTIFACTS]**.

## Harness corrections before fresh runs

- `run_tests.sh` logs exit codes but never rejects ordinary failures; validate expected pass/fail outcomes and return nonzero when the contract is violated. `mutate.py` also prints failures but returns success; inspect individual mutation codes explicitly.
- The prepared CI workflow independently runs `uv lock --upgrade-package policyengine-core` in every job. Pin the same core for main and branch and record its version/hash.
- Add unchanged partner contracts, which the prepared workflow omits.
- `run_mo.py`'s `marked_no_assets` zeroes bank, stock, and bond assets. The required historical sensitivity zeroes bank assets; match that intervention or explicitly report a separate scenario.
- Save year-specific person weights for 2025, since the existing person frame uses only 2026 weights. Existing SPM frames do save per-year weights.
- Save code SHA, core/Python version, and dataset identity/hash in metadata. External CI version logs currently carry some of this but local `run_mo.py` does not.
- The runner saves all-month payment, membership, NPCR, and eligibility, but detailed income/resources only in January; save all-month detail before making all-month causal claims.
- Completion metadata is written only after the costly all-state annual `tanf` calculations. A failure there causes the already-saved Missouri monthly frames to be recomputed. Prefer per-year checkpoints and validate matching provenance before resuming.
- Validate the seven marked person IDs are in Missouri and retain their relationship evidence. Apply all interventions identically to both codes and assert record ID/weight equality in comparison.

## Resource follow-up notes

The prepared follow-up accurately identifies the excluded-grandparent defect and included-NPCR spouse-resource error under current Manual 10.11. Do not indiscriminately remove all nonmembers: some excluded people are financially responsible. The wider SPM-resource aggregation of unrelated/nonresponsible adults remains an open follow-up scope question.

The original `resource-followup.md` falsely refers to a completed 2026-10-06 rerun in `9676-report.md`, which does not exist. Remove that statement from the copied follow-up until fresh paired results exist. It also labels both fixtures as failing even though the included-NPCR spouse fixture is a sketch that still needs its inclusion-branch behavior computed; keep that distinction until the household check runs.

No partner expectations may be rewritten without the top-level three-question user gate. Nothing in this audit requires such an edit.
