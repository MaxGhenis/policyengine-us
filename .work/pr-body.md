Fixes [policyengine-us#9404](https://github.com/PolicyEngine/policyengine-us/issues/9404).

Use optional `parent_1_id` and `parent_2_id` inputs to identify co-resident parents and siblings when constructing Medicaid MAGI households. Resolve a dependent's effective claiming tax unit first, then add the dependent's own co-resident spouse once. Linked filers also count their co-resident spouses reciprocally, including separately filing spouses without a cohabiting flag. A spouse added to a dependent's household does not thereby enter the claimant's household.

The Ohio 2026 regression is a stylized reconstruction of Microcosm Build P household 1009324, not the production record: the 56-year-old's income is set to the $94,504 residual that reproduces the previous $141,848 pooled income, and child ages are placeholders. With parent IDs, four children of the 30-year-old have size 5 and income $23,334, and the 27-year-old's child has size 2 and income $24,010. Those five children qualify for Medicaid; the 17- and 16-year-olds retain size 3 and income $94,504 and remain ineligible. Without parent IDs, the regression retains size 10 and income $141,848 for all seven children. These are fixture results, not a national impact estimate.

### Input contract and compatibility

The compatibility guarantee is exact existing behavior when **all parent IDs are zero throughout the simulation**. It does not guarantee that an isolated zero-ID household stays unchanged inside every mixed simulation. Zero means unknown. Nonzero `person_id` and parent IDs are signed int32 values; person IDs must be unique across the simulation whenever tax units span households or known claiming-unit IDs are supplied. Household-local reuse is supported only for self-contained household and tax-unit graphs. Duplicate-ID fixtures pin deterministic fallback behavior; duplicate IDs cannot establish legal identity.

An ID naming a co-resident resolves to that person. A named parent must be the claiming tax unit's head or spouse, rather than another dependent, for parental claimant recognition. The linked both-parent exception requires the same actually filing parental unit for the joint-return exclusion and correct membership in the identified claiming unit. Raw IDs, including absent-parent links, remain intact.

When exactly one distinct named parent is resident, Medicaid may also recognize that parent's established resident spouse as a stepparent. Evidence is bounded to joint head/spouse roles or a two-person marital unit with a spouse flag. The same effective relationship feeds claimant recognition, the both-parent exception, and non-filer parent/child membership. Two ID slots and this bounded inference do not represent every larger parent or step-relative graph. `cohabitating_spouses` describes the tax-unit head's separately filing spouse; attaching the flag to an unrelated claimant's unit can overcount.

The companion data export is [microcosm#884](https://github.com/PolicyEngine/microcosm/issues/884); its production ID/link coverage still needs verification. The paper disclosure is [obbba-paper#2](https://github.com/PolicyEngine/obbba-paper/pull/2).

### Changes in this fix round

Recovered the six approved commits through `34c6562e2`, retained the later fixes already published at `62aee62351`, and merged current main `dd9cb3f683` through merge commit `b6ad6626ba`. The clean merge tree was `8351b88`; the new main changes were release-only and did not overlap model files. No history was rewritten.

- Added reciprocal spouse membership, including the Ohio missing-flag case and California pregnant-spouse counterpart, with deduplication across same-unit membership, external claims, and the existing flag.
- Added shared, bounded resident-stepparent resolution and regression cases for claimant recognition, separately filing parents, non-filer membership, and unsupported inference shapes.
- Tightened ID documentation, made the co-resident duplicate-ID override independent of member order, and added second-slot collision cases.
- Added grandparent/teen-parent/baby, claiming-head-or-spouse, and same-filing-parental-unit tests.
- Fixed linked flagged-spouse income propagation to adult dependents and cancelled flagged spouse contributions already included through tax-unit membership or known external claims, consistently across size, income and California pregnancies. Three flagged-spouse regressions failed before these fixes.
- Corrected the changelog to state co-resident resolution, the linked both-parent exception, and the simulation-wide all-zero guarantee.
- Reject named parent-child relationships as spouse evidence during bounded stepparent inference. The new grandparent/teen18/baby case reproduced a baby household size of 3 where the legal composition requires baby+teen, size 2; the final composition file passes with baby size 2 and income $0.
- Commit `a4ca85f6fb` gives cross-household married-dependent property scenarios globally unique person IDs and matching parent links; all 11 property tests passed with expected outputs unchanged.

### Validation

Recovered head `62aee62351` passed **34/34 CI checks**, including the partner contracts, in [run 37563630113](https://github.com/PolicyEngine/policyengine-us/actions/runs/37563630113). Current main `dd9cb3f683` also passed [Household API Partners](https://github.com/PolicyEngine/policyengine-us/actions/runs/37581086735/job/112670656867). These are recorded CI results, not local suite runs. No partner expected outputs were edited. Saved targeted local logs at the recovered head show **6 core tests and 11 property tests passed**.

Earlier CI at `38880d4aa0` passed the three parent-ID YAML files (**11 + 43 + 5 cases**) but failed the spouse property for a minor whose inferred tax unit had no head: `s13_spouse` produced $0 versus the generator's expected $13,979. The explicit head inputs in `7d4ad6901a` fixed that setup error; the recovered property file subsequently passed all 11 tests.

- Approved `34c6562e2` reproduced **5 failures/6 passes** across the 11 r8 fix-round cases in an independent archived source tree. The four new recovery-audit cases also failed before the final edits (one ancestor-inference case and three flagged-spouse cases); logs are retained.
- At `409e65e8b2`, all **63 YAML cases (47 composition + 11 Medicaid parent-ID + 5 demographic)** and **17 Python tests (11 properties + 6 core)** passed. Composition includes all 11 r8 fix-round cases and the four new recovery regressions. These were sequential single-file runs; no suites or microsimulations were run locally.
- Independent clean-main `dd9cb3f683` versus `409e65e8b2`: **48 synthetic API cases (24 worlds), 13 variables, 624 arrays identical by dtype/shape/bytes, zero errors and zero differences**. Omitted and explicit-zero inputs also matched within each source. Both model processes ran sequentially with the same Core environment and verified source paths; this is bounded compatibility coverage, not production-data parity.
- `make format` passed after the final membership edits: 6,656 files unchanged and Ruff lint passed.
- Observed 2026-10-07T11:12:11.906106+00:00: **7 successful, 4 running and 24 queued checks**, no failures; [run 37609932407](https://github.com/PolicyEngine/policyengine-us/actions/runs/37609932407). Final-head partner contracts are queued; broad suites remain incomplete.

Historical r8 checks against pristine `ca1805cf0` found zero differences across 22,581 arrays (plus an explicit-zero repeat and 1,440 random-world arrays), with 50 matching errors. The current-main comparison above independently verifies this round and replaces reliance on the old class-restoring AST guard.

Before/after fixtures, logs, differential results and replay commands are retained with the [fix-round report and evidence](https://github.com/MaxGhenis/policyengine-us/tree/wip/hub-resume-sol2-9406/.work).

### Impact and integration

No microsimulation was run in this sandbox. The hub must compare current main and the final branch with the same core, production dataset, weights, take-up, and seed for **2024 and 2026**, optionally 2025. Required outputs: `is_parent`, `medicaid_claimed_by_parent_in_tax_unit`, `medicaid_tax_dependent_exception_other_than_spouse_or_child`, `medicaid_tax_dependent_exception_living_with_both_parents`, `medicaid_tax_dependent_exception_non_custodial_parent`, `medicaid_uses_non_filer_rules`, `medicaid_household_size`, `medicaid_household_income`, `medicaid_income_level` (the household FPL ratio), `ca_medicaid_household_pregnancies`, `is_medicaid_eligible`, `medicaid`, `is_chip_eligible`, `chip`, `is_aca_ptc_eligible`, `aca_ptc`, and `premium_tax_credit`.

Read-only metadata and a narrow `person_id` field inspection of the cached default `populace-us-2024-spm-20260909` build (snapshot `9a814a3b3b53c0ecd6e1737b6ec862c31300ef6f`) found 166,321 globally unique nonzero person IDs, all within int32 range. Both `parent_1_id` and `parent_2_id` columns are absent. Raw CPS `PEPAR1`/`PEPAR2` fields exist, but no transformation into model links was run or verified. This is schema evidence, not a simulation or a weighted impact estimate. A populated-link export or verified transformation is needed to measure feature impact.

Stratify linked and zero-ID populations, children, teen parents, married dependents, multigenerational households, and state. Repeat with all parent IDs zero and require exact zero changes. National net effects and weighted counts remain unknown. No new performance benchmark was run; the historical r8 partial-model benchmark had 199,713 synthetic people and seven variables, taking 0.163 seconds with zero IDs and 1.49 seconds with links.

The separate `medicaid-magi-joint-floor` work overlaps `medicaid_household_income.py`, `medicaid_household_income_member.py`, `medicaid_magi_person.py`, and `medicaid_person_is_required_to_file.py`. Its branch was not imported. Integration must retain this PR's claimant/spouse membership and aggregate signed member income before applying the final household zero floor.

### Methodology choices for Max

- Stepparents are parents under [42 CFR 435.603](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-C/part-435/subpart-G/section-435.603). Two-slot completeness and the bounded spouse-inference scope are data-model choices, not alternative legal definitions.
- The existing exclusion of a non-required-filer dependent spouse's income remains preserved. Whether the taxpayer-household exclusion under (d)(2)(ii) carries into the dependent's own spouse-augmented household remains for Max to decide.
- California's full-time-student-under-21 treatment is established policy in [ACWDL 20-10](https://www.dhcs.ca.gov/wp-content/uploads/2025/10/c20-10.pdf), not an optional policy choice for this build.
- Cross-household ID collisions do not contain enough information to recover the intended identity through legal interpretation.

Final head: `409e65e8b2`.

axiom: needed — rulespec-us parity review is pending; no public issue was filed.
