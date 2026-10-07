## What changes

California's rates above 9.3% expire after tax year 2030. All five filing-status schedules revert to 9.3% on January 1, 2031; Proposition 3's contributed reform extends the pre-sunset rates. The legal boundary is established by [Prop 55 §4, page 16](https://vig.cdn.sos.ca.gov/2016/general/en/pdf/text-proposed-laws.pdf#page=16); Prop 3 removes that boundary in [§4, page 6](https://vig.cdn.sos.ca.gov/2026/general/pdf/prop3-text-proposed-laws.pdf#page=6) and [page 7](https://vig.cdn.sos.ca.gov/2026/general/pdf/prop3-text-proposed-laws.pdf#page=7). [RTC §17045](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17045.&lawCode=RTC) supplies the joint and surviving-spouse treatment.

This round replaces hard-coded rates and bracket positions with the enacted schedules, snapshots rates before applying updates, respects dated app activation, and preserves future rate overrides that differ from the enacted baseline. It also adds coverage for every filing status, AMT, total tax including MHST, and both construction paths. The baseline retains the sunset; thresholds and their existing CA CPI forecasting assumptions remain in place.

## DTrim99's review

The [changes-requested review](https://github.com/PolicyEngine/policyengine-us/pull/9601#pullrequestreview-5310115855) and [program review](https://github.com/PolicyEngine/policyengine-us/pull/9601#issuecomment-5822089855) remain open for re-review. Each requested item is addressed as follows:

| Review item | Change and coverage |
|---|---|
| Critical 1: HOH and shared citations | HOH cites §36(f)(3); the shared toggle, reform comment and sunset fragment cover §36(f)(2)–(3). |
| Critical 2: literal rates and bracket indexes | Determine sunset-affected brackets from the unreformed schedule and copy their user-adjusted 2030 rates. Regression covers a .104 override and bounded lower-rate edits. |
| Should 1: activation misses 2029+ and bounded toggle leaks | Inspect dated `in_effect.values_list`; apply only true intervals intersecting 2031–2100. `Reform.from_dict` tests cover a 2031 start, 2026-only activation, delayed activation and true/false/true intervals. |
| Should 2: operative references | Toggle cites Prop 3 §4 pages 6–7 and [LAO Figure 1, page 2](https://vig.cdn.sos.ca.gov/2026/general/pdf/prop3.pdf#page=2). |
| Should 3: joint/QSS statutory chain | Both schedules cite RTC §17045; direct rate and scaling properties cover their relationship to single. |
| Should 4: missing statuses | Add 2031 baseline/reform HOH, MFS and QSS cases, plus HOH 2030. |
| Should 5: feature changelog | Retain `.fixed.md` for the sunset and add `.added.md` for the public reform and toggle. |
| Should 6: AMT | Assert regular tax, `max(.07 × reduced AMTI − regular tax, 0)`, and total tax with a $1.4M AMTI / $1M taxable-income case. |
| Suggestion 1: CPI-independent assertions and arithmetic | Assert all statuses' rates at 2030, 2031 and 2035, unchanged thresholds/lower rates, and joint scaling; YAML comments state the hand derivations and forecast factors. |
| Suggestion 2: individual surcharge brackets | Add $450,000 and $600,000 cases. The latter rounds to **$54,432.81**, correcting the review's $54,432.80. |
| Suggestion 3: meaningful MHST coverage | Replace the isolated MHST assertion with regular and total tax stacking: $191,942.90 baseline versus $234,169.10 with Prop 3 at $2M. |
| Suggestion 4: test layout | Move YAML to `contrib/states/ca/prop3/ca_prop3.yaml`; explain bypass and baseline controls; remove redundant toggle inputs. |
| Suggestion 5: registration/import style | Group imports, factory creation and registration with the other CA reform; export `create_ca_prop3`; remove the unused import. |
| Suggestion 6: durable citations | Add dated Prop 55 references to all five schedules and identify the applicable §17041 subsections; remove stale federal-indexing comments. |
| Suggestion 7: election follow-up | Schedule comments track the certified November 2026 result and removal of sunset entries if approved. Follow-up will also retire the contributed reform once the baseline reflects enactment. |

The additional independent review identified later-expiry intervals, bounded lower-rate edits, future overrides and endpoint coverage. The recovered implementation addresses those with interval splitting, enacted-schedule comparison, idempotence checks on both construction paths, and transition/adjacent-day probes. Implementing statutory nearest-dollar threshold rounding remains outside this PR.

## Methodology choice for Max

The app toggle honors every dated true interval within **2031-01-01 through 2100-12-31**. A 2026-only override has no out-year effect; delayed activation begins on its effective date; false gaps retain the sunset. The explicit `ca_prop3` bypass used by YAML `reforms:` applies unconditionally within the model horizon.

Only brackets changed by the enacted sunset are extended. Their user-adjusted 2030 rates are copied where the future rate still equals the enacted baseline. Future overrides with a different rate survive, including on repeated application and both system-construction paths. A future user edit numerically equal to the enacted baseline cannot be distinguished from that baseline and is restored by Prop 3.

## Validation

Current head: **a72bca942f106a6cfbb0bda8b13f817318f446c5**, after a clean merge of main **dd9cb3f6839d290c8490c561b54b7afeedc3c888**. Both new commits were pushed immediately. `make format` passes; independent static review approves the recovered model changes and the timing-check adjustment.

Current single-file checks, run sequentially at nice 0:

| Check | Passed | Pytest elapsed | Wall including startup | Peak RSS |
|---|---:|---:|---:|---:|
| Baseline regular tax | 9 | 43.79s | 491.36s | 2.19 GB |
| Prop 3 YAML | 11 | 106.25s | 412.09s | 3.95 GB |
| Baseline AMT | 6 | 17.95s | 372.46s | 2.21 GB |
| Baseline total tax/MHST | 4 | 18.10s | 248.16s | 2.18 GB |
| Window property, 300 examples | 1 | 170.09s | 648.59s | Unavailable |

**30 YAML cases and the remaining Python property passed.** Reused the 14 completed Python passes from the recovered checkpoint rather than rerunning them. The window property's macOS timing wrapper subsequently hit a sandbox-denied `sysctl`; pytest passed. Subsequent measurements used a timer that preserves the test exit code. [Final-head partner CI](https://github.com/PolicyEngine/policyengine-us/actions/runs/37606433807/job/112743784640) passes; [full CI](https://github.com/PolicyEngine/policyengine-us/actions/runs/37606433807) is still running with no failures observed.

Recovered evidence is retained without claiming that older runs validate the final head:

- Original head `ea80e9d0ad`: evidence-only compatible copy of the new activation/rate tests recorded **6 failed, 6 passed, 1 skipped** in **403.56s**. The failures expose the dated activation, bounded timing and rate-copy bugs; the helper property skipped because that head had no helper.
- Recovered fix `279f541dd1`: **14 passed, 1 failed** in **1028.44s**. The only failure was Hypothesis's input-generation health check on the loaded host, after 158.40s; model assertions passed.
- Prior PR head `ef290736bf`: all **36 CI checks passed**, including partner checks. The original human review separately recorded **11 targeted YAML cases passing** at `ea80e9d0ad`.

The affected CI group is **Contrib (other-shard-1)** (`make test-policy-contrib-python`). Local macOS cost at `279f541dd1`, including startup: **1205.73s wall**, **4,060,102,656 bytes maximum RSS**, **3,924,561,136 bytes peak footprint**. The old-head evidence run took **565.10s wall**, **3,921,494,016 bytes maximum RSS**; different test contents and host contention prevent treating this as a controlled before/after delta. The Contrib CI log is now recovered: the Linux Python stage passed **72 tests in 1008.88s**; the CA file occupied **about 224s**, inferred from log timestamps within that shared process. The entire job took **45m24s**. Python-stage/file peak memory is not reported. These are existing CI measurements, not a controlled before/after comparison. The model-building tests protect activation, override replay and both construction paths; lightweight properties cover dates and interval restoration without constructing a model per example.

The PR diff against merged main changes **zero partner test files or expected outputs**. The current tree contains **144 YAML files**, with periods 2024, 2025, 2026 and 2026-01, all before 2031. `git ls-tree` counts 143 at the reviewed head and 144 on merged main; the supplied spec's 145 count is not reproduced.

## Impact and remaining follow-up

No population microsimulation completed in earlier attempts: both queued drivers remained waiting for the heavy lock, with no result files. This Codex sandbox cannot run the host lock and is explicitly prohibited from microsims. Population impact remains for the hub; no aggregate revenue or household-impact result is claimed here.

The hub should compare **main, corrected baseline and Prop 3 enabled** for **2025, 2026, 2030, 2031 and 2035**, using identical cached data, entity order and weights. Calculate `ca_income_tax_before_credits`, `ca_amt`, `ca_mental_health_services_tax`, `ca_income_tax_before_refundable_credits`, `ca_income_tax`, `ca_withheld_income_tax`, `income_tax` and `household_net_income`; exclude enum arrays from numerical comparison. Expect zero direct effects before 2031, a regular-tax reduction after the sunset, possible AMT offsets, unchanged MHST, and reversal of the regular-tax reduction when Prop 3 is enabled.

The existing forecast gives these hand-computed 2031 examples; they are household test expectations, not population estimates:

| Filing status / taxable income | Corrected regular tax | Prop 3 regular tax | Difference |
|---|---:|---:|---:|
| Single or MFS / $1M | $88,942.90 | $101,169.10 | $12,226.20 |
| Joint or QSS / $2M | $177,885.81 | $202,338.20 | $24,452.40 |
| HOH / $1.5M | $133,132.32 | $153,959.95 | $20,827.63 |

Differences are rounded from unrounded hand calculations; displayed taxes are rounded independently.

The $1.4M AMTI example has $98,000 tentative minimum tax: baseline AMT is $9,057.10, while Prop 3 AMT is zero. Dollar expectations still use `gov.states.ca.cpi`; **#9621 remains OPEN** and its IRS-uprating change requires reconciliation when it lands. Rate/date properties do not depend on forecasts. Check the certified election result after November 3, 2026.

axiom: needed
