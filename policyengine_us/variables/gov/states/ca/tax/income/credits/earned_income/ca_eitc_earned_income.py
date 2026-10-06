from policyengine_us.model_api import *


class ca_eitc_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "California earned income for the CalEITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.",
        "https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.html",
        "https://edd.ca.gov/siteassets/files/pdf_pub_ctr/de231eb.pdf",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income
        wages = person("employment_income", period)
        excluded_wages = min_(
            max_(0, wages), add(person, period, p.pre_tax_contributions)
        )
        # FTB 3514 line 13 uses W-2 box 16. California retains payroll HSA
        # contributions in these wages. Subtract only California exclusions
        # before flooring earnings, including when self-employment has losses.
        earnings = max_(0, person("adjusted_earnings", period) - excluded_wages)
        is_filer = not_(person("is_tax_unit_dependent", period))
        return tax_unit.sum(earnings * is_filer)
