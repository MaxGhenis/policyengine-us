"""Independent clean-main global-zero-parent-ID compatibility check.

Run from a dependency environment, for example:
    python .work/zero_id_differential.py --base .work/base --head .

The parent imports no PolicyEngine model. Exactly two fresh model processes run
sequentially, each with an explicit source PYTHONPATH. Twenty-four deterministic
random multi-household worlds cover explicit/synthesized marital units, omitted
tax-unit IDs, external claimants, cross-household tax units, family splits, and
legacy household-local person IDs. Each has omitted and explicit-zero parent-ID
variants. The current-main worker strips inputs for unsupported parent-ID
variables; every other input is identical. This is a bounded synthetic API
compatibility check, not a dataset or weighted microsimulation.

The generator derives from the saved r8 gen.py/zero_id_cases harness, copied here
to keep this check independent of absolute historical paths. No AST rewriting or
formula monkeypatching is used.
"""

import argparse
import copy
import importlib
import os
import pickle
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

Y = "2026"
STATES = ["CA", "OH", "NY", "TX", "MA"]
VARIABLES = [
    "is_parent",
    "is_mother",
    "is_father",
    "medicaid_is_tax_dependent",
    "medicaid_claimed_by_parent_in_tax_unit",
    "medicaid_tax_dependent_exception_other_than_spouse_or_child",
    "medicaid_tax_dependent_exception_living_with_both_parents",
    "medicaid_tax_dependent_exception_non_custodial_parent",
    "medicaid_uses_non_filer_rules",
    "medicaid_household_size",
    "medicaid_household_income",
    "ca_medicaid_household_pregnancies",
    "medicaid_income_level",
]
OPTIONS = [
    {},
    {"omit_marital": True},
    {"omit_tax_unit_ids": True},
    {"cross_hh_units": 0.4, "known_claims": 0.8},
    {"family_splits": 0.6, "is_parent_input": 0.3, "count_noise": 0.4},
    {"local_ids": True, "cross_hh_units": 0.4},
]


def world(seed, n=8, **opts):
    rng = np.random.default_rng(seed)
    ids = opts.get("ids", False)
    local_ids = opts.get("local_ids", False)
    people, hh, fam, mar, tus = {}, {}, {}, {}, {}
    pid_of = {}
    next_pid = [100 + int(rng.integers(0, 50))]
    all_units = []  # (unit name, tax_unit_id)
    persons_by_h = []
    for h in range(n):
        k_adults = int(rng.integers(1, 4))
        k_kids = int(rng.integers(0, 4))
        members = []
        ages = []
        for a in range(k_adults):
            members.append(f"h{h}a{a}")
            ages.append(int(rng.integers(18, 80)) + a * 0)  # may tie; roles explicit
        for c in range(k_kids):
            members.append(f"h{h}c{c}")
            ages.append(int(rng.integers(0, 22)))
        state = STATES[int(rng.integers(len(STATES)))]
        hh[f"H{h}"] = {"members": members, "state_code": {Y: state}}
        for i, (name, age) in enumerate(zip(members, ages)):
            if local_ids:
                pid = i + 1
            else:
                pid = next_pid[0]
                next_pid[0] += int(rng.integers(1, 4))
            pid_of[name] = pid
            female = bool(rng.integers(0, 2))
            people[name] = {
                "age": {Y: age},
                "person_id": {Y: pid},
                "is_female": {Y: female},
                "medicaid_magi_person": {
                    Y: float(rng.integers(0, 60_000 * 8)) / 8 if age >= 14 else 0.0
                },
                "medicaid_person_is_required_to_file": {Y: bool(rng.random() < 0.5)},
                "current_pregnancies": {
                    Y: int(female and 14 <= age <= 45 and rng.random() < 0.2)
                },
                "is_full_time_student": {
                    Y: bool(18 <= age <= 22 and rng.random() < 0.3)
                },
            }
        persons_by_h.append((members, ages))
    # parent links (true relationships) within households
    parents_of = {}
    for h, (members, ages) in enumerate(persons_by_h):
        for i, name in enumerate(members):
            cands = [
                j for j in range(len(members)) if ages[j] >= ages[i] + 14 and j != i
            ]
            k = int(rng.integers(0, min(2, len(cands)) + 1)) if cands else 0
            chosen = (
                [members[j] for j in rng.choice(cands, size=k, replace=False)]
                if k
                else []
            )
            parents_of[name] = chosen
    # own_children_in_household (count) consistent + noise
    # is_parent inputs apply to every person or none (partial inputs would
    # replace the formula with the default for everyone else).
    world_is_parent_input = bool(rng.random() < opts.get("is_parent_input", 0.05))
    for h, (members, ages) in enumerate(persons_by_h):
        for name in members:
            cnt = sum(name in parents_of[o] for o in members)
            if rng.random() < opts.get("count_noise", 0.1):
                cnt = int(rng.integers(0, 3))
            people[name]["own_children_in_household"] = {Y: cnt}
            if world_is_parent_input:
                people[name]["is_parent"] = {Y: bool(rng.integers(0, 2))}
    if ids:
        for name, ps in parents_of.items():
            rec = [pid_of[p] for p in ps]
            r = rng.random()
            if r < opts.get("absent", 0.2) and len(rec) < 2:
                rec.append(900 + int(rng.integers(0, 3)))  # absent parent id
            elif r < 0.25 and rec:
                rec = [rec[0], rec[0]]  # repeated slot
            if rng.random() < opts.get("drop", 0.1):
                rec = []
            rng.shuffle(rec)
            rec = (rec + [0, 0])[:2]
            people[name]["parent_1_id"] = {Y: rec[0]}
            people[name]["parent_2_id"] = {Y: rec[1]}
    # marital units, tax units, families
    unit_counter = [1]

    def new_unit(members, head, spouse, joint, extra):
        u = f"U{unit_counter[0]}"
        tid = 1000 + unit_counter[0] if not opts.get("omit_tax_unit_ids") else None
        unit_counter[0] += 1
        d = {"members": members, "tax_unit_is_filer": {Y: bool(rng.random() < 0.6)}}
        if tid is not None:
            d["tax_unit_id"] = {Y: tid}
        # Set for every unit: a partial input would replace the formula.
        d["filing_status"] = {Y: "JOINT" if joint else "SINGLE"}
        d.update(extra)
        tus[u] = d
        all_units.append((u, tid))
        for m in members:
            people[m]["is_tax_unit_head"] = {Y: m == head}
            people[m]["is_tax_unit_spouse"] = {Y: m == spouse}
        return u

    unit_of = {}
    pending_dependents = []
    for h, (members, ages) in enumerate(persons_by_h):
        adults = [m for m, a in zip(members, ages) if a >= 18]
        kids = [m for m, a in zip(members, ages) if a < 18]
        couple = None
        if len(adults) >= 2 and rng.random() < 0.5:
            # never marry a parent-child pair
            a0, a1 = adults[0], adults[1]
            if a0 not in parents_of[a1] and a1 not in parents_of[a0]:
                couple = (a0, a1)
                mar[f"M{h}"] = {"members": [a0, a1]}
        if couple and rng.random() < 0.7:
            u = new_unit([couple[0], couple[1]], couple[0], couple[1], True, {})
            unit_of[couple[0]] = unit_of[couple[1]] = u
        elif couple:
            flag = bool(rng.random() < 0.6)
            for c in couple:
                u = new_unit([c], c, None, False, {"cohabitating_spouses": {Y: flag}})
                unit_of[c] = u
        for a in adults:
            if a in unit_of:
                continue
            if rng.random() < 0.3 and unit_of:
                pending_dependents.append((a, h))  # adult dependent
            else:
                unit_of[a] = new_unit(
                    [a],
                    a,
                    None,
                    False,
                    {"cohabitating_spouses": {Y: bool(rng.random() < 0.1)}},
                )
        for kid in kids:
            pending_dependents.append((kid, h))
    # place dependents
    units_in_h = {}
    for name, u in unit_of.items():
        h = int(name[1:].split("a")[0].split("c")[0])
        units_in_h.setdefault(h, set()).add(u)
    for name, h in pending_dependents:
        local = sorted(units_in_h.get(h, []))
        r = rng.random()
        if local and r < 0.65:
            u = local[int(rng.integers(len(local)))]
        elif all_units and r < 0.65 + opts.get("cross_hh_units", 0.15):
            u = all_units[int(rng.integers(len(all_units)))][0]
        else:
            u = None
        if u is not None:
            tus[u]["members"].append(name)
            people[name]["is_tax_unit_head"] = {Y: False}
            people[name]["is_tax_unit_spouse"] = {Y: False}
            unit_of[name] = u
        else:
            # alone in own unit (headless minor or adult who files alone)
            adult = people[name]["age"][Y] >= 18
            u2 = new_unit([name], name if adult else None, None, False, {})
            if not adult:
                people[name]["is_tax_unit_head"] = {Y: False}
            unit_of[name] = u2
            if rng.random() < opts.get("known_claims", 0.5) and len(all_units) > 1:
                cu, ctid = all_units[int(rng.integers(len(all_units)))]
                if ctid is not None and cu != u2:
                    people[name]["medicaid_claiming_tax_unit_id"] = {Y: ctid}
                    people[name]["claimed_as_dependent_on_another_return"] = {Y: True}
                elif rng.random() < 0.3:
                    people[name]["claimed_as_dependent_on_another_return"] = {Y: True}
    # families: default household; sometimes split
    for h, (members, ages) in enumerate(persons_by_h):
        if rng.random() < opts.get("family_splits", 0.2) and len(members) > 1:
            cut = int(rng.integers(1, len(members)))
            fam[f"F{h}a"] = {"members": members[:cut]}
            fam[f"F{h}b"] = {"members": members[cut:]}
            # keep married couples together
            for mu in mar.values():
                a0, a1 = mu["members"]
                if (a0 in members[:cut]) != (a1 in members[:cut]):
                    fam[f"F{h}a"]["members"] = [
                        m for m in fam[f"F{h}a"]["members"] if m != a1
                    ]
                    fam[f"F{h}b"]["members"] = [
                        m for m in fam[f"F{h}b"]["members"] if m != a1
                    ]
                    tgt = f"F{h}a" if a0 in fam[f"F{h}a"]["members"] else f"F{h}b"
                    fam[tgt]["members"].append(a1)
            fam = {k: v for k, v in fam.items() if v["members"]}
        else:
            fam[f"F{h}"] = {"members": list(members)}
    for name in people:
        if not any(name in mu["members"] for mu in mar.values()):
            mar[f"S_{name}"] = {"members": [name]}
    sit = {
        "people": people,
        "households": hh,
        "families": fam,
        "tax_units": tus,
        "spm_units": {k: {"members": v["members"]} for k, v in hh.items()},
    }
    if not opts.get("omit_marital"):
        sit["marital_units"] = mar
    return sit


def cases_for(world_count, seed_base):
    cases = []
    for index in range(world_count):
        situation = world(
            seed_base + index, n=8, ids=False, **OPTIONS[index % len(OPTIONS)]
        )
        for explicit_zero in (False, True):
            variant = copy.deepcopy(situation)
            if explicit_zero:
                for person in variant["people"].values():
                    person["parent_1_id"] = {Y: 0}
                    person["parent_2_id"] = {Y: 0}
            cases.append(
                {
                    "name": f"world-{index:02d}-{'zero' if explicit_zero else 'omitted'}",
                    "situation": variant,
                    "year": int(Y),
                }
            )
    return cases


def worker(source, cases_path, output_path):
    # Imports happen only after the independent child process selects a source.
    started = time.perf_counter()
    import policyengine_us
    import policyengine_core
    from policyengine_us import Simulation
    from policyengine_us.system import system

    source = Path(source).resolve()
    imported = Path(policyengine_us.__file__).resolve()
    if not imported.is_relative_to(source):
        raise RuntimeError(f"Wrong model imported: {imported}; expected under {source}")
    system_module_path = Path(sys.modules["policyengine_us.system"].__file__).resolve()
    if not system_module_path.is_relative_to(source):
        raise RuntimeError(f"Wrong country system source: {system_module_path}")
    # Package import creates this pristine module-level system once per worker.
    # Reusing it avoids a redundant full country-model construction.
    modules = {}
    for variable in VARIABLES:
        definition = system.variables[variable]
        module_name = getattr(definition, "__module__", type(definition).__module__)
        module = importlib.import_module(module_name)
        module_path = Path(module.__file__).resolve()
        if not module_path.is_relative_to(source):
            raise RuntimeError(f"Wrong variable source for {variable}: {module_path}")
        modules[variable] = str(module_path)
    with Path(cases_path).open("rb") as stream:
        cases = pickle.load(stream)
    results = {}
    for case in cases:
        situation = copy.deepcopy(case["situation"])
        for person in situation["people"].values():
            for parent_id in ("parent_1_id", "parent_2_id"):
                if parent_id not in system.variables:
                    person.pop(parent_id, None)
        try:
            simulation = Simulation(tax_benefit_system=system, situation=situation)
        except Exception as error:
            results[case["name"]] = {
                "__build__": ("error", type(error).__name__, str(error))
            }
            continue
        values = {"__ids__": tuple(simulation.persons.ids)}
        for variable in VARIABLES:
            try:
                array = np.asarray(simulation.calculate(variable, case["year"]))
                values[variable] = (
                    "value",
                    array.dtype.str,
                    array.shape,
                    array.tobytes(order="C"),
                    array.tolist(),
                )
            except Exception as error:
                values[variable] = ("error", type(error).__name__, str(error))
        results[case["name"]] = values
    output = {
        "source": str(imported),
        "system_source": str(system_module_path),
        "core_source": policyengine_core.__file__,
        "variable_sources": modules,
        "elapsed_seconds": time.perf_counter() - started,
        "results": results,
    }
    with Path(output_path).open("wb") as stream:
        pickle.dump(output, stream)


def comparable(result):
    # Human-readable values are redundant with the exact dtype/shape/byte check.
    return result[:4] if result and result[0] == "value" else result


def compare(main, head, cases):
    arrays = errors = build_errors = 0
    differences = []
    for case in cases:
        name = case["name"]
        left, right = main["results"][name], head["results"][name]
        if "__build__" in left or "__build__" in right:
            if left == right:
                build_errors += 1
            else:
                differences.append((name, "__build__", left, right))
            continue
        if left["__ids__"] != right["__ids__"]:
            differences.append((name, "__ids__", left["__ids__"], right["__ids__"]))
        for variable in VARIABLES:
            a, b = left[variable], right[variable]
            if comparable(a) != comparable(b):
                differences.append((name, variable, a, b))
            elif a[0] == "value":
                arrays += 1
            else:
                errors += 1
    # Check explicit-zero and omitted inputs also agree within each source.
    for side, output in (("main", main), ("head", head)):
        results = output["results"]
        for index in range(len(cases) // 2):
            omitted = results[f"world-{index:02d}-omitted"]
            zero = results[f"world-{index:02d}-zero"]
            for variable in sorted(set(omitted) | set(zero)):
                a, b = omitted.get(variable), zero.get(variable)
                if variable == "__ids__":
                    equal = a == b
                else:
                    equal = comparable(a) == comparable(b)
                if not equal:
                    differences.append(
                        (f"{side}/world-{index:02d}/omitted-v-zero", variable, a, b)
                    )
    print(f"Cases: {len(cases)} ({len(cases) // 2} worlds; omitted + explicit zero)")
    print(f"Compared variables: {len(VARIABLES)}")
    print(f"Identical arrays (dtype/shape/bytes): {arrays}")
    print(f"Matched calculation errors: {errors}; matched build errors: {build_errors}")
    print(f"Differences: {len(differences)}")
    for name, variable, left, right in differences[:30]:
        print(f"DIFFERENCE {name} / {variable}")
        print(f"  main/omitted: {repr(left)[:1200]}")
        print(f"  head/zero: {repr(right)[:1200]}")
    if len(differences) > 30:
        print(f"  {len(differences) - 30} additional differences omitted")
    # An all-error run is not evidence that the model calculations agree.
    if arrays == 0:
        print("FAIL: no successful output arrays were compared")
        return 1
    return int(bool(differences))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path)
    parser.add_argument("--head", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "zero-id-results",
    )
    parser.add_argument("--worlds", type=int, default=24)
    parser.add_argument("--seed", type=int, default=10_000)
    parser.add_argument("--worker", nargs=3, metavar=("SOURCE", "CASES", "OUTPUT"))
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
        # worker() has closed its completed pickle. Avoid a costly collection of
        # the parameter tree at interpreter shutdown; the parent still waits for
        # this child to exit before starting the next independent source.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
    if args.base is None:
        parser.error("--base is required")
    if args.worlds < len(OPTIONS):
        parser.error(
            f"--worlds must be at least {len(OPTIONS)} to cover all option profiles"
        )
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = cases_for(args.worlds, args.seed)
    cases_path = output_dir / "cases.pkl"
    with cases_path.open("wb") as stream:
        pickle.dump(cases, stream)
    script = Path(__file__).resolve()
    outputs = {}
    for side, source in (("main", args.base.resolve()), ("head", args.head.resolve())):
        if not (source / "policyengine_us" / "__init__.py").is_file():
            parser.error(f"Missing model source at {source}")
        result_path = output_dir / f"{side}.pkl"
        env = dict(os.environ, PYTHONPATH=str(source))
        subprocess.run(
            [
                sys.executable,
                str(script),
                "--worker",
                str(source),
                str(cases_path),
                str(result_path),
            ],
            cwd=output_dir,
            env=env,
            check=True,
        )
        with result_path.open("rb") as stream:
            outputs[side] = pickle.load(stream)
        print(f"{side} model: {outputs[side]['source']}", flush=True)
        print(f"{side} country system: {outputs[side]['system_source']}", flush=True)
        print(f"{side} core: {outputs[side]['core_source']}", flush=True)
        print(
            f"{side} elapsed including model setup: {outputs[side]['elapsed_seconds']:.3f}s",
            flush=True,
        )
        for path in sorted(set(outputs[side]["variable_sources"].values())):
            print(f"{side} variable source: {path}", flush=True)
    return compare(outputs["main"], outputs["head"], cases)


if __name__ == "__main__":
    raise SystemExit(main())
