# PolicyEngine US #9601 fix-round report

Code head: **a72bca942f106a6cfbb0bda8b13f817318f446c5**; merged main: **dd9cb3f6839d290c8490c561b54b7afeedc3c888**. Recovered fixes `279f541dd1` were preserved; timing-check commit `8fb31d7218` and merge `a72bca942f` were pushed upstream to `ca-prop3-2030-expiry`. Final CI/draft status: **Ready for review; DTrim99's CHANGES_REQUESTED review retained. CI snapshot 2026-10-07T11:04:21+00:00: 19 passing, 14 running, 2 queued; no failures. Partner CI passes.** `make format` passes; independent static review approves with prose corrections applied.

## Findings, fixes and tests

The PR body explicitly answers [DTrim99's review](https://github.com/PolicyEngine/policyengine-us/pull/9601#issuecomment-5822089855): both critical findings, six should-address findings and seven suggestions. His CHANGES_REQUESTED review remains for re-review.

| Finding | Fix and evidence |
|---|---|
| HOH/shared citations | HOH §36(f)(3), shared §36(f)(2)–(3); independent citation audit. |
| Literal rates/indexes | Identify enacted sunset brackets, snapshot rates, copy adjusted 2030 values; .104 regression fails old head, passes recovered fix. |
| Future activation | Inspect dated toggle values; `test_ca_prop3_app_activation_from_2031` fails old head, passes recovered fix. |
| Bounded/delayed activation | Restore true intervals within 2031–2100; three `test_ca_prop3_respects_delayed_and_bounded_activation` cases fail old head, pass recovered fix. |
| Operative sources | Add [Prop 3 §4 p6](https://vig.cdn.sos.ca.gov/2026/general/pdf/prop3-text-proposed-laws.pdf#page=6), [p7](https://vig.cdn.sos.ca.gov/2026/general/pdf/prop3-text-proposed-laws.pdf#page=7), [LAO Figure 1 p2](https://vig.cdn.sos.ca.gov/2026/general/pdf/prop3.pdf#page=2); audited. |
| Joint/QSS chain | Add [RTC §17045](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17045.&lawCode=RTC); joint/QSS rate/scaling properties. |
| Missing statuses/boundary | Add 2031 HOH/MFS/QSS off/on and HOH 2030 YAML cases; independently checked arithmetic. |
| AMT | Assert regular tax, max(.07 × reduced AMTI − regular tax, 0), total tax; $1.4M AMTI exposes $9,057.10 baseline AMT, zero under extension. |
| Feature changelog | Retain sunset `.fixed.md`; add reform/toggle `.added.md`; inspected. |
| CPI-independent coverage | All-status rates at 2030/2031/2035, unchanged thresholds/lower rates, joint scaling; dedicated properties and YAML derivations. |
| Surcharge/MHST coverage | $450k/$600k cases yield $38,061.02/$54,432.81; total $2M tax $191,942.90 baseline/$234,169.10 extension. |
| Layout/style | Move YAML into `ca/prop3/`, explain bypass, remove redundant toggles; group CA registration/imports, export factory, remove unused import; inspected/formatted. |
| Durable references | Add [dated Prop 55 p16](https://vig.cdn.sos.ca.gov/2016/general/en/pdf/text-proposed-laws.pdf#page=16) to all schedules, identify §17041 subsections, remove stale indexing comments; audited. |
| Election follow-up | Schedule comments require certified-result check and removal of sunset entries if approved; then retire reform. |
| Additional independent findings | Split later-expiry/rate intervals, preserve differing future edits and bounded lower-rate edits; both-construction-path/idempotence regressions and endpoint/adjacent-day properties. |

## Methodology choice for Max

App activation honors dated true intervals intersecting 2031-01-01..2100-12-31. A 2026-only toggle has no out-year effect; delayed starts and false gaps are respected. Explicit `ca_prop3` bypass is unconditional within that horizon. Only enacted sunset brackets are extended. Differing future user-rate overrides survive; baseline-equal explicit edits cannot be distinguished from baseline and are restored.

## Validation and cost

**30 current YAML cases + the remaining 300-example Python property passed**, one file at a time at nice 0. The 14 completed checkpoint Python passes were reused.

| Provenance | Result |
|---|---|
| Old head `ea80e9d0ad`; compatible tests copied from `ef290736bf`, plus evidence-only bypass | **6 failed, 6 passed, 1 skipped**, 403.56s pytest/565.10s wall; max RSS 3,921,494,016 B. Helper property skipped because absent. |
| Recovered fix `279f541dd1` | **14 passed, 1 failed**, 1028.44s pytest/1205.73s wall; max RSS 4,060,102,656 B. Sole failure: Hypothesis input-generation health check under host contention. |
| Current window property | **1 passed**, 170.09s pytest/648.59s wall. Timing wrapper subsequently hit sandbox-denied `sysctl`; pytest passed. |
| Current regular-tax YAML | **9 passed**, 43.79s pytest/491.36s wall; max RSS 2,190,180,352 B. |
| Current contrib YAML | **11 passed**, 106.25s pytest/412.09s wall; max RSS 3,952,623,616 B. |
| Current AMT YAML | **6 passed**, 17.95s pytest/372.46s wall; max RSS 2,208,202,752 B. |
| Current total-tax YAML | **4 passed**, 18.10s pytest/248.16s wall; max RSS 2,183,905,280 B. |

Earlier `ef290736bf` had all **36 CI checks passing**, including partners. Recovered `.resume-evidence/ci-ef-contrib.log`: **Contrib (other-shard-1)** Python stage **72 passed in 1008.88s**; CA file approximately **224s**, inferred from timestamps; entire job **45m24s**. Python peak memory is unreported. These are existing measurements, not controlled before/after deltas; local contents and contention differ.

PR diff against merged main changes **zero partner files/outputs**. Inventory is **143** at reviewed head, **144** on merged main after upstream NC coverage, all periods before 2031; supplied 145 is not reproduced.

## Impact and open work

No population microsim completed; previous drivers only waited for the lock. This sandbox cannot write that lock and explicitly prohibits microsims. Hub must compare **main/corrected-baseline/Prop3** for **2025,2026,2030,2031,2035**, using identical cached dataset/entity order/weights. Calculate `ca_income_tax_before_credits`, `ca_amt`, `ca_mental_health_services_tax`, `ca_income_tax_before_refundable_credits`, `ca_income_tax`, `ca_withheld_income_tax`, `income_tax`, `household_net_income`; exclude enum arrays.

Expect zero direct effects before 2031, regular-tax reductions with possible AMT offsets thereafter, unchanged MHST, and reversal under Prop3. Hand examples: 2031 single/MFS $1M reduction **$12,226.20**; joint/QSS $2M **$24,452.40**; HOH $1.5M **$20,827.63**, rounded from unrounded calculations. These are household expectations, not population results.

Dollar expectations retain CA CPI; **#9621 remains OPEN** and requires later reconciliation. Statutory nearest-dollar threshold rounding remains unimplemented/outside scope. Check certified November 2026 election results. **Axiom parity remains needed** (`axiom: needed`).

Sandbox recovery: original `.git` remains read-only at assigned `e4363903f3`; resumed branch metadata lives in `.resume-git`. Use `GIT_DIR=$PWD/.resume-git GIT_WORK_TREE=$PWD git` or `/private/tmp/9601-git`. All code commits are remote. Only the assigned worktree was used; no other worktrees were created/removed. Hub can copy this report to the requested external reviews folder.

Report and evidence backup branch: [MaxGhenis/policyengine-us `wip/hub-9601-resume-sol2-report`](https://github.com/MaxGhenis/policyengine-us/tree/wip/hub-9601-resume-sol2-report). This backup includes the source tree at the code head plus the explicit report/evidence files; it does not change the PR code branch.
