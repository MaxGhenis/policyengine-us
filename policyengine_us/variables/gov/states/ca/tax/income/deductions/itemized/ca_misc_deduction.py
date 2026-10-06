from policyengine_us.model_api import *


class ca_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California miscellaneous itemized deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17076.",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17024.5.",
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca.pdf#page=6",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
    )

    def formula(tax_unit, period, parameters):
        # Schedule CA (540), Part II, lines 19 through 25. R&TC 17076(a)
        # applies the IRC 67 two percent floor. The IRC 67(g) suspension
        # does not reach California: for 2018 through 2024 the IRC as of the
        # January 1, 2015 specified date (R&TC 17024.5(a)(1)(P)) predates it,
        # and from 2025 R&TC 17076(c) says it does not apply.
        # R&TC 17024.5(h)(2)(A) bases the floor on federal AGI (line 23).
        p = parameters(period).gov.states.ca.tax.income.deductions.itemized.misc
        floor = parameters(period).gov.irs.deductions.itemized.misc.floor
        # Line 22.
        expenses = add(tax_unit, period, p.sources)
        # Line 24.
        misc_floor = floor * tax_unit("positive_agi", period)
        # Line 25.
        return max_(0, expenses - misc_floor)
