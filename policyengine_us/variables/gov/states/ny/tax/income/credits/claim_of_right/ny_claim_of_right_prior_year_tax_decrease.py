from policyengine_us.model_api import *


class ny_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "New York State prior-year tax decrease from excluding repaid claim of "
        "right income"
    )
    unit = USD
    documentation = (
        "New York State income tax reported for the earlier year or years, "
        "less the tax that would have been reported had the income repaid "
        "this year (claim_of_right_repayment) not been included in New York "
        "adjusted gross income (Form IT-257, line 6). The tax unit uses the "
        "sum for its head and spouse."
    )
    definition_period = YEAR
    reference = (
        # N.Y. Tax Law 662(a)(4)
        "https://legislation.nysenate.gov/pdf/laws/TAX662",
        # 2025 Form IT-257, lines 4 to 6
        "https://www.tax.ny.gov/pdf/2025/inc/it257_2025_fill_in.pdf",
        "https://www.tax.ny.gov/pdf/2025/inc/it257i_2025.pdf",
    )
    defined_for = StateCode.NY
