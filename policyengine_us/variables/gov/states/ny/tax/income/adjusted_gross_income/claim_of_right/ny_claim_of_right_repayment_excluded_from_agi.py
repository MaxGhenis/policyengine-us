from policyengine_us.model_api import *


class ny_claim_of_right_repayment_excluded_from_agi(Variable):
    value_type = float
    entity = Person
    label = (
        "Claim of right repayment not included in New York adjusted gross "
        "income when received"
    )
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that was not included in New York "
        "adjusted gross income for the earlier year, such as repaid Social "
        "Security benefits or government pension income that New York "
        "subtracts."
    )
    definition_period = YEAR
    reference = (
        # N.Y. Tax Law 612(c)(45)(A)
        "https://legislation.nysenate.gov/pdf/laws/TAX612#page=23",
    )
    defined_for = StateCode.NY
