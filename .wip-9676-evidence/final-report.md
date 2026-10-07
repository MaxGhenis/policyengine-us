# #9676 fix-round evidence report

Original reviewed PR head: `a6c44418afccac0270dcb9ea155338dac0c9a05d`. Recovered prior head: `aec34394e4fb69aa4411ab700ba783bfde4e97df`. Resumed candidate: `b9e7fff948caf4f33313c942c09caa7c7ccc3dea`, composed with frozen main `5b1d5bdf47044607341d76f3c932ba2e7b74a060`. Evidence-only fork head: `e39bb2c4c248ac4699032d7053f7429213014e75`; [source run 37551528031](https://github.com/MaxGhenis/policyengine-us/actions/runs/37551528031) completed at 2026-10-07 04:49 UTC with conclusion `failure`. All twelve microsimulations and both paired comparison reports completed. The failure includes the known name-check wrapper and two pytest cross-checkout import-path errors, which are preserved below. The [saved-evidence verifier](https://github.com/MaxGhenis/policyengine-us/actions/runs/37573381797) correctly rejected those two missing comparisons. The [two-comparison continuation](https://github.com/MaxGhenis/policyengine-us/actions/runs/37574013106), controller `f38c6fcf3951b2f5cd8a435ef13ddd2f34c5f549`, completed successfully; it reran only that missing evidence. Combined validation is `valid=true`, `errors=[]`, with all 30 sections validated and completed controller run ID/SHA independently matched to GitHub API metadata. The original run remains failed.

All model, test and changelog contents under `policyengine_us/` and `changelog.d/` are identical between candidate `b9e7fff` and tested model `e39bb2c`. Controller commits contain evidence tooling only; their SHAs are not substituted for the tested model SHA. Every Git mutation used sandbox-local `.resume/git`, leaving the original shared `.git` metadata untouched. The sandbox denies writes to the requested `~/reviews/` destination, so the actual local report and body are `.resume/9676-report-draft.md` and `.resume/9676-body-draft.md` in the assigned worktree. Compact reports are backed up on the fork's `wip/9676-evidence-report` branch.

Artifacts: [original full evidence](https://github.com/MaxGhenis/policyengine-us/actions/runs/37551528031/artifacts/11461208006), [combined full evidence](https://github.com/MaxGhenis/policyengine-us/actions/runs/37574013106/artifacts/11462135556), [combined compact validation](https://github.com/MaxGhenis/policyengine-us/actions/runs/37574013106/artifacts/11461908056). Only compact JSON/text reports were transferred to the host; dataset bytes and serialized simulation frames stayed in the cloud.

The prior read-only audit reviewed the C spec, saved current-head review, saved primary Missouri law/manual sources, previous job tail, prior worktree files, and `~/reviews/us-hub/fixes/9676-evidence`. It edited no model, partner, or Git files. The resumed work records a clean current-main merge, preserved formula AST, NPCR helper and partner-expectation equality with frozen main, formatting/lint success, and every new commit backed up on the fork.

The prior implementation preserves main's #9741 NPCR `get_override_branch` helpers. The requested build retains the membership formula and explicit-input contract, with new tests and corrected documentation. There is no new policy or methodology choice needed within that scope. The school-enrolled 18-year-old grouping and relationship imputation remain declared interpretations/limits.

axiom: [TheAxiomFoundation/rulespec-us#1444](https://github.com/TheAxiomFoundation/rulespec-us/issues/1444) queued (still open; no completed dependent-parent encoding claimed). The saved Axiom mirror report includes an unposted draft extension comment; the queued issue citation does not assert that this comment was posted in this round.

## Findings and resolution

| Finding | Recovered change or required disclosure | Evidence status |
|---|---|---|
| 1. Missing own-tax-unit dependent-child guard coverage | Two-tax-unit YAML case and dedicated Python property require `[true,true,false]`, size two, `$234.08628`. Removing `has_dependent_child` produces the intended assertion. | New YAML 16 passed, mutated 15 passed / 1 failed; new properties 26 passed, guard-mutated 25 passed / 1 failed. Original files pass the mutations. |
| 2. Two undisclosed default regressions | Body gives both new zero-income overpayments, exact before/after membership and payments. Relationship-inference correction remains a separate follow-up. | Fresh main/candidate/original-head household JSON confirms both; candidate and original-head household outputs are identical. |
| 3. Excluded grandparent assets | Preserve the legal `$5,000` asset counterexample outside the passing suite. Prepared resource follow-up covers excluded-grandparent assets and INCLUDED NPCR spouse assets together; financially responsible nonmembers cannot all be excluded. | Fresh checks confirm both resource defects on all three checkouts. The main and candidate excluded-grandparent legal YAML each fail through a preserved call-phase assertion. |
| 4. Missing sensitivities and overstated cause | Fresh 2026 and 2025 pairs execute frozen main and candidate separately; income and resources are explained separately. | Twelve completed simulations, all twelve months per scenario, paired identities/weights/interventions validated. Six fresh rows below. |
| 5. School-enrolled 18-year-old grouping | YAML and property docstring label retained interpretation (i), size three. Formula commentary describes the grouping as one reading rather than settled law. Body explains minor-parent definition and alternative size-two readings. | Current Manual 4.3 and archived 0210.005.30; recovered code read |
| 6. Missing converse and dependent oracle | New property independently asserts the entire NPCR identification vector and existence condition. Membership still uses model inclusion; body/docstring narrow independence claims. Flag-off comparisons explicitly run current code. | 66 combined property cases pass. `npcr_never` fails the new independent identification case through a call-phase assertion; original properties pass it. |
| 7. Vacuous final YAML case | Replaced with finding 1's meaningful two-tax-unit case. | Updated member YAML: 16 passed |
| 8. Wrong school variant and weighted-only accuracy | Saved rescore includes `none`, both weightings, false positives/negatives, distinct persons, and effective sample size. Body describes pointer agreement and hedges Census artifact explanation. | `rescore_none.json` and `.out` complete; direct HDF column metadata check complete |
| 9. January snapshot | Formula comment and input documentation identify annual January snapshot and limitation with monthly age changes. | Recovered variable read |
| 10. Adoption omitted | Input documentation and comment identify explicit `true` for adoptive parents outside 12–50 years. Age window is imputation, not law. | Recovered variable read |
| 11. Stale formula accuracy prose | Dataset-specific accuracy claim removed from formula; versioned rescore belongs in body. | Recovered variable read |
| 12. Explicit-input scope | Documentation/body say unspecified people become false for the supplied year, while other years may use the default. | Recovered variable read and saved core contract review |
| 13. Reversed conditional statistic | Body says 73% of parents in another tax unit from their child cohabit with the child's other parent. No inference that most cohabiting parents file separately. | Saved CPS ground-truth report §b: 903 of 1,245 parent records, 1.84M of 2.52M weighted |

## Completed evidence that can be reused

`tests/branch_member_yaml.txt` contains **16 passed** on the previous worktree. The output identifies the module path but does not record a Git SHA. It is evidence for the unchanged recovered member file, not proof of every check on a final composed head. Its pytest test phase took 141.27 seconds; the surrounding command wall time was inflated by severe host contention.

`tests/branch_properties_mutations.txt` from the prior attempt is empty. That attempt left no completed property, mutation, partner, household-check, or paired microsimulation output in its evidence folder, and its prepared workflow never ran. The resumed source workflow completed the evidence sequentially on one GitHub runner with Core 3.32.15. Its artifact was downloaded and independently inspected in the cloud; only compact JSON/text reports were transferred to the host. The two missing cross-checkout YAML comparisons were completed separately as described below. The previous job tail confirms the reusable 16-case YAML pass. Resumed progress is recorded in `.resume/progress.json`.

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

The saved [2026-09-29 study](/Users/maxghenis/reviews/mo-tanf-dependent-parent-2026-09-29/microsim-impact/REPORT.md) used core 3.32.8, branch `0771d2c498`, default Populace tag `populace-us-2024-spm-20260909`, snapshot `9a814a3b3b53c0ecd6e1737b6ec862c31300ef6f`, and dataset SHA-256 `6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84`. Its unmodified comparison turned the parent flag off on then-branch code. Its marked sensitivities also executed actual pre-branch code `10e3f989ba`. The former is not a pre-PR execution. Fresh runtime metadata records Core 3.32.15 and Python 3.14.7.

| Historical 2026 scenario | Annual entitlement delta | January delta | Takeup delta |
|---|---:|---:|---:|
| Unmodified | `$0` | `$0` | `$0` |
| Seven grandparents marked | `−$20,456,424` (−15.7%) | `−$1,704,702` | `$0` |
| Marked and grandparents' bank assets zeroed | `−$15,230,525` (−9.5%) | `−$1,269,211` | `$0` |

The unmodified study added four members, 22,417.5 weighted, without changing entitlement or takeup in any month. All four affected units failed income tests and three failed resources. Once marked, SPM 17211 (weight 5,836) loses the children's `$292.09/month` because their mother's disability income exceeds need. Zeroing excluded-grandparent assets lets SPM 1017211 (weight 8,759) gain `$49.72/month`. These two records dominate the totals. SPM 76134 continues to fail on another parent's income and resources; grandparents' income alone cannot explain all failures.

Fresh pairs execute frozen main and the candidate separately for 2026 and 2025, applying each intervention to both codes. All twelve simulations completed with Python 3.14.7, Core 3.32.15 and installed US distribution 2.29.14. The dataset URI and verified SHA-256 match the pinned build above; the runner resolved the file to its content-addressed blob, rather than recording a snapshot directory. Full population: 166,321 people / 59,900 SPM units. Saved Missouri diagnostics: 2,892 people / 1,051 SPM units. Original weights, entity identities and intervention vectors agree in each pair. Monthly payments, membership and failure partitions are identical across January–December within a scenario/year; monthly entitlement sums reconcile to annual totals.

The twelve simulations consumed 4,264.65 wall seconds / 4,268.49 CPU seconds in total, with maximum peak RSS 8,957,176 kbytes. Each ran in its own sequential process on the original runner. There was no host simulation rerun or additional simulation run in the continuation.

| Targeted evidence | Result | Wall / CPU seconds | Peak RSS kbytes |
|---|---|---:|---:|
| Missouri TANF YAML | 214 passed, 26 files, one worker | 1,569.13 / 1,579.22 | 2,599,764 |
| Both property suites | 66 passed | 55.25 / 55.56 | 1,242,112 |
| Explicit canonical source roles | Four checks passed | 34.01 / 34.33 | 1,087,768 |
| Input definitions | Four passed | 27.49 / 27.82 | 800,468 |
| Unchanged partner contracts | 623 passed, 144 files, one worker | 9,341.00 / 9,398.35 | 2,767,028 |
| Fresh main member comparison | 16 collected: five passed, eleven expected call assertions | 64.92 / 64.20 | 1,798,780 |
| Fresh original-head member comparison | 16 passed | 55.68 / 55.99 | 1,705,096 |

Both excluded-grandparent resource legal fixtures fail through preserved call-phase assertions (one on main and one on candidate); their validating wrapper commands exit zero. The main member comparison's eleven failures are also intended policy differences, not import/setup failures; its wrapper exits zero after validating the assertion evidence and required income pair. The original-head household JSON is exactly equal to the candidate's household JSON.

| Underlying mutation session | Original tests | New tests |
|---|---|---|
| Member YAML, no mutation | 14 passed | 16 passed |
| Member YAML, drop own-tax-unit child guard | 14 passed | 15 passed / one intended guard assertion |
| Dependent-parent properties, no mutation | 24 passed | 26 passed |
| Properties, drop child guard | 24 passed | 25 passed / one intended guard assertion |
| Properties, force NPCR identification false | 24 passed | 25 passed / one intended full-vector assertion |

The added Python tests check the complete identification vector/converse and preserve the simulation-isolation grid. Existing routing assigns them to the core group of **Full Suite - Rest (Python + variables)**, with no permanent runner or group changes. Single-run Linux before/after measurements of the original/new dependent-property commands, including import/setup and all three mutation sessions, were 86.08 / 85.80 seconds wall, 86.38 / 86.11 seconds CPU, and 1,198,112 / 1,201,612 kbytes peak RSS. The unmutated pytest sessions were 14.55 seconds for 24 cases and 14.57 seconds for 26; per-session CPU/RSS were not measured independently. These timings do not establish the peak of the complete Rest group. Existing sequential group and mutable-simulation isolation remain intact.

## Exact fields for the fresh impact table

Downloaded `out/compare_2026.json` and `out/compare_2025.json` each contain three top-level scenarios: `unmodified`, `marked`, and `marked_no_assets`. Read the values below per scenario; do not substitute historical values or infer annual actual TANF from entitlement multiplied by takeup.

| Report field | JSON path under each scenario |
|---|---|
| Main / branch annual entitlement | `annual_entitlement.main_sum` / `.branch_sum` |
| Annual entitlement delta / percent | `annual_entitlement.change` / `.percent_change` |
| January entitlement delta | `monthly["01"].entitlement.change` |
| Each other month's delta | `monthly["02".."12"].entitlement.change` |
| Actual annual Missouri TANF after takeup | `annual_actual_tanf.main_sum`, `.branch_sum`, `.change` |
| Actual national annual TANF delta | `annual_actual_tanf_all_states_change` |
| MO entitlement × takeup diagnostic | `annual_mo_entitlement_with_takeup.change` |
| Added / removed members and weights | `monthly[month].members_added` / `.members_removed` (`records`, `weighted`) |
| Income-only, resource-only, both, neither | `monthly[month].failures_among_membership_changed_units.main` / `.branch` |
| Newly failed income / resources | `monthly[month].new_income_failures` / `.new_resource_failures` |
| Dominance of two largest records | `two_largest_records_share_of_absolute_annual_change` (fraction) |
| Driver IDs, weights, per-record / weighted delta and takeup | `membership_changed_or_payment_changed_records` |
| Driver January incomes, resources, unit size and eligibility | Each driver's `main` / `branch` dictionaries |
| Actual core, Python, code SHA, dataset hashes and completion | `metadata` (main then branch) |

The `annual_actual_tanf` field instead contains `incomplete: true` and `errors` if that requested calculation failed. Monthly evidence can still be valid, but that condition must remain explicit in the report. Compare files do not prove current PR CI is green; tests and workflow exit statuses are separate evidence.

| Fresh scenario | Main annual entitlement | Candidate annual entitlement | Annual delta / percent | Every month's delta | Actual annual MO TANF delta | Added members / weighted | Two-record share |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026 unmodified | $109,786,412.97 | $109,786,412.97 | $0 / 0% | $0 | $0 | 4 / 22,417.537 | Undefined (no change) |
| 2026 marked | $130,242,839.60 | $109,786,412.97 | −$20,456,426.63 / −15.706373% | −$1,704,702.22 | $0 | 4 / 22,417.537 | 100% |
| 2026 marked, bank zeroed | $160,944,079.65 | $145,713,546.56 | −$15,230,533.09 / −9.463245% | −$1,269,211.09 | $0 | 4 / 22,417.537 | 99.999232% |
| 2025 unmodified | $110,229,436.37 | $110,229,436.37 | $0 / 0% | $0 | $0 | 4 / 22,258.586 | Undefined (no change) |
| 2025 marked | $130,540,816.37 | $110,229,436.37 | −$20,311,380.00 / −15.559409% | −$1,692,615.00 | $0 | 4 / 22,258.586 | 100% |
| 2025 marked, bank zeroed | $161,024,369.88 | $145,901,829.32 | −$15,122,540.56 / −9.391461% | −$1,260,211.71 | $0 | 4 / 22,258.586 | 99.999232% |

Actual annual Missouri TANF on both codes is $5,497,666.848239392 in 2026 and $5,458,685.747033298 in 2025 in every scenario. National actual TANF changes are zero throughout. The distinct entitlement × takeup diagnostic is also unchanged, with sums $5,497,666.612117186 and $5,458,685.512585312 respectively; it is never substituted for actual TANF. Monetary table entries are rounded for display; the committed compact JSON retains original precision.

Four members are added in four SPM units every month, with none removed. Failure-partition record counts among those four units are identical in both years and across all twelve months:

| Scenario / code | Income only | Resources only | Both | Neither |
|---|---:|---:|---:|---:|
| Unmodified, main and candidate | 1 | 0 | 3 | 0 |
| Marked, main | 0 | 2 | 1 | 1 |
| Marked, candidate | 1 | 2 | 1 | 0 |
| Marked / bank zeroed, main | 1 | 0 | 0 | 3 |
| Marked / bank zeroed, candidate | 2 | 0 | 0 | 2 |

Both marked scenarios produce one new income failure and zero new resource failures every month. The data drivers are:

| SPM unit | 2026 / 2025 weight | Bank-sensitivity annual per-record change | Weighted 2026 / 2025 change | Cause |
|---|---:|---:|---:|---|
| 17211 | 5,836.223145 / 5,794.841309 | −$3,505.079590 | −$20,456,426.63 / −$20,311,380.00 | Adding the mandatory mother changes size 3→4 and adds $1,290.685791 / $1,247.636597 monthly disability income, above the $990 need standard. Her children's $292.089966 monthly grant is lost. This loss also occurs in marked-only data. |
| 1017211 | 8,758.993164 / 8,696.887695 | +$596.609253 | +$5,225,696.37 / +$5,188,643.67 | Marked-only units fail resources ($18,132.416016 / $17,715.898438). Zeroing bank assets leaves zero income/resources; size 3→4 raises the monthly grant by $49.717438. |
| 1134143 | 0.166978 / 0.165794 | +$1,180.789124 | +$197.17 / +$195.77 | Marked-only units fail resources ($7,964.241699 / $7,781.296387). Bank zeroing leaves zero income/resources; size 1→2 raises the monthly grant by $98.399094. |
| 76134 | 7,822.154297 / 7,766.691406 | $0 | $0 / $0 | Another parent in the unit still contributes countable income of $922.663635 / $877.123840. Removing the grandparents' bank assets resolves the resource failure, but income tests still fail at size 3 and size 4. |

All four affected records have takeup=false. Marked-only annual change comes entirely from SPM 17211. In the bank sensitivity, SPM 17211 and 1017211 account for 99.999232% of absolute annual change; the tiny-weight 1134143 supplies the remainder. Grandparents' income alone cannot explain these failures.

## Mutation evidence-wrapper caveat

The original evidence workflow contains a case-sensitive YAML detecting-case lookup. Its target is `Explicit parent flag requires a dependent child`, while the authored case is `An explicit parent flag requires a dependent child in that person's tax unit`. The uppercase `E` in the target does not match the lowercase `e` in the case. Saved failure records prove the intended case failed with a call-phase `AssertionError`; actual/expected mutation maps are both `{none:0, drop_has_dependent_child:1}`. The exact recorded wrapper reason is `{'drop_has_dependent_child': 'intended detecting case missing: Explicit parent flag requires a dependent child'}`. Independent saved-evidence validation uses case-insensitive matching, with no rerun of that mutation or its model tests.

The wrapper's original command exit is 1 versus expected 0; mutation task flag and `logs/tests_status.txt` remain 1. The original run's red conclusion remains intact. The standard-library summarizer still reports these three warnings and intentionally fails its strict check; underlying mutation matching does not relabel that wrapper or the full source workflow as green.

The other original errors are infrastructure failures: main and original-head comparisons loaded the candidate YAML under `/wip/` while importing `/main/` or `/old_head/`, causing `ImportPathMismatchError` on the empty model `conftest.py`. Main's wrapper recorded exit 1 with underlying pytest exit 4 and no assertion records; the original-head CLI recorded exit 4. Those original logs/JSON/timings/summary receipts are retained in the source artifact and compact continuation artifact's `original-comparison-logs/`.

The continuation copies the exact member fixture (SHA-256 `0a01250de835a9e5067ac7f5e212fd8cb141b7a403262d6cc0e7cf9f97db2d96`) into a temporary directory outside all package checkouts, retaining the original models, Core, Python patch and identical package freeze. It runs only those two comparisons, recording fresh runtime/fixture/collection/exception receipts. Combined validation proves that precisely seven comparison-receipt files were replaced and every other original artifact byte was retained. All 126 original source files are preserved separately. Controller identity is bound to successful completed run 37574013106, while the tested model SHA remains `e39bb2c`. All previously completed source assertion checks, weights and paired arrays were reused; only the two missing YAML comparison assertions were evaluated afresh. The cloud validator hashes serialized frame bytes without unpickling them; host finalization separately checks completed controller metadata.

## Corrections included in the resumed evidence harness

- `run_tests.sh` validates every actual/expected exit and returns nonzero for unexpected results. Mutation JSON requires test-call assertion failures and the intended detecting nodes, rejecting import/setup errors.
- One shared dependency environment pins core 3.32.15 for frozen main, candidate/evidence code, and old PR head. Runtime checks record the exact imported checkout and source hash.
- Unchanged partner contracts are included. Local static comparison confirms partner expectations equal frozen main.
- `marked_no_assets` now zeroes bank assets only, matching the historical sensitivity. Existing NPCR inputs outside the seven selected people are preserved, and interventions apply to both codes.
- Person and SPM weights are saved for each year. Metadata records code SHA, core/Python version, default dataset URI, expected/actual SHA-256, and population sizes.
- Monthly membership, NPCR, income/resources, eligibility, and payment diagnostics are saved. Per-year checkpoints preserve monthly results before the costly all-state annual `tanf`; annual errors and incomplete status remain explicit.
- All seven marked IDs are asserted to be Missouri records. The comparison checks paired identities, weights, interventions, and dataset/core provenance, and reports monthly failure causes separately.
- `.resume/summarize_ci.py` extracts downloaded artifacts using only the standard library. It reads no pickles and imports no model, and leaves missing/incomplete evidence explicit.

## Resource follow-up notes

The prepared follow-up identifies the excluded-grandparent defect and the current Manual 10.11 requirement to count an included NPCR's spouse's resources. Fresh household output confirms the spouse-resource counterexample on main, original head and candidate: grandfather and grandchild are members, grandmother is excluded from membership, NPCR inclusion is true, and her $5,000 is incorrectly dropped, leaving $0 countable resources and a $234.086273 grant. Do not indiscriminately remove all nonmembers: some excluded people are financially responsible. The wider SPM-resource aggregation of unrelated/nonresponsible adults remains an open follow-up scope question.

The original `resource-followup.md` falsely referred to a completed 2026-10-06 rerun in a nonexistent report. The resumed copy removes that claim and clearly dates the historical observation. The previously sketched spouse fixture now has completed fresh inclusion-branch evidence as described above. Both resource errors remain outside this membership-fix scope.

No partner expectations may be rewritten without the top-level three-question user gate. Nothing in this audit requires such an edit.
