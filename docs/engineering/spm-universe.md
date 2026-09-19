# Annual SPM measurement scope

Population datasets must declare `spm_unit_spm_universe_status` for every SPM unit
and every year in which they request an SPM measurement. The country model owns
this source contract; the SPM calculator continues to own threshold amounts.

| Status | Meaning | Measurement behavior |
| --- | --- | --- |
| `INCLUDED` | The source establishes that the unit belongs to that year's SPM universe. | Calculate using the canonical provider and the unit's geography and composition. |
| `OUTSIDE` | The source establishes that the unit is outside that year's SPM universe. | Return missing SPM outcomes without sending the unit to the threshold provider. |
| `UNRESOLVED` | The source has not established scope. | Raise `SPM_UNIVERSE_REQUIRED`. |

The enum's default value is `UNRESOLVED`. Its year-local formula distinguishes
dataset simulations from household situations: absent dataset declarations remain
unresolved, while a household situation defaults to included. Explicit annual
inputs override that formula. Zero assistance, missing geography, and unusual
composition do not establish that a population record is outside the universe.

Automatic extension of a single-year dataset drops this declaration from generated
future years. It preserves the original year and explicit multi-year declarations.
An annual producer must supply a new declaration before measuring a future year.

## Source ownership

`DATASET_SOURCE_INPUTS` includes the annual SPM-unit scope enum and the observed
person-level `is_spm_independent_minor_role`. Neither declaration authorizes a
producer to fabricate missing source evidence. The latter remains an eternal
Boolean input, independent of the annual scope enum.

Datasets cannot store calculator-owned measurements, country-derived poverty
aliases, housing allocation outputs, `spm_unit_oecd_equiv_net_income`, or
`spm_unit_income_decile`. Both dataset ingestion and later dataset `set_input`
calls enforce that boundary. Household situation inputs used in formula tests
retain their existing behavior.

Source scope depends on the survey. The Census Bureau's
[ACS SPM research](https://www.census.gov/content/dam/Census/library/working-papers/2020/demo/SEHSD-WP2020-09.pdf#page=6)
excludes group quarters from its ACS-based SPM universe and describes the inclusion
of some noninstitutionalized group quarters in the CPS ASEC SPM universe.
A producer must establish the applicable source universe rather than applying
one blanket group-quarters rule to every survey.

## Ordinary benefits and housing allocation

Ordinary household benefits and CBO transfers continue to use actual
`housing_assistance`. CARE, FERA and the ordinary-income branches of contributed
reforms retain their existing rules. Those calculations do not require SPM scope
or an SPM threshold provider. The obsolete proposal for an
`spm_unit_ordinary_housing_subsidy` bridge and a reported subsidy input is not part
of this implementation.

The existing household-to-SPM-unit allocation retains every unit's share, including
units outside the measurement universe. Scope masking does not redistribute those
shares to included units. Included assisted units receive the existing cap based
on the canonical housing portion and allocated tenant payment; included unassisted
units receive zero. Outside units receive missing capped subsidies and SPM
benefits. This scope change does not resolve or change the existing A4 tenant
payment assumption.

## Nullable outcomes and denominators

The five public poverty indicators use floating-point stock quantities: `0` or `1`
inside the universe and `NaN` outside. Monthly queries preserve the annual stock
value. Included indicators require finite resources and positive finite
thresholds, otherwise raising `SPM_MEASUREMENT_INVALID`.

Thresholds, poverty lines and gaps, SPM benefits and resources, equivalised income,
and income deciles are also missing outside. Unresolved scope fails before the
measurement, including zero-assistance and HUD-abolition branches. Ordinary income
remains available with absent or unresolved SPM scope.

Income deciles validate every included income and rank only included units with
the existing person-weighted MicroSeries convention. An outside record's income
or weight cannot affect those ranks. All-outside populations return missing ranks
without invoking the ranker. Included nonfinite income is an error, not another
excluded record. Deciles are floating-point stocks with integer-valued ranks
inside the universe.

Missing-aware weighted summaries require Microdf 1.3.0. A weighted `.count()` gives
the included denominator, and `.mean()` gives the poverty rate among included
people. When the denominator is empty, callers should report no estimate, using
JSON `null` when serializing. See the
[microsimulation example](../usage/microsimulation.md). This source change does not
qualify downstream JSON serialization.

## Validation and release holds

This reconciliation is limited to source changes and synthetic validation using
an existing runtime with Core 3.30.2, calculator 1.0.0 and Microdf 1.3.0. It does not
change dependencies, country version, data defaults or population payloads. The
repository lock still selects Microdf 1.2.1, whose weighted missing-value count
behavior is not qualified for these nullable summaries.

The default native population tests retain their SPM decile and 10,000-unit SPM
net-income assertions. They are not run in this bounded reconciliation and are
expected to refuse populations lacking annual scope. These are release blockers,
not skipped assertions or evidence of a qualified dataset. The legacy enhanced-CPS
threshold test now expects the earlier scope error while retaining its geography
and composition checks; that native test is also not run here.

Actual annual source declarations, dependency reconciliation, native population
validation, and cross-repository wrapper/bundle acceptance require separate work.
Synthetic results alone do not establish merge or release readiness.
