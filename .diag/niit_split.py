"""Split the CRFB-run federal income tax correction into NIIT vs everything else.

Reads AGI (main = mutated, fix = correct) and income_tax from the saved crfb_base/crfb_fix
NPZ arrays, computes net_investment_income and filing_status in a fresh baseline
Microsimulation on the same dataset file (neither depends on the surtax), and recomputes
NIIT = 3.8% * min(max(NII,0), max(0, AGI - threshold[filing_status])) under each AGI.
"""
import sys
from pathlib import Path
import numpy as np
from policyengine_us import Microsimulation

OUT = Path("/Users/maxghenis/reviews/pe-us-inplace-cache-writes-2026-10-01/out")
DATASET = "/Users/maxghenis/.cache/huggingface/hub/datasets--policyengine--populace-us/snapshots/9a814a3b3b53c0ecd6e1737b6ec862c31300ef6f/populace_us_2024.h5"
L = lambda n: dict(np.load(OUT / f"{n}.npz", allow_pickle=True))
cb, cf = L("crfb_base"), L("crfb_fix")
sim = Microsimulation(dataset=DATASET)
Y = 2026
agi_b = np.asarray(sim.calculate("adjusted_gross_income", Y).values, dtype=float)
w = np.asarray(sim.calculate("tax_unit_weight", Y).values, dtype=float)
assert np.allclose(w, cf["tax_unit__tax_unit_weight"].astype(float)), "weights misaligned"
agi_fix = cf["tax_unit__adjusted_gross_income"].astype(float)
agi_main = cb["tax_unit__adjusted_gross_income"].astype(float)
print("AGI alignment (baseline sim vs crfb_fix):", np.allclose(agi_b, agi_fix, atol=0.01))
nii = np.asarray(sim.calculate("net_investment_income", Y).values, dtype=float)
fs = sim.calculate("filing_status", Y).values
fs = np.asarray(fs.decode_to_str() if hasattr(fs, "decode_to_str") else fs).astype(str)
thr_map = {"HEAD_OF_HOUSEHOLD": 200e3, "JOINT": 250e3, "SEPARATE": 125e3, "SINGLE": 200e3, "SURVIVING_SPOUSE": 250e3}
thr = np.array([thr_map[s] for s in fs])
niit_model = np.asarray(sim.calculate("net_investment_income_tax", Y).values, dtype=float)
def niit(agi):
    return 0.038 * np.minimum(np.maximum(nii, 0), np.maximum(0, agi - thr))
n_fix, n_main = niit(agi_fix), niit(agi_main)
print("NIIT formula reproduces model NIIT on correct AGI:", np.allclose(n_fix, niit_model, atol=0.01))
d_niit = n_main - n_fix
d_it = (cb["tax_unit__income_tax"] - cf["tax_unit__income_tax"]).astype(float)
print(f"federal income tax overstatement on main: ${(d_it*w).sum()/1e9:.3f}bn")
print(f"  of which NIIT (if read after the write): ${(d_niit*w).sum()/1e9:.3f}bn")
print(f"  residual (credits etc.): ${((d_it-d_niit)*w).sum()/1e9:.3f}bn")
m = np.abs(d_it) > 0.005
match = m & np.isclose(d_it, d_niit, atol=0.05)
print("units with fed tax diff:", m.sum(), " exactly explained by NIIT:", match.sum(),
      f" ($bn {(d_it[match]*w[match]).sum()/1e9:.3f})")
r = d_it - d_niit
mr = np.abs(r) > 0.005
print("units with non-NIIT residual:", mr.sum(), f"residual $bn {(r[mr]*w[mr]).sum()/1e9:.3f}",
      " residual>0 $bn", f"{(r[mr & (r>0)]*w[mr & (r>0)]).sum()/1e9:.3f}",
      " residual<0 $bn", f"{(r[mr & (r<0)]*w[mr & (r<0)]).sum()/1e9:.3f}")
np.savez_compressed(Path(__file__).with_suffix(".npz"), nii=nii, d_niit=d_niit, d_it=d_it, w=w)
