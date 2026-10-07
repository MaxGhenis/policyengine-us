"""Rescore the #9676 parent-flag default against CPS parent pointers, both school variants.

Finding 8 of the 2026-09-29 review: the PR body's Populace accuracy table came
from cps_parent_truth.build(df, "spec"), which treats A_HSCOL as
is_in_secondary_school. No dataset stores that input, so the model sees the
"none" variant. This rescores the implemented default
(own_children > 0, age - youngest dependent child >= 12, age - oldest <= 50)
under both variants and reports weighted and unweighted precision and recall,
false positives and negatives, distinct persons and the Kish effective sample
size of the selected set. It reuses the review's frames and helpers unchanged.

Run with the backlog venv python (pandas, h5py), no policyengine import.
"""

import json
import sys

import h5py
import numpy as np

sys.path.insert(
    0, "/Users/maxghenis/reviews/mo-tanf-dependent-parent-2026-09-29/cps-ground-truth"
)
import cps_parent_truth as c  # noqa: E402


def kish(w):
    return float(w.sum() ** 2 / (w**2).sum()) if len(w) and (w**2).sum() else 0.0


def score(df, name, school):
    built, _ = c.build(df, school)
    units = c.tax_unit_table(built)
    units["max_dc_age"] = built[built.dc].groupby("tu").age.max().reindex(units.index)
    rows = []
    for scope in ("US", "MO"):
        sub_units = units[units.state == c.MISSOURI] if scope == "MO" else units
        e = built[built.E & built.tu.isin(sub_units.index)].join(
            units[["min_dc_age", "max_dc_age"]], on="tu"
        )
        G = e.G.to_numpy()
        r1 = (e.oc > 0).to_numpy()
        guard = (
            r1
            & ((e.age - e.min_dc_age) >= 12).to_numpy()
            & ((e.age - e.max_dc_age) <= 50).to_numpy()
        )
        for label, mask in (("own_children > 0", r1), ("with age guard", guard)):
            tp, sel, g = c.nw(e, mask & G), c.nw(e, mask), c.nw(e, G)
            prec, rec = c.ratio(tp, sel), c.ratio(tp, g)
            w = e.w.to_numpy()
            row = {
                "data": name,
                "school": school,
                "scope": scope,
                "rule": label,
                "eligible_E": c.nw(e, np.ones(len(e), bool)),
                "truth_G": g,
                "selected": sel,
                "true_positive": tp,
                "false_positive": c.nw(e, mask & ~G),
                "false_negative": c.nw(e, ~mask & G),
                "precision": prec,
                "recall": rec,
                "selected_kish_n": kish(w[mask]),
                "largest_false_positive_weight": float(w[mask & ~G].max())
                if (mask & ~G).any()
                else 0.0,
            }
            if "person_key" in e:
                row["selected_distinct_persons"] = int(e.person_key[mask].nunique())
            rows.append(row)
            print(
                f"{name:30s} {school:4s} {scope} {label:17s} "
                f"sel {sel['n']:>4}/{sel['w']:>10,.0f} "
                f"prec w {prec['w']:.3f} n {prec['n']:.3f}  "
                f"rec w {rec['w']:.3f} n {rec['n']:.3f}  "
                f"FP {row['false_positive']['n']}/{row['false_positive']['w']:,.0f} "
                f"FN {row['false_negative']['n']}/{row['false_negative']['w']:,.0f} "
                f"kish {row['selected_kish_n']:.1f}",
                flush=True,
            )
    return rows


if __name__ == "__main__":
    with h5py.File(c.POPULACE_H5, "r") as f:
        keys = set(f.keys())
        groups = {
            k: list(f[k].keys())[:5] for k in keys if isinstance(f[k], h5py.Group)
        }
    stored = {
        v: any(v in k for k in keys) or any(v in str(g) for g in groups.values())
        for v in ("is_in_secondary_school", "is_tax_unit_dependent")
    }
    print("populace h5 stores:", stored, flush=True)
    out = {"populace_stores": stored, "rows": []}
    census = c.pool([c.load_raw_cps(year) for year in c.CENSUS_TAX_UNITS])
    populace = c.load_populace()
    for school in ("none", "spec"):
        out["rows"] += score(census, "census ASEC 2023-2025 pooled", school)
        out["rows"] += score(populace, "populace 2024", school)
    with open(sys.argv[1] if len(sys.argv) > 1 else "rescore_none.json", "w") as f:
        json.dump(out, f, indent=1)
