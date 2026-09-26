from policyengine_us.model_api import *


class eitc_relevant_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC-relevant investment income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#i_2",
        "https://www.irs.gov/pub/irs-prior/p596--2021.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        # Publication 596 Worksheet 1 keeps portfolio income, net capital
        # gains, and net passive income in separate baskets. A loss in one
        # basket cannot offset positive income in another.
        # The worksheet is filled in from the filer's own return, so each
        # basket sums only the head and spouse, as eitc_earned_income does.
        # A dependent's income enters the parent's worksheet only through a
        # Form 8814 election, which the model does not include.
        portfolio_income = sum(
            tax_unit_non_dep_sum(source, tax_unit, period)
            for source in [
                "taxable_interest_income",
                "tax_exempt_interest_income",
                "dividend_income",
            ]
        )
        capital_gains = sum(
            tax_unit_non_dep_sum(source, tax_unit, period)
            for source in [
                "long_term_capital_gains",
                "short_term_capital_gains",
                "non_sch_d_capital_gains",
            ]
        )
        # IRC 32(i)(2)(E) and the Worksheet 1 instructions for lines 11 and
        # 12 leave out passive income or loss that is also earned income.
        # A general partner who does not materially participate has a
        # distributive share that is both passive and net earnings from
        # self-employment. The part of the passive amount matched by
        # partnership self-employment earnings of the same sign, up to the
        # smaller magnitude, is treated as earned.
        person = tax_unit.members
        passive = person("passive_partnership_s_corp_income", period)
        se_earnings = person("partnership_self_employment_net_earnings", period)
        passive_also_earned = where(
            passive >= 0,
            min_(passive, max_(se_earnings, 0)),
            max_(passive, min_(se_earnings, 0)),
        )
        is_filer = ~person("is_tax_unit_dependent", period)
        # The model's undifferentiated rental input is treated as passive
        # rental income, consistently with its NIIT income mapping. Farm
        # rental income is reported on Form 4835, which is used only for a
        # rental activity under the passive activity rules; its Schedule E
        # line 40 total is named on Worksheet 1 lines 11 and 12, so it is
        # treated as passive in the same way. Net the passive amounts across
        # the filers before applying the zero floor.
        passive_income = (
            tax_unit_non_dep_sum("rental_income", tax_unit, period)
            + tax_unit_non_dep_sum("farm_rent_income", tax_unit, period)
            + tax_unit.sum(is_filer * (passive - passive_also_earned))
        )
        return portfolio_income + max_(0, capital_gains) + max_(0, passive_income)
