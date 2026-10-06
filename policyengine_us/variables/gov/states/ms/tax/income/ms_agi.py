from policyengine_us.model_api import *


class ms_agi(Variable):
    value_type = float
    entity = Person
    label = "Mississippi adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100221.pdf#page=14",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80105228.pdf",  # Line 66
        # Form 80-100 (2025): a minor files their own return (page 4); a
        # return has only a Taxpayer column and a Spouse column (page 5).
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=4",
        # 35 Miss. Admin. Code Pt. III, R. 2.08.100: a child's income is the
        # child's, not the parent's.
        "https://www.law.cornell.edu/regulations/mississippi/35-Miss-Code-R-SS-3-02-08-100",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.tax.income
        gross_income = add(person, period, p.income_sources)
        adjustments = person("ms_agi_adjustments", period)
        net_income = max_(gross_income - adjustments, 0)
        # A dependent's income goes on the dependent's own return.
        is_dependent = person("is_tax_unit_dependent", period)
        return ~is_dependent * net_income
