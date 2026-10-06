from policyengine_us.model_api import *


class ca_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California charitable contribution deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17201.",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17024.5.",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17250.1.",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17250.2.",
        "https://www.ftb.ca.gov/forms/2020/2020-540-ca-instructions.html",
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
    )

    def formula(tax_unit, period, parameters):
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash_donations = add(tax_unit, period, ["charitable_non_cash_donations"])
        non_cash_to_non_50_pct = add(
            tax_unit, period, ["charitable_non_cash_donations_non_50_pct_orgs"]
        )
        non_cash_to_50_pct = non_cash_donations - non_cash_to_non_50_pct
        # R&TC 17024.5(h)(2)(A) uses federal AGI for percentage limits.
        positive_agi = tax_unit("positive_agi", period)
        p = parameters(period).gov.irs.deductions.itemized.charity.ceiling
        ca = parameters(period).gov.states.ca.tax.income.deductions.itemized.charity

        # Retain the federal model's non-cash categories. Separate capital-gain
        # property limits and basis-reduction elections are not modeled.
        capped_non_cash_50 = min_(non_cash_to_50_pct, p.non_cash * positive_agi)
        capped_non_cash_non_50 = min_(
            non_cash_to_non_50_pct, p.non_cash_to_non_50_pct_org * positive_agi
        )
        # California retains its 50% ceiling without the federal 0.5% floor.
        # This amount includes all cash gifts. The federal 2020-2021
        # deduction for non-itemizers postdates the January 1, 2015 specified
        # date, and the 2020 Schedule CA (540) instructions (line 11) allow
        # those gifts in California only as itemized deductions. From 2025,
        # R&TC 17250.2 disapplies the IRC 170(p) non-itemizer deduction.
        return min_(
            cash_donations + capped_non_cash_50 + capped_non_cash_non_50,
            ca.ceiling * positive_agi,
        )
