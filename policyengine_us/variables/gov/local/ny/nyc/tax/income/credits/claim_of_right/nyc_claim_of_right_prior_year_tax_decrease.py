from policyengine_us.model_api import *


class nyc_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "New York City prior-year resident tax decrease from excluding repaid "
        "claim of right income"
    )
    unit = USD
    documentation = (
        "New York City resident income tax reported for the earlier year or "
        "years, less the tax that would have been reported had the income "
        "repaid this year (claim_of_right_repayment) not been included "
        "(Form IT-257, line 9). The tax unit uses the sum for its head and "
        "spouse."
    )
    definition_period = YEAR
    reference = (
        # N.Y. Tax Law 1312(a) applies section 662 to the city tax
        "https://legislation.nysenate.gov/pdf/laws/TAX1312",
        # 2025 Form IT-257, lines 7 to 9
        "https://www.tax.ny.gov/pdf/2025/inc/it257_2025_fill_in.pdf",
        "https://www.tax.ny.gov/pdf/2025/inc/it257i_2025.pdf",
    )
    defined_for = StateCode.NY
