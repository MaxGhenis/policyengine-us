#!/usr/bin/env bash
# Run in the tested checkout. WIP_ROOT points at the evidence checkout.
set -uo pipefail
TASK=${1:?task required}
WIP_ROOT=${WIP_ROOT:-$GITHUB_WORKSPACE/wip}
EVID=${EVID:-$WIP_ROOT/.wip-9676-evidence}
PYTHON=${PYTHON:-$WIP_ROOT/.venv/bin/python}
CORE_TEST=${CORE_TEST:-$WIP_ROOT/.venv/bin/policyengine-core}
L=$GITHUB_WORKSPACE/logs/$TASK
mkdir -p "$L"
M=policyengine_us/tests/policy/baseline/gov/states/mo/dss/tanf/mo_tanf_is_assistance_unit_member.yaml
P=policyengine_us/tests/core/test_mo_tanf_dependent_parent_properties.py
Q=policyengine_us/tests/core/test_mo_tanf_non_parent_caretaker_properties.py
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
bad=0
run() {
    local name=$1 expected=$2
    shift 2
    printf 'RUN %s (expected exit %s)\n' "$name" "$expected"
    /usr/bin/time -v -o "$L/$name.time" "$@" >"$L/$name.log" 2>&1
    local rc=$?
    printf '%s actual=%s expected=%s\n' "$name" "$rc" "$expected" | tee -a "$L/summary.txt"
    tail -n 12 "$L/$name.log"
    if [ "$rc" -ne "$expected" ]; then bad=1; fi
}
run runtime_identity 0 "$PYTHON" "$EVID/validate_runtime.py" "$L/runtime.json"
case "$TASK" in
  suites)
    # This targeted folder validates the resumed member YAML on the exact CI
    # model hash and covers adjacent TANF formulas; no full MO-state sweep.
    run mo_tanf_yaml 0 "$PYTHON" policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/gov/states/mo/dss/tanf --mode per-file --workers 1
    run property_suites 0 "$PYTHON" -m pytest -q -rf -p no:cacheprovider "$P" "$Q"
    run explicit_source_roles 0 "$PYTHON" "$EVID/source_role_checks.py"
    run input_definitions 0 "$PYTHON" -m pytest -q -rf -p no:cacheprovider policyengine_us/tests/core/test_input_variable_definitions.py
    run partner_contracts 0 "$PYTHON" policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/partners --mode per-file --workers 1
    run household_checks 0 "$PYTHON" "$EVID/household_checks.py" branch "$L/household_branch.json"
    run known_resource_defect 0 "$PYTHON" "$EVID/assertion_yaml.py" "$EVID/fixture_a_resource.yaml" --results "$L/known_resource_defect.json"
    ;;
  mutations)
    run new_member_mutations 0 "$PYTHON" "$EVID/mutate.py" none drop_has_dependent_child --yaml "$M" --expect '{"none":0,"drop_has_dependent_child":1}' --results "$L/new_member_mutations.json"
    run old_member_mutations 0 "$PYTHON" "$EVID/mutate.py" none drop_has_dependent_child --yaml "$EVID/old_head_member.yaml" --expect '{"none":0,"drop_has_dependent_child":0}' --results "$L/old_member_mutations.json"
    run new_property_mutations 0 "$PYTHON" "$EVID/mutate.py" none drop_has_dependent_child npcr_never --py "$P" --expect '{"none":0,"drop_has_dependent_child":1,"npcr_never":1}' --results "$L/new_property_mutations.json"
    run old_property_mutations 0 "$PYTHON" "$EVID/mutate.py" none drop_has_dependent_child npcr_never --py "$EVID/old_head_test_mo_tanf_dependent_parent_properties.py" --expect '{"none":0,"drop_has_dependent_child":0,"npcr_never":0}' --results "$L/old_property_mutations.json"
    ;;
  main)
    run main_new_member_yaml 0 "$PYTHON" "$EVID/assertion_yaml.py" "$WIP_ROOT/$M" --results "$L/main_new_member_failures.json"
    run main_household_checks 0 "$PYTHON" "$EVID/household_checks.py" main "$L/household_main.json"
    run main_known_resource_defect 0 "$PYTHON" "$EVID/assertion_yaml.py" "$EVID/fixture_a_resource.yaml" --results "$L/main_known_resource_defect.json"
    ;;
  old_head)
    # Membership implementation is intentionally retained. The new cases pass
    # old head; mutation failures above demonstrate the added coverage.
    run old_head_new_member_yaml 0 "$CORE_TEST" test "$WIP_ROOT/$M" -c policyengine_us
    run old_head_household_checks 0 "$PYTHON" "$EVID/household_checks.py" old_head "$L/household_old_head.json"
    ;;
  *) printf 'Unknown task: %s\n' "$TASK" >&2; exit 2 ;;
esac
printf 'Unexpected result flag: %s\n' "$bad" | tee -a "$L/summary.txt"
exit "$bad"
