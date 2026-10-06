from policyengine_us.model_api import *


class estate_income(Variable):
    value_type = float
    entity = Person
    label = "estate income"
    documentation = (
        "Taxable estate or trust income or loss reported by a beneficiary on "
        "Schedule E, excluding inherited principal."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61#a_14",
        "https://www.law.cornell.edu/uscode/text/26/662",
        "https://www.irs.gov/instructions/i1040se",
    )
