from policyengine_us.model_api import *


class id_health_insurance_premiums_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho health insurance premiums subtraction"
    unit = USD
    documentation = (
        "Idaho subtraction for health insurance premiums paid for the "
        "taxpayer, spouse, and dependents that are not otherwise deducted or "
        "accounted for. Form 39R line 18 (health insurance worksheet line 10). "
        "Long-term care insurance premiums (Form 39R line 19) and Idaho "
        "medical savings account payments are not modeled."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022P/",
        # Tax year 2025 Form 39R line 18 instructions and worksheet
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=48",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=49",
        # Tax year 2021 Form 39R line 18 instructions and worksheet
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=35",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=36",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Worksheet line 10 = line 7 - line 8 - line 9. Line 8 is zero for
        # filers who take the Idaho standard deduction: they "don't have to
        # reduce [their] health insurance costs by any amount claimed as a
        # federal itemized deduction."
        premiums = tax_unit("id_eligible_health_insurance_premiums", period)
        itemized_portion = tax_unit(
            "id_health_insurance_premiums_itemized_portion", period
        )
        itemizes = tax_unit("id_tax_unit_itemizes", period)
        return max_(premiums - where(itemizes, itemized_portion, 0), 0)
