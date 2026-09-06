# PROGRESS — FY2024 HUD FMR / SAFMR for the Microcosm US launch path

Branch `policyengine-us-hud-2024-launch-20260906`, worktree
`/Users/maxghenis/PolicyEngine/_worktrees/policyengine-us-hud-2024-launch-20260906`,
base `upstream/main` @ `04a961a2a6`.

## Defect being fixed

`policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv` and
`small_area_fair_market_rents.csv` bundle only FY2025 and FY2026. `nearest_fmr_year`
and `nearest_safmr_year` return `min(available_years)` when no bundled year is
`<= year`, so period **2024 resolves to FY2025** — a fiscal year that begins
2024-10-01, i.e. future data for a past period. The Microcosm US launch runs 2024
(national + congressional district), so every 2024 `hud_fair_market_rent` /
`small_area_fair_market_rent` / `pha_payment_standard` value on the launch path is
FY2025.

Verified independently in the frozen housing-consumer lane
(`R/us-housing-consumer-REPORT.md`, PE-US 1.819.0): "FMR table carries only
`[2025, 2026]`; 2024 resolves to FY2025."

## State

- [x] Discover maintained repo (`/Users/maxghenis/PolicyEngine/policyengine-us`), read AGENTS.md + CLAUDE.md + policyengine-model-development / policyengine-standards skills
- [x] Fetch `upstream/main`; confirm no existing FY2024 fix (issue #8801 CLOSED covering FY2025/FY2026 only, explicitly deferring "years before the earliest bundled year"; PRs #8804, #8916 added FY2026 county FMR and FY2025 SAFMR)
- [x] Fresh worktree from `upstream/main`; isolated `.venv` (Python 3.13.9, editable policyengine-us 1.822.5, policyengine-core 3.32.3, pandas 3.0.5, python-calamine 0.8.2)
- [x] Retrieve official HUD FY2024 workbooks + FY2025/FY2026 controls; record URL, HTTP status, size, SHA-256
- [x] Reproduce bundled FY2025/FY2026 rows from the published workbooks to prove the transform before applying it to FY2024
- [x] Append FY2024 county FMR rows (23,820, from `FMR2024_final_revised.xlsx`)
- [x] Append FY2024 SAFMR rows (2,515), scoped to the three metros HUD had implemented for 2024
- [x] Measure the side effects: FY2025/FY2026 loader digests and every probed engine value are **bit-identical**; periods **before** 2024 now resolve to FY2024 instead of FY2025 (measured, listed below)
- [x] Tests: period-exact resolution, representative jurisdictions, missing-row/refusal behaviour (gov/hud YAML 197 -> 220 passing)
- [x] README vintage/effective dates, changelog fragment, `ruff format` + `ruff check` clean
- [x] Focused test runs + artifacts in `R/us-hud-2024-model-source-fix-REPORT.md/.json`

## Done

**Vintage discovery.** HUD publishes an original *and* a revised workbook per
fiscal year. Reproducing the bundle through the repo's own converter shows the
repo's vintage convention is **inconsistent**, which was not documented anywhere:

| bundled year | matches original | matches revised |
|---|---|---|
| county FMR FY2025 | yes (0/23,820 differ) | no (905 differ) |
| county FMR FY2026 | no (45 differ) | yes (0 differ) |
| SAFMR FY2025 | yes | yes (identical over the bundled ZIPs) |
| SAFMR FY2026 | yes | yes (identical over the bundled ZIPs) |

FY2024 therefore follows the later precedent and HUD's own "final" label:
`FMR2024_final_revised.xlsx`. Original vs revised differ for FY2024 in exactly
5 rows (Honolulu County HI, `1500399999`, all five bedroom counts). The FY2025
original-vintage rows are **left untouched** — replacing them is out of scope and
is recorded as a separate finding.

**Data.** Purely additive: `git diff --stat` = 26,335 insertions, 0 deletions.
Sorted-line diff confirms 0 removed lines in either CSV.

- county FMR: 47,640 → 71,460 rows; FY2024 = 23,820 rows over the same 4,764 HUD
  areas and 56 states as FY2025/FY2026 (key sets identical, so no county/bedroom
  row exists in one year and not the others)
- SAFMR: 7,230 → 9,745 rows; FY2024 = 2,515 rows over 503 ZIPs
  (Dallas 241, Fort Worth 126, San Antonio 136)

**SAFMR metro scope for FY2024.** HUD's designated-SAFMR-areas list gives an
implementation date per metro. Of the six bundled metros only Dallas
(10/1/2011), Fort Worth-Arlington (4/1/2018) and San Antonio-New Braunfels
(4/1/2018) were implemented during 2024; Beaumont-Port Arthur, Kansas City MO-KS
and Wichita KS all implement 1/1/2025. Bundling FY2024 rows only for the three
implemented metros applies the file's own stated selection principle ("the metros
where HUD mandates SAFMR use") to FY2024, and makes `pha_payment_standard` fall
to the county FMR in the other three at period 2024 through the existing
`small_area_fair_market_rent > 0` guard — no variable change needed.

Four bundled ZIPs in the three implemented metros have no FY2024 SAFMR published
(`75099`, `75429`, `78028`, `78284`) and get no FY2024 row, matching the existing
treatment of ZIPs HUD did not publish for FY2025.

## Measured consequences

`nearest_fmr_year` and `nearest_safmr_year` both changed for **2018-2024**
(`2025 -> 2024`) and are unchanged for 2025-2028. Periods before 2024 fall back
to the earliest bundled year, so bundling FY2024 moves them from FY2025 to
FY2024 — closer to the modelled year under the pre-existing nearest-year
convention, but a change beyond period 2024 that has to be stated, not assumed.

Loader tables and engine values at 2025, 2026 and 2027 are **bit-identical**
before and after (per-year SHA-256 digests of the county and SAFMR tables match;
every probed household value matches).

| jurisdiction (2BR) | period 2024 before | period 2024 after |
|---|---|---|
| Los Angeles County CA | 31,500 | 30,528 |
| Alameda County CA | 32,184 | 31,080 |
| Fairfield County CT (median fallback) | 26,844 | 26,652 |
| Honolulu County HI (revised vintage) | 32,244 | 28,656 |
| Harris County TX | 18,348 | 16,284 |
| American Samoa pseudo-county | 12,144 | 11,724 |
| Northern Mariana pseudo-county | 11,952 | 11,544 |
| unmapped county `99999` | 0 | 0 |
| Dallas ZIP 75201 SAFMR | 33,960 | 31,680 |
| Wichita ZIP 67202 payment standard | 12,840 (SAFMR) | 12,204 (county FMR) |

Across the 16,175 shared county/bedroom cells the FY2024 value is lower than
FY2025 in 12,002, higher in 4,116 and equal in 57; the median county 2BR FMR is
**3.1% lower**. Over the 2,515 shared SAFMR cells the median is 5.2% lower. So
the launch path was reading 2024 rents roughly 3% high at the median, and up to
51% high in the tail.

## Checks

| check | result |
|---|---|
| `ruff format` + `ruff check .` | clean |
| all HUD YAML (`gov/hud`) | 220 passed (197 before, +23 new cases) |
| 41 baseline YAML files naming any HUD housing variable, incl. partner contract tests | 397 passed |
| 256 baseline YAML files over the full transitive dependency closure (157 variables) | 1,703 passed |
| `contrib/harris` (the reform reading `small_area_fair_market_rent`) | 19 passed |
| `pytest policyengine_us/tests` excluding `policy/` and `microsimulation/` | 363 passed, 1 skipped |

Before the tests were updated exactly two failed — the two that pinned the defect
by name. No partner contract test needed editing and none was edited. No
microsimulation was run and no national or congressional-district aggregate was
produced.

## Next

Nothing. The branch is a review candidate: not pushed, no PR, worktree clean.

## Out of scope (recorded, not waived)

Utility-allowance coverage, unobserved bedrooms for the assisted universe,
multi-SPM shared budgets, and the undated Los Angeles payment-standard branch stay
open defects. No counterfactual full-charge imputer is built here.
