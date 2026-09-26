from policyengine_us.model_api import *


class LocalSalesTaxTable(Enum):
    A = "Local Table A"
    B = "Local Table B"
    C = "Local Table C"
    D = "Local Table D"


class local_sales_tax_table(Variable):
    value_type = Enum
    possible_values = LocalSalesTaxTable
    default_value = LocalSalesTaxTable.A
    entity = Household
    definition_period = YEAR
    label = "IRS Optional Local Sales Tax Table"
    documentation = (
        "The IRS Optional Local Sales Tax Table for the household's locality, from "
        "the IRS table selector. Defaults to the table for the state's other "
        "localities that impose a local sales tax."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=17",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=17",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=16",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=18",
    )

    def formula(household, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.local_sales_tax_table.default_table
        state_code = household("state_code_str", period)
        return select(
            [
                np.isin(state_code, p.a),
                np.isin(state_code, p.b),
                np.isin(state_code, p.c),
                np.isin(state_code, p.d),
            ],
            [
                LocalSalesTaxTable.A,
                LocalSalesTaxTable.B,
                LocalSalesTaxTable.C,
                LocalSalesTaxTable.D,
            ],
            default=LocalSalesTaxTable.A,
        )
