from policyengine_us.model_api import *


class id_health_insurance_premiums_itemized_portion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho health insurance premiums deducted as itemized medical expenses"
    unit = USD
    documentation = (
        "Portion of the health insurance premiums otherwise eligible for the "
        "Idaho subtraction that is already deducted through the federal "
        "itemized medical expense deduction, which Idaho itemizers use. Form "
        "39R health insurance worksheet line 8, before the rule that "
        "non-itemizers enter zero."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022P/",
        # Form 39R health insurance worksheet line 8
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=49",
        # IRC 162(l)(3) keeps self-employed premiums off Schedule A
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Worksheet line 8 is the lesser of the premiums claimed on federal
        # Schedule A (line 1) and the medical expense deduction allowed after
        # the AGI floor (line 6), so itemized deductions apply to premiums
        # first. Under IRC 162(l)(3), premiums deducted as self-employed
        # health insurance are not also claimed on Schedule A, so line 1 is
        # the premiums not deducted elsewhere.
        premiums = tax_unit("id_eligible_health_insurance_premiums", period)
        medical_deduction = tax_unit("medical_expense_deduction", period)
        return min_(premiums, medical_deduction)
