Fresh 2025: saved baseline US `3266705e426eda2688800732c2ea9f78cc88e7cf` versus prior PR worktree inferred HEAD `7aa7609340f6c27f684578c51d505e3ead0a1b25`, core `757147c7473d6a3baab9341fb045fa6778d1a7fd`. The saved run JSON records import paths rather than SHAs; previous worktree reflog shows that HEAD preceding all runs.

Dataset: `hf://datasets/policyengine/populace-us/populace_us_2024.h5@populace-us-2024-spm-20260909`.

All 15 headline arrays and weights are identical. Numeric deltas are exactly zero. All 207,842 cached arrays match across nine simulations; no cached county array contains UNKNOWN.

| Variable | Base weighted sum | PR weighted sum | Exact weighted delta |
|---|---:|---:|---:|
| county | n/a | n/a | n/a |
| county_fips | n/a | n/a | n/a |
| county_str | n/a | n/a | n/a |
| has_tin | 343234872.2962102 | 343234872.2962102 | 0.0 |
| household_benefits | 1959621379433.0708 | 1959621379433.0708 | 0.0 |
| household_net_income | 16357214862678.418 | 16357214862678.418 | 0.0 |
| household_tax | 3911274134519.4814 | 3911274134519.4814 | 0.0 |
| income_tax | 2415999173478.7236 | 2415999173478.7236 | 0.0 |
| md_ccs | 136838571.20442206 | 136838571.20442206 | 0.0 |
| md_ccs_payment_rate | 1153285405.8018095 | 1153285405.8018095 | 0.0 |
| person_in_poverty | 45907232.89194786 | 45907232.89194786 | 0.0 |
| snap | 99028974270.75998 | 99028974270.75998 | 0.0 |
| spm_unit_is_in_spm_poverty | 18457766.8895201 | 18457766.8895201 | 0.0 |
| spm_unit_net_income | 14085342100641.742 | 14085342100641.742 | 0.0 |
| state_income_tax | 551260176702.9845 | 551260176702.9845 | 0.0 |

County identifiers have no numeric weighted sum; all 57,240 records match exactly.

Probes: 57,240 households and 166,321 people, full default dataset, 66 reads per side/core. Values below count reads; repeated reads are included.

| Core / side | Scenario/order | Reads | UNKNOWN reads | Max UNKNOWN households | Max UNKNOWN MD | CCS errors |
|---|---|---:|---:|---:|---:|---:|
| base832 | upfront/ascending | 18 | 0 | 0 | 0 | 0 |
| base832 | upfront/descending | 18 | 8 | 57240 | 1091 | 8 |
| base832 | ecps/ascending | 15 | 0 | 0 | 0 | 0 |
| base832 | ecps/descending | 15 | 0 | 0 | 0 | 0 |
| pr832 | upfront/ascending | 18 | 0 | 0 | 0 | 0 |
| pr832 | upfront/descending | 18 | 0 | 0 | 0 | 0 |
| pr832 | ecps/ascending | 15 | 0 | 0 | 0 | 0 |
| pr832 | ecps/descending | 15 | 0 | 0 | 0 | 0 |
| basemaster | upfront/ascending | 18 | 8 | 57240 | 1091 | 8 |
| basemaster | upfront/descending | 18 | 8 | 57240 | 1091 | 8 |
| basemaster | ecps/ascending | 15 | 4 | 57240 | 1091 | 4 |
| basemaster | ecps/descending | 15 | 0 | 0 | 0 | 0 |
| prmaster | upfront/ascending | 18 | 0 | 0 | 0 | 0 |
| prmaster | upfront/descending | 18 | 0 | 0 | 0 | 0 |
| prmaster | ecps/ascending | 15 | 0 | 0 | 0 | 0 |
| prmaster | ecps/descending | 15 | 0 | 0 | 0 | 0 |

Branch-only legacy `has_itin=False`: both PR cores returned `has_tin=False` for all 166,321 people in the branch and nested branch; default and unrelated sibling stayed True. Both baseline cores returned True in all four simulations.

Pending impact work:
- core 3.32.8 fresh 2025 baseline/branch comparisons: both saved runs killed by memory watchdog
- core 3.32.8 fresh 2026 baseline/branch comparisons: both saved runs killed by memory watchdog
- core 757147c7 fresh 2026 branch run: failed before Python due no space left on device; baseline completed
- exact core 2e22c8f8016a4873bfc1e1257ee408a5ecc37ba8 fresh comparisons and probes: exported code exists, no results recorded
- original requested full-eCPS comparisons: original evidence full/ directory empty; completed runs here use default pinned populace dataset
