# Archived raw-head evidence; not final calibration or approved contracts

**Exact raw-head partner expectation changes.** There are **43 affected cases in eight files**, all **2026**. The verdict’s 11 failures identify only the edge-case subset. Partner files are unchanged between PR head and main.

All paths below begin `policyengine_us/tests/policy/baseline/partners/`. These are existing fixture values → raw-head values, rounded to cents. They identify expectation edits the uncorrected head would require; **none is presently authorized or recommended as final California calibration**.

| File:line | Output | Existing → raw head |
|---|---|---:|
| `amplifi/2026.yaml:149` | `ca_income_tax_before_credits` | 499.83 → 499.58 |
| `amplifi/2026.yaml:299` | `ca_income_tax_before_credits` | 267.83 → 267.58 |
| `amplifi/2026.yaml:438` | `ca_yctc` | 1,215.95 → 1,216.62 |
| `analytics_coverage/edge_cases/state/ca/cdcc.yaml:78` | `ca_income_tax_before_credits` | 339.83 → 339.58 |
| `cdcc.yaml:81` | `ca_non_refundable_credits` | 1,119.53 → 1,119.89 |
| `cdcc.yaml:154` | `ca_income_tax_before_credits` | 1,192.01 → 1,191.04 |
| `cdcc.yaml:156` | `ca_non_refundable_credits` | 999.23 → 999.59 |
| `cdcc.yaml:158` | `ca_income_tax_before_refundable_credits` | 192.78 → 191.45 |
| `eitc.yaml:282` | `ca_eitc` | 0 → 122.10 |
| `eitc.yaml:283` | `ca_eitc_eligible` | false → true |
| `foster_youth_tax_credit.yaml:50` | `ca_foster_youth_tax_credit` | 1,215.95 → 1,216.62 |
| `foster_youth_tax_credit.yaml:161` | `ca_foster_youth_tax_credit` | 1,583.70 → 1,591.75 |
| `renter_credit.yaml:69` | `ca_income_tax_before_credits` | 539.99 → 539.73 |
| `renter_credit.yaml:71` | `ca_non_refundable_credits` | 432.93 → 433.11 |
| `renter_credit.yaml:73` | `ca_income_tax_before_refundable_credits` | 107.05 → 106.63 |
| `renter_credit.yaml:164` | `ca_renter_credit` | 0 → 60 |
| `tax_credits_composition.yaml:69` | `ca_eitc` | 401.89 → 402.04 |
| `tax_credits_composition.yaml:71` | `ca_yctc` | 1,215.95 → 1,216.62 |
| `tax_credits_composition.yaml:73` | `ca_foster_youth_tax_credit` | 1,215.95 → 1,216.62 |
| `tax_credits_composition.yaml:75` | `ca_refundable_credits` | 2,833.78 → 2,835.27 |
| `tax_credits_composition.yaml:80` | `ca_income_tax` | −2,833.78 → −2,835.27 |
| `tax_credits_composition.yaml:163` | `ca_yctc` | 791.85 → 795.87 |
| `tax_credits_composition.yaml:171` | `ca_non_refundable_credits` | 918.70 → 919.14 |
| `tax_credits_composition.yaml:177` | `ca_refundable_credits` | 882.22 → 886.28 |
| `tax_credits_composition.yaml:178` | `ca_income_tax` | −882.22 → −886.28 |
| `yctc.yaml:68` | `ca_yctc` | 1,215.95 → 1,216.62 |
| `yctc.yaml:199` | `ca_yctc` | 791.85 → 795.87 |

Abbreviated edge-case filenames share `analytics_coverage/edge_cases/state/ca/`.

In `analytics_coverage/signatures/ca.yaml`:

| Output and change | Signature IDs | Corresponding lines |
|---|---|---|
| `ca_income_tax_before_credits`: **499.99 → 499.73** | 15, 21, 22, 28, 31, 41, 44, 58, 60, 61, 63, 67, 68, 78, 79, 80 | 133, 335, 527, 903, 1286, 1480, 1870, 2257, 2641, 2841, 3225, 3801, 3995, 4566, 4762, 4960 |
| `ca_yctc`: **1,215.95 → 1,216.62** | 23, 29, 43, 46, 59, 62, 64, 65, 70, 77, 100, 113, 128 | 718, 1090, 1672, 2058, 2452, 3032, 3416, 3606, 4190, 4381, 5153, 5343, 5528 |

Additional asserted outputs move within the existing $0.10 tolerance and do not require expectation edits:

| Edge-case file:line | Output | Existing → raw head |
|---|---|---:|
| `eitc.yaml:184` | `ca_eitc` | 168.39 → 168.43 |
| `eitc.yaml:235` | `ca_eitc` | 122.08 → 122.11 |
| `renter_credit.yaml:257` | `ca_income_tax_before_credits` | 61.65 → 61.61 |
| `renter_credit.yaml:259` | `ca_non_refundable_credits` | 216.47 → 216.55 |
| `tax_credits_composition.yaml:161` | `ca_eitc` | 90.37 → 90.41 |

The eligibility switches are material: the investment ceiling becomes `4,925.811789` from `4,923.099262`, making $4,924 eligible; the renter ceiling becomes `55,248.085119` from `55,217.661311`, making $55,218 eligible.

Evidence is the preserved [owner transcript](/Users/maxghenis/.claude/projects/-Users-maxghenis-PolicyEngine-policyengine-us--claude-worktrees-hopeful-franklin-72889c/07615452-ac56-4c2b-b6eb-48b839e450c8.jsonl:1429): actual 43-case failure output, the 90-parameter difference table, and hand-computed downstream assertions. Fresh read-only model runs stalled during loading and were interrupted; this is **not** a newly completed main-versus-head simulation.

**Max’s partner gate remains unanswered.** The prior rejected question supplies no approval. After producing the final model and final output inventory, the top-level builder must ask in one `AskUserQuestion` call:

1. Are you sure you want to edit this test file?
2. Have you notified a team member about this change?
3. Have you notified the API partner about this change?

Subagents must not edit partner files.

