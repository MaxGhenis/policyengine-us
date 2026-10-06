# EITC payroll deferral correction

Branch: `pb-fix-eitc-deferrals`, based on `fd6a512362`.

The patch uses federal taxable wages for EITC and state federal-style earned-income credit calculations. ACTC inherits the corrected EITC earnings. A separate California earnings base excludes traditional 401(k), traditional 403(b), and pre-tax health premiums while retaining payroll HSA contributions. The existing CalEITC AGI comparison and gross-earnings AMT kiddie-tax cap are preserved.

## Legal basis

- [IRC 32(c)(2)(A)](https://www.law.cornell.edu/uscode/text/26/32#c_2): includible wages and the existing self-employment adjustment. [EGTRRA section 303(b), (i)](https://www.govinfo.gov/content/pkg/PLAW-107publ16/html/PLAW-107publ16.htm) makes the wage restriction effective after 2001; the patch has no 2026 gate.
- [IRC 24(d)](https://www.law.cornell.edu/uscode/text/26/24#d): ACTC uses section 32 earnings.
- [FTB 3514](https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.html), lines 13 and 23, and [EDD DE 231EB](https://edd.ca.gov/siteassets/files/pdf_pub_ctr/de231eb.pdf): California W-2 wages and payroll HSA treatment.
- [IRC 59(j)](https://www.law.cornell.edu/uscode/text/26/59#j) uses section 911(d)(2) earnings for the AMT cap, so the original gross earnings sum is retained.

## Engine and test files

Relative to `policyengine_us/variables/`:

- `gov/irs/credits/earned_income/eitc_earned_income.py`
- `gov/irs/income/filer_adjusted_earnings.py`
- `gov/irs/tax/federal_income/alternative_minimum_tax/exemption/amt_exemption.py`
- `gov/states/ca/tax/income/credits/earned_income/ca_eitc.py`
- `gov/states/ca/tax/income/credits/earned_income/ca_eitc_earned_income.py` (new)
- `gov/states/ca/tax/income/credits/young_child/ca_yctc.py`

New parameter: `policyengine_us/parameters/gov/states/ca/tax/income/credits/earned_income/pre_tax_contributions.yaml`.

Relative to `policyengine_us/tests/policy/baseline/`:

- `gov/irs/credits/earned_income/eitc_pre_tax_contributions.yaml` (new, 9 cases)
- `gov/irs/income/filer_adjusted_earnings.yaml` (new, 5 cases)
- `gov/irs/tax/federal_income/alternative_minimum_tax/exemption/amt_exemption.yaml` (1 new case; existing input fixtures migrated)
- `gov/irs/tax/federal_income/alternative_minimum_tax/income/amt_income_less_exemptions.yaml` (input fixtures migrated; expectations unchanged)
- `gov/states/ca/tax/income/credits/earned_income/ca_eitc_earned_income.yaml` (new, 7 cases)
- `gov/states/ca/tax/income/credits/young_child/ca_yctc.yaml` (input fixtures migrated; expectations unchanged)
- `gov/states/ca/tax/income/credits/young_child/ca_yctc_payroll_contributions.yaml` (new, 2 cases)

Changelog: `changelog.d/pb-fix-eitc-deferrals.fixed.md`. This report is a handoff artifact, not part of the proposed engine patch.

The 24 added cases cover traditional/Roth contributions, payroll HSA, health premiums, IRA contributions, negative wages, self-employment losses, dependents, earlier years, Oklahoma's recomputed credit, AMT preservation, California AGI comparison, YCTC, and PolicyBench provision regressions. No partner contract tests were changed.

## Verified provision comparisons

Compared the original formulas loaded from `git show HEAD:<path>` with the patch, using the same current parameters and explicit provision inputs:

| Fixture / output | Before | After |
|---|---:|---:|
| 100: EITC | 2,366.00 | 822.29 |
| 100: ACTC | 512.25 | 0.00 |
| 100: federal refundable credits | 2,878.25 | 822.29 |
| 100: MT EITC | 473.20 | 164.46 |
| 119: EITC | 764.23 | 1,276.30 |
| 119: federal refundable credits | 2,854.00 | 3,366.07 |
| 119: VA nonrefundable EITC | 152.85 | 255.26 |
| 119: VA tax before refundable credits | 1,859.09 | 1,756.68 |
| 023: California earned-income base | 17,442.65 | 14,664.17 |

These are provision fixtures, not the audit's raw JSON. Fixture 100 uses the rounded $5,915 gross wages with the audit's $2,055.72 taxable wages. Fixture 119 pins the audit AGI ($52,568.54), unchanged ACTC ($2,089.77), and pre-credit VA tax ($2,011.94); the VA nonrefundable election is explicit. This explains the minor differences between local baseline values and the supplied audit baseline.

Separately rerunning the rounded full prompts on the current checkout produced:

| Household / output | Before | After |
|---|---:|---:|
| 100: federal refundable credits | 2,878.25 | 822.40 |
| 100: MT EITC | 473.20 | 164.48 |
| 119: EITC | 764.23 | 1,276.20 |
| 119: ACTC | 1,543.72 | 1,543.72 |
| 119: federal refundable credits | 2,307.95 | 2,819.92 |
| 119: VA nonrefundable EITC | 152.85 | 255.24 |
| 119: VA tax before refundable credits | 1,948.82 | 1,846.43 |
| 023: CalEITC | 97.51 | 97.51 |

These current-model aggregate results are not a reproduction of version 1.755.4. The scenario 023 comparison verifies zero isolated credit movement with the existing AGI comparison; it does not adjudicate the 2026 California indexed table. Snapshot output: `/tmp/pb-eitc-deferrals-snapshots.jsonl`.

## Validation

Interpreter import was checked and printed this worktree's `policyengine_us` directory. No packages were installed. One test process ran at a time.

Commands below use:

```bash
P=/Users/maxghenis/PolicyEngine/_worktrees/pe-us-review-main/.venv/bin/python
T=policyengine_us/tests/policy/baseline
export PYTHONPATH="$PWD"
```

1. Before the fix: **10 failed, 2 passed**, demonstrating the defect; log `/tmp/pb-eitc-deferrals-before.log`.

   ```bash
   "$P" -m policyengine_core.scripts.policyengine_command test "$T/gov/irs/credits/earned_income/eitc_pre_tax_contributions.yaml" "$T/gov/irs/income/filer_adjusted_earnings.yaml" -c policyengine_us
   ```

2. Initial focused run: **217 passed, 1 failed**. The new AMT fixture initially omitted that the 17-year-old files their own return; `is_tax_unit_head: true` corrects that setup. The negative-wage and Oklahoma cases were added subsequently. Log `/tmp/pb-eitc-deferrals-focused.log`.

   ```bash
   "$P" -m policyengine_core.scripts.policyengine_command test "$T/gov/irs/credits/earned_income" "$T/gov/irs/credits/ctc/refundable" "$T/gov/irs/income/filer_adjusted_earnings.yaml" "$T/gov/irs/tax/federal_income/alternative_minimum_tax" "$T/gov/states/ca/tax/income/credits/earned_income" "$T/gov/states/ca/tax/income/credits/young_child" -c policyengine_us
   ```

3. Complete IRS shard: **1,033 passed, 0 failed** across all 12 batches. Log `/tmp/pb-eitc-deferrals-irs.log`.

   ```bash
   "$P" policyengine_us/tests/test_batched.py "$T/gov/irs" --mode per-subdir --workers 1
   ```

4. Complete baseline state shard: **incomplete**. Batch 1 collected 1,737 cases but exceeded the runner's 1,800-second limit without an assertion failure or final pass count. Stopped the runner in batch 2 (exit 130) and narrowed validation to the affected state credits. Log `/tmp/pb-eitc-deferrals-states.log`.

   ```bash
   "$P" policyengine_us/tests/test_batched.py "$T/gov/states" --batches 16 --workers 1
   ```

5. Affected state credits: **484 passed, 0 failed**, one pytest import-rewrite warning, 91 YAML files, one test process. This is the completed pytest summary; the terminal session remained active during prolonged interpreter shutdown. An interrupt was requested, but final process exit status was unavailable at handoff (execution session `25412`). No further test process was started. Covers all state EITC files and directories, California YCTC, Minnesota/Missouri/Washington working-family credits, Wisconsin earned-income credit, cross-state EITC cases, and direct EITC consumers in Alabama, Colorado, and Oregon. This does not complete general state income-tax integration or benefit-program coverage. Log `/tmp/pb-eitc-deferrals-state-credits.log`; its first line records the exact expanded command. Reproduce the selection and command with:

   ```bash
   PYTHONPATH="$PWD" "$P" - <<'PY'
   import os
   from pathlib import Path
   import re
   import shlex
   import subprocess
   import sys

   files = subprocess.check_output(
       ["git", "ls-files", "--cached", "--others", "--exclude-standard",
        "policyengine_us/tests/policy/baseline/gov/states"], text=True,
   ).splitlines()
   additional_consumers = {
       "al_federal_income_tax_deduction.yaml",
       "co_refundable_ctc.yaml",
       "or_federal_tax_liability_subtraction.yaml",
   }
   paths = sorted({
       path for path in files
       if "/tax/" in path and path.endswith((".yaml", ".yml"))
       and ("/eitc/" in path or re.search(
           r"eitc|earned_income_credit|working_families|mn_wfc|mo_wftc|ca_yctc",
           Path(path).name,
       ) or Path(path).name in additional_consumers)
   })
   command = [sys.executable, "-m", "policyengine_core.scripts.policyengine_command",
              "test", *paths, "-c", "policyengine_us"]
   print(shlex.join(command), flush=True)
   os.execv(sys.executable, command)
   PY
   ```

6. Formatting/lint: **passed**.

   ```bash
   UV_NO_SYNC=1 UV_OFFLINE=1 UV_CACHE_DIR=/tmp/pb-eitc-deferrals-uv-cache UV_PROJECT_ENVIRONMENT=/Users/maxghenis/PolicyEngine/_worktrees/pe-us-review-main/.venv make format
   git diff --check
   ```

## Environment limitations

The required upstream searches were attempted before implementation:

```bash
gh pr list -R PolicyEngine/policyengine-us --state all --search "EITC deferrals" --limit 30
gh issue list -R PolicyEngine/policyengine-us --state all --search "EITC deferrals" --limit 30
gh pr list -R PolicyEngine/policyengine-us --state all --search "earned income contributions" --limit 30
```

All failed to connect to `api.github.com`; web searches/search-page/API fallbacks also could not establish whether an existing fix is open. Local history confirms the separate CalEITC AGI fix is already in the starting checkout.

Git staging failed with `Operation not permitted` creating `/Users/maxghenis/PolicyEngine/policyengine-us/.git/worktrees/pb-eitc-deferrals/index.lock`. Shared Git metadata is outside the writable sandbox. No commit was possible; nothing was pushed or published. Intended commit message:

```text
Exclude pre-tax payroll contributions from EITC earnings

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## Draft PR

Title: Exclude pre-tax payroll contributions from EITC earnings

Federal EITC and derived ACTC calculations counted payroll compensation excluded from gross income, contrary to IRC 32(c)(2)(A)(i). Use taxable wages for federal and shared state credit earnings, and use California's wage exclusions for CalEITC/YCTC while retaining payroll HSA contributions. Preserve the AMT kiddie-tax earnings cap and the existing CalEITC AGI comparison.

Test plan: 24 new statutory regression cases; 1,033 IRS tests passed and the affected state credit run reported 484 passed, covering existing affected-directory tests. The state interpreter's final exit status remained unconfirmed after its pytest summary. `make format` and `git diff --check` passed. The complete state shard was attempted but timed out; general state integration and benefit-program coverage remain incomplete.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
