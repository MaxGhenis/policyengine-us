# Country canonical SPM handoff

Country implementation is complete; independent-review C1/C2 fixes are undergoing final affected-regression validation in this worktree. Changes are intentionally uncommitted under the assignment's final “No commit/push/publish/deploy” instruction. No checkout, reset, push, publication, deployment or partner-test edit was performed.

## State

- Worktree: `/Users/maxghenis/spm-rebuild-20260908/worktrees/policyengine-us-spm-integration-audit`.
- Branch: `max/spm-canonical-default-20260909`.
- Preserved starting HEAD: `42103db1b7d5be74bd28ebfc8e93adb2c7859079`, country version 1.824.7. All prior country integration edits were retained and completed.
- Isolated environment: Python 3.13.9, policyengine-core 3.30.1, spm-calculator 1.0.0. The calculator started as a local editable dependency and was replaced with a locally built wheel for final tests. No global environment was changed.
- Read local `AGENTS.md`, `CLAUDE.md`, the rollout continuation assignment, and model-development/standards skill source files. Delegated workers read the model-development entrypoint and relevant references and supplied load receipts. These were explicit source-file loads, not verification of an installed plugin command.
- `PROGRESS.md` records state, completed steps and next work. Neither it nor implementation changes were committed because the assignment explicitly prohibited commits.

## Completed implementation

- Registered all nine calculator variable classes in `CountryTaxBenefitSystem` before input parsing. Removed the five old country threshold/geography/housing-portion implementations and the threshold entries in both country default uprating and dataset AGI overrides.
- Pinned the published dependency to `spm-calculator==1.0.0`. Wheel metadata contains the registry requirement and no Git or local-path dependency.
- Added `Simulation`, `Microsimulation` and country-system `spm` configuration with exactly `forecast_content_sha256`, `scenario`, `geography_kind`, `geography_id`, `county_vintage` and `as_of`. No external forecast path is accepted. County mode reads household `county_fips`; `geography_id` selects a fixed metro. National mode is explicit.
- Exposed detached JSON-compatible `simulation.spm_config` and `simulation.spm_provenance()` receipts. Fresh simulations start with fresh receipts; calculated clones retain cached-result receipts and isolate subsequent calculations. Shared-policy branches also have separate provider state.
- Fixed core's variable reconstruction during cloning, which otherwise lost inherited reform metadata and neutralization. Full clones preserve variable instance state and detach nested metadata. Supplied reform systems and caller-owned systems remain intact.
- Normalized positional constructor arguments so positional reforms use the selected baseline SPM configuration and positional Microsimulation datasets use country dataset interception. Preserved Core's public `set_input(variable_name=...)` keyword API.
- Confirmed lazy `SPM_GEOGRAPHY_REQUIRED` for state-only SPM requests, even when tax formulas have already cached an inferred county. State-only tax calculation succeeds. SPM never requests computed `county` or `first_county_in_state`.
- Confirmed SPM adult classification uses actual age >=18, or age >=15 with the source-backed independence role. The role defaults to input-only household head/spouse primitives. Generic adult/child counts and native membership remain unchanged; adultless units raise `SPM_COMPOSITION_REQUIRED`.
- Dataset `set_input` rejects the entire calculator `FORMULA_OWNED_INPUTS` set. Tests cover successful small vector datasets, roles, single/multi-year entity datasets, HDFStore rejection, unchanged caller frames and unchanged source HDF bytes. Household formula overrides remain available for model unit tests; public wrapper/API input validation belongs to the coordinator's consumers.
- Kept native housing-cap arithmetic as `min(float64(actual assistance), max(raw canonical housing_portion - float64(actual PE hud_ttp), 0))`, followed by final storage conversion. A real earnings/HUD boundary demonstrates a positive cap that would incorrectly become zero if the stored float32 housing portion were used.
- Replaced obsolete housing YAML fixtures with actual county/age/tenure cases. Added county input to one cash-support net-income fixture without changing its expected output. Added docs and a changelog fragment.

## Validation

All commands used the isolated environment with `UV_CACHE_DIR=/tmp/country-spm-uv-cache uv run --python .venv/bin/python --no-sync` unless stated otherwise.

| Check | Result | Evidence |
| --- | --- | --- |
| Canonical threshold + system/config/dataset Python tests | 41 passed | `/tmp/country-spm-focused-final.log` |
| Real HUD cap, precision, age/role, lazy tax/SPM, metro contracts | 18 passed | Independent test agent final run; `policyengine_us/tests/unit/test_spm_integration_contract.py` |
| Combined focused tests after installing calculator wheel | 59 passed, 1 warning | `/tmp/country-spm-installed-focused.log` |
| SPM income and demographic YAML tests with installed calculator wheel | 31 passed | `/tmp/country-spm-installed-yaml.log` |
| Broader Python checks | 93 passed, 4 warnings | `/tmp/country-spm-broader-python.log` |
| Final keyword `set_input` compatibility regressions | 2 passed | `/tmp/country-spm-keyword-input.log` |
| Independent clone/reform/receipt probe | Passed | `/tmp/country-spm-review-probe-safe.log` |
| Repository-wide Ruff lint | Passed | `/tmp/country-spm-ruff-check.log` |
| Changed Python files and SPM docs formatting | Passed, 9 files | `/tmp/country-spm-ruff-focused.log` |
| Repository-wide formatting | 3 unchanged Markdown files need formatting | `/tmp/country-spm-ruff-format.log` |
| Dependency compatibility | 80 installed packages compatible | `uv pip check --python .venv/bin/python` |
| Country and calculator wheel builds | Passed offline with cached backends | `/tmp/country-spm-wheel-offline-build.log`, `/tmp/country-spm-calculator-wheel-offline-build.log` |
| Final installed wheel imports, canonical calculation, clone receipts and keyword input | Passed | `/tmp/country-spm-wheel-smoke.json` |
| Diff whitespace and partner files | Clean; partner files unchanged | `git diff --check`; `git diff --exit-code -- policyengine_us/tests/policy/baseline/partners` |

The broader Python command selected `test_system_import.py`, `core/test_input_variable_definitions.py`, `core/test_county_fips_fallback.py`, `core/test_state_code_str_backfill.py`, `microsimulation/data/test_dataset_copy.py`, and `microsimulation/data/test_extend_single_year_dataset.py`. It used synthetic small datasets only.

The horizon checks compare all five canonical amounts for all three tenures and every year from 2022 through 2035, asserting final dtype casts and matching year receipts. Configuration coverage includes hash mismatches, unknown scenarios/years, unsupported settings, dates and geography selections, and serializable round trips.

Failing evidence was preserved before correction: four obsolete housing YAML failures in `/tmp/country-spm-yaml-before.log`; the inherited-reform clone failure in `/tmp/country-spm-system-before.log`; and the single missing-county net-income failure from an initial 51-pass/1-fail sweep in `/tmp/country-spm-yaml-after.log`. The final YAML run passes all 31 cases. An initial `/tmp` probe run encountered unrelated module shadowing; only the clean `python -P` rerun is accepted as probe evidence.

## Artifact receipt (historical; superseded by the review-fix receipt below)

- Forecast content SHA-256: `b9dbf5ae49697e3bf3abee2fa22b7429703412cb1e58478938a682a0dfddc821`.
- Resolved default scenario: `ce_trend`; default county vintage: `2020`; years: 2022–2035.
- Calculator source worktree HEAD observed during verification: `52b41b1dbf76f4f31ba78afdca6f0f8f9ba55eb5`. The wheel used the source working-tree snapshot, so its hash below is the exact validation identity.
- Calculator wheel: `/tmp/country-spm-wheels/spm_calculator-1.0.0-py3-none-any.whl`, SHA-256 `3d056279bcc369989625d8cf17de0d9ab7067931090ef5c03903828caa3c8cb9`.
- Country wheel: `/tmp/country-spm-wheels/policyengine_us-1.824.7-py3-none-any.whl`, SHA-256 `355c77d29bb849d276ef7ff8f13e982399600ba897514758fa3c4aa99b2f8ec0`. This wheel matched the earlier integration snapshot; it does not contain the later C1 holder-rebinding fix and must not be promoted as the current source.
- The wheel smoke imports both packages from `/tmp/country-spm-wheel-install`, separate from the country source checkout and calculator editable source, and calculates an explicit-national single-adult 2024 threshold of 18,176.97265625 after model storage conversion.

## Remaining coordinator work and limitations

1. Refresh `uv.lock` against the available calculator 1.0.0 registry release before CI/promotion. The existing lock still records the old >=0.2.0 resolution and was deliberately not replaced with a workstation-only source path or fabricated registry hashes. Registry access in this environment failed DNS lookup. Source/wheel tests use `--no-sync`; ordinary `uv sync` and registry installation were not validated here.
2. Finish wrapper/API client configuration, typed-error handling and household formula-owned input validation in their respective repositories. No partner expected output was edited or approved for change. The full partner suite and full country suite were not run, so this handoff makes no claim that all existing state-only resource requests satisfy the new explicit-geography contract.
3. Coordinate the production dataset release carrying the source-backed minor-role input. This country patch does not change `DEFAULT_DATASET` or certify the old default population as carrying the new primitive. Validate the new release at rollout.
4. Perform the separately requested population comparison against actual baseline country 1.764.6. This worktree is on 1.824.7 and includes unrelated upstream changes; no heavy population run or aggregate attribution was attempted.
5. Repository-wide `ruff format --check .` still reports pre-existing formatting in `docs/usage/microsimulation.md`, `docs/usage/parameter-discovery.md`, and `policyengine_us/parameters/gov/ssa/ssi/eligibility/resources/README.md`. These unrelated files were left unchanged. Broader test warnings concern existing NumPy division, HDF natural names, and pytest plugin rewriting; the executed tests pass.
6. Only Python 3.13.9/core 3.30.1 was exercised. Other supported interpreter/core versions and full CI remain rollout verification work. Temporary build logs and wheels live under `/tmp`; copy any needed artifacts with this report before they are cleaned up.

## Bounded follow-up: resource geography and generic benefit counts

The final contract deliberately requires geography for **every unit whenever the SPM housing cap is evaluated, including units with zero housing assistance**. There is no masking or zero-assistance shortcut. Under default policy, `household_benefits`, `household_net_income`, `marginal_tax_rate`, `equiv_household_net_income` and `household_income_decile` depend on that cap. Tax-only success does not imply these resource outputs can run with state alone.

Added four real household regressions in `policyengine_us/tests/unit/test_spm_integration_contract.py`: state-only `household_net_income` and `marginal_tax_rate` each raise `SPMInputError` with `code` and serialized `to_dict()["code"]` equal to `SPM_GEOGRAPHY_REQUIRED`; the corresponding explicit-national calls return finite positive results and year provenance. All four cases first calculate actual housing assistance as zero and use the unchanged resource/MTR formulas.

Confirmed `spm_unit_count_adults.py` and `spm_unit_count_children.py` are unchanged against HEAD. The new SPM-specific counts remain `spm_measurement_adults` and `spm_measurement_children`. Two additional vector regressions use separate 16-year-old units with and without a source-backed independence role: generic counts remain adults `[0, 0]`, children `[1, 1]`, while measurement counts are adults `[0, 1]`, children `[1, 0]`. The unchanged Colorado `co_tanf_need_standard` and Minnesota `mn_mfip_child_support_income_exclusion` formulas return the same positive benefit amounts for both units, without composition errors or SPM forecast receipts. This verifies that a unit lacking a classified SPM adult can still use those generic benefit consumers.

Follow-up checks:

- **6 new Python regressions passed**, 18 existing cases deselected, in 41.42 seconds: `/tmp/country-spm-followup-regressions.log`. Seven warnings come from existing NumPy divide expressions in unemployment-income allocation and MTR self-employment shares; all assertions pass.
- **13 unchanged benefit YAML cases passed** for Colorado TANF need standards and Minnesota MFIP child-support exclusions: `/tmp/country-spm-followup-benefits.log`.
- Focused Ruff lint/formatting and `git diff --check` pass. Generic count files and partner fixtures have no diff. No production formula was changed in this follow-up; only regression tests and handoff/progress records were updated. No heavy population run, commit or publication occurred.

The actual BuildP file `/Users/maxghenis/spm-rebuild-20260908/rollout/data/populace_us_2024.h5` was verified read-only with pandas 3.0.5 `HDFStore(mode="r")`. Its `/household` key contains `county_fips` with dtype `str`: **57,240 rows, zero missing, zero empty, all 57,240 matching five digits, and 2,826 unique counties**. The file size is 462,915,783 bytes and its recomputed SHA-256 is `48b9d479fb4fd1c3537f9383ce4697d130b6f618658409d74f6233c43b994c7e`. The complete recomputed evidence matches `/Users/maxghenis/spm-rebuild-20260908/rollout/native-county-input-receipt.json` exactly. This confirms the county primitive under the pandas household key; it does not certify the separately coordinated minor-role dataset release.


## Independent-review C1/C2 follow-up

Read `rollout/country-independent-review.md` and preserved the existing branch and all prior owned changes. This continuation modifies only the country worktree. No commits, pushes, dependency installs, calculator edits, population runs, SNAP policy changes or partner fixture changes occurred.

**C1:** Added actual calculation-object rebinding in `policyengine_us/spm.py`. After constructor baseline selection, cloning and reform application, each population resolves variables through its own policy system and each existing holder references that system's variable instance. Existing branches are rebound against their own policies. Reform-only holders and input metadata are removed from the baseline, with copied metadata detached before filtering; later baseline cache invalidation remains valid. Cached arrays and calculator receipts retain their existing clone semantics.

Before the fix, five focused regressions failed: two cloned neutralization mutations remained at $0, household and tiny-dataset reform baselines incorrectly returned $0 instead of $4,016, and a reform applied to a calculated clone retained a detached holder variable. The evidence is `.country-c1-before.log`. The first correction passed 23 system tests; final tests additionally cover new reform variables, supplied reform-only inputs, population entity bindings and shared versus separate policy branches.

The numerical contract for an adult age 40 with $50,000 employment income in 2024 is ordinary federal income tax **$4,016**, neutralized reform **$0**, and the reform's baseline **$4,016**. Clones preserve both cached and recomputed results. Unneutralizing only a clone restores **$4,016** there while the original remains **$0**. The partial household-market-income reform remains **$123**, with baseline **$50,000**. Coverage includes both Simulation and a two-person/two-household synthetic Microsimulation.

**C2:** The existing labor-supply substitution, capital-gains response and local-tax household-net-income fixtures now explicitly select national SPM geography. Only constructor settings and a test helper's optional `spm` forwarding changed. All **14 original assertions** are preserved. The three targeted tests passed before C1 editing; their complete modules are included in final validation. The all-units geography requirement remains, including zero-assistance cap evaluation.

### Final validation receipt

Final canonical SPM validation passes **52 cases** (31 YAML + 21 threshold/provenance Python). Two new reform-input tests initially lacked the framework-required variable label; after fixing that test metadata, **both pass** in `.country-review-added-input-final.log`. The broader run is still finishing. It exposed three pre-existing routing mocks whose mocked Core constructor omitted population state required by the new binding step. The shared test helper now uses the prepared system and supplies empty populations/input/branch metadata; all five routing assertions remain AST-identical to HEAD, and all three routing reruns pass (`.country-review-routing-final.log`). The original fixture-construction failures are retained and will be reported alongside focused reruns. Logs are `.country-review-final-python.log` (system/config, real cap, behavioral response, local tax, business income, labor-supply guard, credit cap, state/county and small dataset regressions) and `.country-review-final-spm.log` (31 YAML cases plus 21 threshold/provenance Python cases). Repository-wide Ruff passes (`.country-review-ruff.log`); final formatting and whitespace checks are recorded at completion. Earlier interim runs are retained separately, not substituted for final-source validation.

All execution uses the existing isolated Python 3.13.9 / Core 3.30.1 environment with `uv run --python .venv/bin/python --no-sync`, `PYTHONDONTWRITEBYTECODE=1`, and `PYTHONPATH="$PWD/../spm-calculator-production:$PWD"`. This explicitly exercises current calculator 1.0.0 source, matching the independent review's dependency method; it is not a new installed-wheel certification. Calculator HEAD at verification is `dcd366dc69155ebc8b1589cb332177f49b349363`; its `spm_calculator/` source has no diff from reviewed `c89d20f08f8d9d0896c88944fdb685ea01cecbb1`. Adapter SHA-256 is `bdc6878167a6e24877dbcc9ae58970c6fdf1a5543fc0af3fa9c1b38450aab0ac`.

### Source hashes and population-rerun implications

`COUNTRY-SPM-REVIEW-FIX-HASHES.json` records exact pre/post SHA-256 values, the preserved country HEAD, unchanged canonical components, final logs and handoff hashes. The only runtime file changed by this continuation is `policyengine_us/spm.py`, SHA-256 `6c7cb1cd50a4434a1b7f8577e58ffa628730571c8717511e928fc76b90011758` → `1553c0ebca131555c95e3aaeda1174eb6c454f1831ac8e772bca95ddb6e08270`; test changes are limited to `test_spm_system.py`, `test_behavioral_response_measurements.py` and `test_local_employee_taxes.py`, and the shared dataset-routing mock in `tests/microsimulation/data/fixtures/test_extend_single_year_dataset.py`, plus the existing changelog and handoff/progress artifacts.

Canonical measurement formulas, the provider implementation and raw float64 native housing-cap expression are unchanged. C1 changes which policy definitions are actually evaluated by clones, reform baselines and existing branches. Earlier reform/behavioral or cloned-system population outputs may therefore be stale even though canonical threshold arithmetic is unchanged. The tiny-household checks establish the reported correction; they do not certify population invariance. The coordinator should use the exact hashes and whether its acceptance path uses those operations to decide which runs need refreshing. No population rerun was attempted here, and earlier wheel/source hashes are superseded for promotion.

### Separate upstream SNAP issue

The no-income 2026 single-adult annual SNAP change from **$3,596.039794921875** on actual country 1.764.6 (`92e6052d3e057c4e03b955d01a7ee4e3c2fb3131`) to **$298** reproduces on unchanged country 1.824.7 (`42103db1b7d5be74bd28ebfc8e93adb2c7859079`) and the canonical-SPM candidate, with identical monthly traces and **$0 SPM contribution**. The exact upstream trigger is `82745ca2390e57d8ecc108de3ca50abcbc7cb283`, changing omitted weekly work hours from 40 to 0. January remains eligible under the CA statewide waiver, encoded by `74b0a75e5f6bf9356156f5c6df2f0b2100f2d8b3`; February onward exposes the pre-existing immediate-ineligibility assumption that omits California's screening transition and three countable months.

The separate primary-source audit finds that full June screening implies earliest exhaustion in September; its controlled Jan–Aug receipt scenario is **$2,384 SNAP** and **$2,383 household net income**, each **$2,086 above** the candidate. Exact later eligibility depends on screening/recertification history. This is an upstream entitlement-timing issue exposed by an intentional input-default change, not an SPM or aggregation defect. See `/tmp/snap-upgrade-audit.md` and its source/result artifacts. It remains separate from C1/C2; this continuation neither changes SNAP policy nor rewrites its snapshots.
