This change includes a biological or adoptive parent in Missouri's TANF assistance unit when someone else claims that parent as a tax dependent. In the target household—a marked non-parent grandparent, a dependent adult mother, and her child—the mother and child form the unit. The mother's income counts and can reduce or eliminate the children's grant.

The fix round retains the membership implementation, the explicit-input contract, and main's #9741 `get_override_branch` helpers. It replaces the vacuous adult-only-child YAML case with a two-tax-unit guard case, adds the income-loss case and its zero-income pair, and independently checks the complete non-parent-caretaker identification vector, including households where a caretaker must be found. It also corrects the interpretation and evidence claims below.

axiom: [TheAxiomFoundation/rulespec-us#1444](https://github.com/TheAxiomFoundation/rulespec-us/issues/1444) queued (still open; this does not claim that the dependent-parent rule has been encoded).

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

Fresh evidence passed 214 Missouri TANF YAML cases across 26 files, 66 property cases, four explicit-source-role checks, four input-definition cases, and 623 partner cases across 144 files. Both YAML folders ran with one worker, and partner expectations remain unchanged. The new member file passes all 16 cases; removing `has_dependent_child` fails the intended guard case, while the original 14-case file passes that mutation. New properties detect both the guard removal and `npcr_never`; the original properties pass both mutations. Every intended failure is a saved call-phase `AssertionError`. The original PR head passes all 16 current member cases; frozen main has five passes and eleven expected call-phase assertions, including the income-loss and zero-income pair.

The original evidence workflow remains failed: its case-sensitive detecting-name wrapper misses the authored guard title, and its two cross-checkout comparisons initially encountered pytest `ImportPathMismatchError`. The successful [minimal continuation](https://github.com/MaxGhenis/policyengine-us/actions/runs/37574013106) reran only those two comparisons from an exact temporary fixture outside the package checkouts. Combined saved-evidence validation is `valid=true`, `errors=[]`, with completed controller provenance checked and 126 source files preserved; all other completed tests and simulations were reused byte-for-byte. The original failing receipts and wrapper exit remain preserved. See the [compact artifact](https://github.com/MaxGhenis/policyengine-us/actions/runs/37574013106/artifacts/11461908056) and [full evidence report](https://github.com/MaxGhenis/policyengine-us/blob/wip/9676-evidence-report/.wip-9676-evidence/final-report.md). Normal PR CI is a separate check.

The added Python coverage checks the complete NPCR identification vector and converse, while retaining the existing simulation-isolation grid. It belongs to the existing Rest/core CI group. On the sequential Linux runner, both property files took 55.25 seconds wall / 55.56 seconds CPU, peak RSS 1,242,112 kbytes. The old/new dependent-property commands, each including import/setup and three mutation sessions, took 86.08 / 85.80 seconds wall, with peaks 1,198,112 / 1,201,612 kbytes. Their unmutated pytest sessions were 24 cases in 14.55 seconds versus 26 in 14.57 seconds; per-session CPU/RSS were not separately measured. These are single-run measurements, not a measurement of the whole Rest group. Permanent CI routing and runner count are unchanged; all evidence runs are sequential.

Payment expectations retain the model's unrounded convention; payment rounding is a separate limitation.

## Parent-pointer evidence

The saved 2026-10-06 rescore uses the actual `none` school variant, rather than imputing school enrollment from `A_HSCOL`. A direct read of the pinned Populace HDF table's 318 person-column names confirms that `A_HSCOL` exists but `is_in_secondary_school` does not. The school input defaults to false in the model.

These figures measure agreement with resolved CPS parent pointers among the tax-dependent, non-child candidate population with a dependent child in its own tax unit. They are not a legal determination of parenthood. The Populace build is `populace-us-2024-spm-20260909`, snapshot `9a814a3b3b53c0ecd6e1737b6ec862c31300ef6f`, SHA-256 `6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84`.

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

The excluded-grandparent resource defect predates this PR. A marked grandparent's separately owned `$5,000` still counts against the otherwise asset-free mother/child unit, producing zero rather than `$234.08628`. The legal counterexample is preserved outside the passing suite with a prepared resource follow-up. Fresh household checks also confirm the opposite error on main, original head and candidate: an included NPCR's spouse's `$5,000` is dropped, leaving zero countable resources and a `$234.086273` grant. Those resources must count under [current Manual 10.11](https://my.mo.gov/cms_fsd?id=kb_article_view&sys_kb_id=13aa0cb6873f32147dd8113d3fbb3538). Excluding every nonmember would be wrong because excluded financially responsible people can still contribute resources.

The completed [source run](https://github.com/MaxGhenis/policyengine-us/actions/runs/37551528031) compares frozen main `5b1d5bdf47044607341d76f3c932ba2e7b74a060` with candidate `b9e7fff948caf4f33313c942c09caa7c7ccc3dea`, through evidence checkout `e39bb2c4c248ac4699032d7053f7429213014e75`. Candidate and evidence checkout have identical model, test and changelog contents. All twelve simulations completed on Python 3.14.7 and Core 3.32.15, using the exact default dataset digest above. The full population was 166,321 people / 59,900 SPM units; saved Missouri diagnostics contain 2,892 people / 1,051 units. Each intervention applied to both codes, with identities, weights and intervention vectors checked before comparison.

| Fresh year/scenario | Annual entitlement change | Percent | January change | Actual annual MO TANF change |
|---|---:|---:|---:|---:|
| 2026 unmodified | `$0` | 0% | `$0` | `$0` |
| 2026 seven grandparents marked | `−$20,456,426.63` | −15.706373% | `−$1,704,702.22` | `$0` |
| 2026 marked, bank assets zeroed | `−$15,230,533.09` | −9.463245% | `−$1,269,211.09` | `$0` |
| 2025 unmodified | `$0` | 0% | `$0` | `$0` |
| 2025 seven grandparents marked | `−$20,311,380.00` | −15.559409% | `−$1,692,615.00` | `$0` |
| 2025 marked, bank assets zeroed | `−$15,122,540.56` | −9.391461% | `−$1,260,211.71` | `$0` |

Every month's payment, membership and failure partition equals January's within each scenario/year; the twelve monthly entitlement sums reconcile to annual totals. Actual annual Missouri TANF remains `$5,497,666.85` in 2026 and `$5,458,685.75` in 2025 on both codes; national actual TANF changes are also zero. The separately saved entitlement × takeup diagnostic is unchanged and is not substituted for actual TANF.

Four members are added in four units every month, with none removed: 22,417.537 weighted in 2026 and 22,258.586 in 2025. Under unmodified data, all four units fail income tests and three also fail resources. After marking, SPM 17211's mandatory mother's disability income (`$1,290.69/month` in 2026, `$1,247.64` in 2025) eliminates the children's `$292.089966/month` grant; there is one new income failure and no new resource failure in each month. SPM 76134 still fails on its own parent's income after bank assets are zeroed. Zeroing bank assets lets SPM 1017211 gain `$49.717438/month`; SPM 1134143, with tiny weight, gains `$98.399094`. None of the four affected records takes up TANF. SPM 17211 and 1017211 account for 99.999232% of absolute annual change in the bank sensitivity. Complete drivers, failure partitions and receipts are in the evidence report.

For context, the saved **2026-09-29** study measured the following 2026 sensitivities under core 3.32.8 and branch `0771d2c498`. These are historical results, not measurements against today's main. Its unmodified comparison used then-branch code with the parent flag off; its marked sensitivities separately executed pre-branch code `10e3f989ba`.

| Historical scenario | Annual entitlement change | January change | Takeup-adjusted change |
|---|---:|---:|---:|
| Unmodified data | `$0` | `$0` | `$0` |
| Seven grandparents marked NPCR | `−$20,456,424` (−15.7%) | `−$1,704,702` | `$0` |
| Same marks, grandparents' bank assets zeroed | `−$15,230,525` (−9.5%) | `−$1,269,211` | `$0` |

Four members, about 22,418 weighted, were added in the unmodified study. All four affected units failed the income tests, and three also failed the resource limit. Grandparents' income alone does not explain all the failures: the mandatory mother's disability income eliminates one children's grant after marking, while another unit retains income from its own parent. In the asset sensitivity another mother/children unit gains `$49.71744/month`. Two records weighted about 5,836 and 8,759 dominate the totals; none of the moved records takes up TANF.
