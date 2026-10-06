from policyengine_us.model_api import *


class wi_earned_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin earned income credit (WI EITC)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=26"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=26"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        potential = tax_unit("wi_earned_income_credit_potential", period)
        # Wis. Stat. 71.05(6)(b)54m.d bars s. 71.07 credits on a return that
        # claims the Schedule SB line 16 retirement income subtraction.
        claimed = tax_unit("wi_retirement_income_exclusion_claimed", period)
        return where(claimed, 0, potential)
