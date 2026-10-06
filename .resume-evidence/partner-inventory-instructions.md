# Partner inventory runner for US #9621

Prepared only; no country model or partner test has been run by this agent.

`partner_inventory.py` reads contract fixtures and records their current model
outputs. It never edits a partner file and never accepts new expectations.
The archived 43 raw-head failures remain separate historical evidence; the new
published California anchors can produce a different, broader inventory.

The generator uses core's `YamlFile.collect()` and `YamlItem.runtest()` without
reimplementing input preprocessing. Inline parameter reforms, named reforms,
extensions, entity construction, default periods, nested entity outputs,
output-specific periods, and enum comparisons therefore follow the installed
core test runner. It intercepts only `assert_near` to record the original
comparison result and continue to later outputs. It also records individual
calculation errors and fixture/build errors.

Each model invocation accepts exactly one existing partner YAML file. This
does not exempt a coordinated multi-file inventory from the machine-wide heavy
lock. A single pytest/Python file processing multiple fixture files is still a
multi-file workload. Run in the foreground at nice 0, with no background jobs.
The root agent owns scheduling and must follow the current host rule.

From the assigned workspace, set `task_python` to the interpreter root has
selected. Always include the assigned workspace first on `PYTHONPATH`; the
generator also checks that `policyengine_us` was imported from this checkout.

```bash
task_python=/Users/maxghenis/.subfleet/worktrees/20261006-083854-hub-fix-9621/.venv/bin/python
task_model_label='9621 resumed build, published CA 2026 anchors; REPLACE WITH ACTUAL HEAD AND DIRTY-STATE NOTE'
```

Discover the complete requested-year inventory without constructing a model:

```bash
PYTHONPATH="$PWD" "$task_python" .resume-evidence/partner_inventory.py list-files \
  --year 2026 > .resume-evidence/partner-2026-files.txt
```

A separately scheduled, targeted invocation for one file:

```bash
PYTHONPATH="$PWD" "$task_python" .resume-evidence/partner_inventory.py run \
  --file policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/renter_credit.yaml \
  --year 2026 \
  --model-label "$task_model_label"
```

For a coordinated batch, hold the shared lock for the entire foreground loop.
Use a dedicated output directory per model build so evidence from different
models cannot accidentally be combined. The label below is an example; root
must fill in the real model label and interpreter. All files, including partners
outside California, are required to claim that the final inventory is complete.

```bash
~/reviews/us-hub/scripts/heavy_run.sh 9621-partner-inventory \
  env PYTHONPATH="$PWD" TASK_PYTHON="$task_python" TASK_MODEL_LABEL="$task_model_label" \
  bash -c '
    inventory_status=0
    while IFS= read -r partner_file; do
      "$TASK_PYTHON" .resume-evidence/partner_inventory.py run \
        --file "$partner_file" --year 2026 --model-label "$TASK_MODEL_LABEL" \
        --output-dir .resume-evidence/partner-inventory-final || inventory_status=2
    done < .resume-evidence/partner-2026-files.txt
    exit "$inventory_status"
  '
```

There is no automatic retry or overwrite of existing evidence. A partially
completed invocation writes its results after every case. After interruption,
retain those files and choose a fresh output directory for a repeat run, or use
`--overwrite` only when intentionally replacing that file's partial evidence.
Exit status 0 means the requested assertions were collected without execution
errors, even when expected outputs fail tolerance. Exit status 2 means an
execution/collection error or incomplete merge; inspect the saved evidence.

Combine recorded files without constructing a model:

```bash
PYTHONPATH="$PWD" "$task_python" .resume-evidence/partner_inventory.py merge \
  --year 2026 \
  --model-label "$task_model_label" \
  --input-dir .resume-evidence/partner-inventory-final \
  --output-stem .resume-evidence/9621-partner-inventory
```

The merge checks fixture hashes and reports files that still lack a completed
run. A calculation error also prevents a complete result. Review the model
labels in the JSON's per-file metadata before copying the final Markdown into
the hub's requested report location. Writes outside the assigned workspace are
root's responsibility and remain subject to the workspace permissions.

The JSON preserves every assertion's file, one-based case index, case name,
scoped output, period, original expectation, full current value, effective
absolute/relative tolerance, and result from core's comparator. The Markdown
shows expected outputs outside tolerance, changes within tolerance, and errors.
Arithmetic-string expectations are displayed as their evaluated amount;
`old_fixture` retains the source expression in JSON.
Its financial values are rounded to cents; full precision remains in JSON.
Unchanged displays are omitted from Markdown while retained in JSON.

This comparison establishes contract-output changes against existing fixtures.
It is not a main-versus-branch microsimulation and does not replace that impact
analysis. Leave all partner expectations unchanged for the hub's three-question
gate, and identify the published CA calibration separately from federal
index-window changes when explaining the proposed contract changes.
