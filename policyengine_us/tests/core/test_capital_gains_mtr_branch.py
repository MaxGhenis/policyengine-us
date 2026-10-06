"""The capital gains marginal tax rate equals a rerun with $1,000 more gain.

marginal_tax_rate_on_capital_gains raises each ranked adult's gain in a branch
of the simulation: it deletes the computed arrays, stores the higher gain with
set_input and recomputes household net income. The branch used to raise
person-level capital_gains, which only AGI reads. The 26 USC 1(h) rates, the
NIIT base and the EITC investment income test read long-term gains, so the
rate was an ordinary-income rate that missed the NIIT and the EITC cliff at
the 26 USC 32(i) investment income limit.

The YAML cases in tests/policy/baseline/gov/simulation pin household values.
A YAML case cannot compare two simulations, so this test checks the branch
machinery against an independent path. For each adult rank k
(adult_index_cg), a second simulation is built from the same situation with
the gain input, long_term_capital_gains_before_response, of each rank-k adult
raised by 1,000. Over a seeded population that straddles the EITC investment
income limit, the 1(h) rate breakpoints and the NIIT threshold:

1. For every rank-k adult, the rate equals
   1 - (rerun household net income - household net income) / 1,000.
2. Everyone else gets zero.
3. Computing the rate leaves the simulation's own values unchanged and
   removes its branches.

The population is checked to reach the EITC cliff, the 15% and 20% bands and
the NIIT, so the first property is not met vacuously.
"""

import copy

import numpy as np

from policyengine_us import Simulation

YEAR = 2025
DELTA = 1_000
SEED = 20261006
# Household net income is float32; a 1e-3 rate error is 1 dollar on 1,000.
RATE_TOLERANCE = 1e-3
EITC_INVESTMENT_INCOME_LIMIT = 11_950
STATES = ["TX", "CA", "NY", "MA"]
# Values computed before the rate, compared after it.
UNCHANGED = [
    "long_term_capital_gains",
    "capital_gains",
    "adjusted_gross_income",
    "eitc_relevant_investment_income",
    "eitc",
    "net_investment_income_tax",
    "household_net_income",
]


def _household(rng, kind):
    """One household: (people, whether joint, state)."""
    if kind == "cliff":
        # A head of household whose interest and gain put investment income
        # within 1,000 below the limit, so 1,000 more gain crosses it.
        investment_income = EITC_INVESTMENT_INCOME_LIMIT - rng.uniform(1, 999)
        gain = round(rng.uniform(100, 2_000))
        head = {
            "age": 30,
            "employment_income": round(rng.uniform(5_000, 30_000)),
            "taxable_interest_income": round(investment_income - gain),
            "long_term_capital_gains_before_response": gain,
        }
        children = [{"age": 8}] * int(rng.integers(1, 3))
        return [head] + children, False, "TX"
    if kind == "single":
        head = {
            "age": 45,
            "employment_income": round(rng.uniform(0, 700_000)),
            "long_term_capital_gains_before_response": round(rng.uniform(0, 300_000)),
            "short_term_capital_gains": round(rng.uniform(-20_000, 20_000)),
        }
        return [head], False, STATES[int(rng.integers(len(STATES)))]
    if kind == "joint":
        # Spouses with different gains, so each gets its own rank.
        head = {
            "age": 50,
            "employment_income": round(rng.uniform(0, 400_000)),
            "long_term_capital_gains_before_response": round(
                rng.uniform(50_000, 250_000)
            ),
        }
        spouse = {
            "age": 50,
            "long_term_capital_gains_before_response": round(rng.uniform(0, 40_000)),
            "taxable_interest_income": round(rng.uniform(0, 20_000)),
        }
        return [head, spouse], True, STATES[int(rng.integers(len(STATES)))]
    # A net loss beyond the 1211(b) limit, which the extra gain only shrinks.
    head = {
        "age": 60,
        "employment_income": round(rng.uniform(20_000, 150_000)),
        "long_term_capital_gains_before_response": -round(rng.uniform(5_000, 30_000)),
    }
    return [head], False, "TX"


# Fixed households that the properties must cover, all in TX: the 15% band
# (single, wages 100,000, gain 10,000), the 15% band with NIIT (wages 250,000,
# gain 50,000) and the 20% band with NIIT (wages 600,000, gain 100,000).
FIXED = [
    (
        [
            {
                "age": 40,
                "employment_income": w,
                "long_term_capital_gains_before_response": g,
            }
        ],
        False,
        "TX",
    )
    for w, g in [(100_000, 10_000), (250_000, 50_000), (600_000, 100_000)]
]


def _situation(households):
    situation = {
        "people": {},
        "tax_units": {},
        "families": {},
        "spm_units": {},
        "marital_units": {},
        "households": {},
    }
    for h, (people, joint, state) in enumerate(households):
        names = []
        for i, inputs in enumerate(people):
            name = f"h{h}p{i}"
            names.append(name)
            person = {key: {YEAR: value} for key, value in inputs.items()}
            if inputs["age"] < 18:
                person["is_tax_unit_dependent"] = {YEAR: True}
                situation["marital_units"][f"{name}mu"] = {"members": [name]}
            situation["people"][name] = person
        filers = names[:2] if joint else names[:1]
        situation["marital_units"][f"h{h}mu"] = {"members": filers}
        situation["tax_units"][f"h{h}tu"] = {"members": names}
        situation["families"][f"h{h}f"] = {"members": names}
        situation["spm_units"][f"h{h}s"] = {"members": names}
        situation["households"][f"h{h}"] = {
            "members": names,
            "state_code": {YEAR: state},
        }
    return situation


def _population():
    rng = np.random.default_rng(SEED)
    kinds = ["cliff"] * 12 + ["single"] * 12 + ["joint"] * 8 + ["loss"] * 4
    return FIXED + [_household(rng, kind) for kind in kinds]


def _household_net_income(simulation):
    # Each person's household net income, as the rate's formula reads it.
    return np.asarray(simulation.person.household("household_net_income", YEAR))


def test_capital_gains_mtr_equals_a_rerun_with_more_long_term_gain():
    situation = _situation(_population())
    simulation = Simulation(situation=situation)
    before = {name: simulation.calculate(name, YEAR).copy() for name in UNCHANGED}
    rank = np.asarray(simulation.calculate("adult_index_cg", YEAR))
    base_income = _household_net_income(simulation)

    rate = np.asarray(simulation.calculate("marginal_tax_rate_on_capital_gains", YEAR))

    # Property 3: the branches leave the simulation as it was.
    for name in UNCHANGED:
        np.testing.assert_array_equal(simulation.calculate(name, YEAR), before[name])
    assert not any(name.endswith("_cg_rise") for name in simulation.branches)

    names = list(situation["people"])
    reference = np.zeros_like(rate)
    for k in (1, 2):
        mask = rank == k
        rerun_situation = copy.deepcopy(situation)
        for name in np.array(names)[mask]:
            gain = rerun_situation["people"][name].setdefault(
                "long_term_capital_gains_before_response", {YEAR: 0}
            )
            gain[YEAR] += DELTA
        rerun_income = _household_net_income(Simulation(situation=rerun_situation))
        reference[mask] = 1 - (rerun_income[mask] - base_income[mask]) / DELTA

    # Properties 1 and 2.
    ranked = (rank == 1) | (rank == 2)
    np.testing.assert_allclose(rate[ranked], reference[ranked], atol=RATE_TOLERANCE)
    np.testing.assert_array_equal(rate[~ranked], 0)

    # The population reaches each case the rate must get right.
    eitc_lost = rate[ranked] > 1
    assert eitc_lost.sum() >= 10
    fixed = rate[: len(FIXED)]
    np.testing.assert_allclose(fixed, [0.15, 0.188, 0.238], atol=RATE_TOLERANCE)
