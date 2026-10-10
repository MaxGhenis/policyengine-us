from policyengine_us.model_api import *


class ny_income_tax_if_subtracting_claim_of_right_repayment(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York State and local income tax if subtracting the claim of right repayment"
    unit = USD
    documentation = (
        "New York State, New York City and Yonkers income tax if subtracting the claim of right repayment "
        "from New York adjusted gross income (Tax Law 612(c)(45))."
    )
    definition_period = YEAR
    reference = "https://legislation.nysenate.gov/pdf/laws/TAX612#page=23"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "ny_claim_of_right_subtraction",
            period,
            {
                "ny_claim_of_right_subtraction_applies": np.ones(
                    tax_unit.count, dtype=bool
                )
            },
        )
        return (
            branch.calculate("ny_income_tax", period)
            + branch.calculate("nyc_income_tax", period)
            + branch.calculate("ny_yonkers_income_tax", period)
        )
