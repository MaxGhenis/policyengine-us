import pytest

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM
from policyengine_us.variables.gov.states.tax.payroll.unemployment._jurisdictions import (
    STATE_UNEMPLOYMENT_TAX_JURISDICTIONS,
)

PERIOD = "2026"
# select_state_unemployment_tax_parameter reads these parameters for every
# jurisdiction and every person, whatever the household's state.
HELPER_PARAMETERS = ("taxable_wage_base", "default_rate")


def make_simulation(state_code: str) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 30},
                    "employment_income": {PERIOD: 1_000},
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {PERIOD: state_code},
                }
            },
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


@pytest.mark.parametrize(
    ("state_code", "slug"),
    [
        (state_code, slug)
        for _, state_code, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS
    ],
    ids=[state_code for _, state_code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS],
)
def test_jurisdiction_specific_employer_state_unemployment_tax_formula(
    state_code: str, slug: str
):
    sim = make_simulation(state_code)

    expected = (
        sim.calculate("employer_state_unemployment_tax_rate", PERIOD)[0]
        * sim.calculate("taxable_earnings_for_state_unemployment_tax", PERIOD)[0]
    )
    jurisdiction_tax = sim.calculate(f"{slug}_employer_state_unemployment_tax", PERIOD)[
        0
    ]
    aggregate_tax = sim.calculate("employer_state_unemployment_tax", PERIOD)[0]

    assert jurisdiction_tax == pytest.approx(expected)
    assert aggregate_tax == pytest.approx(jurisdiction_tax)


@pytest.mark.parametrize(
    ("group", "slug"),
    [(group, slug) for group, _, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS],
    ids=[state_code for _, state_code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS],
)
def test_jurisdiction_unemployment_helper_parameters_cover_every_period(
    group: str, slug: str
):
    # A jurisdiction whose parameter starts after a simulated period would make
    # the all-jurisdiction helper raise ParameterNotFoundError for every
    # household in that period, not only households in that jurisdiction.
    unemployment = getattr(
        getattr(SYSTEM.parameters.gov, group), slug
    ).tax.payroll.unemployment
    instants = ["0001-01-01"] + [f"{year}-01-01" for year in range(2000, 2031)]
    for name in HELPER_PARAMETERS:
        parameter = getattr(unemployment, name)
        missing = [instant for instant in instants if parameter(instant) is None]
        assert not missing, f"{parameter.name} has no value at {missing}"
