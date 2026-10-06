from policyengine_us.model_api import *


class nj_taxable_earnings_for_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "New Jersey taxable earnings for state unemployment tax"
    documentation = (
        "Earnings subject to New Jersey employee and employer unemployment "
        "insurance contributions and employee Health Care Subsidy Fund and "
        "workforce fund contributions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        return min_(
            max_(0, person("employment_income", period)),
            parameters(period).gov.states.nj.tax.payroll.unemployment.taxable_wage_base,
        )
