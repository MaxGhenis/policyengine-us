# Country canonical SPM continuation

## State

- Country implementation complete; independent-review fixes C1/C2 in progress on `max/spm-canonical-default-20260909` at `42103db1b7` (country 1.824.7), preserving all prior edits.
- Scope: canonical calculator 1.0.0 integration, focused household and small dataset checks, documentation and handoff. Other repositories and population screening belong to the rollout coordinator.
- Changes remain uncommitted under the assignment's explicit “No commit/push/publish/deploy” instruction, which supersedes the standing commit order.

## Done

- Read local `AGENTS.md`, `CLAUDE.md`, continuation assignment, existing country edits and prior rollout context.
- Loaded model-development and standards skill entrypoints from `/Users/maxghenis/.codex/policyengine-skills/skills/` via filesystem tools; read agent-loading, variables, periods/aggregation, vectorization, tests, reforms and style references.
- Confirmed isolated Python 3.13 environment with policyengine-core 3.30.1 and local editable spm-calculator 1.0.0 exposing `policyengine_amount`.
- Delegated independent integration review and focused contract/boundary tests with separate file ownership.
- Existing canonical threshold tests passed: 21 cases.
- Fixed core clone reconstruction losing partial reform metadata and neutralization; preserved detached variable state and per-simulation receipts, including shared-policy branches. Independent safe-path probe passed.
- Normalized positional constructor arguments so reform baseline configuration and Microsimulation dataset interception match keyword calls.
- Added small dataset and constructor regressions; first 8 system cases passed before expanded positional/config coverage.
- Added 18 passing integration cases covering real HUD arithmetic, float64 rounding boundaries, lazy geography errors, age/role boundaries, native membership and fixed metro receipts.
- Replaced obsolete housing YAML fixtures with canonical primitive-input cases (6 passing); added a missing county to a net-income fixture without changing its expected output (3 passing).
- Broader SPM YAML/Python sweep initially had 51 passes and that single missing-county failure, subsequently fixed.
- Preserved keyword compatibility for `set_input(variable_name=...)`; both household and microsimulation regression cases pass.
- Built country and calculator wheels offline with cached backends after registry DNS access failed. Installed calculator wheel into the isolated `.venv`, with 59 focused Python tests and 31 SPM YAML tests passing. Final separate installed-country/calculator wheel smoke passed calculation, cloning, provenance and keyword input.
- Broader Python checks passed: 93 tests covering construction, input metadata, county/state behavior and dataset copying/extension.
- Repository-wide Ruff lint, changed-file formatting, dependency compatibility and diff whitespace pass. Whole-repository format check still flags three unchanged Markdown files, documented in the handoff. Partner files remain unchanged.
- Wrote final results, wheel hashes, before-fix evidence and rollout limitations to `COUNTRY-SPM-HANDOFF.md`.
- Bounded follow-up complete: 6 new regressions pass for state-only resource/MTR geography errors, explicit-national success with zero assistance, and generic benefit count isolation. The unchanged CO TANF/MN MFIP YAML cases also pass (13 cases); focused Ruff and diff checks pass. No production or partner changes in the follow-up.
- Verified actual BuildP HDFStore `/household.county_fips`: all 57,240 values present and five digits, 2,826 unique counties; recomputed file hash and statistics exactly match `rollout/native-county-input-receipt.json`. Recorded the all-units cap/geography contract and evidence in the handoff.

## Next

- Finish C1 holder rebinding with numeric baseline/reform and clone isolation regressions; migrate three C2 nonpartner geography fixtures, run affected suites and record exact changed-file hashes.

- Coordinator: copy `COUNTRY-SPM-HANDOFF.md` and any desired temporary evidence/wheels to rollout storage.
- Refresh the registry lockfile once calculator 1.0.0 is available to the resolver; finish wrapper/API and source-role dataset releases in their repositories.
- Run coordinated population comparison against actual baseline 1.764.6 and broader CI/partner verification. No heavy population run or promotion occurred here.

## Independent-review continuation

- Read current branch/diff, independent review, local guidance and model-development references before editing. C1 reproduced by review as ordinary federal income tax 4,016 versus incorrectly neutralized baseline 0.
- Delegated C2 fixture migration; worker supplied filesystem load evidence for the full model skill and tests/periods/style references. SNAP policy, generic counts and calculator source remain outside this edit scope. No commits or population runs authorized.

- C1 fixed constructor/clone/reform holder and entity rebinding, branch traversal and reform-only baseline input cleanup. Five before-fix failures preserved; first correction passed 23 tests. Final expanded suite is running. C2 worker confirmed 3 passes with all 14 original assertions preserved; final read-only C1 review found no further issue.

- Final runtime passes all 52 SPM threshold/provenance/YAML checks. Added-input tests passed after supplying their required variable label (2 cases). Broader validation exposed 3 mocked dataset-routing constructor cases; adapted only their shared test helper and all 3 targeted reruns pass, preserving original assertions. No new production change was required. Broader selected suite is finishing.
