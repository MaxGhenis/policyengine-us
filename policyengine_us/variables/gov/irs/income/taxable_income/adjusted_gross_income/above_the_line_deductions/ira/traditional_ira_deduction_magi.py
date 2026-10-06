from policyengine_us.model_api import *


class traditional_ira_deduction_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Traditional IRA deduction modified adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g_3_A",
        "https://www.irs.gov/publications/p590a#en_US_2025_publink1000256090",
    )

    adds = [
        "traditional_ira_deduction_magi_before_social_security",
        "taxable_social_security_before_ira_deduction",
    ]
