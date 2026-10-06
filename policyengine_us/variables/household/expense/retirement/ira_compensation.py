from policyengine_us.model_api import *


class ira_compensation(Variable):
    value_type = float
    entity = Person
    label = "Compensation for IRA contributions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#f_1",
        "https://www.law.cornell.edu/uscode/text/26/401#c_2",
        "https://www.irs.gov/publications/p590a#en_US_2025_publink1000230355",
    )

    def formula(person, period, parameters):
        earnings = add(
            person,
            period,
            [
                "self_employment_income",
                "sstb_self_employment_income",
                "farm_operations_income",
                "partnership_self_employment_net_earnings",
            ],
        )
        deductions = add(
            person,
            period,
            [
                "self_employment_tax_ald_person",
                "self_employed_pension_contribution_ald_person",
            ],
        )
        # Publication 590-A: a self-employment loss does not reduce wages.
        net_earnings = max_(0, earnings - deductions)
        return (
            person("irs_employment_income", period)
            + person("taxable_alimony_income", period)
            + net_earnings
        )
