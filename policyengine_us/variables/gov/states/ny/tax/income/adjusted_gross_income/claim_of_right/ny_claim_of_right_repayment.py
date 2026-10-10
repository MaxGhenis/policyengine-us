from policyengine_us.model_api import *


class ny_claim_of_right_repayment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Repayment of claim of right income that New York taxed"
    unit = USD
    documentation = (
        "Total repaid this year by the head and spouse of income that was "
        "included in New York adjusted gross income for an earlier year "
        "under a claim of right."
    )
    definition_period = YEAR
    reference = (
        # N.Y. Tax Law 612(c)(45)(A)
        "https://legislation.nysenate.gov/pdf/laws/TAX612#page=23",
        # 2025 Form IT-225 instructions, S-141
        "https://www.tax.ny.gov/pdf/2025/inc/it225i_2025.pdf#page=19",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        repayment = person("claim_of_right_repayment", period)
        excluded = person("ny_claim_of_right_repayment_excluded_from_agi", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(max_(repayment - excluded, 0) * head_or_spouse)
