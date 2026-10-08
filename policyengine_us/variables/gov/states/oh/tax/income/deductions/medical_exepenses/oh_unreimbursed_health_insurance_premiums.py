from policyengine_us.model_api import *


class oh_unreimbursed_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Ohio unreimbursed health insurance premiums"
    unit = USD
    documentation = (
        "Dental, vision and health insurance premiums the person paid that "
        "were not excluded or deducted in computing federal adjusted gross "
        "income. Lines 1 and 3 of the Ohio unreimbursed medical care expenses "
        "worksheet split this amount."
    )
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # (A)(10)(a)-(b)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # Line 44
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # R.C. 5747.01(A)(10)(a) and (b) count premiums only to the extent not
        # otherwise excluded or deducted in computing federal AGI: premiums
        # paid through pre-tax payroll deductions are excluded from wages, and
        # worksheet line 1 is reduced by the federal self-employed health
        # insurance deduction.
        premiums = person("medical_expense_health_insurance_premiums", period)
        # NOTE: Pre-tax payroll premiums are treated as part of the reported
        # premiums, not in addition to them.
        pre_tax = person("pre_tax_health_insurance_premiums", period)
        self_employed_deduction = person(
            "self_employed_health_insurance_ald_person", period
        )
        return max_(premiums - pre_tax - self_employed_deduction, 0)
