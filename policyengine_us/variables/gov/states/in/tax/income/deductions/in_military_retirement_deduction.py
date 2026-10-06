from policyengine_us.model_api import *


class in_military_retirement_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana military retirement deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/indiana/title-6/article-3/chapter-2/section-6-3-2-4",  # (a)(2)
        "https://www.in.gov/dor/files/ib06.pdf#page=2",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        # IC 6-3-2-4(a)(2): the lesser of the military retirement benefits
        # included in AGI and the base amount plus a share of the benefits
        # above it (25% in 2019 rising to 100% from 2022). Survivor's benefits
        # also qualify but are not part of military_retirement_pay.
        p = parameters(period).gov.states["in"].tax.income.deductions
        p = p.military_retirement
        person = tax_unit.members
        benefits = person("military_retirement_pay", period)
        allowed = p.base + p.excess_rate * max_(benefits - p.base, 0)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(min_(benefits, allowed) * head_or_spouse)
