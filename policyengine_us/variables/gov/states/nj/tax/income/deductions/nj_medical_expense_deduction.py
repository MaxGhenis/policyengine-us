from policyengine_us.model_api import *


class nj_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey medical expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # Worksheet F: medical expenses for the filer, spouse and dependents
        # above 2% of line 29, plus the filer's own self-employed health
        # insurance deduction.
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2024/1040i.pdf#page=25",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.deductions.medical_expenses
        # nj_agi leaves out tax unit dependents' income, so a dependent's own
        # self-employed health insurance deduction stays on their own return
        # too; self_employed_health_insurance_ald covers the head and spouse.
        self_employed_medical_expense_deduction = tax_unit(
            "self_employed_health_insurance_ald", period
        )
        medical_expenses = tax_unit("itemized_medical_expenses", period)
        agi = tax_unit("nj_agi", period)
        floor = p.rate * agi
        applicable_medical_expenses = max_(0, medical_expenses - floor)
        return self_employed_medical_expense_deduction + applicable_medical_expenses
