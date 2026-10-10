from policyengine_us.model_api import *


class ny_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York State claim of right credit"
    unit = USD
    documentation = (
        "When 26 U.S.C. 1341(a)(5) applies to the repaid income for federal "
        "tax, New York State tax is reduced by the decrease in the earlier "
        "year's New York tax from excluding that income, and any excess over "
        "the year's tax is refunded (Tax Law 662, Form IT-257). There is no "
        "credit under the federal deduction method, or when the filer "
        "subtracts the repayment from New York adjusted gross income "
        "instead (Tax Law 612(c)(45)(B))."
    )
    definition_period = YEAR
    reference = (
        "https://legislation.nysenate.gov/pdf/laws/TAX662",
        # 2025 Form IT-257, line 6, and instructions
        "https://www.tax.ny.gov/pdf/2025/inc/it257_2025_fill_in.pdf",
        "https://www.tax.ny.gov/pdf/2025/inc/it257i_2025.pdf",
        # 2025 Form IT-201-ATT, line 15
        "https://www.tax.ny.gov/pdf/2025/inc/it201att_2025_fill_in.pdf#page=2",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        subtracts = tax_unit("ny_claim_of_right_subtraction", period) > 0
        person = tax_unit.members
        decrease = person("ny_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(credit_applies & ~subtracts, prior_year_tax_decrease, 0)
