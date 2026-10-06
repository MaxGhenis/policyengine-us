from policyengine_us.model_api import *


class ca_military_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "California military retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17132.9.",
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=60",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # R&TC 17132.9 (taxable years 2025 through 2029): exclude uniformed
        # services retirement pay up to the cap per return, when federal AGI
        # does not exceed the limit for the filing status. Survivor Benefit
        # Plan annuities have a separate cap under 17132.10 and are not part
        # of military_retirement_pay.
        p = parameters(period).gov.states.ca.tax.income.agi
        p = p.military_retirement_exclusion
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        pay = tax_unit.sum(person("military_retirement_pay", period) * head_or_spouse)
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        eligible = agi <= p.agi_limit[filing_status]
        return where(eligible, min_(pay, p.cap), 0)
