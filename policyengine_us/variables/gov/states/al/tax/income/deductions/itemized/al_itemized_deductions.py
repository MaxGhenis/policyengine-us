from policyengine_us.model_api import *


class al_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/",  # Code of Alabama Section 40-18-15
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1",  # 2022 Schedule A (Form 1040)
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1",  # 2021 Schedule A (Form 1040)
        # 2025 Form 40 Booklet, Schedule A line 6: "FICA tax ... withheld on
        # your income" and "the Federal self-employment tax you paid".
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=19",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        # Payroll and self-employment taxes are deductible on the return that
        # reports the wages and earnings they were paid on, so a tax unit
        # dependent's stay on the dependent's own return, as their income
        # does in al_agi. Real estate taxes are summed over every member, as
        # in the federal itemized deductions.
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            p.sources,
            include_dependents=["real_estate_taxes"],
        )
