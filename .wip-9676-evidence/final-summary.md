# #9676 downloaded CI evidence

Artifact root: `/Users/maxghenis/.subfleet/worktrees/20261006-181319-hub-resume-sol-9676/.resume/ci-validation-combined/reports`.

Phase statuses: compare_status=0, impact_status=0, tests_status=1.

| Task/run | Actual / expected exit | Reported test counts | Wall / CPU seconds |
|---|---:|---|---:|
| main/runtime_identity | 0 / 0 | not reported | 27.35 / 27.67 |
| main/main_new_member_yaml | 0 / 0 | 11 failed, 5 passed, 1 warnings | 64.92 / 64.2 |
| main/main_household_checks | 0 / 0 | not reported | 31.1 / 31.41 |
| main/main_known_resource_defect | 0 / 0 | 1 failed, 1 warnings | 54.05 / 54.36 |
| mutations/runtime_identity | 0 / 0 | not reported | 24.61 / 24.93 |
| mutations/new_member_mutations | 1 / 0 | 1 failed, 31 passed, 2 warnings across separate mutation sessions | 96.99 / 97.29 |
| mutations/old_member_mutations | 0 / 0 | 28 passed, 2 warnings across separate mutation sessions | 94.78 / 95.09 |
| mutations/new_property_mutations | 0 / 0 | 2 failed, 76 passed, 3 warnings across separate mutation sessions | 85.8 / 86.11 |
| mutations/old_property_mutations | 0 / 0 | 72 passed, 3 warnings across separate mutation sessions | 86.08 / 86.38 |
| old_head/runtime_identity | 0 / 0 | not reported | 25.94 / 26.25 |
| old_head/old_head_new_member_yaml | 0 / 0 | 16 passed, 1 warnings | 55.68 / 55.99 |
| old_head/old_head_household_checks | 0 / 0 | not reported | 29.16 / 29.41 |
| suites/runtime_identity | 0 / 0 | not reported | 32.6 / 31.59 |
| suites/mo_tanf_yaml | 0 / 0 | 214 passed, 26 warnings | 1,569.13 / 1,579.22 |
| suites/property_suites | 0 / 0 | 66 passed | 55.25 / 55.56 |
| suites/explicit_source_roles | 0 / 0 | not reported | 34.01 / 34.33 |
| suites/input_definitions | 0 / 0 | 4 passed | 27.49 / 27.82 |
| suites/partner_contracts | 0 / 0 | 623 passed, 144 warnings | 9,341 / 9,398.35 |
| suites/household_checks | 0 / 0 | not reported | 29.97 / 30.29 |
| suites/known_resource_defect | 0 / 0 | 1 failed, 1 warnings | 53.31 / 53.62 |

Runtime (main): `{"code_sha": "5b1d5bdf47044607341d76f3c932ba2e7b74a060", "membership_formula_sha256": "63ccbb403d9f75050caa8c692da743eeb2761b11fd4227bf588927c8667507a6", "policyengine_core": "3.32.15", "policyengine_us_file": "/home/runner/work/policyengine-us/policyengine-us/main/policyengine_us/__init__.py", "policyengine_us_version": "2.29.14", "python": "3.14.7"}`.

Runtime (mutations): `{"code_sha": "e39bb2c4c248ac4699032d7053f7429213014e75", "membership_formula_sha256": "31410601f79d20ae5104896745dc531a0443c1088c232cd1acbd48fedcfadbfa", "policyengine_core": "3.32.15", "policyengine_us_file": "/home/runner/work/policyengine-us/policyengine-us/wip/policyengine_us/__init__.py", "policyengine_us_version": "2.29.14", "python": "3.14.7"}`.

Mutation `new_member_mutations/drop_has_dependent_child`: exit 1 / expected 1; contract matched=True; intended detecting case=Explicit parent flag requires a dependent child; case failed=True.

Mutation `new_member_mutations/none`: exit 0 / expected 0; contract matched=True; intended detecting case=None; case failed=None.

Mutation `new_property_mutations/drop_has_dependent_child`: exit 1 / expected 1; contract matched=True; intended detecting case=test_parent_flag_needs_a_dependent_child_in_the_persons_tax_unit; case failed=True.

Mutation `new_property_mutations/none`: exit 0 / expected 0; contract matched=True; intended detecting case=None; case failed=None.

Mutation `new_property_mutations/npcr_never`: exit 1 / expected 1; contract matched=True; intended detecting case=test_non_parent_caretaker_identification_matches_independent_rule; case failed=True.

Mutation `old_member_mutations/drop_has_dependent_child`: exit 0 / expected 0; contract matched=True; intended detecting case=None; case failed=None.

Mutation `old_member_mutations/none`: exit 0 / expected 0; contract matched=True; intended detecting case=None; case failed=None.

Mutation `old_property_mutations/drop_has_dependent_child`: exit 0 / expected 0; contract matched=True; intended detecting case=None; case failed=None.

Mutation `old_property_mutations/none`: exit 0 / expected 0; contract matched=True; intended detecting case=None; case failed=None.

Mutation `old_property_mutations/npcr_never`: exit 0 / expected 0; contract matched=True; intended detecting case=None; case failed=None.

Runtime (old_head): `{"code_sha": "a6c44418afccac0270dcb9ea155338dac0c9a05d", "membership_formula_sha256": "bbf8d1c6824ca6fe3d5bf1bd48a35664abcd091b8d7cdc127e54e9da216ba862", "policyengine_core": "3.32.15", "policyengine_us_file": "/home/runner/work/policyengine-us/policyengine-us/old_head/policyengine_us/__init__.py", "policyengine_us_version": "2.29.14", "python": "3.14.7"}`.

Runtime (suites): `{"code_sha": "e39bb2c4c248ac4699032d7053f7429213014e75", "membership_formula_sha256": "31410601f79d20ae5104896745dc531a0443c1088c232cd1acbd48fedcfadbfa", "policyengine_core": "3.32.15", "policyengine_us_file": "/home/runner/work/policyengine-us/policyengine-us/wip/policyengine_us/__init__.py", "policyengine_us_version": "2.29.14", "python": "3.14.7"}`.

## Household checks: branch_minus_main

| Case | Main grant | Compared grant | Change |
|---|---:|---:|---:|
| income_loss_disability_14400 | 292.089966 | 0 | -292.089966 |
| income_loss_zero_income_pair | 292.089966 | 341.807404 | 49.717438 |
| regression_dependent_45_adult_child | 234.086273 | 292.089966 | 58.003693 |
| regression_unmarked_grandparent | 234.086273 | 292.089966 | 58.003693 |
| resource_fixture_a_excluded_grandparent_assets | 0 | 0 | 0 |
| resource_fixture_b_included_npcr_spouse_assets | 234.086273 | 234.086273 | 0 |

## Household checks: old_head_minus_main

| Case | Main grant | Compared grant | Change |
|---|---:|---:|---:|
| income_loss_disability_14400 | 292.089966 | 0 | -292.089966 |
| income_loss_zero_income_pair | 292.089966 | 341.807404 | 49.717438 |
| regression_dependent_45_adult_child | 234.086273 | 292.089966 | 58.003693 |
| regression_unmarked_grandparent | 234.086273 | 292.089966 | 58.003693 |
| resource_fixture_a_excluded_grandparent_assets | 0 | 0 | 0 |
| resource_fixture_b_included_npcr_spouse_assets | 234.086273 | 234.086273 | 0 |

## Microsimulation measured cost

| Run | Exit | Checkpoint | Wall / CPU seconds | Peak RSS kbytes |
|---|---:|---|---:|---:|
| branch_marked_2025 | 0 | complete | 343.84 / 344.04 | 8,542,576 |
| branch_marked_2026 | 0 | complete | 359.21 / 359.4 | 8,732,492 |
| branch_marked_no_assets_2025 | 0 | complete | 352.33 / 352.53 | 8,553,728 |
| branch_marked_no_assets_2026 | 0 | complete | 363.44 / 363.58 | 8,733,988 |
| branch_unmodified_2025 | 0 | complete | 343.41 / 343.62 | 8,553,956 |
| branch_unmodified_2026 | 0 | complete | 361.72 / 361.93 | 8,729,016 |
| main_marked_2025 | 0 | complete | 342.26 / 342.45 | 8,549,672 |
| main_marked_2026 | 0 | complete | 366.92 / 367.11 | 8,733,696 |
| main_marked_no_assets_2025 | 0 | complete | 348.48 / 348.67 | 8,556,960 |
| main_marked_no_assets_2026 | 0 | complete | 372.55 / 372.73 | 8,727,768 |
| main_unmodified_2025 | 0 | complete | 339.73 / 339.94 | 8,557,184 |
| main_unmodified_2026 | 0 | complete | 370.76 / 372.49 | 8,957,176 |

## Paired impact: 2026

| Scenario | Annual entitlement change | Annual actual MO TANF change | January entitlement change | Two-record share |
|---|---:|---:|---:|---:|
| unmodified | 0 | 0 | 0 | undefined |
| marked | -20,456,426.62567 | 0 | -1,704,702.218806 | 100% |
| marked_no_assets | -15,230,533.091659 | 0 | -1,269,211.090972 | 99.9992% |

unmodified: 12 months reported; monthly entitlement change range 0 to 0; monthly sum matches annual=True.

January membership/failure evidence: `{"failures_among_membership_changed_units": {"branch": {"both_income_and_resources": {"records": 3, "weighted": 16581.314453125}, "income_only": {"records": 1, "weighted": 5836.22314453125}, "neither": {"records": 0, "weighted": 0.0}, "resources_only": {"records": 0, "weighted": 0.0}}, "main": {"both_income_and_resources": {"records": 3, "weighted": 16581.314453125}, "income_only": {"records": 1, "weighted": 5836.22314453125}, "neither": {"records": 0, "weighted": 0.0}, "resources_only": {"records": 0, "weighted": 0.0}}}, "members_added": {"records": 4, "weighted": 22417.537109375}, "members_removed": {"records": 0, "weighted": 0.0}, "new_income_failures": 0, "new_resource_failures": 0, "units_with_membership_change": 4}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 6.0, "mo_tanf_countable_income": 5206.22509765625, "mo_tanf_countable_resources": 295.1788635253906, "mo_tanf_gross_earned_income": 3585.23828125, "mo_tanf_gross_unearned_income": 2896.06640625, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 5.0, "mo_tanf_countable_income": 3915.53955078125, "mo_tanf_countable_resources": 295.1788635253906, "mo_tanf_gross_earned_income": 3585.23828125, "mo_tanf_gross_unearned_income": 1605.3807373046875, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 17211, "takeup": false, "weight": 5836.22314453125}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 5.0, "mo_tanf_countable_income": 3488.01025390625, "mo_tanf_countable_resources": 2108.42041015625, "mo_tanf_gross_earned_income": 2321.9794921875, "mo_tanf_gross_unearned_income": 2100.02392578125, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 3488.01025390625, "mo_tanf_countable_resources": 2108.42041015625, "mo_tanf_gross_earned_income": 2321.9794921875, "mo_tanf_gross_unearned_income": 2100.02392578125, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 76134, "takeup": false, "weight": 7822.154296875}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 6.0, "mo_tanf_countable_income": 2310.43212890625, "mo_tanf_countable_resources": 18132.416015625, "mo_tanf_gross_earned_income": 3585.648193359375, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 5.0, "mo_tanf_countable_income": 2310.43212890625, "mo_tanf_countable_resources": 18132.416015625, "mo_tanf_gross_earned_income": 3585.648193359375, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1017211, "takeup": false, "weight": 8758.9931640625}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 2174.78564453125, "mo_tanf_countable_resources": 7964.24169921875, "mo_tanf_gross_earned_income": 2447.873046875, "mo_tanf_gross_unearned_income": 702.870361328125, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 2174.78564453125, "mo_tanf_countable_resources": 7964.24169921875, "mo_tanf_gross_earned_income": 2447.873046875, "mo_tanf_gross_unearned_income": 702.870361328125, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1134143, "takeup": false, "weight": 0.1669781506061554}`.

marked: 12 months reported; monthly entitlement change range -1,704,702.218806 to -1,704,702.218806; monthly sum matches annual=True.

January membership/failure evidence: `{"failures_among_membership_changed_units": {"branch": {"both_income_and_resources": {"records": 1, "weighted": 7822.154296875}, "income_only": {"records": 1, "weighted": 5836.22314453125}, "neither": {"records": 0, "weighted": 0.0}, "resources_only": {"records": 2, "weighted": 8759.16015625}}, "main": {"both_income_and_resources": {"records": 1, "weighted": 7822.154296875}, "income_only": {"records": 0, "weighted": 0.0}, "neither": {"records": 1, "weighted": 5836.22314453125}, "resources_only": {"records": 2, "weighted": 8759.16015625}}}, "members_added": {"records": 4, "weighted": 22417.537109375}, "members_removed": {"records": 0, "weighted": 0.0}, "new_income_failures": 1, "new_resource_failures": 0, "units_with_membership_change": 4}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": -3505.07958984375, "annual_main": 3505.07958984375, "annual_weighted_change": -20456426.625670195, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 1290.685791015625, "mo_tanf_countable_resources": 295.1788635253906, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 1290.685791015625, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 295.1788635253906, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 17211, "takeup": false, "weight": 5836.22314453125}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 922.6636352539062, "mo_tanf_countable_resources": 2108.42041015625, "mo_tanf_gross_earned_income": 1246.4080810546875, "mo_tanf_gross_unearned_income": 171.7248992919922, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 922.6636352539062, "mo_tanf_countable_resources": 2108.42041015625, "mo_tanf_gross_earned_income": 1246.4080810546875, "mo_tanf_gross_unearned_income": 171.7248992919922, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 76134, "takeup": false, "weight": 7822.154296875}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 18132.416015625, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 18132.416015625, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1017211, "takeup": false, "weight": 8758.9931640625}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 2.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 7964.24169921875, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 1.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 7964.24169921875, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1134143, "takeup": false, "weight": 0.1669781506061554}`.

marked_no_assets: 12 months reported; monthly entitlement change range -1,269,211.090972 to -1,269,211.090972; monthly sum matches annual=True.

January membership/failure evidence: `{"failures_among_membership_changed_units": {"branch": {"both_income_and_resources": {"records": 0, "weighted": 0.0}, "income_only": {"records": 2, "weighted": 13658.376953125}, "neither": {"records": 2, "weighted": 8759.16015625}, "resources_only": {"records": 0, "weighted": 0.0}}, "main": {"both_income_and_resources": {"records": 0, "weighted": 0.0}, "income_only": {"records": 1, "weighted": 7822.154296875}, "neither": {"records": 3, "weighted": 14595.3837890625}, "resources_only": {"records": 0, "weighted": 0.0}}}, "members_added": {"records": 4, "weighted": 22417.537109375}, "members_removed": {"records": 0, "weighted": 0.0}, "new_income_failures": 1, "new_resource_failures": 0, "units_with_membership_change": 4}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": -3505.07958984375, "annual_main": 3505.07958984375, "annual_weighted_change": -20456426.625670195, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 1290.685791015625, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 1290.685791015625, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 17211, "takeup": false, "weight": 5836.22314453125}`.

Driver: `{"annual_branch": 4101.6888427734375, "annual_change_per_record": 596.6092529296875, "annual_main": 3505.07958984375, "annual_weighted_change": 5225696.368027568, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 1017211, "takeup": false, "weight": 8758.9931640625}`.

Driver: `{"annual_branch": 2809.0352783203125, "annual_change_per_record": 1180.7891235351562, "annual_main": 1628.2461547851562, "annual_weighted_change": 197.16598410376355, "branch": {"mo_tanf_assistance_unit_size": 2.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 1.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 1134143, "takeup": false, "weight": 0.1669781506061554}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 922.6636352539062, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 1246.4080810546875, "mo_tanf_gross_unearned_income": 171.7248992919922, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 922.6636352539062, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 1246.4080810546875, "mo_tanf_gross_unearned_income": 171.7248992919922, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 76134, "takeup": false, "weight": 7822.154296875}`.

## Paired impact: 2025

| Scenario | Annual entitlement change | Annual actual MO TANF change | January entitlement change | Two-record share |
|---|---:|---:|---:|---:|
| unmodified | 0 | 0 | 0 | undefined |
| marked | -20,311,379.997135 | 0 | -1,692,614.999761 | 100% |
| marked_no_assets | -15,122,540.558423 | 0 | -1,260,211.713202 | 99.9992% |

unmodified: 12 months reported; monthly entitlement change range 0 to 0; monthly sum matches annual=True.

January membership/failure evidence: `{"failures_among_membership_changed_units": {"branch": {"both_income_and_resources": {"records": 3, "weighted": 16463.744140625}, "income_only": {"records": 1, "weighted": 5794.84130859375}, "neither": {"records": 0, "weighted": 0.0}, "resources_only": {"records": 0, "weighted": 0.0}}, "main": {"both_income_and_resources": {"records": 3, "weighted": 16463.744140625}, "income_only": {"records": 1, "weighted": 5794.84130859375}, "neither": {"records": 0, "weighted": 0.0}, "resources_only": {"records": 0, "weighted": 0.0}}}, "members_added": {"records": 4, "weighted": 22258.5859375}, "members_removed": {"records": 0, "weighted": 0.0}, "new_income_failures": 0, "new_resource_failures": 0, "units_with_membership_change": 4}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 6.0, "mo_tanf_countable_income": 5006.95751953125, "mo_tanf_countable_resources": 288.3983459472656, "mo_tanf_gross_earned_income": 3465.6572265625, "mo_tanf_gross_unearned_income": 2776.51953125, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 5.0, "mo_tanf_countable_income": 3759.32080078125, "mo_tanf_countable_resources": 288.3983459472656, "mo_tanf_gross_earned_income": 3465.6572265625, "mo_tanf_gross_unearned_income": 1528.8828125, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 17211, "takeup": false, "weight": 5794.84130859375}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 5.0, "mo_tanf_countable_income": 3326.6689453125, "mo_tanf_countable_resources": 2059.98828125, "mo_tanf_gross_earned_income": 2244.532958984375, "mo_tanf_gross_unearned_income": 1990.3138427734375, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 3326.6689453125, "mo_tanf_countable_resources": 2059.98828125, "mo_tanf_gross_earned_income": 2244.532958984375, "mo_tanf_gross_unearned_income": 1990.3138427734375, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 76134, "takeup": false, "weight": 7766.69140625}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 6.0, "mo_tanf_countable_income": 2230.7021484375, "mo_tanf_countable_resources": 17715.8984375, "mo_tanf_gross_earned_income": 3466.053466796875, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 5.0, "mo_tanf_countable_income": 2230.7021484375, "mo_tanf_countable_resources": 17715.8984375, "mo_tanf_gross_earned_income": 3466.053466796875, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1017211, "takeup": false, "weight": 8696.8876953125}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 2067.318359375, "mo_tanf_countable_resources": 7781.29638671875, "mo_tanf_gross_earned_income": 2366.22705078125, "mo_tanf_gross_unearned_income": 649.833740234375, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 2067.318359375, "mo_tanf_countable_resources": 7781.29638671875, "mo_tanf_gross_earned_income": 2366.22705078125, "mo_tanf_gross_unearned_income": 649.833740234375, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1134143, "takeup": false, "weight": 0.16579420864582062}`.

marked: 12 months reported; monthly entitlement change range -1,692,614.999761 to -1,692,614.999761; monthly sum matches annual=True.

January membership/failure evidence: `{"failures_among_membership_changed_units": {"branch": {"both_income_and_resources": {"records": 1, "weighted": 7766.69140625}, "income_only": {"records": 1, "weighted": 5794.84130859375}, "neither": {"records": 0, "weighted": 0.0}, "resources_only": {"records": 2, "weighted": 8697.0537109375}}, "main": {"both_income_and_resources": {"records": 1, "weighted": 7766.69140625}, "income_only": {"records": 0, "weighted": 0.0}, "neither": {"records": 1, "weighted": 5794.84130859375}, "resources_only": {"records": 2, "weighted": 8697.0537109375}}}, "members_added": {"records": 4, "weighted": 22258.5859375}, "members_removed": {"records": 0, "weighted": 0.0}, "new_income_failures": 1, "new_resource_failures": 0, "units_with_membership_change": 4}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": -3505.07958984375, "annual_main": 3505.07958984375, "annual_weighted_change": -20311379.9971354, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 1247.6365966796875, "mo_tanf_countable_resources": 288.3983459472656, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 1247.6365966796875, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 288.3983459472656, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 17211, "takeup": false, "weight": 5794.84130859375}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 877.1238403320312, "mo_tanf_countable_resources": 2059.98828125, "mo_tanf_gross_earned_income": 1204.8358154296875, "mo_tanf_gross_unearned_income": 153.8999481201172, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 877.1238403320312, "mo_tanf_countable_resources": 2059.98828125, "mo_tanf_gross_earned_income": 1204.8358154296875, "mo_tanf_gross_unearned_income": 153.8999481201172, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 76134, "takeup": false, "weight": 7766.69140625}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 17715.8984375, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 17715.8984375, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1017211, "takeup": false, "weight": 8696.8876953125}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 2.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 7781.29638671875, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "main": {"mo_tanf_assistance_unit_size": 1.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 7781.29638671875, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 0.0}, "spm_unit_id": 1134143, "takeup": false, "weight": 0.16579420864582062}`.

marked_no_assets: 12 months reported; monthly entitlement change range -1,260,211.713202 to -1,260,211.713202; monthly sum matches annual=True.

January membership/failure evidence: `{"failures_among_membership_changed_units": {"branch": {"both_income_and_resources": {"records": 0, "weighted": 0.0}, "income_only": {"records": 2, "weighted": 13561.533203125}, "neither": {"records": 2, "weighted": 8697.0537109375}, "resources_only": {"records": 0, "weighted": 0.0}}, "main": {"both_income_and_resources": {"records": 0, "weighted": 0.0}, "income_only": {"records": 1, "weighted": 7766.69140625}, "neither": {"records": 3, "weighted": 14491.89453125}, "resources_only": {"records": 0, "weighted": 0.0}}}, "members_added": {"records": 4, "weighted": 22258.5859375}, "members_removed": {"records": 0, "weighted": 0.0}, "new_income_failures": 1, "new_resource_failures": 0, "units_with_membership_change": 4}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": -3505.07958984375, "annual_main": 3505.07958984375, "annual_weighted_change": -20311379.9971354, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 1247.6365966796875, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 1247.6365966796875, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 17211, "takeup": false, "weight": 5794.84130859375}`.

Driver: `{"annual_branch": 4101.6888427734375, "annual_change_per_record": 596.6092529296875, "annual_main": 3505.07958984375, "annual_weighted_change": 5188643.670713782, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 1017211, "takeup": false, "weight": 8696.8876953125}`.

Driver: `{"annual_branch": 2809.0352783203125, "annual_change_per_record": 1180.7891235351562, "annual_main": 1628.2461547851562, "annual_weighted_change": 195.76799831410335, "branch": {"mo_tanf_assistance_unit_size": 2.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 1.0, "mo_tanf_countable_income": 0.0, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 0.0, "mo_tanf_gross_unearned_income": 0.0, "mo_tanf_income_eligible": 1.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 1134143, "takeup": false, "weight": 0.16579420864582062}`.

Driver: `{"annual_branch": 0.0, "annual_change_per_record": 0.0, "annual_main": 0.0, "annual_weighted_change": 0.0, "branch": {"mo_tanf_assistance_unit_size": 4.0, "mo_tanf_countable_income": 877.1238403320312, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 1204.8358154296875, "mo_tanf_gross_unearned_income": 153.8999481201172, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "main": {"mo_tanf_assistance_unit_size": 3.0, "mo_tanf_countable_income": 877.1238403320312, "mo_tanf_countable_resources": 0.0, "mo_tanf_gross_earned_income": 1204.8358154296875, "mo_tanf_gross_unearned_income": 153.8999481201172, "mo_tanf_income_eligible": 0.0, "mo_tanf_non_parent_caretaker_included": 0.0, "mo_tanf_resources_eligible": 1.0}, "spm_unit_id": 76134, "takeup": false, "weight": 7766.69140625}`.

## Missing or unexpected evidence

- Nonzero phase status: tests_status=1
- Unexpected test result in task: mutations
- Exit mismatch: mutations/new_member_mutations
