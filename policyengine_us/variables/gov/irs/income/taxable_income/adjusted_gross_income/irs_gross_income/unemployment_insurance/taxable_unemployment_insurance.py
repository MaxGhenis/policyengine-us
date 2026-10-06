from policyengine_us.model_api import *


class taxable_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "Taxable unemployment compensation"
    unit = USD
    documentation = """
    Unemployment compensation included in gross income on the return that
    carries it. The head and spouse each have their own compensation less
    their own 2020 exclusion, which sums to the tax unit's taxable
    compensation. A tax unit dependent's compensation is on the dependent's
    own return, where the 2020 exclusion depends on the dependent's own
    modified AGI.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/85",
        # 2020 Form 1040 instructions, Unemployment Compensation Exclusion
        # Worksheet (Schedule 1, line 8).
        "https://www.irs.gov/pub/irs-prior/i1040gi--2020.pdf#page=88",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.unemployment_compensation.exemption
        uc = person("unemployment_compensation", period)
        excludable = min_(max_(0, uc), p.amount)
        tax_unit = person.tax_unit
        filer = ~person("is_tax_unit_dependent", period)

        # The taxable amount is decided at the tax unit level, but gross income
        # is person-level, so per-person AGI must reflect the actual recipient
        # (required by states with combined-return optimization). The 2020
        # exclusion applies to each spouse's own compensation (IRC 85(c)(1)),
        # so each keeps their own compensation less their own exclusion.
        filing_status = tax_unit("filing_status", period)
        eligible = tax_unit("taxable_uc_agi", period) < p.cutoff[filing_status]
        filer_own = uc - where(eligible, excludable, 0)
        amount = tax_unit("tax_unit_taxable_unemployment_compensation", period)
        filers_own = tax_unit.sum(filer * filer_own)
        # A tax unit amount that differs, as when it is an input, is shared in
        # proportion to the head's and spouse's compensation, and nothing is
        # shared when their compensation is not positive in total. The amount
        # is stored in float32, so compare in its precision.
        filer_uc = tax_unit.sum(filer * uc)
        matches = (amount == filers_own.astype(amount.dtype)) & (filer_uc > 0)
        share = np.divide(
            uc,
            filer_uc,
            out=np.zeros_like(filer_uc, dtype=float),
            where=filer_uc > 0,
        )
        filer_amount = where(matches, filer_own, amount * share)

        # A dependent's own exclusion. Their modified AGI is their AGI after
        # IRC 86 and without the compensation, figured from the IRC 86(b)(2)
        # modified AGI on their own return, which includes the compensation
        # and tax-exempt interest and leaves out taxable Social Security. The
        # $150,000 cutoff is the same for every filing status.
        dependent_modified_agi = (
            person("dependent_taxable_ss_magi", period)
            - max_(0, uc)
            - person("tax_exempt_interest_income", period)
            + person("dependent_taxable_social_security", period)
        )
        dependent_eligible = dependent_modified_agi < p.cutoff["SINGLE"]
        dependent_amount = uc - where(dependent_eligible, excludable, 0)
        return where(filer, filer_amount, dependent_amount)
