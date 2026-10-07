## What and why

Read stored county and TIN inputs using the requesting simulation's branch name. County lookup tries readable periods from latest start date to earliest, resolves branch/ancestor/default storage, skips sibling-only periods, and falls through to FIPS mapping when none is readable. Canonical `has_tin` takes precedence over legacy `has_itin`, then default `True`.

The county carry-over assumes dataset households are geographically static, preserving existing behavior even when the readable input is from a later year. Annual moves would require a separate data-model decision.

This round preserves the existing 40 county and three legacy-TIN cases, the two canonical direct-formula branch/nested cases, the YAML seed, and the two property tests committed during the previous attempt. It merges current main without conflicts, retaining #9738/#9741 and the complementary #9751 SPM county-input fix. The inherited county dataset-path coverage exclusion is removed so changed reads are measured directly.

## Test plan

- Policy YAML expectations from legal sources: not applicable; branch/cache input plumbing changes no policy rule.
- `make format` and lint pass; changelog fragment retained; partner expectations preserved.
- Current head `8ecffe6d29`: **51 cases pass on each requested core** (3.32.8 and exact `2e22c8f8`): TIN 6, county branch/order 41, existing FIPS fallback 4. The two canonical direct-formula cases fail against current main’s exact formula on both cores (`True` versus expected branch/nested `False`). The same test file runs green before the harness installs main’s formula; no holder or input behavior is mocked.
- All **65 source statements and 15 changed executable lines** are covered on both cores, with **zero exclusions**. County statement/branch coverage is 100%; TIN statement coverage is 100% (whole-file combined coverage 93%, with two unchanged `None` guards partially covered).
- The **actual selective runner passes six TIN cases**. Current main intentionally disables source coverage when its mapped directory targets are deferred, even if an explicit Python test exercises that source. Direct single-file coverage commands above establish coverage independently; the runner was preserved.
- Exported core `2e22c8f8016a4873bfc1e1257ee408a5ecc37ba8` matches all 194 tracked package files by Git blob hash (0 missing/changed); no `c574` WIP substitution.
- Recorded CI snapshot: 27 checks pass, 8 pending, none failing. Full suites are left to CI.
- Reused saved checks at `7aa7609340`: 73 passes on locked core 3.32.8; 52 passes on core master `757147c7`. Saved canonical coverage executes `has_tin.py:21`. The prior main-side commands failed to locate copied tests and are not counted as regression failures.

## Impact evidence and remaining runs

The completed saved fresh 2025 comparison uses main `3266705e42` versus the prior PR worktree at `7aa7609340`, with core `757147c7` and pinned default dataset `populace_us_2024.h5@populace-us-2024-spm-20260909`. All 15 headline arrays and all 207,842 cached arrays across nine simulations are bitwise identical; numeric weighted deltas are exactly zero. No cached county array contains `UNKNOWN`. This is saved evidence, not a new measurement of the updated head.

Completed saved reused/nested probes covered both 2025→2026→2027 and reverse, 57,240 households and 166,321 people, and 66 reads per run on each core. The PR had zero erroneous `UNKNOWN` counties, mapping mismatches, or Maryland CCS rate errors. Baseline had eight erroneous reads on 3.32.8 and 20 on `757147c7`; each affected 57,240 households including 1,091 in Maryland. A branch-only legacy `False` input made `has_tin=False` for all people in the branch and nested branch while default and sibling remained `True`.

Fresh locked-core 2025/2026 comparisons were killed by the memory watchdog. The saved master 2026 baseline completed, but the branch run failed before Python because disk was full. No completed full-eCPS comparison exists. Under this resume's sandbox instruction, no new real microsimulations were run.

Hub follow-up: compare current main against updated head in fresh 2025 and 2026 runs, on locked core 3.32.8 and exact `2e22c8f8`; repeat reused/nested ascending and descending 2025–2027 probes and fingerprint all branch-tree caches. Compare `county`, `county_fips`, `county_str`, `has_tin`, `md_ccs_payment_rate`, `md_ccs`, `income_tax`, `state_income_tax`, `snap`, `household_tax`, `household_benefits`, `household_net_income`, `spm_unit_net_income`, `spm_unit_is_in_spm_poverty`, and `person_in_poverty`. Expect zero ordinary single-year deltas; this expectation remains to be confirmed for the new head. The historical 27 Maryland households in a 3,000-household sample is reproduction evidence from before #9738.

Keep draft until the remaining impact checks are complete.

axiom: n/a: branch/cache plumbing for reading stored inputs; no policy rule changes

Detailed resume report and saved run evidence: [9748 report](https://github.com/MaxGhenis/policyengine-us/blob/wip/hub-resume-sol2-9748/9748-report.md).
