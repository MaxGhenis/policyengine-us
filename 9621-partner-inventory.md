# US #9621 partner output inventory

**Incomplete: final multi-file model inventory is blocked by the mandatory shared heavy-lock wrapper in this sandbox. No contract fixture edit is authorized.**

Model build: `3126a708c9`, based on current main `2d0815ae23621f974bcb79e4a53b09e0b801119c`, with published CA 2026 anchors. Partner files have zero branch diff against that main. The model changes California 2026 tax brackets, deductions, exemption credits, and renter ceilings; final outputs can differ materially from the archived 43-case raw-head inventory. Compared with the archived pre-fix projection of $55,217.661311, the published renter ceiling is $55,830, so the $55,218 boundary qualifies. Unpublished CalEITC/YCTC/FYTC amounts remain projections and must not be described as final statutory publications.

The complete final file/case/output/old → new inventory has not been computed. The targeted file below provides a partial inventory; missing results must not be substituted with archived raw-head numbers. The preserved archived inventory, source transcript link, and within-tolerance differences are in `.resume-evidence/raw-head-partner-evidence.md`. Original specification: `~/reviews/us-hub/specs/B2-9621.md`; owner transcript: `~/.claude/projects/-Users-maxghenis-PolicyEngine-policyengine-us--claude-worktrees-hopeful-franklin-72889c/07615452-ac56-4c2b-b6eb-48b839e450c8.jsonl:1429`.

The prepared generator, `.resume-evidence/partner_inventory.py`, uses core's actual YAML loading, preprocessing, and comparisons. It records asserted outputs at full precision and captures errors; it never edits fixtures. `.resume-evidence/partner-inventory-instructions.md` describes single-file runs and a full inventory under the shared lock. A coordinated multi-file inventory must hold that lock. Every partner fixture with 2026 outputs is required to claim completion because eligibility and aggregate-credit outputs can change.

Pending hub gate, in one call after final inventory:

1. Are you sure you want to edit this test file?
2. Have you notified a team member about this change?
3. Have you notified the API partner about this change?

No previous rejected question is approval. Keep failures as evidence and explain each final intended change. Do not rewrite snapshots merely to pass CI.

## Completed targeted file (partial inventory)

This independently scheduled single file completed 5 cases/11 assertions with 6 changes beyond the $0.10 absolute tolerance and 0 calculation errors. No relative tolerance is set. The $55,218 renter case changes eligibility, and all six output differences are preserved for the gate. No changed outputs within tolerance were recorded for this file. The full partner sweep remains incomplete.

## Expected outputs outside fixture tolerance

| File | Case | Output | Old | New | Tolerance | Within tolerance |
| --- | --- | --- | --- | --- | --- | --- |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 1: ca_renter_credit_joint_fully_usable_against_liability (ca) | tax_units.tax_unit.ca_income_tax_before_credits@2026 | 539.99 | 534.88 | $0.10 absolute | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 1: ca_renter_credit_joint_fully_usable_against_liability (ca) | tax_units.tax_unit.ca_non_refundable_credits@2026 | 432.93 | 436.00 | $0.10 absolute | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 1: ca_renter_credit_joint_fully_usable_against_liability (ca) | tax_units.tax_unit.ca_income_tax_before_refundable_credits@2026 | 107.05 | 98.88 | $0.10 absolute | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 3: ca_renter_credit_single_above_income_cap_55218 (ca) | tax_units.tax_unit.ca_renter_credit@2026 | 0.00 | 60.00 | $0.10 absolute | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 5: ca_renter_credit_limited_by_liability_single_12000 (ca) | tax_units.tax_unit.ca_income_tax_before_credits@2026 | 61.65 | 61.00 | $0.10 absolute | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 5: ca_renter_credit_limited_by_liability_single_12000 (ca) | tax_units.tax_unit.ca_non_refundable_credits@2026 | 216.47 | 218.00 | $0.10 absolute | false |
