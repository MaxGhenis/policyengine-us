from policyengine_us.model_api import *


class nj_employee_unemployment_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee unemployment insurance contribution"
    documentation = (
        "Employee unemployment insurance contribution under N.J.S.A. "
        "43:21-7(d)(1)(D), including the unemployment compensation "
        "administration fund contribution."
    )
    reference = (
        "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf#page=60",
        "https://pub.njleg.state.nj.us/Bills/2024/AL24/101_.HTM",
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.nj.tax.payroll.unemployment.employee_rate
        return rate * person("nj_taxable_earnings_for_state_unemployment_tax", period)
