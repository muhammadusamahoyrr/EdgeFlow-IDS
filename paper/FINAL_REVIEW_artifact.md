# Artifact Evaluation Report: Reproducibility

**Paper:** "What Benchmark Scores Hide: Auditing a Flow-Based IoT Intrusion Detector from Labels to Live Blocking"
**Artifact:** `D:\EdgeFlow-IDS` (claimed public at github.com/muhammadusamahoyrr/EdgeFlow-IDS, MIT)
**Reviewer role:** artifact-evaluation committee, reproducibility track
**Method:** static inspection only. I read the paper sections, README, docs, every run script and the producing code for each result file, and spot-checked about 60 numbers in the paper against `results/`. I ran no experiments and no git commands. To see what would actually be public, I parsed `.git/index` read-only: 220 staged/committed paths, `main` only, no tags. Repository files were not modified. The `paper/` folder is excluded on purpose and not counted against the artifact.

---

## 1. Badge estimate

| Badge | Estimate | Reason |
|---|---|---|
| **Available** | **Not yet. Easy to fix.** | (a) Many files the paper depends on are on disk but **not in the git index**, so the public repo would not contain them: all of `src/iot23/`, `patches/`, 10 scripts in `src/analysis/`, `src/run_review_r5..r8.sh`, `src/make_nfstream_diff.sh`, and every file under `results/iot23/` (see section 3, B1). (b) There is no tagged release and no archival DOI. The paper itself has a placeholder for one. GitHub alone is not an archival repository under ACM/USENIX rules. |
| **Functional** | **Borderline. Fails as staged, passes after the P0/P1 fixes.** | The core CIC-IoT2023 pipeline is documented end to end in the README (steps 1–7) and is scripted, seeded and version-pinned. However, the IoT-23 pipeline, the official-CSV baseline and the round-5 to round-8 analyses have no README entry. Five driver scripts hard-code `/mnt/d/EdgeFlow-IDS`. There are no data checksums. Two paper tables have no generating script. |
| **Results Reproduced** | **Likely for offline results. Qualitative only for live results.** | Offline: every random choice uses seed 0 (verified in code), direct dependencies are pinned, and inputs are fixed public pcaps. Bit-identical regeneration is plausible if the same pcap bytes are obtained (HF mirror, unpinned revision, no hashes). Live: results depend on timing, as the paper admits. Also, `run1` and `edge100` used an earlier harness that **no longer exists in the code**, so those two runs cannot be re-run as reported. |

---

## 2. Paper table/figure → script → result file

Legend: ✅ script and result present and tracked · ⚠️ works but has a gap · ❌ blocking gap. "Untracked" means present on disk but not in the git index.

| Paper item | Generating command (as documented, or inferred) | Result file | Status |
|---|---|---|---|
| **Tab. background** (background share per capture) | `src/label_shares.py` (README step 7). Evidence column: `data/attackers.json` + `src/diag/*` | `results/label_shares.md` | ✅ Numbers match (4,992/0.985 … 511,936/0.001). |
| **Tab. filelabel**, CIC rows | `src/analysis/file_label_baseline.py` via `src/analysis/run_analyses.sh` | `results/file_label_baseline.md` | ⚠️ Matches. `run_analyses.sh` is not mentioned in the README. |
| **Tab. filelabel**, IoT-23 rows | `src/iot23/file_label_baseline.py` (no driver) | `results/iot23/file_label_baseline.md` | ❌ Script and result are **untracked**. Not in the README. |
| **Tab. perclass** + macro-F1 0.869/0.731, FPR 1.1/3.9% | `src/train_baseline.py --split {temporal,stratified}` via `src/run_offline2.sh` (step 4) | `results/baseline_{temporal,stratified}/report.md`, `metrics.json` | ✅ |
| Host-pair CIs [0.577, 0.823], [0.735, 0.877] (text, Tab. perclass) | `src/analysis/cluster_ci.py` via `run_analyses.sh` | `results/cluster_ci.md` | ⚠️ Tracked. Driver is not in the README. |
| Seed spread 0.8535–0.8726 | `src/analysis/random_seed_spread.py` via `src/run_review_r8.sh` | `results/random_seed_spread.md` | ❌ Untracked. Driver hard-codes `/mnt/d`. |
| Paired diff +0.137 [0.024, 0.278] / +0.142 [0.025, 0.287] | `src/analysis/paired_diff.py` via `run_review_r5.sh` | `results/paired_diff.md` | ❌ Untracked. Hard-coded path. |
| Cluster-unit sensitivity ([0.002, 0.165], [0.001, 0.151], [−0.004, 0.164]) | `src/analysis/cluster_sensitivity_cic.py` (r8), `..._present.py` (**no driver**) | `results/cluster_sensitivity_cic{,_present}.md` | ❌ Untracked. `_present.py` is not invoked by any script. |
| BruteForce recall CI 0.053 [0.000, 0.842], Mirai 0.90, MITM 0.16 | `src/analysis/round2_checks.py` (**no driver, not in README**) | `results/round2_checks.md` | ⚠️ Tracked. The file computes these with the **edge tree**, but the paragraph sits next to the decision-tree Table perclass. Say which model in the text. |
| Boundary-spanning 36.1%, 0.725→0.604, 0.700→0.690 | `src/diag/check_split_overlap.py` (README step 7) | `results/split_overlap.md` | ✅ |
| **Fig. split** (`split_recall.png`) | `src/make_figures.py` (step 7) | `docs/figures/split_recall.png` | ✅ |
| **Tab. iot23split** | `src/iot23/splits.py` via `src/iot23/run_splits.sh` | `results/iot23/splits.md`; common-class CI in `results/iot23/common_class_ci.md` | ❌ All untracked. `run_splits.sh` hard-codes `/mnt/d`. |
| IoT-23 text: paired −0.017 [−0.039, −0.009], originator/capture CIs, 91.5% singletons, 348,350 clusters | `src/iot23/common_class_ci.py` (r5), `src/iot23/cluster_sensitivity.py` (r7), `src/iot23/spanning_common.py` (r6) | `results/iot23/{common_class_ci,cluster_sensitivity,spanning_common}.md` | ❌ Untracked. Hard-coded paths. |
| IoT-23 setup: 756,306 flows, 99.99% matched, 38 dropped, 35.2% / 270 overlap | `src/iot23/download.py` → `src/iot23/extract_label.py`, `src/iot23/zeek_agreement.py` | `results/iot23/match_rates.md`, `results/iot23/zeek_agreement.md` | ❌ Untracked. No driver. Not in the README. |
| IoT-23 FPR per capture (0.709 vs 0.049, 97–100%) and background shares | `src/iot23/fpr_per_capture.py` (r5), `src/iot23/label_shares.py` (no driver) | `results/iot23/fpr_per_capture.md`, `label_shares.md` | ❌ Untracked. |
| Official CSV baseline (0.749/0.803, 0.727/0.778, 483,053 rows) | `src/analysis/download_official_csv.py` → `src/analysis/official_csv_baseline.py` (**no driver**) | `results/official_csv_baseline.md` | ❌ Untracked. Not in the README. |
| Edge tree (depth 32, 1,767 nodes, 222 KiB, 0.725) / NSGA-II (14 of 54, 0.723, 211 KiB) | `src/tune_edge_tree.py`, `src/nsga_select.py`, `src/train_edge_model.py` (step 4) | `results/edge_tree_tuning.md`, `results/edge_tree.json`, `results/nsga/summary.md` | ✅ |
| Fidelity: 148,756 matched / 23 / 128, 96.62–100%, host-pair CIs [0.457, 0.823] | `src/analysis/match_live_offline.py --tag run1` via `run_analyses.sh` | `results/live/run1/flow_match.md` | ⚠️ Tracked. Re-running requires `results/live/run1/flows.csv`, which **.gitignore excludes**. |
| Packet ratio 0.9919–1.0064, 0 kernel drops, 12,271 pps, 0.44 ms / 209 flows | `topology/live_experiment.py` + `src/eval_live.py` via `src/run_live3.sh` (step 5) | `results/live/run1/live_vs_offline.{json,md}` | ⚠️ The harness has changed since run1 (see B3). |
| **Tab. repeats** | Runs: `run_live3.sh` (run1, edge100), `run_final_live.sh` (edge50), `src/analysis/run_repeats.sh` (\_r2, \_r3). "3 win." column: `src/analysis/same_window.py` (r7). | `results/repeats.md` (**hand-written; no script produces it**), `results/live/same_window.md` (untracked), `results/live/*/live_vs_offline.json` | ❌ (1) No script assembles the table. (2) `same_window.md` is untracked, and `same_window.py` needs the ignored `flows.csv`. (3) The **One-core "Live flows" cell is "--: not recorded"**, but `results/live/edge100/live_vs_offline.json` records `live_flows: 142725` for the DDoS-SYN window. Fill the cell. |
| **Fig. delay** (`live_delay.png`) | `src/make_figures.py` (reads run1, edge100, edge50) | `docs/figures/live_delay.png` | ✅ |
| NFStream defect: 82.5→15.6 s, 49.2→15.5 s, 64.5% | `src/run_bug_check.sh` (step 6) | `results/nfstream_bug_check.md` | ✅ |
| Two-flow repro (export order A,B,A vs B,A,A) | `src/diag/run_lru_repro.sh` | **none**: output goes to stdout only | ⚠️ Claimed in the paper, no result file. |
| Patch diff | `src/make_nfstream_diff.sh` | `patches/nfstream-6.6.0-lru.diff` | ❌ Both untracked. The script hard-codes `/mnt/d` for input and output. |
| ARP watcher (1 high alert at 1.7 s, none elsewhere) | `src/eval_arp.py` (step 7) | `results/arp_eval.md` | ✅ |
| Validation policy (k=1: 128 false; k=10+ign: 1; 0.995/0.996) | `src/tune_block_policy.py` (`run_enforce2.sh` / `run_final_live.sh`) | `results/block_policy.{md,json}` | ✅ |
| **Tab. blocking** (79/19/60/326,268; 9/9/0/163,546; 19/26, 60/1,674, 0/1,675) | `run_final_live.sh` → `src/eval_enforce.py`. Denominators from `src/analysis/blocking_accounting.py` (r5). | `results/live/enforce_{k1,policy}/enforcement.md` (tracked), `results/blocking_accounting.md` (**untracked**) | ⚠️/❌ The eligible-pair denominators and the trigger breakdown (32/21/5/1/1) are only in the untracked file. |
| MITM-triggered false blocks by window (7 vs 14), per-class "after block" (10.5%, 10.3 of 11.1 pts) | `src/analysis/blocking_r6.py` (r6) | `results/blocking_accounting_r6.md` | ❌ Untracked. |
| **Tab. kcurve** | `src/analysis/block_curve.py --tag run1` (`run_analyses.sh`); per-class columns from `blocking_accounting.py` | `results/live/run1/block_curve.md` (tracked), `results/blocking_accounting.md` §k-table (untracked) | ⚠️ Values match. Per-class columns come only from the untracked file. |
| Per-class live counts (Mirai 4–5, MITM 2, Web 12) | `src/analysis/perclass_counts.py` (r6) | `results/live/perclass_counts.md` | ❌ Untracked. |
| **Tab. checklist** | n/a (qualitative); claims that scripts are in `src/analysis/` and `src/iot23/` | — | ❌ `src/iot23/` is not in the repo as staged, so the claim fails on the public repo. |

**Spot-check outcome.** All roughly 60 numbers I checked match a file in `results/`. There is one factual mismatch: the "--" cell in Table repeats. I found **no** case of a script writing to a file that the paper cites under a different name.

Some result files have **no producing script**, and nothing in the repo says how they were made:
- `results/repeats.md` (hand-written summary that the paper's Table repeats is based on)
- `results/iot23/cluster_sensitivity_run1_mislabelled.md` (stale output of an earlier buggy run; it will confuse evaluators)
- `results/download.log`, `results/iot23/download.log`, `results/iot23/extract_label.log` (manual `tee` captures)

---

## 3. Blocking problems

**B1. Paper-critical code and results are not in the repository as staged.** About 67 files are present on disk but absent from `.git/index`:
- `src/iot23/*` (11 files)
- `src/analysis/{blocking_accounting, blocking_r6, cluster_sensitivity_cic, cluster_sensitivity_cic_present, download_official_csv, official_csv_baseline, paired_diff, perclass_counts, random_seed_spread, same_window}.py`
- `src/run_review_r5..r8.sh`, `src/make_nfstream_diff.sh`
- `patches/nfstream-6.6.0-lru.diff`
- `results/iot23/*.md`
- `results/{paired_diff, random_seed_spread, cluster_sensitivity_cic*, blocking_accounting*, official_csv_baseline}.md`
- `results/live/{same_window, perclass_counts}.md`

None of these is gitignored; they were simply never added. Without them the IoT-23 half of the paper, the paired-bootstrap and clustering claims, and the patch diff named in the Artifact Availability paragraph are all absent. The paper's sentence "scripts that reproduce every number are available" is false for the public repo today.

**B2. No archival release.** There are no git tags and no Zenodo DOI. The paper has a placeholder comment for both. An "Available" badge requires a persistent archive that pins the exact version.

**B3. The live harness used for run1 and edge100 no longer exists.** `topology/live_experiment.py` now always runs the quiet-wait and per-window reset. The paper itself says run1 and the one-core run used an earlier harness without them. There is no flag such as `--legacy-harness`, so `run_live3.sh` produces runs that differ from the reported ones. This affects Tab. repeats, Fig. delay, the fidelity numbers and Tab. kcurve, which is computed on the run1 verdict stream. Either add a switch that restores the old behaviour, or say explicitly in the README and the paper that exact re-execution of run1/edge100 is not possible and the final-harness repeats are the reproducible reference.

**B4. Raw live outputs needed by the analysis scripts are gitignored.** `.gitignore` excludes `results/live/*/flows.csv`, about 360 MB in total. That input is required by `match_live_offline.py`, `block_curve.py`, `blocking_accounting.py`, `blocking_r6.py`, `same_window.py`, `round2_checks.py`, `eval_live.py` and `eval_enforce.py`. `data/processed/*.parquet` (30 + 41 MB) and `results/models/*.pkl` (6.5 MB) are ignored too. As a result an evaluator cannot re-derive any live table or any post-hoc analysis without a full Mininet re-run on WSL2, and that re-run will not reproduce the same flows (B3, timing). Put these in the Zenodo archive.

**B5. Undocumented pipelines.** The README "Reproduce" section covers only the CIC-IoT2023 core (steps 1–7). It does not mention:
- the IoT-23 download, extraction and analysis order
- the official-CSV download and baseline
- `src/analysis/run_analyses.sh`, `src/analysis/run_repeats.sh` or `run_review_r5..r8.sh`
- `round2_checks.py` and `cluster_sensitivity_cic_present.py`, which have no driver at all

The README text is also out of date and contradicts the paper:
- "One dataset … IoT-23 is future work"
- "Each live setting was run once"
- live CIs [0.710, 0.845], which are flow-level, against the host-pair CIs in the paper
- replay rate "69–77%", against "52–77%" in the paper

**B6. Hard-coded absolute paths.** The following files contain `cd /mnt/d/EdgeFlow-IDS/src` or similar and fail on any other checkout location:
- `src/run_review_r5.sh`, `r6.sh`, `r7.sh`, `r8.sh`
- `src/iot23/run_splits.sh`
- `src/make_nfstream_diff.sh` (input **and** output paths)
- `src/diag/_peek_iot23_r7.py`

`/opt/edgeflow/bin/python` is also hard-coded in every driver, in `src/eval_arp.py` (instead of `sys.executable`) and in `topology/live_experiment.py` (`VENV_PY`). That one is documented in the README, but it should be overridable, for example with `PY=${EDGEFLOW_PY:-/opt/edgeflow/bin/python}`.

---

## 4. Other findings (non-blocking)

**Dependencies and environment**
- `requirements.txt` pins 8 direct packages: nfstream 6.6.0, scikit-learn 1.9.1, pymoo 0.6.2, pandas 3.1.0, pyarrow 26.0.0, numpy 2.5.4, tabulate 0.10.0, matplotlib 3.11.2.
- Transitive packages are **not** pinned: scipy, joblib, threadpoolctl, cffi/psutil (nfstream), and autograd/cma/dill/Deprecated (pymoo). No lock file or `pip freeze` output is included. The pickled models depend on the sklearn/numpy ABI.
- The Python version (3.12, the Ubuntu 24.04 system interpreter) is stated in the README but not enforced.
- System package versions are not recorded: Open vSwitch, tcpreplay, tshark/tcpdump, libpcap. Only "Mininet 2.3.0" and "kernel 6.6" are given.
- The WSL bring-up steps (`modprobe openvswitch`, `service openvswitch-switch start`) appear only in `docs/VERIFIED_TOOLCHAIN.md`, which is marked "kept for history". The README covers only `systemd=true`.

**NFStream patch**
- `setup_venv.sh` applies the patch automatically, and `run_live3.sh`, `run_final_live.sh` and `run_repeats.sh` re-apply it idempotently.
- `run_bug_check.sh` reverts and restores the patch with a trap. Good.
- `run_all.sh` (offline extraction) does not check whether the patch is applied. This does not matter for the features, as the paper argues, but it should be stated.
- The `.diff` was produced from the installed package. `make_nfstream_diff.sh` optionally cross-checks it against the PyPI wheel. Keep that check and record its output.

**Seeds**
- The "seed 0 everywhere" claim **holds in the code**:
  - `train_baseline.SEED=0` (split, DT/RF/HGB, flow bootstrap)
  - `EDGE_TREE.random_state=0`
  - `nsga_select --seed 0` (sampling and pymoo)
  - `B=1000`, `SEED=0` in all cluster-bootstrap modules
  - `extract_flows` sampling uses `random_state=0`, but sampling is off by default
- One fragility: `config.py` silently falls back to `max_depth=16, min_samples_leaf=10` when `results/edge_tree.json` is missing. Running `train_baseline.py` or any `src/iot23/*` script before `tune_edge_tree.py` would therefore give a different "deployed tree" with no warning. The IoT-23 scripts depend on the CIC tuning output through this mechanism. Document this, or fail loudly.

**Data acquisition**
- **CIC-IoT2023 pcaps.** `src/download_data.sh all` fetches 10 named files from the **unofficial** Hugging Face mirror `bencorn/CIC-IoT-2023` at `resolve/main` (no pinned revision). The paper says only that the data are "available from their authors" and mentions the mirror only for the CSVs. Disclose that the pcaps also came from the mirror. Publish SHA-256 sums of the 10 pcaps, of the 5 trimmed pcaps (deterministic `tcpdump -c 1000000`) and of the 10 live-window pcaps, and pin an HF commit hash.
- **Official CSVs.** `src/analysis/download_official_csv.py` uses the same mirror at `CSV/CSV/<Folder>/<file>.pcap.csv`. It has no hashes, and it requires the pcaps to be present first, because it iterates over them.
- **IoT-23.** `src/iot23/download.py` downloads from `mcfp.felk.cvut.cz` (live server) and names the scenarios exactly. The Zenodo DOI 10.5281/zenodo.4743746 appears only in a docstring. It has no hashes, but it does record a `sizes.csv`, which is untracked. `docs/DATASETS.md` still lists the old plan of 5 scenarios (~265 MB); the paper uses 10 (~869 MB on disk).

**Scripts**
- `run_live3.sh` and `run_bug_check.sh` lack `set -e`.
- `run_live3.log` shows the tag `enforce`, while the script now uses `enforce_k1`. The committed log does not match the committed script.
- The README says `run_final_live.sh` produced the committed `enforce_*` and `edge50` runs, but the numbered steps call `run_live3.sh` and `run_enforce2.sh`. Following the steps re-tunes the policy twice and overwrites runs in a different order from the one that produced the results.

**Results and paper text**
- `results/iot23/cluster_sensitivity_run1_mislabelled.md` is a stale output with no producer. Delete it, or keep it with a note.
- `src/diag/_peek_iot23_r7.py` is a throwaway script with an absolute path. Delete it.
- Paper wording: the recall CIs in the splits paragraph (`round2_checks.md`) are for the **edge tree**, while Table perclass is the baseline decision tree. Name the model.
- `src/diag/run_lru_repro.sh` only prints its output. Commit `results/nfstream_lru_repro.txt` so the A,B,A / B,A,A claim has evidence.
- `notebooks/` is empty. Remove it, or drop it from the docs if it is mentioned.

---

## 5. Prioritized fix list

### P0: required before the "Available" badge
1. **Add the untracked artifact files** (B1): `src/iot23/`, `patches/`, the 10 `src/analysis/*.py` listed above, `src/run_review_r5..r8.sh`, `src/make_nfstream_diff.sh`, `results/iot23/*.md`, `results/{paired_diff, random_seed_spread, cluster_sensitivity_cic, cluster_sensitivity_cic_present, blocking_accounting, blocking_accounting_r6, official_csv_baseline}.md`, `results/live/{same_window, perclass_counts}.md`. Delete `src/diag/_peek_iot23_r7.py` and `results/iot23/cluster_sensitivity_run1_mislabelled.md`, or document them.
2. **Tag a release** (for example `v1.0-paper`), archive it on Zenodo, and fill in the paper placeholder with the tag and DOI.
3. **Zenodo data bundle** (B4). Licensing allows these derived files:
   - `data/processed/flows.parquet` (30 MB) and `iot23_flows.parquet` (41 MB)
   - `results/models/*.pkl` (6.5 MB) together with `pip freeze`
   - `results/live/*/flows.csv` and `arp_watch.log` (~360 MB)
   - `data/raw/live/manifest.json`, `data/raw/iot23/sizes.csv`
   - SHA-256 sums of all inputs

   With this bundle, every post-hoc table can be regenerated without Mininet.

### P1: required for "Functional"
4. **Remove hard-coded paths** (B6). Replace `cd /mnt/d/EdgeFlow-IDS/src` with `cd "$(dirname "$0")"` (or `/..` as appropriate). Make `PY` overridable in every driver. Use `sys.executable` in `eval_arp.py`, and an env var for `VENV_PY` in `topology/live_experiment.py`.
5. **Add one driver per paper part**, for example:
   - `src/reproduce_offline.sh`: CIC tables, figures, `run_analyses.sh`, round-2/r5/r8 CIC analyses, `round2_checks.py`, `cluster_sensitivity_cic_present.py`
   - `src/iot23/reproduce_iot23.sh`: download → extract_label → label_shares → file_label_baseline → splits → common_class_ci → fpr_per_capture → zeek_agreement → spanning_common → cluster_sensitivity
   - `src/analysis/reproduce_official_csv.sh`
   - `src/reproduce_live.sh`: the exact sequence behind the committed runs (run_live3 for run1/edge100 → run_final_live → run_repeats → bug_check → post-hoc analyses)
6. **Add a script that generates Table repeats** (for example `src/analysis/repeats_table.py`, reading `live_vs_offline.json` and `same_window.md`). Then mark `results/repeats.md` as generated, or drop it. Fix the paper's One-core "Live flows" cell to 142,725.
7. **Rewrite the README** with these sections:
   - **"Paper ↔ artifact map"**: the table in section 2 of this report, compacted
   - **"Datasets"**: CIC-IoT2023 pcaps and official CSVs (HF mirror, pinned revision, hashes, UNB registration note), IoT-23 (10 scenarios, server URL + Zenodo DOI, ~869 MB), and the trimming rule
   - **"Environment"**: Windows 11 + WSL2 Ubuntu 24.04, kernel 6.6, `systemd=true`, `modprobe openvswitch`, OVS service start, exact `dpkg -l` versions of mininet/openvswitch/tcpreplay/tshark, Python 3.12.x
   - **"Expected runtime and disk"**: download ~5 GB + 0.9 GB, trimmed 2.6 GB, extraction time, ~20 min per live run, ~4 h total
   - **"What is deterministic"**: offline results with seed 0 and expected bit-identity; live results with expected variation, citing the repeats table
   - **"Known non-reproducible items"**: the run1/edge100 harness (B3)
   - Fix the stale statements listed in B5 (IoT-23 "future work", "one run per setting", flow-level CIs, 69–77%)

### P2: strengthens "Reproduced"
8. Restore the pre-reset harness behind a flag (`--legacy-harness`: no quiet wait, no per-window reset) so that run1/edge100 can be re-executed as reported (B3). Otherwise state in the paper that only the final-harness runs can be re-executed.
9. Add `requirements.lock` (full `pip freeze` with hashes) next to `requirements.txt`. Record system package versions in `docs/ENVIRONMENT.md` or in the README.
10. Make `config.py` refuse to fall back silently when `results/edge_tree.json` is missing; print a warning or raise an error.
11. Commit `results/nfstream_lru_repro.txt` (the output of `run_lru_repro.sh`) and the wheel cross-check output of `make_nfstream_diff.sh`.
12. Add `set -euo pipefail` to `run_live3.sh` and `run_bug_check.sh`. Regenerate `run_live3.log`, or note that the `enforce` → `enforce_k1` tag was renamed.
13. Update `docs/DATASETS.md` (IoT-23 scenario list) and say in the paper which model the recall CIs in the splits paragraph refer to.
14. Optional: provide a small smoke test (`download_data.sh small` + `run_all.sh` on 5 small pcaps, without Mininet) that finishes in under 15 minutes, so evaluators can check that the code runs before committing to the full pipeline.

---

## 6. Summary for the committee

The core experimental code is well built: settings are shared between offline and live, seeds are fixed throughout, every metric module writes a self-describing markdown file, and the numbers in the paper trace to result files almost without exception. The main obstacle is **packaging**. About half of the scripts behind the paper's newer claims (IoT-23, paired and cluster-sensitivity bootstraps, official CSVs, blocking denominators, the patch diff) are not in the repository as staged. Several drivers assume `/mnt/d/EdgeFlow-IDS`. The README describes an earlier, single-dataset version of the paper. There is no archived release.

If P0 and P1 are done, I would expect **Available + Functional**, and **Results Reproduced** for the offline and IoT-23 claims. The live claims would be reproducible qualitatively, within the run-to-run variation the paper already reports.
