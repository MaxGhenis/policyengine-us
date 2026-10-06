from policyengine_us.model_api import *


class wi_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/a",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/d",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        income_tax_before = tax_unit("wi_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("wi_non_refundable_credits", period)
        standard_tax = max_(0, income_tax_before - nonrefundable_credits)
        p = parameters(
            period
        ).gov.states.wi.tax.income.subtractions.retirement_income.exclusion
        if not p.in_effect:
            return standard_tax

        # A return that claims the Schedule SB line 16 subtraction pays tax on
        # the reduced income and claims no credits (Wis. Stat. 71.05(6)(b)54m.d).
        claimed = tax_unit("wi_retirement_income_exclusion_claimed", period)
        exclusion_tax = tax_unit("wi_retirement_income_exclusion_tax", period)
        return where(claimed, exclusion_tax, standard_tax)
