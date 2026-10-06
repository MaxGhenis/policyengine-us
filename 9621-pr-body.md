**Draft: resumed fix build is backed up on the fork WIP branch. The PR branch has not been promoted, and partner fixture edits remain unapproved.**

Fixes #9105. Fixes #9608.

The resumed build retains the IRS September–August chained CPI window and separate CBO tax-year projections; preserves published IRS anchors and statutory dependent-deduction calculations; documents CPI revision-vintage limits and missing-month completion as estimates; and separates Vermont and Wisconsin statutory unchained indexes. It encodes WI's published 2026 deduction schedules and CA's published 2026 June CCPI, deductions, exemption credits, renter ceilings, and brackets. Vermont 2026 bracket anchors are explicitly preliminary; its calculated deduction/exemption projections are not represented as published values. Louisiana's newer extension is preserved.

Independent review also found and corrected overwritten CBO 2035 calendar forecast points and WI's small HOH offset above its published switch. Current upstream/main was merged, keeping its WI 2025 correction and both sets of ordinary regression cases. Partner fixtures have zero branch diff from that main.

The current model/merge build is `3126a708c9`, based on upstream/main `2d0815ae23621f974bcb79e4a53b09e0b801119c`. Backup: [MaxGhenis WIP branch](https://github.com/MaxGhenis/policyengine-us/tree/wip/hub-resume-sol-9621). This is a separate reviewable build; the PR head remains `194c1f6237`.

Tests actually run: `make format` and ruff lint passed; 33 distinct selected federal Python tests passed across full and focused runs after correcting two new fixture issues; 35 state-rounding tests, 8 Oregon Kids' Credit tests, 14 federal deduction YAML cases, and 8 California tax-before-credits cases passed. These include the 2040 dependent floor of $1,800 and six published 2026 CA schedule calculations. On the same ten Wisconsin deduction YAML cases, the recovered pre-fix model produced 7 failed/3 passed, while the corrected build produced 10 passed. The default-dataset retirement test was excluded. Other added YAML behavioral runs and broader suites remain pending. The synthetic actual-source endpoint test produces 175 on saved main and 110 after the window correction. The completed targeted partner inventory is described below and in the workspace report.

Impact: **not measured**. The machine-wide wrappers required for multi-file tests and microsimulations refuse to start because this sandbox denies `ps`; the microsimulation wrapper also cannot write its global progress log. No microsimulation or full partner sweep started, and the wrappers were not bypassed. Comparisons with identical inputs and weights for 2025 (control), 2026, 2027, 2028, 2030, and 2036 remain required, including weighted totals and changed-unit counts. Missing aggregate results do not establish that outputs are unchanged.

## Methodology choices for Max

- Partial-window completion: retain prior-month carry-forward for missing October 2025 and flat unobserved tails, explicitly labelled estimates.
- Post-CBO extrapolation: retain constant final forecast-year growth after tax-year 2036/calendar 2035, preserving the last official points.
- Future state forecast proxies: VT uses separate CBO unchained tax-year averages; WI uses existing geometric monthly interpolation toward CBO unchained calendar averages after observed NSA data. CA retains its prior national chained proxy after the published June 2026 anchor; its replacement and unpublished credit forecasting remain decisions for Max. No new CA forecasting scheme was invented.

Release-date statutory C-CPI vintage reconstruction remains a correctness limitation. Vermont's 2017 base window is inferred from reproduced agency amounts rather than an explicitly stated statutory base year. Published anchors take precedence.

Partner inventory: the archived 43-case raw-head California inventory remains evidence and does not supply approved final statutory calibration. Published CA 2026 anchors change the candidate inventory. A targeted renter partner file completed 5 cases/11 assertions with 6 output changes outside tolerance, including $55,218 becoming eligible; fixtures remain unchanged. The complete final output inventory is pending shared-lock execution. Partner fixtures stay untouched until the hub completes all three gate questions. Formal standard-tier review, required CI-suite replays, and coordination with #9601/#9718/#9709 remain open; core #552 was not bundled.

Evidence and remaining steps: [resume report](https://github.com/MaxGhenis/policyengine-us/blob/wip/hub-resume-sol-9621/9621-report.md), [partial partner inventory](https://github.com/MaxGhenis/policyengine-us/blob/wip/hub-resume-sol-9621/9621-partner-inventory.md), and [saved logs and runners](https://github.com/MaxGhenis/policyengine-us/tree/wip/hub-resume-sol-9621/.resume-evidence).

axiom: needed
