# Form 4952 dataset lineage and outstanding impact request

Read-only source audit, 2026-10-07. No tests or microsimulations were run for this audit. No dataset or model policy was changed.

## Finding: the saved input is an imputed deduction residual

**The saved $53.68B input total is not an observed total of raw investment interest paid.** The default dataset's `investment_interest_expense` is imputed from a residual of IRS Schedule A interest deductions. The residual also includes deductible mortgage points and mortgage-insurance premiums. Treating all of it as raw Form 4952 line 1 can apply the investment-income cap to non-investment deduction components and re-limit an already reported deduction. The old screen's $30.35B potentially disallowed amount, $26.97B among itemizers, and illustrative +$5.4–9.4B tax estimate therefore cannot be interpreted as a validated §163(d) revenue score.

The synthetic-household policy implementation can be assessed independently using explicit raw paid-interest inputs. Do not silently alter statutory formulas to accommodate the dataset. Publish microsimulation results as mechanical changes on the pinned dataset, with the input-concept limitation disclosed. A defensible economic score needs corrected source concepts or a documented sensitivity design supplied by the data/hub owners.

## Release-specific evidence

1. The saved baseline log `/Users/maxghenis/reviews/pe-us-163d-2026-10-03/microsim/main_2026.log` records `populace-us-2024-spm-20260909` and policyengine-core 3.32.12. The recovery snapshot `40a7fcbca6:policyengine_us/system.py:64-74` uses that same default URI and pins SHA-256 `6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84`.
2. Cached release/build manifests are under `/Users/maxghenis/.cache/huggingface/hub/datasets--policyengine--populace-us/snapshots/9a814a3b3b53c0ecd6e1737b6ec862c31300ef6f/releases/populace-us-2024-spm-20260909/`. They record that SHA and SPM enrichment code pin `295130c9f901e08db11457f16dbdee4e2349c5ba`.
3. The small [parent build manifest](https://huggingface.co/datasets/policyengine/populace-us/raw/populace-us-2024-spm-20260909/releases/populace-us-2024-spm-20260909/parent_build_manifest.json) was read over HTTPS, without downloading a dataset. It identifies parent `populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z`, source code commit `cae8640f9e65e274aea65c7916cb37b956978e32`, dataset SHA `48b9d479fb4fd1c3537f9383ce4697d130b6f618658409d74f6233c43b994c7e`, and base H5 SHA `5d8a31622e6f4772188944385c5a6d4bd0e589f846043e6fd56634c9f6ef7d61`.
4. At that exact parent commit, [puf_interest_components.py:164-175](https://github.com/PolicyEngine/populace/blob/cae8640f9e65e274aea65c7916cb37b956978e32/packages/populace-build/src/populace/build/us_runtime/puf_interest_components.py#L164) explicitly states that the residual sent to `investment_interest_expense` is broader than the table's investment-interest column and includes deductible points and qualified mortgage-insurance premiums. [puf_support.py:714-730](https://github.com/PolicyEngine/populace/blob/cae8640f9e65e274aea65c7916cb37b956978e32/packages/populace-build/src/populace/build/us_runtime/puf_support.py#L714) splits total E19200 by the source-year AGI band's mortgage share and assigns `donor["investment_interest_expense"] = non_mortgage`.
5. SPM enrichment at commit `295130c9f901e08db11457f16dbdee4e2349c5ba`, `tools/build_us_spm_role_enrichment.py:117-122,158-162,180-198`, checks the exact parent SHA and appends only `is_spm_independent_minor_role`, preserving prior columns. `packages/microcosm-data/src/microcosm/data/h5_enrichment.py` carries original row bytes into the expanded compound table and verifies preservation. This links the saved SPM pin to its parent's investment-interest concept.
6. Archived data code has the same deduction, rather than paid-expense, ancestry: at `policyengine-us-data` commit `42ed5d45c56df80d754fbe24cce21cfeb8d05cbe`, `policyengine_us_data/datasets/puf/puf.py:654` sets `interest_deduction = E19200`, and lines 1548-1550 initially treat that as deductible mortgage interest. `policyengine_us_data/calibration/puf_impute.py:96,139,161,189` separately imputes the total-interest and mortgage-deduction targets. `policyengine_us_data/utils/mortgage_interest.py:268-320` derives `investment_interest_expense` as `max(total_interest_deduction - tax_unit_deductible, 0)` and distributes it to people. These are modeled deduction targets, not observed Form 4952 current expenses.
7. [IRS TY2015 Publication 1304](https://www.irs.gov/pub/irs-soi/15inalcr.pdf), Figure C footnote 3 and Table 2.1 printed pp. 100–101, distinguish home-mortgage interest, points, mortgage-insurance premiums, and investment-interest deductions. [The official Table 2.1 workbook](https://www.irs.gov/pub/irs-soi/15in21id.xls) is the component-share source. The packaged all-return amounts are $304.461163B total interest, $283.004465B home-mortgage interest, $1.273716B points, $6.287486B mortgage-insurance premiums, and $13.895495B investment interest. Thus the modeled $21.456698B conserving non-mortgage residual is conceptually larger than investment-interest deductions even before imputation/uprating.

Exact local source reads used `git -C /Users/maxghenis/PolicyEngine/populace show <pin>:<file>` and the analogous read-only command for policyengine-us-data. No files in those repositories were edited. The initial assigned checkout used a different June 2026 default; recovery snapshot and saved microsim pin above are the applicable comparison inputs.

## Hub impact request: years, variables and breakdowns

Run foreground locked comparisons of current upstream/main against final PR HEAD for **2025 and 2026**, using the same pinned default URI, H5 content SHA, core version, entity ordering, and weights. The Codex sandbox cannot use the host heavy lock and must not run microsimulations. Use `/Users/maxghenis/reviews/pe-us-merge-backlog-2026-10-02/impact/lockrun.sh` with its `run.py` and `compare.py`. Keep enums `filing_status` and `state_code` out of numeric comparisons.

Tax-unit outputs:

```text
tax_unit_id tax_unit_weight
form_4952_disallowed_investment_interest_expense_prior_year
form_4952_total_investment_interest_expense
form_4952_gross_investment_income
form_4952_qualified_dividends
form_4952_capital_gain_distributions
form_4952_net_investment_gain
form_4952_net_capital_gain
form_4952_elected_investment_income
form_4952_investment_income
form_4952_investment_expenses
form_4952_net_investment_income
form_4952_investment_interest_carryforward
investment_interest_expense_deduction
investment_income_form_4952
interest_deduction
tax_unit_itemizes
total_itemized_taxable_income_deductions
itemized_taxable_income_deductions
standard_deduction
taxable_income_less_qbid
qualified_business_income_deduction
taxable_income
net_capital_gain
dividend_income_reduced_by_investment_income
adjusted_net_capital_gain
dwks09
section_911_qualified_dividend_income
section_911_net_capital_gain
regular_tax_before_credits
alternative_minimum_tax
income_tax_before_credits
income_tax
state_income_tax
```

Form 4952 line 1 is the filer-only sum of current `investment_interest_expense`; line 2 is the explicit prior-year input; line 3 is their sum. Derive line 4c as `gross_investment_income - qualified_dividends` and line 4f as `net_investment_gain - net_capital_gain`; remaining lines map directly to the variables above. Main lacks most new Form 4952 variables; its runner should mark them missing instead of aborting.

Person inputs and attributes to retain for correct aggregation and attribution:

```text
person_id person_tax_unit_id person_household_id
is_tax_unit_head is_tax_unit_spouse is_tax_unit_dependent
investment_interest_expense investment_expenses
investment_income_elected_form_4952
taxable_interest_income qualified_dividend_income non_qualified_dividend_income
short_term_capital_gains long_term_capital_gains non_sch_d_capital_gains
deductible_mortgage_interest deductible_interest_expense
```

Export `household_id` and `state_code` as a categorical sidecar, mapping state to tax units using the member links. Convert decoded state labels to numeric FIPS for breakouts; exclude the original enum arrays from compare.py. Aggregate Form 4952 eligible inputs with the branch's filer mask. Separately retain the all-member current raw investment interest removed from existing Schedule A aggregate, so dependent exclusion can be audited.

Break out all tax units, baseline itemizers, units remaining itemizers, switches to the standard deduction, positive expense inputs, positive election inputs, positive effective elections, and CA/NY/VA/MT individually (FIPS 6/36/51/30), with AR (FIPS 5) for the miscellaneous-fee pool, including electing units within each state. Report weighted changes and affected unit counts for the deduction, taxable income, QBID, regular tax, AMT, income tax and state income tax. Check line 7 + line 8 = line 3, deduction bounded by lines 3 and 6, and effective-election agreement between deduction and capital-gain/§911 consumers. Do not label the input total “paid investment interest.”

Run historical **2017** explicit-input scenarios for miscellaneous investment expenses and the 2%-of-AGI restriction; **2023** scenarios for Montana separate spouse limits and joint pooling, including `mt_itemized_deductions_indiv`, `mt_itemized_deductions_for_federal_itemization_indiv`, `mt_itemized_deductions_joint`, `mt_itemized_deductions_for_federal_itemization_joint`, and state income tax. Current default data is based in 2024; do not claim nationally representative 2017/2023 impacts by backcasting it without a validated historical dataset.

AMT's second Form 4952 and NIIT Form 8960 line 9a remain explicit modeling follow-ups. Gain-first election allocation remains the supported default; the taxpayer's alternative “Elec.” allocation is unsupported. Investment-property classification and missing annuity/royalty/K-1 details remain coverage limitations.
