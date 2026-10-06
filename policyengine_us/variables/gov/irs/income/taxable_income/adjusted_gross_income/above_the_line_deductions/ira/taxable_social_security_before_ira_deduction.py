from policyengine_us.model_api import *


class taxable_social_security_before_ira_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable Social Security before the IRA deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86",
        "https://www.irs.gov/publications/p590a#en_US_2025_publink1000256090",
    )
    documentation = (
        "Publication 590-A Appendix B Worksheet 1 computes taxable benefits "
        "before the IRA deduction for use in the IRA phase-out. Final taxable "
        "benefits are calculated separately after the allowed IRA deduction."
    )

    def formula(tax_unit, period, parameters):
        irs = parameters(period).gov.irs
        p = irs.social_security.taxability
        magi = tax_unit("traditional_ira_deduction_magi_before_social_security", period)
        # Section 86 additionally disregards the territorial income exclusions.
        additional_exclusions = [
            deduction
            for deduction in irs.ald.deductions
            if deduction in p.income.revoked_deductions
            and deduction not in irs.ald.ira.magi.excluded_deductions
        ]
        # Do not mutate the cached IRA MAGI array when adding SS-only income.
        magi = magi + add(tax_unit, period, additional_exclusions)
        person = tax_unit.members
        magi = magi + tax_unit.sum(
            ~person("is_tax_unit_dependent", period)
            * person("tax_exempt_interest_income", period)
        )
        benefits = tax_unit("tax_unit_social_security_for_taxability", period)
        combined_income = magi + p.combined_income_ss_fraction * benefits
        status = tax_unit("filing_status", period)
        separate_cohabitating = (status == status.possible_values.SEPARATE) & tax_unit(
            "cohabitating_spouses", period
        )
        base = where(
            separate_cohabitating,
            p.threshold.base.separate_cohabitating,
            p.threshold.base.main[status],
        )
        adjusted_base = where(
            separate_cohabitating,
            p.threshold.adjusted_base.separate_cohabitating,
            p.threshold.adjusted_base.main[status],
        )
        first_tier = min_(
            p.rate.base.benefit_cap * benefits,
            p.rate.base.excess * max_(0, combined_income - base),
        )
        second_tier = min_(
            p.rate.additional.benefit_cap * benefits,
            p.rate.additional.excess * max_(0, combined_income - adjusted_base)
            + min_(first_tier, p.rate.additional.bracket * (adjusted_base - base)),
        )
        return where(combined_income <= adjusted_base, first_tier, second_tier)
