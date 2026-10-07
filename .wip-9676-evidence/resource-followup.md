# Follow-up from #9676: whose resources Missouri TANF counts

Prepared 2026-10-06 in the hub fix round for PolicyEngine/policyengine-us#9676. Not filed: hub follow-ups need Max's go or a chip. This defect predates #9676. #9676 makes it more visible, because its target household (a grandparent marked as a non-parent caretaker with a dependent adult parent) is exactly where it bites.

## The rule

Combined IM Policy Manual 10.11, "Whose Resources Are Counted for TA" (https://my.mo.gov/cms_fsd?id=kb_article_view&sys_kb_id=13aa0cb6873f32147dd8113d3fbb3538; saved text in `~/reviews/mo-tanf-dependent-parent-2026-09-29/law-minor-parent/sources/fsd/10.11_Whose_Resources_Are_Counted.txt`):

> "FSD includes resources owned by the parents and eligible children in the TA household. ... If a needy non-parent caretaker relative (NPCR) or legal guardian is included in the TA household, FSD counts all the resources owned by the NPCR or legal guardian and their spouse."

> "The resources of all household members, and financially responsible people, including disqualified household members are countable."

13 CSR 40-2.310(3) (https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310): "This policy applies to a child and to a parent(s), or to step-parents, or if included in the grant, a needy nonparent caretaker relative or legal guardian with whom the child is living."

## What the code does

`policyengine_us/variables/gov/states/mo/dss/tanf/eligibility/mo_tanf_countable_resources.py` starts from `spm_unit_cash_assets` and subtracts the assets of SSI recipients and of `mo_tanf_non_parent_caretaker_budget_member & ~member`. Two errors follow:

1. **An excluded non-parent caretaker's own assets count.** Budget membership needs `mo_tanf_non_parent_caretaker`, which is false whenever a parent is in the home. So a marked grandparent living with the children's parent (the #9676 target household) is not subtracted, and their bank account counts against the parent and child.
2. **An included NPCR's spouse's assets are dropped.** The spouse is a budget member but not a unit member, so `npcr_family & ~member` subtracts the spouse's assets. The comment at lines 34-35 ("The caretaker's spouse is not a listed member, so their resources are excluded in every case") contradicts the current manual quoted above.

Do not fix this by excluding every nonmember. Excluded financially responsible people (a parent excluded for immigration status, an SSN failure or a sanction, for example) still contribute resources under 10.11.

## Fixtures (both fail on current main and on #9676's head)

A. From the #9676 hub spec, with hand-computed expectations. The grandparent is excluded, so the mother and child hold $0 and get 678 x 0.34526 = $234.08628. Current code: resources $5,000, `mo_tanf` 0.

```yaml
- name: Excluded grandparent's separately owned assets do not count
  period: 2026-01
  input:
    people:
      grandparent:
        age: 55
        mo_tanf_is_non_parent_caretaker: true
        bank_account_assets: 5_000
      mother:
        age: 20
        is_tax_unit_dependent: true
        own_children_in_household: 1
      child:
        age: 3
        is_tax_unit_dependent: true
    tax_units:
      tax_unit:
        members: [grandparent, mother, child]
    spm_units:
      spm_unit:
        members: [grandparent, mother, child]
    households:
      household:
        members: [grandparent, mother, child]
        state_code: MO
  output:
    mo_tanf_is_assistance_unit_member: [false, true, true]
    mo_tanf_countable_resources: 0
    mo_tanf: 234.08628
```

B. Included NPCR's spouse (sketch; the builder must compute and confirm the inclusion branch). Grandfather 62 (head) and grandmother 60 (spouse), both marked `mo_tanf_is_non_parent_caretaker`, no income; the grandmother has `bank_account_assets: 5_000`; grandchild 8, their tax dependent. The grandfather is the NPCR, and the grandmother enters the neediness budget as his spouse.
- Under 10.11, including the NPCR counts the spouse's $5,000, which exceeds the $1,000 limit, so the included budget is ineligible. Excluding the NPCR (an optional member) leaves the child alone with $0 of resources: size 1, 393 x 0.34526 = $135.68718.
- Current code drops the spouse's assets, includes the NPCR, and pays size 2, $234.08628.
- Expected after the fix: `mo_tanf_non_parent_caretaker_included: false`, size 1, `mo_tanf` 135.68718. This assumes `mo_tanf_non_parent_caretaker_included` compares the two budgets, as its #9741 helpers do. Confirm that before writing the expectation.

## Microsim sensitivity that motivates it

The 2026-09-29 study (`~/reviews/mo-tanf-dependent-parent-2026-09-29/microsim-impact/REPORT.md`, "Sensitivity") found SPM unit 1017211 (weight 8,759) ineligible only because of the marked grandmother's $18,132.42 of bank assets. Fresh current-main comparisons are recorded in the resumed evidence report when completed; this historical observation is not a fresh measurement.

## Open scope question for the builder

10.11 also implies that a non-member who is neither a household member nor financially responsible (an adult sibling, an unrelated adult in the SPM unit) contributes nothing, while the model counts the whole `spm_unit_cash_assets`. That is wider than the two errors above. Check it, and either fix it with fixtures or record it as a known limit.
