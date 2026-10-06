# PROGRESS (hub fix round, us#9621) — untracked journal, never stage
- branch hub-fix-9621 = PR head 194c1f6237 + merge upstream/main 843bcdaca1 -> 0efc557d36 (no conflicts)
- pushed wip to origin wip/hub-fix-9621
- research done (agents): WI/VT/CA reports; scratch copied to ~/reviews/us-hub/fixes/9621-research/{wi_idx,vtcpi,ca_cpi}
  - WI: (dp)/(dt) bases 7200/9300/10380 (Aug1999), joint 19010/21360 & sep 9030/10140 (Aug2015); brackets (1r)/(2)(k)/(L) Act15 2025 amounts x Aug2024 base from 2026 ((2e)(bm)); round nearest $10, $5 up; no decrease. 80/80 reproduce. repo 2025 2nd bracket WRONG (51130/68170/34090 -> 50480/67300/33650). 2027: max 14430/18640/26720/12690; start 20810/30020/14250; brackets s 15620/53720/344020 j 20840/71620/458700 sep 10420/35810/229350
  - VT: unchained NSA CPI-U avg Sep-Aug; base window ending Aug 2017 (243.391833); amount=base+floor(base*cola/step)*step; step 50 ($25 MFS brackets); bases PE 4150, SD 6000/9000/12000, add'l 1000, brackets 5822(a). 2026 brackets published PRELIMINARY (IN-114-Instr-2026). 2026 SD 7850/15700/11800, add 1300, PE 5400 COMPUTED.
  - CA: DIR June2026 CCPI 364.969; FTB Oct 2026 published 2026 values (SD 5900/11800, credits 158/316, dep 491, renter 55830/111660, brackets X/Y/Z); renter income_cap leaves never uprated (no propagate); 2025 joint renter cap should be 107988
## Session 2 (05699066) plan, 2026-10-06 ~13:20
- research reports extracted to ~/reviews/us-hub/fixes/9621-research/reports/{wi,vt,ca}.md; scratch scripts in ~/reviews/us-hub/fixes/9621-work/
- merged upstream/main 6440b3e604 -> CONFLICT test_uprating_extensions.py (main's #9833 educator cap tests); resolve keeping both, adapt SimpleNamespace test to tax_year_projection, recompute anchors (2032 cap likely 400->350)
- NOTE renter cap IS uprated (partner evidence: 55,217.66 -> 55,248.09); CA research claim it is frozen is wrong; don't add propagate
- commits planned: (1) merge (2) federal docs/tests + 2040 dep YAML (3) cpi_u_nsa series + VT extension (4) WI extension + 2026 published + 2025 2nd-bracket fix (5) CA CPI 2026 + FTB 2026 published (6) replace state snapshot tests (7) changelog
- venv: .venv in worktree (py3.13, editable). Machine load ~390: model load >10 min
