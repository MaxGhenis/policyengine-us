"""Convert HUD's FY-XXXX Small Area FMR workbook into the PolicyEngine CSV schema.

HUD publishes one SAFMR workbook per fiscal year on huduser.gov (browse to
``Datasets > Fair Market Rents > Small Area FMRs``). Each row is one
(ZIP, HUD FMR area) pair with ``SAFMR 0BR``…``SAFMR 4BR`` columns plus the
90%/110% payment-standard columns, which this script ignores — the bundled
``value`` column is the raw SAFMR, not a payment-standard limit.

The bundled CSV is deliberately narrower than HUD's file: it covers only the
metros where HUD mandates SAFMR use for Housing Choice Voucher payment
standards *and* PolicyEngine has ZIP coverage, under curated metro labels in
``hud_area_name``. This script therefore reuses the ZIP set and curated labels
already in ``--output`` rather than re-deriving them, which is the refresh
procedure documented in
``policyengine_us/parameters/gov/hud/fmr/README.md``.

A ZIP HUD did not publish for the requested fiscal year is skipped and listed
on stderr; no value is carried across fiscal years.

Dependency: ``python-calamine`` (``pip install python-calamine``), as for
``convert_hud_fmr_xlsx``. Not a runtime dependency of the model.

Usage:
    python -m policyengine_us.tools.convert_hud_safmr_xlsx \
        --input ~/Downloads/fy2024_safmrs_revised.xlsx \
        --year 2024 \
        --metro "Dallas, TX" --metro "Fort Worth, TX" --metro "San Antonio, TX" \
        --output policyengine_us/parameters/gov/hud/fmr/small_area_fair_market_rents.csv

Omit ``--metro`` to refresh every curated metro already in the output. Pass it
when a fiscal year predates a metro's SAFMR implementation date, so that year's
rows are not written for a metro where SAFMRs were not yet the HCV basis.

Re-running for a new year appends a block rather than overwriting; the script
de-duplicates on ``(zip_code, year, bedrooms)``.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

BEDROOM_COLUMN_TEMPLATE = "SAFMR {bedrooms}BR"
BEDROOMS = range(5)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse the newlines HUD embeds in its header cells."""
    return df.rename(columns={c: " ".join(str(c).split()) for c in df.columns})


def read_safmr_sheet(path: Path) -> pd.DataFrame:
    workbook = pd.ExcelFile(path, engine="calamine")
    for sheet in workbook.sheet_names:
        df = normalize_columns(workbook.parse(sheet))
        if BEDROOM_COLUMN_TEMPLATE.format(bedrooms=0) in df.columns:
            return df
    raise ValueError(f"No sheet in {path} has a '{BEDROOM_COLUMN_TEMPLATE}' column.")


def zip_level_values(df: pd.DataFrame) -> pd.DataFrame:
    """Return one (zip_code, bedrooms, value) row per ZIP.

    A ZIP can appear under several HUD FMR area codes (its own metro plus
    adjacent nonmetro county areas). HUD publishes the same SAFMR for the ZIP
    in every such row, so collapsing on the ZIP is lossless — this asserts it
    rather than assuming it.
    """
    df = df.copy()
    df["zip_code"] = df["ZIP Code"].astype(int).astype(str).str.zfill(5)
    frames = []
    for bedrooms in BEDROOMS:
        column = BEDROOM_COLUMN_TEMPLATE.format(bedrooms=bedrooms)
        frame = df[["zip_code", column]].rename(columns={column: "value"})
        frame = frame.assign(bedrooms=bedrooms)
        frames.append(frame)
    tidy = pd.concat(frames, ignore_index=True)
    conflicting = tidy.groupby(["zip_code", "bedrooms"]).value.nunique()
    conflicting = conflicting[conflicting > 1]
    if len(conflicting):
        raise ValueError(
            "HUD publishes conflicting SAFMRs for the same ZIP and bedroom count: "
            f"{conflicting.index.tolist()[:10]}"
        )
    return tidy.drop_duplicates(["zip_code", "bedrooms"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--metro",
        action="append",
        default=None,
        help="curated hud_area_name to include; repeatable, defaults to all",
    )
    args = parser.parse_args()

    existing = pd.read_csv(args.output, dtype={"zip_code": str})
    existing["zip_code"] = existing["zip_code"].str.strip().str.zfill(5)
    labels = existing.drop_duplicates("zip_code").set_index("zip_code")["hud_area_name"]
    if args.metro is not None:
        labels = labels[labels.isin(args.metro)]
        unknown = set(args.metro) - set(labels)
        if unknown:
            raise KeyError(f"No bundled ZIP carries metro label(s) {sorted(unknown)}")

    published = zip_level_values(read_safmr_sheet(args.input))
    new = published[published.zip_code.isin(labels.index)].copy()
    new["hud_area_name"] = new.zip_code.map(labels)
    new["year"] = args.year
    new = new[["zip_code", "hud_area_name", "year", "bedrooms", "value"]].sort_values(
        ["hud_area_name", "zip_code", "bedrooms"]
    )

    unpublished = sorted(set(labels.index) - set(new.zip_code))
    if unpublished:
        print(
            f"  {len(unpublished)} bundled ZIP(s) absent from the FY{args.year} "
            f"workbook, left without FY{args.year} rows: {', '.join(unpublished)}",
            file=sys.stderr,
        )

    combined = pd.concat([existing, new], ignore_index=True).drop_duplicates(
        subset=["zip_code", "year", "bedrooms"], keep="last"
    )
    combined.to_csv(args.output, index=False)
    print(f"Wrote {len(combined):,} rows ({len(new):,} for FY{args.year}) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
