# #9406 fix-round report

PR: https://github.com/PolicyEngine/policyengine-us/pull/9406. Model head: **`409e65e8b29feb87b8fc7cf245b35be28bb6b152`**. Recovered `62aee62351`, preserving approved `34c6562e2` and all prior fixes. Current main `dd9cb3f683` merged cleanly; merge-tree `8351b88` matched the merge. Its new changes were release-only, with no model overlap.

New commits, each pushed: `b6ad6626ba` (merge main), `a4ca85f6fb` (globally unique generator IDs), `409e65e8b2` (membership/income fixes and four regressions). No rebase, force push, PR merge, partner expected-output edit, or public issue occurred.

The requested `~/reviews/us-hub/fixes/9406-report.md` is outside this sandbox. Report and evidence remain in the assigned workspace and are backed up separately to **`MaxGhenis/policyengine-us:wip/hub-resume-sol2-9406`**. The PR model head stays unchanged by that evidence commit. Original Git metadata is outside the writable sandbox, so commits used private workspace `.git-local`; see `validation-manifest.md`. Caller and prior job checkouts were read only. No registered extra worktree was created.

## Findings

| Finding | Fix and regression coverage |
| --- | --- |
| Published spouse-income bug | Retained effective-claimant lookup before adding the applicant's spouse; dependent T gets P+T+S, size 3/$30,000, while P retains P+T. |
| r8 #1 ID contract | Require globally unique nonzero int32 IDs for cross-household tax units or known claimant IDs. Local reuse is limited to self-contained graphs. Co-resident resolution is explicit; collisions test fallback, not legal identity. |
| r8 #2 resident stepparent | Shared effective-parent resolution recognizes the established resident spouse of exactly one distinct named resident parent, consistently for claimant, both-parent exception and non-filer membership. Child with mother $20,000/stepfather $40,000 now uses the both-parent exception and size 3/$60,000. Raw absent-parent links remain intact. |
| r8 #3 reciprocal spouse | Own-unit linked filers count resident spouses without a flag; deduplicate unit membership, external claims and flags. OH sizes [2,3,2], incomes [0,30000,30000]; CA pregnancy counterpart sizes [2,4,3], pregnancies [0,1,1]. |
| r8 #4 differential guard | Independent clean-main processes replace reliance on the incomplete class-restoring AST guard. Fresh comparison: 624 exact arrays, zero differences/errors. |
| r8 #5 duplicate IDs | Tightened contract plus order-independent co-resident fallback. Invalid-duplicate permutation and valid-ID permutation properties retained. |
| r8 #6 tests | Grandparent/teen-parent/baby, claiming head-or-spouse, same actually filing parental unit, identified claimant membership and second-slot collisions; extended reciprocal-spouse properties. |
| r8 #7 changelog | Explicit co-resident resolution, linked both-parent exception, and simulation-wide all-zero-parent-ID compatibility. |

Additional recovery-audit fixes in `409e65e8b2`:

- Raw named parent-child links veto spouse inference: G60/T18/baby no longer misidentifies G as baby's stepparent. Baby size was 3; now 2 with income $0.
- A head's flagged separate-spouse income propagates to linked tax-household dependents. OH/CA dependent income was $20,000; now $60,000.
- Flagged spouse contributions already present through unit membership or known external claims are cancelled consistently for size, income and CA pregnancies. The external-claim case's pregnancies were [2,2]; now [1,1].

`a4ca85f6fb` gives cross-household property scenarios globally unique IDs and matching links, with expected outputs unchanged. Earlier `7d4ad6901a` explicitly makes separately filing minor spouses tax heads; the prior property failure was a scenario-role error ($0 versus $13,979).

## Tests

| Check | Result / evidence |
| --- | --- |
| Final composition YAML | **47 passed**, including all 11 r8 fix-round cases and four new recovery cases; `logs/composition-after-409e65e8b2.log` |
| Final Python files | **11 properties + 6 core passed**; `logs/properties-after-409e65e8b2.log`, `logs/core-after-409e65e8b2.log` |
| Other final parent-ID YAML files | **11 Medicaid + 5 demographic passed**; `logs/medicaid-parent-ids-after-409e65e8b2.log`, `logs/demographic-parent-ids-after-409e65e8b2.log`. Total final local: **17 Python + 63 YAML**. |
| Approved-head before run | At `34c6562e2`, 5 failed/6 passed across 11 r8 cases; `logs/r8-approved-before.log` |
| New regressions before run | At `a4ca85f6fb`, ancestor case 1 failed and flagged-spouse cases 3 failed; `logs/ancestor-before.log`, `logs/flagged-spouse-before.log`. All pass in final composition. |
| Current-main zero-ID differential | **48 synthetic API cases/24 worlds, 13 variables, 624 identical dtype/shape/byte arrays, zero build/calculation errors and differences**. Omitted/explicit-zero variants agree within each source; `logs/zero-id-differential-409e65e8b2.log`, `zero-id-results/*.pkl`. |
| Format/lint | `make format` and Ruff passed; `logs/format-final.log`, `validation-manifest.md` |
| Recovered CI | **34/34 passed** at `62aee62351`, including contracts; [run 37563630113](https://github.com/PolicyEngine/policyengine-us/actions/runs/37563630113) |
| Current-main contracts | Passed at `dd9cb3f683`; [Household API Partners](https://github.com/PolicyEngine/policyengine-us/actions/runs/37581086735/job/112670656867) |
| Final-head CI | Observed 2026-10-07T11:12:11.906106+00:00: **7 successful, 4 running and 24 queued checks**, no failures; [run 37609932407](https://github.com/PolicyEngine/policyengine-us/actions/runs/37609932407). Final-head partner contracts are queued; broad suites remain incomplete. Snapshot: `ci-409e65e8b2.json`. |

These are single-file foreground runs, not local suites. No partner outputs were edited; any final-head contract failure must be preserved, investigated and gated by Max's three questions before edits. Current-main/recovered CI are not final-head passes. The differential verifies package/system/all 13 variable source paths with identical Core. Setup-inclusive times were 161.588s main/166.735s head; peak memory unavailable. This bounded synthetic check is not production-data parity.

Historical r8 checks at `34c6562e2` versus `ca1805cf0`: 14 Python/48 YAML passed; 22,581 arrays with zero differences (explicit-zero repeat too), 50 matching errors; 120 random worlds/3,313 people/1,440 arrays with zero differences. Historical log references and commands are retained in the validation manifest. Empty saved a1/a2/a3r YAML logs are not evidence of completion.

## Hub impact work

No microsimulation or new benchmark was run: this sandbox cannot acquire the host heavy lock. Compare current main and final branch for **2024 and 2026**, optionally 2025, using identical Core, production dataset, weights, take-up and seed. Exact outputs:

```text
is_parent
medicaid_claimed_by_parent_in_tax_unit
medicaid_tax_dependent_exception_other_than_spouse_or_child
medicaid_tax_dependent_exception_living_with_both_parents
medicaid_tax_dependent_exception_non_custodial_parent
medicaid_uses_non_filer_rules
medicaid_household_size
medicaid_household_income
medicaid_income_level
ca_medicaid_household_pregnancies
is_medicaid_eligible
medicaid
is_chip_eligible
chip
is_aca_ptc_eligible
aca_ptc
premium_tax_credit
```

Cached default `populace-us-2024-spm-20260909`, snapshot `9a814a3b3b53c0ecd6e1737b6ec862c31300ef6f`: 166,321 globally unique nonzero person IDs, all fitting int32, but **both parent-ID columns absent**. Raw CPS PEPAR1/PEPAR2 exist; no model-link transformation was run or verified. Inspection read only schema and the narrow person-ID column, not economic data. See `dataset-metadata.txt`. A populated-link export/verified transformation is needed for feature impact; the Microcosm export description remains unverified.

Stratify linked/zero-ID people, children, teen parents, married dependents, multigenerational households and state. All-zero-parent-ID copies must show exact zero changes. Exclude enums from numeric comparison. Fixture directions: five Ohio child eligibility gains with income $141,848→$23,334/$24,010 (83–84% reduction); two older children remain ineligible at $94,504. Baby income $40,000→$0; dependent spouse repair $0→$30,000 and size 2→3 may reduce eligibility. National weighted net effects remain unknown.

Hub must repeat production-size performance. Historical r8 was only a precomputed-dependency synthetic benchmark: 199,713 people/seven variables, 0.163s zero IDs versus 1.49s linked.

## Integration and open policy work

The separate joint-floor branch was not imported. Overlap: `medicaid_household_income.py`, `medicaid_household_income_member.py`, `medicaid_magi_person.py`, `medicaid_person_is_required_to_file.py`. Preserve #9406 claimant/spouse membership, then sum signed member income before the final household zero floor; do not restore per-person floors or its older AGI stack.

Methodology choices are in the PR body: stepparents are legally parents; two-slot completeness/bounded inference are data choices. Existing non-required-filer dependent-spouse income exclusion is preserved pending Max's interpretation of (d)(2)(ii) in the dependent's spouse-augmented household. CA's under-21 student rule is established policy. Collisions cannot legally identify a person. `cohabitating_spouses` describes that unit head's separately filing spouse; residual child-count proxies do not represent every relationship.

Separate follow-ups, report only, with no public issues:

- **CA full-time students under 21:** non-filing P40/$20,000 and C20 student should both have size 2/$20,000; inherited sizes [1,1], incomes [$20,000,$0]. Files: `medicaid_non_filer_child_age_eligible.py`, `uses_full_time_student_under_21_rule.yaml`.
- **External adult claimant:** own-unit C18 claimed by grandparent $40,000, resident with parent $10,000 and sibling, should use non-filer 3/$10,000; inherited 2/$40,000. Current-unit dependency gate in `medicaid_tax_dependent_exception_other_than_spouse_or_child.py`.
- **Young non-filer own income:** unclaimed T18 alone earning $10,000 should have 1/$10,000; inherited 1/$0. Missing parental-household condition in `medicaid_household_income_member.py`.
- **Custody:** preserve trusted noncustodial input; an order/agreement, otherwise majority nights, controls. Do not infer custody from residence or IDs alone.

Axiom rulespec-us parity awaits maintainer follow-up (`axiom: needed`); no public issue was filed.
