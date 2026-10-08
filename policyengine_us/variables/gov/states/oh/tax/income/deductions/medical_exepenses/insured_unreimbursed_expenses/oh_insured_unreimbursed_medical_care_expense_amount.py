from policyengine_us.model_api import *


class oh_insured_unreimbursed_medical_care_expense_amount(Variable):
    value_type = float
    entity = Person
    label = "Ohio insured unreimbursed medical and health care expense amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)(b)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # Line 44
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet lines 3 to 5
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # Line 3: premiums paid while "eligible for Medicare or an
        # employer-paid health care plan through your or your spouse's
        # employer". Line 1 takes the rest.
        medicare_eligible = person("is_medicare_eligible", period)
        employer_plan_eligible = person.tax_unit(
            "oh_employer_paid_health_plan_eligible", period
        )
        premiums = person("oh_unreimbursed_health_insurance_premiums", period)
        line_3 = premiums * (medicare_eligible | employer_plan_eligible)
        # Line 4: medical care other than insurance premiums.
        line_4 = person("other_medical_expenses", period)
        return line_3 + line_4
