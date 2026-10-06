# US #9621 resumed fix report

Status: WIP build backed up to `MaxGhenis/policyengine-us:wip/hub-resume-sol-9621`; not merged or promoted to the PR branch. The model implementation is `9d247513a1` plus current-main merge `3126a708c9`; the commit containing this report also preserves the ordinary historical WI fixture correction, citations, and evidence. The comparison base is upstream/main `2d0815ae23621f974bcb79e4a53b09e0b801119c`. Resolve the final backup revision with `git ls-remote origin refs/heads/wip/hub-resume-sol-9621`.

The previous attempt's `549b26ffe2` merge and snapshot `d1b072db90` were reused. All three snapshot paths (`PROGRESS.md`, `uprating_extensions.py`, and `cpi_u_nsa.yaml`) were recovered. An exact blob-to-file comparison verified recovery against the previous worktree, including its untracked NSA series; details are in `.resume-evidence/snapshot-completeness.txt`. The originally untracked journal is archived as `.resume-evidence/9621-recovered-progress.md`, and main's unrelated tracked `PROGRESS.md` was restored. No completed microsimulation or behavioral test output from the previous attempt was found; its research and source evidence were reused. The previous worktree and caller checkout were not written.

The assigned worktree's Git metadata is outside the sandbox and read-only. Commits therefore live in the workspace-local `.resume-git`, selected using `git --git-dir=.resume-git --work-tree=.`. The original `.git` pointer remains untouched. Every new commit is backed up on the fork WIP branch. The requested `~/reviews/us-hub/fixes/` report location is outside writable roots; this report and the inventory are kept in the assigned workspace.

## Findings and fixes

| Finding | Implementation and verification |
|---|---|
| IRS ending-August window | Retained the September–August average and separate CBO tax-year series: row 153 chained, row 152 unchained. Added endpoint and projection-isolation properties and a 2040 dependent-floor YAML case ($1,800). Actual source-function comparison on synthetic data: saved main returns 175; corrected helper returns 110. |
| Published IRS amounts and revision vintage | Retained explicit anchors and statutory dependent/educator calculations. Documented that one stored vintage per month does not reconstruct §1(f)(6)(A)'s release-date vintage. CPI-refresh preservation property covers all encoded standard-deduction and educator anchors. |
| Missing observations | Documented previous-month completion of October 2025 and flat unobserved tails as estimates. Added explicit synthetic completion property. |
| Vermont chained index | Added independent BLS CUUR0000SA0 observations and statutory-base indexing with unchained September–August CPI-U. Preserved 2025 agency anchors; encoded official 2026 **preliminary** brackets from `IN-114-Instr-2026`, page 2. Generated 2026 deductions and exemption remain calculated estimates, not published values. The 2017 base window is inferred from agency amounts; the statute does not explicitly name that base year. Corrected the MFS increment to $25 and the 2025 schedule links. |
| Wisconsin annual federal index | Added statutory base/year metadata, prior-August NSA CPI-U, decimal half-up $10 rounding, and a no-decrease floor. Encoded published 2026 maxima, phase-out starts, and HOH switch; preserved published 2026 brackets. The dependent limitation's statutory federal indexing exception is outside this helper; no missing dependent model was bundled. |
| Unsupported state snapshots | Replaced VT/WI snapshots with published anchors and independent statutory arithmetic; added chained-index isolation, half-up ties, and falling-CPI properties. Unrelated state tests retained. |
| WI citations and formula | Corrected §71.05(22)(dp)/(dt) titles and Form 1-ES page 2/page 3 links. Added the five requested 2026 YAML cases and exact HOH single-formula continuation above $58,827. With published 2026 anchors at AGI $60,000, the old marginal continuation gives $9,174.35895; the correct formula gives $9,174.40. |
| WI 2025 second bracket | Independently verified Act 15 amounts $50,480/$67,300/$33,650. Current main has since merged this correction; retained its additional worksheet tests alongside our boundary cases. |
| California calibration | Encoded DIR June 2026 CCPI 364.969 and FTB published 2026 deductions, exemption credits, renter ceilings, and brackets. Added 24 ordinary YAML cases. Preserved 2025 CA anchors. Unpublished credits remain projections, and the future national chained proxy remains unresolved. |
| Final CBO calendar anchors | Corrected the extension that started after 2034 despite explicit 2035 values; it now preserves 2035 CPI-U 407.3 and chained CPI 219.2, then extrapolates afterward. Added source-anchor preservation regressions. |
| Main compatibility | Merged current upstream/main; sole conflict was WI ordinary tax YAML, resolved retaining both sets of cases. Louisiana helpers/invocation preserved. Partner fixtures have **zero diff relative to current main**; inherited main partner updates were not rewritten. |

## Tests actually run

- `make format`: passed with the cached environment and `UV_NO_SYNC=1`; ruff format and lint both passed. The cached Python 3.13 interpreter satisfies repository support for Python 3.11–3.14, though uv reports a project interpreter preference of 3.14.
- Federal Python file: first run 29 passed/2 failed/1 deselected; second run 32 passed/1 failed/1 deselected. The failures came from new fixture construction (`Parameter.update` on an unattached parameter and empty nodes), corrected at their source. Focused published-anchor rerun: 1 passed/33 deselected. Thus 33 distinct selected federal tests passed across full and focused runs. The default-dataset retirement test was excluded.
- Single state-rounding Python file: 35 passed, covering published anchors, independent VT/WI indexing, federal-index isolation, falling CPI, half-up ties, and retained other-state checks.
- Federal basic standard deduction YAML: 14 passed, including the required 2040 dependent floor of $1,800 and the retained statutory dependent-deduction cases.
- Touched Oregon Kids' Credit Python file: 8 passed, including observed, incomplete, and projected CPI windows and the preserved credit sunset/reform behavior. One existing divide warning occurred; no assertion failed.
- California tax-before-credits YAML: 8 passed, including six new published 2026 schedule calculations. Other added CA YAML files remain pending behavioral runs.
- Isolated source window check: 175 → 110, passed. YAML syntax and all new case arithmetic were independently verified.
- WI deduction YAML before/after: the recovered pre-fix model on the current ten cases produced 7 failed/3 passed; the corrected build produced 10 passed. The before-run log is `.resume-evidence/wi-deduction-before-final.log`. An earlier corrected-build run produced 9 passed/1 failed: all five requested 2026 cases and the new 2026 HOH crossover passed, while the existing 2022 above-crossover case expected continuation of a rounded HOH amount. Its ordinary fixture was corrected to the statutory single formula: $11,790 − ($59,705 − $16,990) × .12 = $6,664.20. The final ten-case rerun passed. Other added YAML files remain pending behavioral runs. No full suites or microsimulations were run.
- Independent agent source review identified CBO-anchor overwrite and HOH offset; both addressed. Inventory generator separately reviewed.
- Static comparison confirms all three Louisiana helpers are identical to comparison main, their invocation is retained, main's journal is exactly restored, and partner diff is empty. Evidence: `.resume-evidence/main-compatibility.txt`.

Logs and prepared runners: `.resume-evidence/`. No claim of a completed before/after model suite or aggregate impact.

The source helpers and Python tests remain in the existing Rest core/policy CI groups; policy examples remain in the existing IRS and state YAML shards. No CI matrix or concurrency setting changed. Logged pytest execution times exclude the slow model import. Setup-inclusive before/after elapsed time and peak memory were not measured, so this report makes no CI cost claim.

## Impact and remaining work

**Unmeasured.** The wrappers required for multi-file tests and microsimulations refuse to start: the sandbox denies `ps`, and the microsimulation wrapper also cannot write its global progress log. No dataset was downloaded, no heavy lock was bypassed, and no microsimulation began. Run comparisons against current main with identical inputs and weights for 2025 (control), 2026, 2027, 2028, 2030, and 2036, including federal and CA/VT/WI components. Exclude enum arrays from comparison. Weighted totals and changed-unit counts are still required; none are available here.

The targeted renter partner file completed 5 cases/11 assertions with 6 changes outside tolerance and 0 calculation errors; fixtures remain untouched. Its partial old → new table is in `9621-partner-inventory.md`. The complete partner inventory and all six failed CI-suite replays remain pending a working shared-lock execution environment. The archived 43-case raw-head inventory is preserved separately and does not supply approved final CA values. Partner fixtures remain unchanged relative to main, and the hub's three-question gate remains unanswered.

Axiom parity follow-up is marked `axiom: needed` as required by the PR template. Formal standard-tier hub review and coordination with #9601 projected CA expectations/#9718 shared extension edits/#9709 partner gate remain for the hub. No messages to those owners were sent. #552 input-uprating implementation was not bundled.

## Methodology choices for Max

1. **Partial-window completion:** retain previous-month carry-forward for missing October 2025 and last-observation flat tails. Both are forecasts/completion estimates, not statutory observations.
2. **Post-CBO extrapolation:** retain constant final forecast-year growth, after tax-year 2036 and calendar 2035. Preserve the last official forecast point.
3. **Future state forecast proxies:** VT uses CBO's unchained tax-year window forecast when no monthly observation exists. WI uses the existing monthly geometric interpolation policy toward CBO unchained calendar averages after the last NSA observation; future August values are proxies. CA's existing federal chained proxy remains after the published June 2026 anchor. Its replacement and treatment of unpublished CA 2026 credit forecasts require Max's decision; no new CA forecasting scheme was invented.

The release-date C-CPI statutory vintage is a reconstruction limitation, not a discretionary methodology choice. Vermont's inferred 2017 base window is corroborated by reproduced agency amounts but remains distinct from an explicitly stated statutory base year. Final VT 2026 deduction/exemption publications were not retrieved; withholding allowances are not presented as those published values.

Because forecast choices and mandatory heavy validation remain open, the model was backed up only to a fork WIP branch. Do not promote or mark the PR ready on this report alone.
