from policyengine_us.model_api import *


class ny_claim_of_right_subtraction_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Subtracts a claim of right repayment from New York adjusted gross income"
    documentation = (
        "Whether the filer subtracts repaid claim of right income from New "
        "York adjusted gross income (Tax Law 612(c)(45), Form IT-225 "
        "modification S-141). The subtraction is not allowed with the "
        "section 662 credit for the same repayment, or when the repayment "
        "is included in the New York itemized deduction, so the filer "
        "chooses. The model takes whichever gives less New York State, New "
        "York City and Yonkers income tax; when they are equal the filer "
        "does not subtract."
    )
    definition_period = YEAR
    reference = (
        "https://legislation.nysenate.gov/pdf/laws/TAX612#page=23",
        # 2025 Form IT-225 instructions, S-141
        "https://www.tax.ny.gov/pdf/2025/inc/it225i_2025.pdf#page=19",
        # 2025 Form IT-257 instructions: itemized deduction or subtraction,
        # but not both
        "https://www.tax.ny.gov/pdf/2025/inc/it257i_2025.pdf",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.agi.subtractions
        nobody = np.zeros(tax_unit.count, dtype=bool)
        if not p.claim_of_right.in_effect:
            return nobody
        has_repayment = tax_unit("ny_claim_of_right_repayment", period) > 0
        if not has_repayment.any():
            # Comparing the two choices takes two more tax computations;
            # skip them when no New York filer repaid anything.
            return nobody
        tax_if_subtracting = tax_unit(
            "ny_income_tax_if_subtracting_claim_of_right_repayment", period
        )
        tax_if_not_subtracting = tax_unit(
            "ny_income_tax_if_not_subtracting_claim_of_right_repayment", period
        )
        # The tolerance keeps floating-point noise from deciding a tie.
        TOLERANCE = 0.01
        return has_repayment & (tax_if_subtracting < tax_if_not_subtracting - TOLERANCE)
