from policyengine_us.model_api import *


class id_tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the tax unit itemizes deductions for Idaho"
    documentation = (
        "Idaho filers use federal itemized deductions or the standard "
        "deduction, whichever benefits them more, and must itemize if married "
        "filing separately with a spouse who itemizes. Itemizing also reduces "
        "the Idaho health insurance premiums subtraction by the premiums "
        "deducted as itemized medical expenses, so the comparison nets that "
        "loss against the itemized deductions."
    )
    definition_period = YEAR
    reference = (
        # Form 40 lines 13-16: "whichever benefits you more" and "You must
        # itemize if" (tax years 2025 and 2021)
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=10",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=9",
        # Form 39R health insurance worksheet: non-itemizers enter zero on line 8
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=49",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        itemized = tax_unit("id_itemized_deductions", period)
        standard = tax_unit("standard_deduction", period)
        # Premium subtraction given up by itemizing (worksheet line 8).
        premium_subtraction_lost = tax_unit(
            "id_health_insurance_premiums_itemized_portion", period
        )
        # Itemizing lowers Idaho taxable income only if the itemized
        # deductions exceed the standard deduction by more than the premium
        # subtraction lost. Ties keep the standard deduction.
        itemizing_benefits = itemized - premium_subtraction_lost > standard
        must_itemize = tax_unit("separate_filer_itemizes", period)
        return must_itemize | itemizing_benefits
