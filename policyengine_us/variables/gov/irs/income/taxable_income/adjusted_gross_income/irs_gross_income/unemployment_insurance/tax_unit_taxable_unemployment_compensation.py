from policyengine_us.model_api import *


class tax_unit_taxable_unemployment_compensation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable unemployment compensation"
    unit = USD
    documentation = """
    Unemployment compensation included in AGI: the head's and spouse's
    compensation, less the 2020 exclusion. A tax unit dependent's
    compensation is on the dependent's own return, as in irs_gross_income.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/85",
        # 2020 Form 1040 instructions, Unemployment Compensation Exclusion
        # Worksheet (Schedule 1, line 8).
        "https://www.irs.gov/pub/irs-prior/i1040gi--2020.pdf#page=88",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.unemployment_compensation.exemption
        person = tax_unit.members
        uc = person("unemployment_compensation", period)
        filer = ~person("is_tax_unit_dependent", period)
        uc_amount = tax_unit.sum(filer * uc)
        # IRC 85(c)(1): for 2020, if modified AGI is less than $150,000,
        # exclude up to $10,200 of the compensation paid to the taxpayer, or
        # on a joint return up to $10,200 paid to each spouse (worksheet
        # lines 8 to 10). Modified AGI leaves out the compensation itself
        # (IRC 85(c)(2)(B); worksheet lines 1 to 6), as taxable_uc_agi does.
        modified_agi = tax_unit("taxable_uc_agi", period)
        filing_status = tax_unit("filing_status", period)
        uc_excludable = tax_unit.sum(filer * min_(max_(0, uc), p.amount))
        uc_excluded = where(
            modified_agi < p.cutoff[filing_status],
            uc_excludable,
            0,
        )
        return uc_amount - uc_excluded
