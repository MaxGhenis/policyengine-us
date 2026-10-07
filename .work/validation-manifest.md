# Validation manifest for #9406

Model PR head: `409e65e8b29feb87b8fc7cf245b35be28bb6b152`.
Clean main: `dd9cb3f6839d290c8490c561b54b7afeedc3c888`.
Approved review source: `34c6562e2b17bea1793f933f670ccbec33d98ae1`.
Recovered head: `62aee62351b1ba740c98cb9a6dff117653e3fd47`.
Current-main merge: `b6ad6626baa0b555cf4dea796e4f8c251b6a366d`.
Test-generator commit: `a4ca85f6fbaab2b8870486b09ee71ca711ed13f0`.

All commands ran in the assigned workspace, one model/test process at a time in the foreground. No local microsimulation, full suite, heavy-lock acquisition, dataset download, background shell process, partner expected-output edit, or public issue filing occurred.

Environment: read-only Python executable `/Users/maxghenis/PolicyEngine/_worktrees/policyengine-us-parent-ids/.venv/bin/python`; Python 3.14.4, PolicyEngine Core 3.30.2, NumPy 2.4.1, pytest 8.4.2. Bytecode was redirected to the workspace with `PYTHONPYCACHEPREFIX=$PWD/.work/pycache`; model commands selected `PYTHONPATH=$PWD`.

## Commands

Each pytest command took one file; each YAML command used one file and the official Core `run_tests` API. The YAML wrapper imports the fresh module-level country system once and exits after the completed runner result, avoiding redundant initialization and parameter-tree cleanup. It does not patch formulas. Reported pytest summary durations do not measure country-model startup or peak memory.

```sh
python -m pytest policyengine_us/tests/core/test_parent_links_properties.py -q
python -m pytest policyengine_us/tests/core/test_parent_links.py -q
python .work/run_yaml.py policyengine_us/tests/policy/baseline/gov/hhs/medicaid/income/parent_ids_composition.yaml
python .work/run_yaml.py policyengine_us/tests/policy/baseline/gov/hhs/medicaid/income/parent_ids.yaml
python .work/run_yaml.py policyengine_us/tests/policy/baseline/household/demographic/person/parent_ids.yaml
python .work/zero_id_differential.py --base .work/base --head .
```

The independent differential archives `policyengine_us` and `pyproject.toml` from the exact main SHA into `.work/base`; main archive contents matched Git. It runs main and head sequentially in independent child processes, verifies package/system/all compared variable source paths, uses identical Core, compares dtype/shape/raw bytes, and also checks omitted/explicit-zero parity within each source. Forty-eight synthetic cases compare 13 variables: 624 exact arrays, no build/calculation errors, no differences. Elapsed setup-inclusive times were 161.588s main and 166.735s head; peak memory was unavailable. Results and generated cases are preserved in `zero-id-results/*.pkl`.

Before fixtures: approved-head `r8_new_cases.yaml` had 5 failures/6 passes; at `a4ca85f6fb`, `ancestor_regression.yaml` had 1 failure and `flagged_filer_spouse.yaml` had 3 failures. All these cases are in the final 47-case composition file and passed. Logs preserve the failure assertions.

Before each commit, formatting and lint used:

```sh
UV_CACHE_DIR="$PWD/.work/uv-cache" UV_NO_SYNC=1 UV_PROJECT_ENVIRONMENT=/Users/maxghenis/PolicyEngine/_worktrees/pe-us-backlog/main/.venv make format
ruff format .work/run_yaml.py .work/zero_id_differential.py
ruff check .work/run_yaml.py .work/zero_id_differential.py
```

The local ignored `.ruff.toml` extends `pyproject.toml` and excludes `.work` and `.git-local` so archives and evidence cannot be formatted inadvertently. Final outputs are retained in `logs/format-final.log`.

## Git and CI provenance

The original worktree Git metadata points outside the writable sandbox. All Git operations therefore used a private workspace `.git-local` with read-only object alternates. Original metadata, caller checkout, prior worktrees and review directories were not written. The private assigned branch is `hub-resume-9406`; each model commit was pushed by fast-forward to the PR branch. Report/evidence is a separate fork-only commit at `MaxGhenis/policyengine-us:wip/hub-resume-sol2-9406`, leaving the PR's model head above unchanged. No registered extra worktree was created; archived main/approved sources are disposable evidence inputs.

Recovered CI: [run 37563630113](https://github.com/PolicyEngine/policyengine-us/actions/runs/37563630113), head `62aee62351`, success. Final CI: [run 37609932407](https://github.com/PolicyEngine/policyengine-us/actions/runs/37609932407), head `409e65e8b2`. Check snapshots are accompanied by run metadata and an observation timestamp. Current main `dd9cb3f683` also passed Household API Partners in [run 37581086735](https://github.com/PolicyEngine/policyengine-us/actions/runs/37581086735/job/112670656867), as recorded in `ci-main-dd9cb3f683-checks.json`. Historical checks are not presented as current-head passes.

## Historical evidence reused, not rerun

- Recovered six core/eleven property passes: `~/reviews/us-hub/fixes/9406-work/a3r/logs/test_parent_links-62aee62.log` and `test_parent_links_properties-62aee62.log`.
- Earlier CI generator failure: `~/reviews/us-hub/fixes/9406-work/ci/job-112445945712.log` (broader log `job-112445945827.log`).
- r8 at approved34 versus pristineca1805cf0: `~/reviews/us-hub/fixes/9406-work/r8-harness/review-r8/out/pytest.log`, `yaml_parent_ids.log`, `yaml_compare.txt`, and `zero0.log` through `zero3.log`.
- Saved r8 counts are historical only: 14 Python/48 YAML, 22,581 arrays/50 matching errors/zero differences, explicit-zero repeat and 120-world/3,313-person/1,440-array random check with zero differences. These host-only paths are not archived source inputs for the new differential.

The recovered a1/a2/a3r YAML logs were empty; no completion was inferred from them.

Final-head CI observation: 2026-10-07T11:12:11.906106+00:00, {'IN_PROGRESS': 4, 'SUCCESS': 7, 'QUEUED': 24}. See `ci-409e65e8b2.json`; broad suites remain incomplete and final-head partners are queued. All final local tests passed: 17 Python and 63 YAML. No test/model process remained running after the last file completed.
