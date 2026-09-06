# HUD Fair Market Rents (FMRs)

## What

`fair_market_rents.csv` holds HUD's published Fair Market Rents at the FMR-area
level, indexed by `(state, hud_fmr_area_code, year, bedrooms)`. FMRs are the
40th-percentile gross-rent estimates HUD uses to cap rents under the Housing
Choice Voucher program and size other federal housing subsidies (24 CFR Part
888).

The model variable `hud_fair_market_rent` reads from this CSV and normalizes
HUD FMR-area codes to PolicyEngine's five-digit `county_fips` input. When
several HUD FMR areas map to one county and no direct county row exists, the
loader uses the median FMR-area value as a lossy county-level fallback.

## Scope today

- **Years**: FY2024, FY2025 and FY2026. `nearest_fmr_year` resolves each queried
  period to the matching fiscal year when its rows are present (period 2024 →
  FY2024, 2025 → FY2025, 2026 → FY2026). Periods outside the bundled range fall
  back to the nearest bundled year: later periods to the latest bundled year
  (2027 → FY2026), **earlier periods to the earliest bundled year** (2023 →
  FY2024). Before FY2024 was bundled, period 2024 fell *forward* to FY2025 — a
  fiscal year beginning 2024-10-01, so a 2024 simulation read data that did not
  exist during most of the year it was modelling.
- **Geography**: county-level lookup from HUD FMR areas (no SAFMR ZIP-level
  resolution here). Where HUD publishes one pseudo-area for a territory, that
  pseudo-area is expanded to the territory's county FIPS codes.
- **Connecticut**: HUD's FY2026 file adopts Connecticut's nine Census planning
  regions (FIPS `09110`–`09190`) in place of the eight legacy counties (FIPS
  `09001`–`09015`); Connecticut abolished county government in 1960 and the
  Census Bureau approved the planning regions as county-equivalents in 2022.
  PolicyEngine's `County` enum still uses the legacy counties. When a queried
  county/bedroom row is absent from the preferred fiscal year, such as legacy
  Connecticut counties in FY2026, `hud_fair_market_rent` falls back to the most
  recent earlier bundled year with a matching row rather than returning zero.
  **TODO**: this fallback depends on FY2025 remaining in the bundle. Migrate
  the `County` enum to Connecticut's planning regions (tracked in #8803)
  before FY2025 rows are ever dropped, or legacy CT counties will silently
  resolve to $0.
- **Data**: full FY2024, FY2025 and FY2026 county-level HUD files. All three
  years carry the same 23,820 rows over the same 4,764 HUD FMR areas in 56
  states, so no county/bedroom row exists in one bundled year and not another,
  and the earlier-year fallback above never fires between FY2024 and FY2025.

## Fiscal year to period: the convention

A HUD fiscal year runs from October 1 of the previous calendar year to
September 30 of the labelled year — FY2024 covers 2023-10-01 to 2024-09-30. The
model maps a calendar-year period to **the fiscal year carrying the same
label** (period 2024 → FY2024). It does **not** average the two fiscal years
overlapping a calendar year, and it does not weight them by month. That
approximation is the pre-existing convention for every HUD table here; it is
recorded rather than introduced.

## Vintage: HUD publishes an original and a revised workbook per year

For each fiscal year HUD serves both `FYXX_FMRs.xlsx` and a revised file, and
they differ. The bundled rows are **not** from a single vintage:

| bundled year | vintage | evidence |
|---|---|---|
| FY2024 | revised (`FMR2024_final_revised.xlsx`) | matches 23,820/23,820 rows |
| FY2025 | **original** (`FY25_FMRs.xlsx`) | matches 23,820/23,820; the revised file differs in 905 rows |
| FY2026 | revised (`FY26_FMRs_revised.xlsx`) | matches 23,820/23,820; the original differs in 45 rows |

FY2024 follows HUD's own `final_revised` label and the later FY2026 precedent.
The FY2024 revision touches exactly one FMR area — Honolulu County, HI
(`1500399999`), all five bedroom counts — which is precisely what the revising
Federal Register notice describes ("updates the FY 2024 FMRs for one area based
on new survey data"). **FY2025's original-vintage rows are deliberately left as
they are**; re-sourcing them from the revised file would move 905 rows and is a
separate decision, not part of adding FY2024.

## Schema

| column | type | meaning |
|---|---|---|
| `state` | str | two-letter state abbreviation |
| `hud_fmr_area_code` | str | HUD FMR-area code from the county-level source file |
| `year` | int | HUD fiscal year |
| `bedrooms` | int | 0 (efficiency) through 4 |
| `value` | float | monthly FMR in current-year dollars |

## Refresh

Two equivalent tools write this CSV; both **append** a new `--year` rather than
overwriting, so multiple fiscal years coexist.

From the HUD User API (needs a free `HUD_API_TOKEN`, register at
<https://www.huduser.gov/hudapi/>):

```
python -m policyengine_us.tools.download_hud_fmr --year 2025 --output \
    policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv
```

From HUD's published per-year Excel workbook (no token; needs `python-calamine`
— browse to Datasets > Fair Market Rents and download the year's workbook).
Prefer the revised file where HUD publishes one:

```
python -m policyengine_us.tools.convert_hud_fmr_xlsx \
    --input FMR2024_final_revised.xlsx --year 2024 --output \
    policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv
```

## Source

- HUD User FMR documentation: <https://www.huduser.gov/portal/datasets/fmr.html>
- FY2024 workbook (bundled vintage):
  <https://www.huduser.gov/portal/datasets/fmr/fmr2024/FMR2024_final_revised.xlsx>
  (retrieved 2026-09-06, SHA-256
  `0a6634d5745e07f0638efe2aca65161b4b8d6982ebd4d257e8191ed18ecfbf98`). The
  superseded original is `FY24_FMRs.xlsx` (SHA-256
  `9f6b3d53b7d53bf3a0285caf0874bd6e61d0ed0a906e6e355776080eef1f1127`).
- FY2024 Federal Register notice:
  <https://www.federalregister.gov/documents/2023/08/31/2023-18402> (published
  2023-08-31), corrected by
  <https://www.federalregister.gov/documents/2023/09/05/2023-19156>, which fixes
  the effective date to **2023-10-01**. Revised by
  <https://www.federalregister.gov/documents/2024/02/09/2024-02666> (effective
  2024-03-11), the one-area update reflected in the bundled FY2024 rows.
- FY2025 Federal Register notice: <https://www.federalregister.gov/documents/2024/08/14/2024-18002>
- FY2026 Federal Register notice: <https://www.federalregister.gov/documents/2025/08/22/2025-16060>
  (effective 2025-10-01).
- Regulatory citation: 24 CFR §888 (FMR rules), 24 CFR §982.503 (HCV payment
  standards bound to 90-110 percent of FMR).

---

# Small Area Fair Market Rents (SAFMRs)

## What

`small_area_fair_market_rents.csv` holds HUD's ZIP-code-level Small Area FMRs,
indexed by `(zip_code, year, bedrooms)`. SAFMRs replace a single metro-wide FMR
with a per-ZIP 40th-percentile rent so Housing Choice Voucher payment standards
track neighborhood rents. HUD mandates SAFMR use for HCV payment standards in
designated metros (24 CFR §888.113; HUD's designated-SAFMR-areas list).

The model variable `small_area_fair_market_rent` reads this CSV, and
`safmr_used_for_hcv` gates whether a ZIP's SAFMR is the household's HCV payment
standard basis (only inside the mandatory-SAFMR metros bundled here).

## Scope today

- **Years**: FY2024, FY2025 and FY2026. `nearest_safmr_year` resolves each
  queried period to the matching fiscal year when its rows are present (period
  2024 → FY2024, 2025 → FY2025, 2026 → FY2026). Periods outside the bundled
  range fall back to the nearest bundled year (2023 → FY2024, 2027 → FY2026).
  Before FY2024 was bundled, period 2024 fell forward to FY2025.
- **Geography**: the six metros where HUD mandates SAFMRs and PolicyEngine has
  ZIP coverage — Dallas, Fort Worth-Arlington, San Antonio-New Braunfels, and
  Beaumont-Port Arthur (TX) plus Kansas City (KS side) and Wichita (KS). The
  `hud_area_name` column is a curated metro label, not HUD's raw FMR-area name;
  the ZIP set is the union HUD publishes across these metros.
- **Metro coverage is per fiscal year, keyed to HUD's implementation dates.**
  HUD's designated-SAFMR-areas list gives, for each mandatory metro, the date
  PHAs must have implemented SAFMRs:

  | metro | year designated | implemented | bundled fiscal years |
  |---|---|---|---|
  | Dallas, TX | 2011 | 10/1/2011 | FY2024, FY2025, FY2026 |
  | Fort Worth-Arlington, TX | 2016 | 4/1/2018 | FY2024, FY2025, FY2026 |
  | San Antonio-New Braunfels, TX | 2016 | 4/1/2018 | FY2024, FY2025, FY2026 |
  | Beaumont-Port Arthur, TX | 2023 | 1/1/2025 | FY2025, FY2026 |
  | Kansas City, MO-KS | 2023 | 1/1/2025 | FY2025, FY2026 |
  | Wichita, KS | 2023 | 1/1/2025 | FY2025, FY2026 |

  HUD published FY2024 SAFMRs for all six, but the 2023 cohort's SAFMRs were
  not the HCV payment-standard basis during FY2024 (2023-10-01 to 2024-09-30)
  under either the designating notice's implementation date (2024-10-01) or the
  1/1/2025 date HUD's designated-areas list records. Their FY2024 rows are
  therefore not bundled, and `small_area_fair_market_rent` returns zero for
  them at period 2024, which leaves `pha_payment_standard` on the county FMR —
  the correct FY2024 basis — through its existing `> 0` guard. See "Known gap"
  below for the part of this that the model still gets wrong.
- **Data**: 724 ZIPs for FY2026, 722 for FY2025, 503 for FY2024. Two ZIPs
  (`75429` Dallas, `78284` San Antonio) exist only in the FY2026 SAFMR file —
  HUD did not publish FY2025 SAFMRs for them, so they have no FY2025 rows and
  resolve to the county FMR at period 2025 rather than a fabricated value. Four
  bundled ZIPs in the three FY2024 metros (`75099`, `75429`, `78028`, `78284`)
  have no FY2024 SAFMR published and are handled the same way. Each ZIP carries
  0-4 bedrooms; larger units add 15% of the 4-bedroom value per extra bedroom in
  the variable.
- **Vintage**: HUD serves an original and a revised SAFMR workbook per year. For
  the bundled ZIP set the two agree exactly in FY2024, FY2025 and FY2026, so the
  vintage choice is immaterial here; FY2024 was taken from
  `fy2024_safmrs_revised.xlsx`.

## Known gap

`safmr_used_for_hcv` has no year dimension: it returns `true` for every bundled
ZIP at every period, including 2024 for the three metros HUD had not yet
required to use SAFMRs. The dollar path is unaffected — `pha_payment_standard`
also requires `small_area_fair_market_rent > 0`, and those metros have no FY2024
rows — but the boolean itself is wrong before a metro's implementation date. Its
curated metro labels also group in ZIPs that HUD assigns to adjacent
non-designated FMR areas (for example Wise County and Sherman-Denison ZIPs under
`Dallas, TX`), which over-includes them in every year.

## Schema

| column | type | meaning |
|---|---|---|
| `zip_code` | str | five-digit ZIP code |
| `hud_area_name` | str | curated metro label (e.g. `Dallas, TX`) |
| `year` | int | HUD fiscal year |
| `bedrooms` | int | 0 (efficiency) through 4 |
| `value` | float | monthly SAFMR (the raw `SAFMR XBR` column, not a 90/110% payment-standard limit) in current-year dollars |

## Refresh

SAFMRs are extracted from HUD's published per-year SAFMR Excel workbook (browse
to Datasets > Fair Market Rents > Small Area FMRs) by
`tools/convert_hud_safmr_xlsx.py`, which reuses the bundled ZIP set and curated
metro labels and merges on `(zip_code, year, bedrooms)` so fiscal years coexist.
The workbook's raw `SAFMR 0BR`…`SAFMR 4BR` columns become the `value` column;
the 90%/110% payment-standard columns are ignored. Pass `--metro` when a fiscal
year predates a metro's implementation date:

```
python -m policyengine_us.tools.convert_hud_safmr_xlsx \
    --input fy2024_safmrs_revised.xlsx --year 2024 \
    --metro "Dallas, TX" --metro "Fort Worth, TX" --metro "San Antonio, TX" \
    --output \
    policyengine_us/parameters/gov/hud/fmr/small_area_fair_market_rents.csv
```

`convert_hud_fmr_xlsx.py` handles the county-FMR workbook only, not the SAFMR
workbook.

## Source

- HUD SAFMR data portal: <https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html>
- FY2024 SAFMR workbook: <https://www.huduser.gov/portal/datasets/fmr/fmr2024/fy2024_safmrs_revised.xlsx>
  (retrieved 2026-09-06, SHA-256
  `a39172cf275fa6a8c017ade5ee5423746b86868edeeaffc06473bb46993ec4cf`; the
  original `fy2024_safmrs.xlsx` is SHA-256
  `467a96d011969b82cc0b508469010f73acf90ab7f6a4010df76341b1b2f1d423` and is
  identical over the bundled ZIPs).
- FY2024 SAFMR designation notice (the 2023 cohort and its implementation date):
  <https://www.federalregister.gov/documents/2023/10/25/2023-23685> (published
  2023-10-25, "Implementation date: October 1, 2024").
- FY2025 SAFMR workbook: <https://www.huduser.gov/portal/datasets/fmr/fmr2025/fy2025_safmrs.xlsx>
  (retrieved 2026-07-06).
- FY2026 SAFMR workbook: <https://www.huduser.gov/portal/datasets/fmr/fmr2026/fy2026_safmrs.xlsx>
  (retrieved 2026-07-06).
- FY2025 designated-SAFMR-areas list (mandatory metros, implementation dates):
  <https://www.huduser.gov/portal/datasets/fmr/fmr2025/designated-safmr-areas.pdf>
  (retrieved 2026-07-06).
- Regulatory citation: 24 CFR §888.113 (mandatory SAFMR metros), 24 CFR
  §982.503 (HCV payment standards, 90-110 percent of the applicable FMR).
