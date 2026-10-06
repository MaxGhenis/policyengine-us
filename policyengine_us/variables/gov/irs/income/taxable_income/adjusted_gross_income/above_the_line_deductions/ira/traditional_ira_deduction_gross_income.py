from policyengine_us.model_api import *


class traditional_ira_deduction_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income for the traditional IRA deduction modified AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g_3_A",
        # Topic E, Q1: IRA deduction MAGI uses unemployment compensation
        # unreduced by the 2020 exclusion.
        "https://www.irs.gov/newsroom/2020-unemployment-compensation-exclusion-faqs-topic-e-impact-to-income-credits-and-deductions",
    )
    documentation = (
        "Each person's positive gross income sources other than Social Security, "
        "counting unemployment compensation in full. Unlike irs_gross_income, "
        "this includes dependents' income, so it can approximate the modified "
        "AGI on a dependent's own return."
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        magi_sources = [
            source
            for source in sources
            if source
            not in ["taxable_social_security", "taxable_unemployment_compensation"]
        ]
        # IRS guidance on the 2020 section 85(c) exclusion: IRA deduction MAGI
        # includes unemployment compensation unreduced by the exclusion.
        if "taxable_unemployment_compensation" in sources:
            magi_sources.append("unemployment_compensation")
        total = 0
        for source in magi_sources:
            # Follow gross-income accounting: losses enter through loss_ald.
            total += max_(0, add(person, period, [source]))
        return total
