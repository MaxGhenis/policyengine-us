from policyengine_us.model_api import *


class taxable_pension_income(Variable):
    value_type = float
    entity = Person
    label = "taxable pension income"
    unit = USD
    documentation = (
        "Taxable pensions and annuities (Form 1040 line 5b). Military retired "
        "pay is a pension includible in gross income, so it enters here once "
        "through military_retirement_pay and is not entered again in the "
        "public or private pension inputs."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61#a_11",
        "https://www.irs.gov/publications/p525#en_US_2024_publink1000229456",
    )

    adds = [
        "taxable_public_pension_income",
        "taxable_private_pension_income",
        "military_retirement_pay",
    ]
