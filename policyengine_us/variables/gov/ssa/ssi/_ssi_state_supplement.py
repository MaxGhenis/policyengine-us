from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_living_arrangement_amount import (
    ssi_living_arrangement_amount,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


def ssi_deemed_state_supplement(
    person, period, parameters, individual_rate, couple_rate
):
    """State supplement of an individual whose ineligible spouse's income is deemed.

    POMS SI 01320.430 D computes the state supplement separately on an
    individual basis (the individual rate less the person's own countable
    income above the individual federal amount) and on a couple basis (the
    couple rate, or the individual rate where higher (D.2), less the combined
    countable income above the federal couple amount), and pays the lesser.
    Rates are monthly state supplements excluding federal SSI; couple_rate is
    the couple's total. 20 CFR 416.1163(d)(2)(iii) points to 416.2025(b).
    """
    countable = person("ssi_countable_income", period)
    federal_amount = person("ssi_amount_if_eligible", period)
    excess = max_(countable - federal_amount, 0)
    deemed = person("ssi_income_deemed_from_ineligible_spouse", period)
    own_income = max_(countable - deemed, 0)
    own_federal_amount = ssi_living_arrangement_amount(
        person, period, parameters, parameters(period).gov.ssa.ssi.amount.individual
    )
    own_payment = max_(individual_rate - max_(own_income - own_federal_amount, 0), 0)
    deemed_payment = max_(max_(couple_rate, individual_rate) - excess, 0)
    return min_(own_payment, deemed_payment)


def ssi_state_supplement(
    person, period, parameters, individual_rate, couple_rate, federal_payment_rules=True
):
    """Apply SSI-based supplement income, couple and spouse-deeming rules.

    Rates are state supplements, excluding federal SSI. Each member supplies
    the same-category couple rate; averaging these rates implements mixed
    arrangements where the state's published schedule supports that method.
    Set federal_payment_rules only for SSA-administered payments; state
    administrators do not inherit the federal rounding or minimum payment.
    Sources: 20 CFR 416.2025; POMS SI 01320.430 D, SI 02005.030 G,
    SI 02001.005 and SI 02001.010. Callers apply state-specific eligibility.
    """
    joint = person("ssi_couple_computation_applies", period)
    couple_total = _ssi_couple_total(person, period.this_year, couple_rate / 2)
    standard = where(joint, couple_total / 2, individual_rate)
    countable = person("ssi_countable_income", period)
    federal_amount = person("ssi_amount_if_eligible", period)
    excess = max_(countable - federal_amount, 0)
    payment = max_(standard - excess, 0)

    deeming = person("is_ssi_spousal_deeming_applies", period.this_year)
    # SI 01320.430 D.2: use the higher individual rate where it exceeds
    # the couple rate (including New Jersey's ineligible-spouse variation).
    deemed_payment = ssi_deemed_state_supplement(
        person, period, parameters, individual_rate, couple_rate
    )
    payment = where(deeming, deemed_payment, payment)
    ssi = parameters(period).gov.ssa.ssi

    eligible = person("is_ssi_eligible", period) & person(
        "takes_up_ssi_if_eligible", period.this_year
    )
    # Federal administration discards digits beyond the third decimal place,
    # rounds up to cents, and pays at least one dollar for a positive amount.
    rounded = np.ceil(np.floor(payment * 1_000) / 10) / 100
    federal_payment = where(
        rounded > 0, max_(rounded, ssi.state_supplement.minimum_payment), 0
    )
    return eligible * where(federal_payment_rules, federal_payment, payment)
