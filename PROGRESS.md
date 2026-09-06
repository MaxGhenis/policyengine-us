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
- [ ] Reproduce bundled FY2025/FY2026 rows from the published workbooks to prove the transform before applying it to FY2024
- [ ] Append FY2024 county FMR rows
- [ ] Append FY2024 SAFMR rows, scoped to metros actually implemented for 2024
- [ ] Measure the 2025/2026 side effects (county-FMR missing-row fallback; SAFMR HCV ZIP union)
- [ ] Tests: period-exact resolution, representative jurisdictions, missing-row/refusal behaviour
- [ ] README vintage/effective dates, changelog fragment, `make format`
- [ ] Focused test run + artifacts in `R/us-hud-2024-model-source-fix-REPORT.md/.json`

## Done

Nothing committed to the branch yet beyond this file.

## Next

Reproduce the bundled FY2025 county FMR rows from `FY25_FMRs.xlsx` through
`policyengine_us/tools/convert_hud_fmr_xlsx.py` and diff against the bundled CSV.

## Out of scope (recorded, not waived)

Utility-allowance coverage, unobserved bedrooms for the assisted universe,
multi-SPM shared budgets, and the undated Los Angeles payment-standard branch stay
open defects. No counterfactual full-charge imputer is built here.
