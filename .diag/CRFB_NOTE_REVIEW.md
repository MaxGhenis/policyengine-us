# Review of the held CRFB correction note (2026-10-02)

Draft: /Users/maxghenis/reviews/pe-us-inplace-cache-writes-2026-10-01/crfb_note.html
Verdict: REQUEST CHANGES. Nothing was sent, drafted or modified in Gmail.

## Evidence run in this review

- `niit_split.py` (this folder): a real baseline Microsimulation on the same dataset file
  (sha 6496cc4393d4) computed `net_investment_income` and `filing_status`. The script
  recomputed NIIT under the main run's corrupted AGI and the fix run's AGI from the saved NPZ
  arrays. On correct AGI the recomputed NIIT matches the model's own `net_investment_income_tax`
  exactly.
  - Result: the $1.792bn federal income tax overstatement splits into $1.340bn NIIT and
    $0.452bn credits.
  - NIIT alone explains the change exactly in 2,209 of the 2,976 tax units that moved.
- Tax-unit-to-household mapping from the dataset h5 (weights match): the $0.299bn of
  household tax that sits outside federal income tax and `household_state_income_tax` is all
  state-level.
  - Breakdown: WI $203.5m, NC $37.8m, IL $32.7m, CA $14.4m, OK $10.8m.
  - Cause: `household_state_tax_before_refundable_credits` adds `state_use_tax`;
    `nc_use_tax` reads AGI and `ca_use_tax` reads `ca_agi`. In WI, the household tax path uses
    the standard computation, while `wi_income_tax` takes `min_(standard, exclusion)`.
- An independent Opus reviewer (agent a288ee157ee653f8e) reached the same NIIT/credit split
  by a different method ($1.340bn at most NIIT, $0.452bn at least credits).

See the final session report for the findings and the recommended rewrite.
