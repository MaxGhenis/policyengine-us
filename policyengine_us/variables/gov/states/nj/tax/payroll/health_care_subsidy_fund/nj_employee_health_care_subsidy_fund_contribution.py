from policyengine_us.model_api import *


class nj_employee_health_care_subsidy_fund_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee Health Care Subsidy Fund contribution"
    documentation = (
        "Employee contribution to the Health Care Subsidy Fund under N.J.S.A. "
        "43:21-7b, levied on unemployment insurance taxable wages until "
        "June 30, 2004."
    )
    reference = (
        "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf#page=70"
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        rate = parameters(
            period
        ).gov.states.nj.tax.payroll.health_care_subsidy_fund.employee_rate
        return rate * person("nj_taxable_earnings_for_state_unemployment_tax", period)
