from policyengine_us.model_api import *


class oh_uniformed_services_retirement_income_deduction(Variable):
    value_type = float
    entity = Person
    label = "Ohio Uniformed services retirement income"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=4",
        # R.C. 5747.01(A)(23): deduct retired personnel pay for service in the
        # uniformed services, to the extent included in federal AGI.
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        # 2025 IT 1040 instructions, Schedule of Adjustments line 34.
        "https://dam.assets.ohio.gov/image/upload/v1735920104/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=24",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # Military retirement pay is part of taxable_pension_income and so of
        # federal AGI, which (A)(23) requires.
        return person("military_retirement_pay", period)
