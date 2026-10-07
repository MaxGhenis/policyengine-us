# §163(d) / Form 4952 fix report

PR: https://github.com/PolicyEngine/policyengine-us/pull/9977 (draft; do not merge).
Code head: `05228167642374813d0afbdf4c0aa2cf559de7aa` on upstream `investment-interest-163d-limit`.
Current main merged: `dd9cb3f6839` through merge commit `839c951f8b3`.

## Recovery and fixes

Recovered completed build commits at `79b96595f5` and saved dirty snapshot `40a7fcbca6`. All 24 snapshot files exactly match the previous attempt's 22 modified and two untracked files. No previous work was discarded or history rewritten. The three imported build commits remain in the ancestry; recovery started from the saved work, rather than rebuilding it.

1. Carryover: explicit TaxUnit line-2 input defaults to zero. Line 3 includes current filer debt plus carryover, and lines 7/8 conserve line 3. No automatic propagation of computed carryforward.
2. Schedule A: subtract all members' current raw investment interest from the existing aggregate, then add allowed line 8. Carryover is never subtracted from current paid interest. Direct aggregate/mortgage inputs remain supported.
3. Attribution: Form 4952 debt, income, gains, elections and expenses exclude dependents. The pre-2018 line-5 miscellaneous floor uses a filer-only expense cap. The shared miscellaneous pool also excludes dependent investment fees, preserving other existing sources and direct total overrides; new NY/AR regressions cover the state consumers. The property oracle was corrected and now includes carryover.
4. Election: Schedule D reads effective lines 4g/4e; raw worksheet line 7 remains independent. Net gain, dividends and §911 consumers use filer amounts and preserve direct net-gain overrides. Default gain-first allocation remains.
5. Montana: each spouse computes a separate limit before 2024. Joint pooling and federal treatment from 2024 remain. A zero-current-debt reporting fallback attributes carryover-only federal deductions to the head. Verified live 2023 instructions; main's 2022 `revenuefiles.mt.gov` references remain.
6. CA/NY/VA: retained substitutions to allowed federal interest. CA's high-AGI exclusion stays on the federal-form approach and does not depend on the pending California methodology decision. The legacy CA federal-line-8 input remains a default-computed alias.
7. §67: retained permanent post-2017 federal disallowance of miscellaneous investment fees, including 2026. Updated changelog and capital-loss carryover documentation (memo amounts already included in net long-term gains).

## Validation

**90 targeted cases passed**, with each file run separately in the foreground using core 3.32.20. Federal and property files were rerun after the final formula change. The earlier Montana runs remain applicable: their cases supply zero miscellaneous fees or override that deduction, so the later shared-fee filter does not change their inputs or calculation paths.

| Single-file target | Passed | Evidence |
| --- | ---: | --- |
| Federal Form 4952 | 25 | [form4952-final.log](form4952-final.log) |
| Vectorized properties | 15 | [properties-final.log](properties-final.log) |
| Montana separate limits and federal alias | 4 | [montana-separate.log](montana-separate.log) |
| Montana allocation | 2 | [montana-allocation.log](montana-allocation.log) |
| Virginia allowed-interest exclusion | 5 | [virginia.log](virginia.log) |
| New York dependent fees | 1 | [new-york-fees.log](new-york-fees.log) |
| Arkansas dependent fees | 8 | [arkansas-fees-fixed.log](arkansas-fees-fixed.log) |
| California interest replacement | 2 | [california.log](california.log) |
| New York allowed-interest exclusion | 7 | [new-york-phase-out.log](new-york-phase-out.log) |
| Schedule D election | 13 | [election.log](election.log) |
| Section 911 dividends | 5 | [section911-dividends.log](section911-dividends.log) |
| Section 911 adjusted gain | 3 | [section911-gain.log](section911-gain.log) |

Seven externally specified source-overlay checks failed under prior formulas and passed under final formulas; see [before-after.log](before-after.log). This overlays saved build `79b96595f5` sources into the current system, retaining the new input to expose the old carryover omission. The cap case uses pre-build main's uncapped Schedule A formula. It is not a full old-checkout replay. Examples: federal tax $20,447 → $21,647; carryover-only deduction $0 → $4,000; Montana spouse deductions [150,450] → [300,0].

The first AR run rejected the added fixture because Person variable `ar_agi_joint` was placed on TaxUnit. Moving it to the head left expectations and formulas unchanged; all eight cases then passed. [Original failure](arkansas-fees.log) is preserved. An initial core 3.32.15 attempt was interrupted during initialization before assertions. The final federal run's 25 assertions passed, but the external macOS time wrapper exited 1 afterward because the sandbox blocks `kern.clockrate`; this is separate from test outcomes.

`make format` and ruff checks passed before every commit. Core 3.32.20 and Hypothesis use workspace/read-only test dependencies; no dependency or lockfile change is in the PR. The prior saved build's 21 YAML cases, six properties and 60 serial targets remain historical evidence, not final-head results.

The Python properties use independent seeded restatements and invariants on 400 mixed single/joint returns per cohort, including dependents and carryovers. The final local run took 158.62 s including setup, peaking at 1,095,139,328 bytes (~1.02 GiB); pytest reported 23.43 s. The earlier property run reported 87.95 s but did not measure setup or peak memory, so these are not comparable performance measurements. The asymmetric before/after harness timings likewise are not a speed comparison. CI routes this file to the existing Rest Python core group; no jobs or concurrency were added. Main's Makefile records an older ~142s Linux core-group baseline; current Linux resource artifacts are not yet available.

As of 2026-10-07 11:35 UTC, `gh pr checks` reports three queued prerequisite checks. Full suites, including API partner contracts, are pending CI. No partner expectations were edited or recalibrated; the PR has no partner-file diff against merged main. No suites or microsimulations ran locally.

## Impact and remaining work

No fresh microsimulation was run: the sandbox cannot write the host heavy lock and the explicit job restriction prohibits microsimulations. The hub must compare pinned main `dd9cb3f6839` and final PR HEAD for 2025/2026, exporting all Form 4952 lines, interest/itemized deductions and choice, taxable income, QBID, regular tax, AMT, income tax and state tax, with CA/NY/VA/MT and election breakdowns, plus AR for miscellaneous investment fees. Run 2017 fees and 2023 Montana explicit-input scenarios. Exact variables, dataset SHA and source provenance are in `dataset-audit.md` alongside this report.

**The dataset input is an imputed deduction residual, not raw paid investment interest.** At parent dataset code `cae8640f9e65e274aea65c7916cb37b956978e32`, `puf_interest_components.py:164-175` and `puf_support.py:714-730` send residual Schedule A deductions, including mortgage points and insurance premiums, to `investment_interest_expense`. The old $53.68B screen, $30.35B potentially disallowed / $26.97B among baseline itemizers, and illustrative +$5.4–9.4B estimate are not validated §163(d) scores. A current-default comparison needs this limitation; economic interpretation needs data-owner follow-up.

Remaining coverage: California’s own FTB 3526 income/election/carryover calculation remains the separate CA task; federal AMT's second Form 4952; NIIT Form 8960 line 9a; alternative “Elec.” allocation; investment/noninvestment asset split and separate annuity/royalty/K-1 inputs; Montana income adjustments and separate spouse carryovers. Axiom encoding is unperformed (`axiom: needed`); the saved parity draft remains available to the hub. PR remains draft pending fresh impact and review/CI confirmation.

## Workspace handoff

All work was confined to the assigned workspace. Its original shared `.git` metadata is read-only in this sandbox. Writable metadata is `.git-local`; use `git --git-dir=.git-local` here. All code commits and the main merge were immediately pushed upstream. No changes were made to the caller checkout or previous attempt's worktree, no worktrees were created elsewhere, and the assigned workspace remains for Subfleet salvage.

The sandbox cannot write `~/reviews/us-hub/fixes/163d-report.md`; this workspace copy is the handoff report. Evidence is backed up separately to fork branch `wip/hub-resume-163d-evidence`, keeping the PR diff focused on policy and tests. All test processes exited; no background processes remain. An independent final federal agent review found no concrete remaining formula/oracle defects; this is internal review, not maintainer approval.
