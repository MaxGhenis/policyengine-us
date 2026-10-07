Temporary #9676 resumed evidence harness, prepared without executing tests or
microsimulations. These files belong only on the fork evidence branch. Copy
helpers to `.wip-9676-evidence/` and the YAML workflow to `.github/workflows/`.
Never include the preserved failing resource fixture in the passing suite.

The workflow uses frozen main `5b1d5bdf47044607341d76f3c932ba2e7b74a060`, original
PR head `a6c44418afccac0270dcb9ea155338dac0c9a05d`, and the evidence branch's
model. All jobs install the branch's locked dependency environment, then select
core **3.32.15** exactly. `PYTHONPATH` and runtime identity checks ensure the
requested checkout supplies the model. The workflow does not change
itemization or update the core lock to an unpinned latest release.

Before publication, root must verify the frozen main default dataset metadata
matches the pinned September 9 build used by the branch. The impact runner
asserts both URI and actual SHA-256, so metadata disagreement fails clearly.

Tests cover only Missouri TANF YAML, both property files, input definitions,
and unchanged partner contracts. Folder YAML is batched with one worker.
Every command has a required exit code: failure to import or collect cannot
stand in for an expected assertion failure. Failure-report plugins also reject
fixture setup errors and non-assertion test-call exceptions, even when pytest
returns 1. The old tests must survive the two
mutations while the new cases must detect them. Old-head new-member tests
intentionally pass: membership formulas are retained and this round closes
coverage gaps. Main's new-member cases and both resource fixtures retain their
expected failing evidence. Artifacts upload on failed jobs too.

One Ubuntu runner executes all targeted tests sequentially, then all six paired
2026 microsimulations before optional 2025 replication. Python 3.14 matches
current repository CI. Microsimulations retain the full default dataset and
all original weights; only saved rows are Missouri. The three scenarios are
unmodified, seven NPCR marks preserving
all other NPCR inputs, and those same marks with **bank assets only** zeroed.
Frames checkpoint atomically each month and before annual national TANF, keeping evidence
if that later calculation fails. Metadata records code SHA, Python/core,
actual dataset hash and completion status. Per-year person and SPM weights,
complete monthly diagnostics including monthly age, annual entitlement, MO entitlement with takeup,
actual annual TANF and national weighted TANF are saved.

`compare_mo.py OUTDIR --years 2026 2025` validates the paired hashes, versions,
entity IDs, intervention flags and weights before summarizing payment changes.
It separates income/resource failures in units whose membership changes,
lists drivers, and reports the largest two records' share of absolute impact.
Missing actual annual TANF is reported explicitly and produces exit 1 after
the available monthly comparison is written.

Core's YAML runner caches cloned systems. `mutate.py` retires this cache entry
between mutations so the requested patch executes, and verifies the intended
guard/converse assertion names in its saved failure reports. The explicit
source-role script runs the existing membership grid with canonical
`is_tax_unit_head` and `is_tax_unit_spouse` supplied for every person.
