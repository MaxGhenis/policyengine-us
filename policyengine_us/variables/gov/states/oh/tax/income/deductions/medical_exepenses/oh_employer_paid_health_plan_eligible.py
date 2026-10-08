from policyengine_us.model_api import *


class oh_employer_paid_health_plan_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ohio filer eligible for an employer-paid health plan"
    documentation = (
        "Whether the head or spouse is eligible for a health plan through "
        "their employer for which the employer pays any portion of the cost. "
        "Premiums paid while eligible go on line 3 of the Ohio unreimbursed "
        "medical care expenses worksheet instead of line 1."
    )
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # (A)(10)(a)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet lines 1 and 3
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        # R.C. 5747.01(A)(10)(a): "any subsidized health plan maintained by any
        # employer of the taxpayer or of the taxpayer's spouse", where the
        # employer "pays any portion of the plan's cost". Only the head's and
        # spouse's employers count, so a dependent's own coverage does not.
        person = tax_unit.members
        category = person(
            "employer_contribution_to_health_insurance_premiums_category", period
        )
        levels = category.possible_values
        employer_pays = (
            (category == levels.SOME)
            | (category == levels.ALL)
            | (person("employer_sponsored_insurance_premiums", period) > 0)
        )
        # NOTE: Employer coverage, or an offer of it, counts as subsidized: the
        # contribution category defaults to NONE, which records no observation.
        eligible = (
            person("has_esi", period)
            | person("offered_aca_disqualifying_esi", period)
            | employer_pays
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.any(eligible & head_or_spouse)
