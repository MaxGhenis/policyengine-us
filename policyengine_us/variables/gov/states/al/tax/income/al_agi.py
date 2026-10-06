from policyengine_us.model_api import *


class al_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama adjusted gross income"
    documentation = (
        "Alabama adjusted gross income of the head and spouse. A tax unit "
        "dependent who meets the filing requirement files their own Alabama "
        "return, so the dependent's income and adjustments are left out of "
        "the filers' return."
    )
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    reference = (
        # The Code of Alabama 1975
        "https://alison.legislature.state.al.us/code-of-alabama",
        # Ala. Code § 40-18-27(a): every taxpayer over the filing threshold
        # files a return stating the taxpayer's items of gross income.
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-27",
        # 2025 Form 40 Booklet, "Dependent's and Student's Income": dependents
        # who meet the filing requirement must file their own return.
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.agi
        # Person-level income and adjustments are summed over the head and
        # spouse only; tax-unit-level adjustments already describe this return.
        gross_income = tax_unit_non_dep_add(tax_unit, period, p.gross_income_sources)
        deductions = tax_unit_non_dep_add(tax_unit, period, p.deductions)
        return gross_income - deductions
