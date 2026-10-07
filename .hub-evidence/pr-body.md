## What and why

Apply the §163(d) investment-interest deduction limit through Form 4952. Schedule A replaces current raw investment interest with allowed line 8, preserving the existing aggregate interest and mortgage conventions. Explicit prior-year disallowed interest is available on line 2 and the unused amount is exposed on line 7; carryover is not automatically propagated between simulations.

All Form 4952 income, gains, elections, current debt and expenses belong to the filer and spouse. The deduction and Schedule D/§911 calculations share the effective capped election and investment gains, retaining independent Schedule D gain arithmetic and default gain-first allocation. Montana spouses compute separate limits before 2024. California, New York and Virginia substitutions use allowed federal interest; California's high-AGI exclusion retains the federal-form approach. Federal miscellaneous investment fees remain disallowed after 2017, including 2026.

Sources: [26 USC 163(d)](https://www.law.cornell.edu/uscode/text/26/163#d), [IRS Form 4952](https://www.irs.gov/pub/irs-prior/f4952--2025.pdf), [26 USC 67(h)](https://www.law.cornell.edu/uscode/text/26/67#h), and [2023 Montana instructions, printed page 31](https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=38).

## Test plan

- [x] Externally derived YAML cases for the deduction cap, carryover, dependent exclusion and Montana separate limits; independent vectorized restatement, bounds, monotonicity and conservation properties.
- [x] `make format` and changelog fragment.
- [x] 90 targeted passes: federal Form 4952 (25), properties (15), Montana (6), California (2), New York (8), Arkansas (8), Virginia (5), election (13), and §911 (8). Each file ran separately, serially in the foreground, with core 3.32.20.
- [ ] CI suites, including partner contracts: queued at the latest check. Partner expectations are unchanged.

Seven source-overlay regressions fail with prior formulas and pass with final formulas (not a full old-checkout replay). The federal example changes tax from $20,447 to $21,647; Montana separate deductions change from [150,450] to [300,0]. The new AR fixture initially failed entity parsing; correcting its input placement preserved the expected deduction. Local property setup-inclusive time was 158.62s and peak memory ~1.02GiB; Linux CI resource evidence is pending. The federal assertions passed even though its external timing wrapper hit a sandbox restriction afterward.

The saved build's 21 federal YAML cases, six property cases and 60 serial targets passed on an older baseline; these are historical evidence, not validation of this head.

## Impact and data limitation

Fresh 2025/2026 microsimulations are pending the hub: this Codex sandbox cannot write the host heavy lock, and the job explicitly prohibits local microsimulations. Required exports include every Form 4952 line, interest/itemized deductions, itemization choice, taxable income, QBID, regular tax, AMT, income tax and state income tax; break out CA/NY/VA/MT and electing units, plus AR for investment fees. Historical explicit-input scenarios cover 2017 miscellaneous fees and 2023 Montana.

The default `populace-us-2024-spm-20260909` input is **an imputed Schedule A deduction residual, not observed raw investment interest paid**. Its [parent build](https://github.com/PolicyEngine/populace/blob/cae8640f9e65e274aea65c7916cb37b956978e32/packages/populace-build/src/populace/build/us_runtime/puf_interest_components.py#L164) assigns deductible points, mortgage-insurance premiums and investment-interest deductions to this residual. The old $53.68B input screen and illustrative +$5.4–9.4B estimate are therefore not a validated §163(d) revenue score. A pinned comparison can show mechanical model changes; economic interpretation needs corrected data concepts or a sensitivity design from the data owners.

Coverage limits: no alternative “Elec.” allocation; no investment/noninvestment capital-asset split; missing distinct annuity/royalty/K-1 income; no Montana-specific income adjustments or per-spouse carryover inputs. Federal AMT's second Form 4952 and NIIT Form 8960 line 9a remain explicit follow-ups. California’s own FTB 3526 income/election/carryover calculation remains assigned to the separate California work. This PR precedes that work because both touch its pre-limitation formula and exclusion parameter.

axiom: needed

Recovery and detailed evidence: [fix report](https://github.com/MaxGhenis/policyengine-us/blob/wip/hub-resume-163d-evidence/.hub-evidence/163d-report.md), [dataset lineage and exact hub impact request](https://github.com/MaxGhenis/policyengine-us/blob/wip/hub-resume-163d-evidence/.hub-evidence/dataset-audit.md). Code head: `05228167642374813d0afbdf4c0aa2cf559de7aa`; main merged at `dd9cb3f6839`.
