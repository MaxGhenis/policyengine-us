from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    tax_at_main_rates,
)


class income_tax_main_rates_on_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax at the main rates on all taxable income"
    documentation = (
        "The tax on all taxable income at the main rates, as if section 1(h) "
        "did not apply. Section 1(h)(1) limits the regular tax to the smaller "
        "of this amount and the sum of the amounts section 1(h) taxes. For a "
        "taxpayer excluding foreign earned income, the tax on taxable income "
        "plus the excluded amount less the tax on the excluded amount alone "
        "(26 U.S.C. 911(f)(1)(A))."
    )
    unit = USD
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(1)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_1",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Schedule D Tax Worksheet, lines 46 and 47",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=16",
        ),
        dict(
            title="2025 Form 1040 instructions, Qualified Dividends and Capital Gain Tax Worksheet, lines 24 and 25",
            href="https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=38",
        ),
    ]

    def formula(tax_unit, period, parameters):
        # Schedule D Tax Worksheet line 46: "Figure the tax on the amount on
        # line 1". A taxpayer excluding foreign earned income enters line 3
        # of the Foreign Earned Income Tax Worksheet on line 1.
        taxable_income = tax_unit("taxable_income_plus_section_911_exclusion", period)
        bracket = parameters(period).gov.irs.income.bracket
        filing_status = tax_unit("filing_status", period)
        tax = tax_at_main_rates(max_(0, taxable_income), filing_status, bracket)
        # As in income_tax_main_rates: less the tax on the excluded amount
        # alone (Foreign Earned Income Tax Worksheet, lines 5 and 6).
        excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
        tax_on_excluded = tax_at_main_rates(excluded, filing_status, bracket)
        return where(excluded > 0, max_(0, tax - tax_on_excluded), tax)
