from policyengine_us.model_api import *


class tax_unit_social_security_for_taxability(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit Social Security for taxability"
    unit = USD
    documentation = """
    The head's and spouse's Social Security benefits. A tax unit dependent's
    benefits are taxable, if at all, on the dependent's own return
    (dependent_taxable_social_security), so they are left out. A
    tax_unit_social_security amount supplied for the tax unit is not read.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86",
        "https://www.irs.gov/faqs/social-security-income",
        # IRS Pub. 915 (2025), "Who is taxed": benefits are taxable to the
        # person with the legal right to receive them.
        "https://www.irs.gov/pub/irs-prior/p915--2025.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        # Sum the head's and spouse's benefits directly. Taking dependents'
        # benefits out of the float32 tax unit total would let a large
        # dependent amount move the filers' amount through rounding.
        return max_(0, tax_unit_non_dep_add(tax_unit, period, ["social_security"]))
