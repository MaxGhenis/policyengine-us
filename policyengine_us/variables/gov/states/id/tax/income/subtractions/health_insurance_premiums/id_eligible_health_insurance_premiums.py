from policyengine_us.model_api import *


class id_eligible_health_insurance_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho health insurance premiums not deducted elsewhere"
    unit = USD
    documentation = (
        "Health insurance premiums the tax unit paid for the taxpayer, spouse, "
        "and dependents, less premiums already deducted in arriving at federal "
        "adjusted gross income. Form 39R health insurance worksheet line 7 "
        "minus line 9."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022P/",
        # Form 39R line 18 instructions and worksheet lines 7 and 9
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=48",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=49",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Worksheet line 7: premiums paid for the taxpayer, spouse, and
        # dependents. This is the same premium aggregate the federal medical
        # expense deduction uses. It leaves out employer-paid premiums
        # (employer_sponsored_insurance_premiums), which the taxpayer did not
        # pay, and pre-tax payroll premiums (pre_tax_health_insurance_premiums),
        # which Form 39R excludes as paid through a salary-reduction
        # arrangement. Absent a direct health_insurance_premiums input, it
        # adds modeled Medicare Part B premiums net of Medicare Savings
        # Program coverage, which Form 39R allows.
        premiums = add(tax_unit, period, ["medical_expense_health_insurance_premiums"])
        # Worksheet line 9: premiums deducted elsewhere on the federal return,
        # i.e. the self-employed health insurance deduction.
        deducted_elsewhere = tax_unit("self_employed_health_insurance_ald", period)
        return max_(premiums - deducted_elsewhere, 0)
