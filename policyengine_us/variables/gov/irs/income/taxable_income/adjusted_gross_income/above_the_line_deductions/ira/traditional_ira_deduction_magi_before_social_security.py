from policyengine_us.model_api import *


class traditional_ira_deduction_magi_before_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Traditional IRA deduction MAGI before Social Security"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/219#g_3_A"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross_income = tax_unit.sum(
            not_dependent * person("traditional_ira_deduction_gross_income", period)
        )
        deductions = [
            deduction
            for deduction in p.ald.deductions
            if deduction not in p.ald.ira.magi.excluded_deductions
        ]
        magi = gross_income - add(tax_unit, period, deductions)
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            magi += tax_unit("basic_income", period)
        return magi
