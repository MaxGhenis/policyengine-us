from policyengine_us.model_api import *


class medicaid_adjusted_gross_income_person(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income for Medicaid MAGI household rules"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    def formula(person, period, parameters):
        gross_income = person("medicaid_irs_gross_income", period)
        # The head's and spouse's deductions are their own parts of their
        # return's deductions, so one spouse's IRA deduction, for example,
        # lowers only that spouse's AGI. A tax unit dependent's own deductions,
        # such as their IRA deduction, reduce the dependent's own AGI, since
        # the dependent's income is figured on the dependent's own return.
        agi = gross_income - person("above_the_line_deductions_person", period)

        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            filing_status = person.tax_unit("filing_status", period)
            frac = where(
                filing_status == filing_status.possible_values.JOINT,
                0.5,
                1.0,
            )
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            basic_income = person.tax_unit("basic_income", period)
            agi += head_or_spouse * basic_income * frac

        return agi
