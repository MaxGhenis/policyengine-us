from policyengine_us.model_api import *


class ny_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/613"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        itemized = tax_unit("ny_itemized_deductions", period)
        standard = tax_unit("ny_standard_deduction", period)
        # A filer who subtracts a repayment that the itemized deduction
        # would include takes the standard deduction (Tax Law 612(c)(45)(B)).
        standard_only = tax_unit("ny_claim_of_right_subtraction_bars_itemizing", period)
        return where(standard_only, standard, max_(itemized, standard))
