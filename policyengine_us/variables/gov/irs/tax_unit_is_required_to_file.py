from policyengine_us.model_api import *

# Gross income sources that are earned income, which the unearned income test
# leaves out.
EARNED_GROSS_INCOME_SOURCES = [
    "irs_employment_income",
    "self_employment_income",
    "sstb_self_employment_income",
]


class tax_unit_is_required_to_file(Variable):
    value_type = bool
    entity = TaxUnit
    label = "required to file federal taxes"
    documentation = """
    Whether this tax unit is legally required to file a federal income tax
    return under IRC § 6012, based on gross income thresholds and filing
    status. Only the head's and spouse's income counts: a tax unit
    dependent's income is on the dependent's own return, as in
    irs_gross_income, and the dependent's own filing requirement is separate.
    The unearned income test applies only to a head or spouse who can be
    claimed as a dependent on another return.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/6012#a_1",
        "https://www.law.cornell.edu/uscode/text/26/6012#f",
        "https://www.law.cornell.edu/uscode/text/26/63#c_5",
        # 2025 Form 1040 instructions, Charts A and B.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=9",
    )

    def formula(tax_unit, period, parameters):
        # irs_gross_income is zero for tax unit dependents.
        gross_income = add(tax_unit, period, ["irs_gross_income"])
        p = parameters(period).gov.irs
        exemption = p.income.exemption
        exemption_amount = 0 if exemption.suspended else exemption.amount

        # (a)(1)(A), (a)(1)(B)
        filing_status = tax_unit("filing_status", period).decode_to_str()
        separate = filing_status == "SEPARATE"
        standard_deduction = tax_unit("standard_deduction", period)
        threshold = where(
            separate,
            exemption_amount,
            standard_deduction + exemption_amount,
        )

        income_over_exemption_amount = gross_income > threshold

        # (a)(1)(C)(i)(I): an individual described in IRC 63(c)(5), one whom
        # another taxpayer can claim as a dependent, must also file if their
        # own income other than earned income exceeds the 63(c)(5)(A) amount
        # plus their additional standard deduction (Chart B of the Form 1040
        # instructions). It does not apply to other filers (Chart A). For
        # 2018 through 2025, IRC 6012(f)(2)(D) compares a dependent filing
        # jointly against the 63(c)(5)(A) amount alone; that case is not
        # distinguished here.
        person = tax_unit.members
        sources = p.gross_income.sources
        earned_gross_income = sum(
            max_(0, person(source, period))
            for source in EARNED_GROSS_INCOME_SOURCES
            if source in sources
        )
        unearned_income = person("irs_gross_income", period) - earned_gross_income
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        head_unearned_income = tax_unit.sum(is_head * unearned_income)
        spouse_unearned_income = tax_unit.sum(is_spouse * unearned_income)

        standard = p.deductions.standard
        additional_amount = standard.aged_or_blind.amount[
            tax_unit("filing_status", period)
        ]
        head_additional = additional_amount * (
            tax_unit("aged_head", period).astype(int)
            + tax_unit("blind_head", period).astype(int)
        )
        spouse_additional = additional_amount * (
            tax_unit("aged_spouse", period).astype(int)
            + tax_unit("blind_spouse", period).astype(int)
        )
        head_unearned_income_over_threshold = tax_unit(
            "head_is_dependent_elsewhere", period
        ) & (head_unearned_income > standard.dependent.amount + head_additional)
        spouse_unearned_income_over_threshold = tax_unit(
            "spouse_is_dependent_elsewhere", period
        ) & (spouse_unearned_income > standard.dependent.amount + spouse_additional)

        return (
            income_over_exemption_amount
            | head_unearned_income_over_threshold
            | spouse_unearned_income_over_threshold
        )
