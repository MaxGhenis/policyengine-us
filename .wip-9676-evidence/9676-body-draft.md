This change includes a biological or adoptive parent in Missouri's TANF assistance unit when someone else claims that parent as a tax dependent. In the target household—a marked non-parent grandparent, a dependent adult mother, and her child—the mother and child form the unit. The mother's income counts and can reduce or eliminate the children's grant.

The fix round retains the membership implementation, the explicit-input contract, and main's #9741 `get_override_branch` helpers. It replaces the vacuous adult-only-child YAML case with a two-tax-unit guard case, adds the income-loss case and its zero-income pair, and independently checks the complete non-parent-caretaker identification vector, including households where a caretaker must be found. It also corrects the interpretation and evidence claims below.

## Rule and retained interpretation

Parents of eligible children are mandatory members regardless of tax dependency. SSI recipients are excluded, and a biological or adoptive parent's presence excludes a non-parent caretaker. These rules follow [13 CSR 40-2.300 and 40-2.310](https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-2.pdf) and [Combined IM Policy Manual 4.2](https://my.mo.gov/cms_fsd?id=kb_article_view&sys_kb_id=98e1ef0c1b543650ba12657ae54bcbd1).

For a school-enrolled 18-year-old parent, the model retains interpretation (i): one combined three-generation unit, size three in the zero-income example. This is an interpretation rather than settled law. Both [archived 0210.005.30](https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-30/) and [current 4.3](https://my.mo.gov/cms_fsd?id=kb_article_view&sys_kb_id=a7d900b21b58aa10ba12657ae54bcbe3) define minor parent as under 18, including the birthday month. Alternative readings give size two; separate grouping and major-parent deeming remain outside this build.

The default `mo_tanf_is_parent_of_dependent_child` requires own children in the household and a dependent child in the person's tax unit who is 12–50 years younger. This age window imputes a relationship; it is not an eligibility rule. Genuine adoptive parents outside the window require an explicit `true`. The flag is annual and uses January's dependent-child status: changing `monthly_age` later in the year does not recalculate that year's flag.

An explicit flag overrides the default for the supplied year. Supplying it for one person makes unspecified people false for that year, so callers should supply it for every applicable parent. Other years can still use the formula. An explicit `true` does not add a person whose own tax unit has no dependent child, even when another tax unit supplies the SPM unit's eligible child.

## Tests and hand-computed expectations

- The two-tax-unit guard case expects membership `[true, true, false]`, size two, and `$234.08628` (`678 × 0.34526`). It closes a coverage gap: main and the old PR head pass, while dropping `has_dependent_child` must fail.
- A marked grandparent, dependent mother, and three children with the mother's annual disability benefits of `$14,400` produce size four and `$1,200` monthly countable income. That exceeds the `$990` need standard, so the grant is zero. Main excludes the mother and pays `$292.08996` to the children.
- Changing only those disability benefits to zero preserves size four and pays `$341.8074` (`990 × 0.34526`), `$49.71744/month` above main.
- The NPCR property independently asserts every person's identification flag and the existence/converse condition. Membership expectations still use the model's inclusion decision; they do not independently restate neediness or the grant comparison. Flag-on/flag-off property comparisons both run current code and do not execute pre-PR code.

Recovered local evidence: the updated member YAML file passed all 16 cases. Fresh verification against the final head, the two property suites, input definitions, unchanged partner contracts, and the `drop_has_dependent_child` / `npcr_never` mutation results: **[PENDING FRESH CI RESULTS AND ARTIFACT LINKS]**. Partner expectations remain unchanged.

Payment expectations retain the model's unrounded convention; payment rounding is a separate limitation.

## Parent-pointer evidence

The saved 2026-10-06 rescore uses the actual `none` school variant, rather than imputing school enrollment from `A_HSCOL`. A direct read of the pinned Populace HDF table's 318 person-column names confirms that `A_HSCOL` exists but `is_in_secondary_school` does not. The school input defaults to false in the model.

These figures measure agreement with resolved CPS parent pointers among the tax-dependent, non-child candidate population with a dependent child in its own tax unit. They are not a legal determination of parenthood. The Populace build is `populace-us-2024-spm-20260909`, SHA-256 `6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84`.

| Data and rule (`none`) | Selected records | Precision weighted / unweighted | Recall weighted / unweighted |
|---|---:|---:|---:|
| Census ASEC 2023–2025 pooled: own children only | 85 | 64.21% / 68.24% | 100% / 100% |
| Census ASEC 2023–2025 pooled: age guard | 71 | 74.82% / 78.87% | 95.63% / 96.55% |
| Populace 2024: own children only | 74 | 95.17% / 94.59% | 100% / 100% |
| Populace 2024: age guard | 71 | 99.999993% / 95.77% | 99.999984% / 97.14% |

In Populace, the guarded default retains three false positives and loses two pointer parents, all with very small weights. Missouri has only four selected records, three distinct source persons, and Kish effective sample size 2.92; pointer precision and recall are 100% in that thin sample. The pooled Census Missouri sample selects no candidates, so its precision and recall are undefined. The Census tax-unit artifact explanation is an inference from the observed structures.

The out-of-unit-parent statistic runs in this direction: 73% of parents in another tax unit from their child cohabit with the child's other parent. It does not establish that most cohabiting parents file separately. Parents whose own tax unit has no dependent child remain outside this implementation even when their child lives in the same SPM unit.

## Two new default regressions

The available child count and ages cannot establish the correct relationships in these zero-income households. The PR introduces overpayments in both; relationship inference remains a separate follow-up.

| Household | Main | PR | Legal unit |
|---|---|---|---|
| Unmarked grandparent 55; dependent mother 20; child 3 | Grandparent and child, size two, `$234.08628` | All three, size three, `$292.08996` | Mother and child, size two |
| Head 40 and child 10; dependent adult 45 whose own child is 20 | Head and child, size two, `$234.08628` | Adds adult 45, size three, `$292.08996` | Head and child, size two |

Each overpayment is `$58.00368/month`, or `$696.04416/year`. Callers can mark a non-parent grandparent and explicitly mark a dependent adult as not being the parent of an eligible child when they know those relationships.

## Resources and impact

The excluded-grandparent resource defect predates this PR. A marked grandparent's separately owned `$5,000` still counts against the otherwise asset-free mother/child unit, producing zero rather than `$234.08628`. The legal counterexample is preserved outside the passing suite with a prepared resource follow-up. That follow-up also addresses the opposite error: an included NPCR's spouse's resources must count under [current Manual 10.11](https://my.mo.gov/cms_fsd?id=kb_article_view&sys_kb_id=13aa0cb6873f32147dd8113d3fbb3538). Excluding every nonmember would be wrong because excluded financially responsible people can still contribute resources.

Fresh paired current-main versus final-branch runs use identical core and pinned default microdata, apply each intervention to both codes, and cover all twelve months and annual totals for 2026 and 2025: **[PENDING FRESH IMPACT RESULTS, CODE/CORE PROVENANCE, AND ARTIFACT LINKS]**.

For context, the saved **2026-09-29** study measured the following 2026 sensitivities. These are historical results, not measurements against today's main. Its unmodified comparison used current code with the parent flag off; its marked sensitivities separately executed pre-branch code.

| Historical scenario | Annual entitlement change | January change | Takeup-adjusted change |
|---|---:|---:|---:|
| Unmodified data | `$0` | `$0` | `$0` |
| Seven grandparents marked NPCR | `−$20,456,424` (−15.7%) | `−$1,704,702` | `$0` |
| Same marks, grandparents' bank assets zeroed | `−$15,230,525` (−9.5%) | `−$1,269,211` | `$0` |

Four members, about 22,418 weighted, were added in the unmodified study. All four affected units failed the income tests, and three also failed the resource limit. Grandparents' income alone does not explain all the failures: the mandatory mother's disability income eliminates one children's grant after marking, while another unit retains income from its own parent. In the asset sensitivity another mother/children unit gains `$49.71744/month`. Two records weighted about 5,836 and 8,759 dominate the totals; none of the moved records takes up TANF.
