from policyengine_us.model_api import *


class local_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local sales tax"
    unit = USD
    reference = (
        # State and Local General Sales Tax Deduction Worksheet.
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=4",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=4",
        # Worksheet line 3 instructions (California and Nevada).
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        state_code = tax_unit.household("state_code", period)
        state_code_str = tax_unit.household("state_code_str", period)
        # Line 4: the state rate in the state table heading. The California and
        # Nevada headings include their uniform local rates (table footnotes 3
        # and 5); Alaska and the states without a state table have 0.
        heading_rate = p.state_sales_tax_table.rate[state_code]
        # Line 3: the local rate, which is the part of the combined rate above
        # the heading rate. For California and Nevada that is "the part of the
        # combined rate that is more than" 7.25% or 6.85% (line 3 instructions);
        # a combined rate at or below the heading rate enters nothing. The
        # combined rate is stored in single precision, so subtract the heading
        # rate at the same precision: equal rates then leave exactly 0.
        combined_rate = tax_unit.household("combined_sales_tax_rate", period)
        local_rate = max_(combined_rate - heading_rate.astype(combined_rate.dtype), 0)
        # Line 2: the Optional Local Sales Tax Tables give the base local tax
        # for a 1% local rate, by the state table's income row and family size.
        table = tax_unit.household("local_sales_tax_table", period)
        TAX_UNIT_SIZE_CAP = 6
        tax_unit_size = tax_unit("tax_unit_size", period)
        family_size = max_(min_(tax_unit_size, TAX_UNIT_SIZE_CAP), 1).astype(int)
        income_bracket = max_(
            tax_unit("state_sales_tax_income_bracket", period), 1
        ).astype(int)
        base_local_tax = p.local_sales_tax_table.tax[table][family_size][
            income_bracket
        ]
        # Line 6, "No" (line 2 is not 0): line 2 x line 3, with line 3 in
        # percentage points.
        table_amount = base_local_tax * local_rate / 0.01
        # Line 6, "Yes": line 1 x line 5, where line 5 = line 3 / line 4.
        ratio = np.divide(
            local_rate,
            heading_rate,
            out=np.zeros_like(local_rate),
            where=heading_rate > 0,
        )
        ratio_amount = tax_unit("state_sales_tax", period) * ratio
        uses_local_table = np.isin(state_code_str, p.local_sales_tax_table.states)
        # Full-year residents of these jurisdictions "skip lines 2 through 5,
        # enter -0- on line 6" of the worksheet.
        has_local_sales_tax = ~np.isin(
            state_code_str, p.state_sales_tax_table.no_local_sales_tax_states
        )
        return has_local_sales_tax * where(
            uses_local_table, table_amount, ratio_amount
        )
