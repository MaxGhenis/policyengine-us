# IRS/state indexing partner output inventory

Partner fixtures were read without edits. Calculated values are proposed output changes, not approved contract changes.

Model: 3126a708c9 CA published 2026 calibration; fixtures unchanged. Year: 2026.
Assertions: 11; outside tolerance: 6; changed within tolerance: 0; errors: 0.

Each case index is one-based within its YAML file. Tables round financial values to cents; JSON retains full precision and every assertion, including unchanged outputs.

## Expected outputs outside fixture tolerance

| File | Case | Output | Old | New | Tolerance | Within tolerance |
| --- | --- | --- | --- | --- | --- | --- |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 1: ca_renter_credit_joint_fully_usable_against_liability (ca) | tax_units.tax_unit.ca_income_tax_before_credits@2026 | 539.99 | 534.88 | {"absolute": 0.1, "relative": null} | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 1: ca_renter_credit_joint_fully_usable_against_liability (ca) | tax_units.tax_unit.ca_non_refundable_credits@2026 | 432.93 | 436.0 | {"absolute": 0.1, "relative": null} | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 1: ca_renter_credit_joint_fully_usable_against_liability (ca) | tax_units.tax_unit.ca_income_tax_before_refundable_credits@2026 | 107.05 | 98.88 | {"absolute": 0.1, "relative": null} | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 3: ca_renter_credit_single_above_income_cap_55218 (ca) | tax_units.tax_unit.ca_renter_credit@2026 | 0.0 | 60.0 | {"absolute": 0.1, "relative": null} | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 5: ca_renter_credit_limited_by_liability_single_12000 (ca) | tax_units.tax_unit.ca_income_tax_before_credits@2026 | 61.65 | 61.0 | {"absolute": 0.1, "relative": null} | false |
| policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml | 5: ca_renter_credit_limited_by_liability_single_12000 (ca) | tax_units.tax_unit.ca_non_refundable_credits@2026 | 216.47 | 218.0 | {"absolute": 0.1, "relative": null} | false |

## Changed outputs within fixture tolerance

| File | Case | Output | Old | New | Tolerance | Within tolerance |
| --- | --- | --- | --- | --- | --- | --- |
