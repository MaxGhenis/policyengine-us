from policyengine_us.model_api import *


class nj_employee_workforce_fund_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee workforce fund contribution"
    documentation = (
        "Combined employee Workforce Development Partnership Fund and "
        "Supplemental Workforce Fund for Basic Skills contributions under "
        "N.J.S.A. 34:15D-13 and 34:15D-22."
    )
    reference = (
        "https://pub.njleg.state.nj.us/Bills/2000/PL01/152_.HTM",
        "https://www.nj.gov/labor/ea/employer-services/rate-info/",
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.nj.tax.payroll.workforce.employee_rate
        return rate * person("nj_taxable_earnings_for_state_unemployment_tax", period)
