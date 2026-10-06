from policyengine_us.model_api import *


class wi_retirement_income_exclusion_line17_offset(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin retirement income subtraction lost when claiming the exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=8",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.subtractions.retirement_income
        if not p.exclusion.in_effect:
            return 0

        person = tax_unit.members
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        retirement_income = max_(0, add(person, period, p.sources)) * head_or_spouse
        line17_eligible = age >= p.min_age
        line16_eligible = (age >= p.exclusion.min_age) & head_or_spouse

        # Schedule SB line 17 worksheet subtracts line 16 before applying
        # the $5,000 cap separately to each spouse's remaining income.
        person_line16 = min_(p.exclusion.max_amount.single, retirement_income)
        person_line16 *= line16_eligible
        remaining_income = max_(0, retirement_income - person_line16)
        remaining_line17 = tax_unit.sum(
            min_(p.max_amount, remaining_income) * line17_eligible
        )

        # Both age-eligible spouses share the $48,000 line 16 cap. Allocate
        # that subtraction against income above each spouse's line 17 cap
        # first, preserving the largest permitted combined subtraction.
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        both_eligible = tax_unit.sum(line16_eligible) >= 2
        line16 = tax_unit("wi_retirement_income_exclusion_amount", period)
        line17 = tax_unit("wi_retirement_income_subtraction", period)
        pooled_remaining = max_(0, tax_unit.sum(retirement_income) - line16)
        remaining_line17 = where(
            joint & both_eligible,
            pooled_remaining,
            remaining_line17,
        )
        return max_(0, line17 - remaining_line17)
