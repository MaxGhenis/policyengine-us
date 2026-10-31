from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


def _ssi_established_spouse_indices(person, period, first, second):
    """Rows of each person's co-resident spouse, or -1.

    SSI resource deeming uses this one test for a claimant's spouse
    (416.1202(a)), a parent's spouse (416.1202(b)) and whether a child is
    married (416.1856). A marital unit holds an unmarried person or a married,
    cohabiting couple, so the members of a two-person marital unit who live in
    the same household are spouses. So are the head and spouse of one tax
    unit who share a marital unit, which covers situations that omit marital
    units (those put everyone in one unit). Parent links that name one as the
    other's parent always rule a pair out. When the simulation has a single
    marital unit, which may be that default group, a pair is also ruled out
    when exactly one of them is a dependent of the tax unit they share (no
    one can claim a spouse), so a default unit never pairs a parent with the
    child they claim. Explicit marital units otherwise stand, whatever tax
    roles the model infers. Ambiguous candidates resolve to no spouse.
    Known limitation: a simulation holding only a married couple in which
    one spouse is the other's tax dependent (as the model infers for a
    married minor when tax roles are omitted) cannot be told apart from a
    default group, so that couple is not treated as married; supply tax roles
    that do not make a spouse a dependent.
    """
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    dependent = person("is_tax_unit_dependent", period)
    joint = head_or_spouse & person.tax_unit("tax_unit_married", period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    couple = person.marital_unit.nb_persons() == 2
    marital_unit = person.marital_unit.reference_entity.members_entity_id
    possible_default = person.marital_unit.count == 1
    own_index = np.arange(person.count)
    spouse = np.full(person.count, -1, dtype=int)
    candidates = np.zeros(person.count, dtype=int)
    household = person.household
    for position in range(
        int(np.max(household.reference_entity.members_position, initial=-1)) + 1
    ):
        member = household.value_nth_person(position, own_index, default=-1)
        safe = np.maximum(member, 0)
        names_applicant = (first[safe] == own_index) | (second[safe] == own_index)
        named_by_applicant = (first == member) | (second == member)
        same_tax_unit = tax_unit[safe] == tax_unit
        # One claims the other when exactly one of them is a dependent of
        # the tax unit they share; two dependents can be a married couple.
        claims = possible_default & same_tax_unit & (dependent != dependent[safe])
        same_marital_unit = marital_unit[safe] == marital_unit
        shown = (
            (member >= 0)
            & (member != own_index)
            & same_marital_unit
            & (couple | (joint & head_or_spouse[safe] & same_tax_unit))
            & ~claims
            & ~names_applicant
            & ~named_by_applicant
        )
        spouse = np.where(shown, member, spouse)
        candidates += shown
    return np.where(candidates == 1, spouse, -1)


def _ssi_spouse_index(person, period):
    """The row of each person's co-resident spouse, or -1."""
    first, second = co_resident_parent_indices(person, period)
    return _ssi_established_spouse_indices(person, period, first, second)


def _ssi_eligible_apart_from_means(person, period):
    """Aged, blind or disabled and meeting SSI's citizenship condition.

    416.1160(d) makes an ineligible spouse one who 'is not eligible for SSI
    benefits'. The resource test runs before eligibility is known, so this
    tests the conditions that do not depend on it: aged, blind or disabled
    status, and citizenship or qualified-noncitizen status (as is_ssi_eligible
    requires).
    """
    immigration_status = person("immigration_status", period)
    is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
    return person("is_ssi_aged_blind_disabled", period) & (
        is_citizen | person("is_ssi_qualified_noncitizen", period)
    )


def _ssi_resource_couple(person, period):
    """Whether 416.1205(b) combines a joint claim's resources.

    A joint claim pairs two aged, blind or disabled spouses. When one of them
    fails the citizenship condition, they are not an eligible couple
    (416.1801(c)), so the other's resources are tested with the spouse's
    deemed under 416.1202(a), with the ineligible-spouse exclusions.
    """
    eligible = _ssi_eligible_apart_from_means(person, period)
    spouse = np.maximum(_ssi_spouse_index(person, period), 0)
    return person("ssi_claim_is_joint", period) & eligible & eligible[spouse]


def _ssi_spouse_value(person, period, values, default=0):
    """The co-resident spouse's value, or ``default`` without a spouse.

    Programs that follow SSI's financial responsibility rules combine a
    married couple living together (416.1801, 416.1806, 42 CFR 435.602). A
    marital unit can hold more than the couple, as the default unit of a
    situation that omits marital units does, so they read the spouse through
    _ssi_spouse_index rather than summing the unit. ``period`` is the year of
    the spouse test.
    """
    spouse = _ssi_spouse_index(person, period)
    return where(spouse >= 0, values[np.maximum(spouse, 0)], default)


def _ssi_couple_total(person, period, values):
    """Each person's value plus their co-resident spouse's, if they have one.

    For a marital unit of two whose members _ssi_spouse_index pairs, and for
    a person alone, this equals the marital-unit sum. It adds only the spouse
    when a unit holds more people. It differs from the unit sum for a
    two-person unit that _ssi_spouse_index does not pair: spouses in
    different households (416.1806), a pair whose parent links name one as
    the other's parent, and the documented case of a simulation holding only
    a married couple in which one spouse is the other's tax dependent.
    """
    return values + _ssi_spouse_value(person, period, values)


def _ssi_both_spouses(person, period, condition):
    """Whether a person and their co-resident spouse both meet ``condition``.

    False for a person without a spouse.
    """
    return condition & _ssi_spouse_value(person, period, condition, False)
