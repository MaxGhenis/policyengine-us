# US #9621 resume evidence

The resume reused snapshot `d1b072db90` and prior merge `549b26ffe2` in the
assigned workspace. Model changes are in `9d247513a1` and current-main merge
`3126a708c9`, based on main `2d0815ae23621f974bcb79e4a53b09e0b801119c`.
Later handoff changes only correct the ordinary historical WI expectation,
add documentation/citations, and restore main's unrelated PROGRESS journal.
See the root report for the final backup revision and remaining blockers.

Git mutations used the workspace-local metadata:

```bash
git --git-dir=.resume-git --work-tree=. status
```

The original `.git` pointer remains read-only. All new commits are on the fork
branch `wip/hub-resume-sol-9621`; no PR-head promotion or merge occurred.

Behavioral runs used the prior attempt's cached Python 3.13 environment and
core 3.32.20, with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH` pointing to the
assigned workspace (except the explicitly labelled WI before run). Every
model run was a separately scheduled single file in the foreground; no
parallel models, background jobs, full suites, or microsimulations ran.

- `federal-tests.log`, `federal-tests-final.log`: selected federal Python
  runs before all new fixture construction errors were corrected.
- `federal-anchor-test.log`: final focused preservation test passed.
- `state-rounding-tests.log`: all 35 selected-file tests passed.
- `wi-deduction-yaml.log`, `wi-deduction-yaml-final.log`: ordinary historical
  expectation failure, then all 10 cases passed.
- `wi-deduction-before.log`: initial before harness import collision.
- `wi-deduction-before-final.log`: recovered pre-fix model, 7 failures and
  3 passes on the same 10 cases. `run_before_wi.py` and the copied YAML are
  the read-only harness and exact inputs.
- `federal-basic-deduction-yaml.log`: final required federal YAML run.
- `or-ctc-tests.log`: all 8 touched Oregon Kids' Credit tests passed.
- `ca-tax-yaml.log`: targeted published California tax-bracket cases.
- `main-compatibility.txt`: unchanged Louisiana helpers/invocation, restored
  main journal, and empty partner diff.
- `format-handoff.log`: mandatory `make format`, with no dependency sync.
- `heavy-wrapper-blocker.log`, `impact-blocker.log`: required host wrappers
  refuse to start because sandbox blocks `ps` and global progress writes.
- `snapshot-completeness.txt`: exact recovery verification for all three
  prior snapshot paths. `9621-recovered-progress.md` preserves the prior
  journal separately from main's unrelated tracked PROGRESS.md.
- `raw-head-partner-evidence.md`: archived raw-head failure inventory.
- `partner-renter-run.log`, `partner-inventory/`: partial current-build
  inventory, 5 cases and 11 assertions, 6 outside tolerance, no errors.
  JSON includes full precision and fixture hashes.

`partner_inventory.py` and `partner-inventory-instructions.md` prepare the
remaining complete inventory. The mandatory machine-wide wrapper must hold
the lock for any coordinated multi-file run. No partner fixture was edited.
No aggregate impact or full-inventory completion is claimed.
