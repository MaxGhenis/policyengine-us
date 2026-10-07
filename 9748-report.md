# us#9748 resume report — 2026-10-07

PR: https://github.com/PolicyEngine/policyengine-us/pull/9748

Pushed PR head: `8ecffe6d2980ef54c07ac957c44e5359b5860a73` on `upstream/fix-county-branch-carry-over`. Left draft; not merged.

## Changes

Continued the saved clean head `7aa7609340`, preserving prior regression commit `4fcf82d2cb`, the county/TIN formulas, all original 43 cases, canonical branch/nested cases and YAML seed, property tests, and changelog. No partner expected outputs were edited.

- `2474804faf`: merged main `dd9cb3f6839d290c8490c561b54b7afeedc3c888` cleanly. The actual `merge-tree --write-tree` succeeded; the staged merge tree matched its result. Preserved #9738/#9741 and merged #9751’s complementary SPM county read.
- `8ecffe6d29`: removed the inherited county dataset coverage exclusion/comment. Both commits were pushed immediately. This resume does not change county/TIN formula behavior; the existing PR formula changes still require the fresh impact comparisons below.

The cached finding was missed execution of canonical `has_tin.py:21`. The preserved direct-formula cases cover that line: branch canonical False overrides inherited legacy True; nested inherits False; default and unrelated sibling retain True. Ordinary calculate with canonical input bypasses the formula and cannot establish this coverage.

## Validation

| Current head / core | TIN | County branch/order | Existing FIPS fallback | Unique cases |
|---|---:|---:|---:|---:|
| Locked 3.32.8 | 6 pass | 41 pass | 4 pass | 51 pass |
| Exact 2e22c8f8016a4873bfc1e1257ee408a5ecc37ba8 | 6 pass | 41 pass | 4 pass | 51 pass |

Both canonical cases **fail against main’s exact formula on both cores**, returning True rather than False. The harness runs the full TIN file green, loads main’s formula from Git at dd9cb3f683, then reruns those two cases. It does not mock holders or inputs. Expected red runs exit 1; logs preserve both assertions.

Direct coverage on each core: **65/65 source statements and 15/15 changed executable lines covered, zero exclusions**. County: 44/44 statements, 14/14 branches (100%). TIN: 21/21 statements, 6/8 branches (93% combined); the two partial None guards are unchanged. The canonical read at line 21 executes.

Actual command `python policyengine_us/tests/run_selective_tests.py --coverage --files policyengine_us/tests/core/test_has_tin_branch_inputs.py policyengine_us/variables/household/demographic/person/has_tin.py` passed six cases. Main intentionally disables source coverage after deferring the mapped folders; direct coverage establishes coverage separately. No runner changes were made. All runs were single files, sequential, foreground, at nice 0. County tests use synthetic three-household data. No local suite or real microsimulation ran.

The exact core export matches all **194** tracked package files by Git blob hash, with zero missing/changed files, excluding c574 WIP substitution. Reused prior results: **73 passes on 3.32.8**, **52 on 757147c7**, including the unchanged five-case TIN YAML seed file and existing legacy/counties. Earlier baseline attempts collected no tests (copy failed); they are not counted as red evidence.

`make format` (ruff format and lint) passed before every commit. Latest `gh pr checks`: **27 passing, 8 pending, zero failures**. Full suites remain with CI. PR body refreshed with completed results and limits.

## Saved impact evidence

For saved main `3266705e42` versus prior PR `7aa7609340`, core `757147c7`, fresh 2025 on pinned default `populace_us_2024.h5@populace-us-2024-spm-20260909`: all **15 headline arrays and weights**, and **207,842 cached arrays across nine simulations**, are bitwise identical. Numeric weighted and maximum record deltas are exactly **0**; no cached UNKNOWN counties. PR SHA is inferred from the prior worktree reflog; saved JSON records import paths. This is historical evidence, not a fresh measurement of the new head.

Saved full-population branch probes: 57,240 households, 166,321 people, 66 reads per core/side across ascending and descending 2025–2027. Updated PR has zero UNKNOWN counties, mapping mismatches or CCS errors. Baseline has eight bad reads on 3.32.8 and 20 on 757147c7, affecting all households including 1,091 Maryland households. Branch-only legacy False changes TIN to False for all people in branch/nested while default/sibling stay True. The original 27 Maryland households in a 3,000-household sample is earlier reproduction evidence, not a current-main prediction.

The detailed audit and exact sums are in `.resume-evidence/impact-audit.md` and JSON. Saved locked-core fresh runs were killed by the memory cap; master 2026 branch failed before Python because disk was full. No completed full-eCPS comparison exists.

## Hub follow-up

Sandbox instructions prohibit new microsims here. Compare current main dd9cb3f683 against PR head 8ecffe6d29 on **3.32.8 and exact 2e22c8f8**, with fresh **2025 and 2026** runs; repeat forced reused/nested **2025→2026→2027 and reverse**. Fingerprint all branch-tree caches. Variables: county, county_fips, county_str, has_tin, md_ccs_payment_rate, md_ccs, income_tax, state_income_tax, snap, household_tax, household_benefits, household_net_income, spm_unit_net_income, spm_unit_is_in_spm_poverty, person_in_poverty. Expect zero ordinary deltas and no erroneous UNKNOWN counties; confirm on the new head before leaving draft. Household geography remains static as before; annual moves are a separate data-model decision.

## Delivery

The requested ~/reviews report path and original shared Git metadata are not writable in this sandbox. Report and evidence are saved in the assigned workspace, using local `.resume-git` metadata. The model commits are on the PR branch; report/evidence are mirrored on `origin/wip/hub-resume-sol2-9748`. Retrieve that ref to preserve the report independently of the original protected worktree metadata. No extra worktrees were created, no caller files were written, and all local test processes finished.
