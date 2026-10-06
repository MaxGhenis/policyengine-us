from policyengine_us.model_api import *


class ar_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas itemized deductions when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR3_ItemizedDeduction.pdf",
        # Form AR3 instructions, lines 31-35 (prorated itemized deductions)
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=22",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Arkansas does not tie itemization choice to federal choice.
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized.sources
        unit_deds = add(person.tax_unit, period, p.individual)
        person_agi = person("ar_agi_indiv", period)
        total_agi = person.tax_unit.sum(person_agi)

        prorate = np.zeros_like(total_agi)
        mask = total_agi > 0
        prorate[mask] = person_agi[mask] / total_agi[mask]

        # Round prorate to the nearest percent and then divide by 100
        prorate = np.round(prorate * 100) / 100

        # Form AR3 lines 31-33 prorate between the spouses' AGIs (lines 25A
        # and 25B). Dependents' AR AGI is zero (their income is on their own
        # return), so they get no share.
        return unit_deds * prorate
