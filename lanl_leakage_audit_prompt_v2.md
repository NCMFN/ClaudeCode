# LANL leakage-audit pipeline: agent prompt v2

## What changed from v1 (read first)

| # | Problem in v1 | Fix in v2 |
|---|---|---|
| 1 | Signed LANL URL and token were pasted into the prompt, contradicting the secret rule and persisting in the agent's task log. | The prompt contains no URL token. Links are supplied only as environment variables or Colab secrets. The URLs pasted into v1 should be treated as exposed; request fresh ones and never paste them into any prompt. |
| 2 | The link carries a Unix timestamp (1793395825 = 2026-10-30 21:30 UTC). That is very probably the expiry; it passed before this revision. | Stage 0 checks reachability first and stops at the Decision Gate on 401/403/404/410. The user must re-submit the form for fresh links. |
| 3 | The agent was asked to pull a ~7.2 GB file inside its own sandbox and wait for it. Two sessions errored out during the download phase. | Acquisition is split from analysis. Stage 0 (download) is run by the user, or by a resumable detached job. The agent never blocks on a command longer than 10 minutes. |
| 4 | Section numbering was broken: "Section 1" and "Rule 8" were referenced but unnumbered; Sections 0, 8 and 10 were truncated. | Sections renumbered; rules labelled R1 to R14; the test list is restored in full. |
| 5 | Dry run (days 1-2) conflicted with "never analyse a half-downloaded file". | Benchmark-only reads of a partial file are allowed for throughput and memory timing; output is discarded and never reported. |
| 6 | "One pass over auth, never a second pass" conflicted with building features from partitions. | One pass over the gzip file. Later stages read the derived Parquet, which is allowed. |
| 7 | Disk requirement of 20 GB was too low for gzip plus the derived Parquet. | 45 GB free, or the stage stops. |
| 8 | No checkpointing; an interrupted session lost its place. | Each stage is idempotent and writes `outputs/run_state.json`; commit after every stage. |
| 9 | Unmatched-reason precedence was undefined. | Precedence defined in 4.4. |
| 10 | Minimum-positives rule and bootstrap procedure were unspecified. | Both defined in config and in 5.4. |

---

## ROLE

You are a senior ML-security research engineer and reproducibility auditor. Build, run and document a leakage-aware chronological evaluation on the real LANL cyber-security dataset (Kent, 2015). Prepare manuscript fragments that present the work as a temporal-leakage / evaluation-methodology study, not as a validated insider-threat detector.

Work in small commits. Write failing tests first, then code. Run pytest after every task.

---

## 0. INTEGRITY RULES (non-negotiable)

- **R1 Provenance.** Every number in any table, figure, caption or manuscript text is computed by code in this repo from the real LANL files and is traceable through `outputs/provenance.json`.
- **R2 No substitution.** If the real files are absent or unobtainable, follow the Decision Gate (Section 9). Never substitute a mirror, an overlay, a tiny sample or invented numbers and then report results.
- **R3 Forbidden code.** `verify=False`, `curl -k`, `--insecure`, disabled TLS verification; `random.*` creating any label or feature; hardcoded metrics; padding artifacts; a `try/except` that silently falls back to fake data.
- **R4 Forbidden text.** In figures, captions, tables, README and paper text: "illustrative", "schematic", "placeholder", "dummy", "synthetic". The sole exception is a sentence that explicitly describes the earlier flawed pipeline. Also forbidden: any figure whose only content is text, a watermark or a label in place of data or a real diagram.
- **R5 Claims.** Never say the system "detects insider threats", is "validated", "state-of-the-art" or "enterprise-ready". LANL red-team events are authentication events from a red-team exercise, not insider behaviour; say so wherever claims are made.
- **R6 Uncertainty.** Anything uncertain (link expired, column missing, reference unverifiable) goes into `STATUS.md`. Do not guess.
- **R7 Report what was measured**, including inconvenient results, never an expected number.
- **R8 Secrets.** Signed download URLs contain an access token. Never write the full URL or token to any file, commit message, log, `provenance.json`, `STATUS.md`, `links_checked.csv`, README, paper text, test output or the deliverables zip. The only permitted form is the redacted `https://csr.lanl.gov/data-fence/<REDACTED>/cyber1/<file>`. If a token ever appears in the agent's own context, do not echo it.
- **R9 Network scope.** Network access is permitted only for the two user-supplied signed LANL URLs, only through `src/download.py`, plus the public reachability checks in Section 2. Do not guess, rewrite or enumerate other URLs; do not scrape; do not fetch proc, flows or dns; do not try to bypass the form or the expiry.
- **R10 Data scope.** Use only `auth.txt.gz` and `redteam.txt.gz`.
- **R11 Time-boxing.** No single command may block longer than 10 minutes. Long jobs run detached (`nohup ... &`) with a log file and a heartbeat line every 60 s; poll the log. If the sandbox restarts, resume from `outputs/run_state.json`; do not restart from scratch.
- **R12 Commits.** Commit after every completed stage. Never commit raw data, `.part` files, `.env`, or Parquet.
- **R13 Fixtures.** Test fixtures are tiny, schema-faithful, and every file carries the marker `TEST_FIXTURE_NEVER_REPORT`. They never reach `outputs/`, `paper_revision/` or `deliverables/`.
- **R14 No silent scope changes.** If a requirement cannot be met within budget, record it in `STATUS.md` and `revision_log.md` and reduce scope openly (for example, drop a model); never reduce it quietly.

---

## 1. DATA ACCESS

The files are behind a download form at https://csr.lanl.gov/data/cyber1/. The user submits the form and receives two signed, time-limited links. The links are supplied **only** as:

- `LANL_AUTH_URL` and `LANL_REDTEAM_URL` (environment variables), or
- the Colab secrets of the same names (read them into the environment inside `src/download.py`, in memory only).

If neither is set and the files are not local, go to the Decision Gate. Do not ask the user to paste links into the chat or the prompt.

### Resolution order (implemented in `src/download.py` and `src/ingest.py`)

- **Mode A (local).** If `LANL_DATA_DIR` (env) or `data.local_dir` (config, default `data/lanl`) already holds `auth.txt.gz` and `redteam.txt.gz` that pass `gzip -t` and the schema check, use them. No network.
- **Mode B (signed-link download).** Otherwise download the missing file(s) from the env URLs. Runs only with an explicit `--download` flag. Never part of tests.
- **Mode C (nothing works).** Decision Gate, status PROPOSED METHODOLOGY.

### Download procedure

1. Check free disk on the target volume. Require at least 45 GB free (gzip about 7.2 GB, plus derived Parquet and working space). Otherwise stop with the shortfall in `STATUS.md`.
2. Reachability check first: HTTP HEAD, or GET with `Range: bytes=0-0`. Record the redacted URL, status and Content-Length. If the status is 401, 403, 404 or 410, or the body mentions expiry or denial: **stop**. Do not retry in a loop and do not alter the URL. Write `STATUS.md` as `PROPOSED METHODOLOGY: download links expired or denied (HTTP <code>)` and tell the user to re-submit the form and export fresh links, then follow `RESUME.md`.
3. Start `auth.txt.gz` first, detached, then `redteam.txt.gz` (about 4.8 KB). Use TLS verification, follow redirects, fail on HTTP errors, and make it resumable, for example `curl -L --fail --silent --show-error -C - --retry 5 --retry-delay 10 -o <file>.part`. Rename to the final name only after validation. Never pass the URL on a command line that is echoed to a log; pass it through an environment variable.
4. While it runs, do scaffolding, tests and docs. Do not analyse a partial file (benchmark exception in 5.6).
5. Per file record: redacted URL, HTTP status, final host, Content-Length, bytes on disk, retrieval date (UTC), SHA-256 (streamed) in `outputs/provenance.json`.
6. Validate: `gzip -t` (or Python streaming read to EOF); size sanity (auth about 7.2 GB, redteam about 4.8 KB; a large mismatch fails loudly); the first auth line has 9 fields and starts at time 1; redteam has 4 fields and about 749 rows (confirm from the file).
7. If the connection drops, resume with `-C -`. After the retry cap, report the exact byte offset reached and stop at the Decision Gate.
8. Add `data/`, `.env`, `*.part` to `.gitignore`.

### Dataset facts (official page)

58 consecutive days; 1,648,275,307 events across the five LANL files (12,425 users; 17,684 computers); time starts at epoch 1 with 1-second resolution; real timeframe undisclosed; failed authentications are included only for users with at least one successful authentication; comma-delimited, no header, `?` for missing; CC0; cite Kent (2015), DOI 10.17021/1179829.

- `auth.txt`: `time,source user@domain,destination user@domain,source computer,destination computer,authentication type,logon type,authentication orientation,success/failure`
- `redteam.txt`: `time,user@domain,source computer,destination computer`. These events are taken from the authentication data.

### Colab profile (optional)

If `google.colab` is importable: mount Drive only for outputs and small artifacts; keep the gzip and Parquet on the local runtime disk; read links from `google.colab.userdata`; checkpoint `run_state.json` and the committed outputs to Drive after every stage; assume the runtime can disconnect and design every stage to resume. Free runtimes may not hold 45 GB; if `df` shows less, stop at the Decision Gate with the shortfall rather than truncating.

---

## 2. LINKS (Task 0)

Before anything except starting the auth download, fetch every public URL below, record HTTP status, final URL and UTC date in `docs/links_checked.csv`, and mark unreachable ones UNVERIFIED. Never cite an unverified reference as confirmed. Never invent DOIs or page numbers. Tag unconfirmed citations `[VERIFY]`.

**Data and citation:** dataset page https://csr.lanl.gov/data/cyber1/ ; index https://csr.lanl.gov/data/ ; DOI http://dx.doi.org/10.17021/1179829 ; OSTI https://www.osti.gov/biblio/1179829 ; Kent (2015), "Cybersecurity Data Sources for Dynamic Network Research", Dynamic Networks in Cybersecurity, Imperial College Press (BibTeX keys on the page: `akent-2015-enterprise-data`, `kent-2015-cyberdata1`); CC0 https://creativecommons.org/publicdomain/zero/1.0/ ; contact cyberdata@lanl.gov.

**Methodology (verify before citing):** TESSERACT https://www.usenix.org/conference/usenixsecurity19/presentation/pendlebury ; Arp et al. 2022 https://www.usenix.org/conference/usenixsecurity22/presentation/arp ; Kapoor and Narayanan https://reproducible.cs.princeton.edu/ ; Saito and Rehmsmeier https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432 ; Glasser and Lindauer (cite via the KiltHub record https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247 ; often WAF-gated, skip gracefully; secondary only) ; Hyndman and Athanasopoulos https://otexts.com/fpp3/tscv.html

**Tooling:** pyarrow dataset / ParquetFile.iter_batches / csv docs on arrow.apache.org ; Polars, DuckDB, numba ; scikit-learn TimeSeriesSplit (gap parameter), average_precision_score, IsolationForest ; XGBoost ; imbalanced-learn (inside training windows only) ; SHAP (only if non-degenerate) ; SciPy bootstrap (reference only) ; Python `resource` (ru_maxrss units differ by OS) ; pytest ; Matplotlib ; Okabe-Ito palette (Wong 2011, https://www.nature.com/articles/nmeth.1618) ; Poppler pdftotext ; booktabs ; JAIR submission guidelines https://www.jair.org/index.php/jair/about/submissions

The two signed data URLs get only a lightweight reachability check, recorded in redacted form.

---

## 3. STARTING POINT AND REPO STRUCTURE

If a legacy repo or zip is supplied, treat it as untrusted legacy. List its defects in `revision_log.md`, then rebuild rather than patch. Known defects:

- a. `phase1_ingestion.py` used an unofficial mirror with `verify=False`.
- b. Malicious rows received a random `event_type` (`random.choice`): fabricated features.
- c. Benign rows came from only the first ~500,000 lines of `auth.txt`, while red-team events start around day 2 and run to about day 58, so malicious and benign events lived in different time ranges. The resulting near-1.0 PR-AUC (driven by `hour_cos`, zero SHAP on graph/peer features) and the collapse to roughly 0.032 under shift are temporal leakage from sampling, not detection ability. These legacy values are a motivating artefact only; label them as legacy in text and never place them in a results table.
- d. `phase3_modeling.py` used GroupShuffleSplit / StratifiedGroupKFold, not chronological splits.
- e. Every file in `outputs/tables` and `outputs/figures` came from that flawed overlay, including a text-only placeholder figure. Delete them all.
- f. No `requirements.txt`; no paper `.tex`. Deliver LaTeX fragments.

```
config/protocol.yaml
data/lanl/            (git-ignored)
docs/links_checked.csv
.gitignore            (data/, .env, *.part)
src/{download,ingest,sampling,features,protocols,models,evaluate,figures,figure_lint,package_deliverables,run_pipeline}.py
tests/
outputs/{tables,figures,provenance.json,run_state.json,figure_manifest.csv,table_manifest.csv,revision_log.md}
deliverables/{figures,tables,paper,meta}  +  leakage_audit_bundle.zip
paper_revision/       (LaTeX fragments + CHANGES.md)
STATUS.md  README.md  RESUME.md  requirements.txt (pinned)  downloads.md (generated)
```

---

## 4. TASK 1: INGEST AND GROUND TRUTH

- **4.1 Obtain** the files through Section 1 (Mode A or B). Validate on load: gzip integrity; SHA-256 and byte size to provenance; schema (auth 9 fields, no header; redteam 4 fields); non-decreasing time in auth; epoch starts at 1. Fail loudly on any mismatch.
- **4.2 Single pass.** Stream `auth.txt.gz` across the entire file once. Never load it into memory. Never re-read the gzip. Use column-pruned, typed chunks; map strings to integer ids with persisted dictionaries; write day-partitioned Parquet. Later stages may re-read that Parquet.
- **4.3 Labelling.** Label by exact join on `(time, source_user, source_computer, destination_computer)` after documented string normalisation (log the rule). Index red-team rows by timestamp so diagnostics are collected in the same pass.
- **4.4 Unmatched events.** Write `outputs/tables/redteam_unmatched.csv`: one row per unmatched event with exactly one reason code, assigned by this precedence: `outside_file_coverage`, `no_auth_at_timestamp`, `time_match_user_mismatch`, `time_user_match_computer_mismatch`, `multiple_candidates`. Record counts per reason in provenance. Never force-match and never inject red-team rows lacking an auth event.
- **4.5 Features** use only real fields: authentication type, logon type, orientation, success, source and destination computer, user domain. `?` is missing, not data.
- **4.6 Prevalence.** Record true event-level prevalence beside the sampled prevalence in every output.

---

## 5. TASKS 2 AND 3: SAMPLING, CAUSAL FEATURES, PROTOCOLS, MODELS, METRICS

**Memory rule:** never materialise the full dataset and never `pd.concat` over all partitions. Iterate with `iter_batches` on pruned columns and keep only sampled rows.

### 5.1 Sampling

- Equal benign quota per day (or hour) over all 58 days; class balance must not vary with time.
- Deterministic inclusion by hashing `(time, user, src, dst)` with the seed; hash-threshold stream selection, refined to the exact daily quota.
- Count the true daily total `N_d` in the same pass. Weight = `quota_d / N_d`, stored per event, so metrics can be re-weighted to true prevalence. Write per-day counts, quotas and fractions to provenance.
- Red-team-involved users: a documented per-user-per-day cap with recorded weights.
- Write each day's sample to disk as it is produced.

### 5.2 Causal features

- Features at time `t` use only events with time `< t`. No global statistics over the full data.
- No per-row Python state loops at 10^9 scale. Use vectorised or compiled paths (Polars or DuckDB window functions, numba, or per-batch group aggregates merged across batches). Bound per-user and per-host state with capped counters or sketches; caps in config.
- Peer-group z-scores and graph features are fitted on the training window only, then applied to later windows. Scalers, encoders, resampling, thresholds and calibration are fitted inside training or validation windows only.

### 5.3 Protocols (same data, same models)

- **P1** random stratified split.
- **P2** grouped by user.
- **P3** single chronological split: earliest days train, next block validation, latest block test, no overlap, purge gap at each boundary.
- **P4** rolling origin with at least 4 folds and a purge gap at least as long as the longest feature lookback.

### 5.4 Leakage probes and statistics

- Time-only baseline (hour, day index, hour sin/cos) under P1 to P4.
- Label-shuffle control inside each training window.
- Ablations: no time features; no graph or peer features.
- `legacy_sampling_replay`: rebuild the earlier flawed design from real rows only (benign from the first ~500k lines of `auth.txt.gz` plus the real matched red-team events, with the same unmatched reason codes) and run the time-only baseline on it. Report whatever is measured.
- `leakage_delta.csv` (computed in `evaluate.py`): `metric(P1) - metric(P3)` and `metric(P1) - metric(P4)` per model including the time-only baseline, reported separately. Also score P1- and P2-trained models on the P3 test block (paired).
- **Confidence intervals:** block bootstrap resampling days and users within each protocol (not over the ~4 folds), `n_boot` and block length in config, percentile intervals, seed fixed. Never subtract CI endpoints; bootstrap the paired difference.
- **Minimum positives:** `min_positives_per_window` in config. Windows below it report `NA` with a reason code and are marked INCONCLUSIVE, never 0.

### 5.5 Models and metrics

Logistic regression, XGBoost, Isolation Forest. Keep legacy LSTM/MLP/SVM/meta only if they run cleanly within budget; otherwise remove them and say so in `revision_log.md` (R14).

Metrics: PR-AUC with the prevalence baseline, ROC-AUC (secondary), recall at 1, 10 and 100 alerts per day, precision@k, user-level detection (any red-team user flagged; days to first detection), 95% block-bootstrap CIs, positive counts per window.

### 5.6 Reproducibility and dry run

- Fixed seeds, deterministic splits, pinned `requirements.txt`, one entrypoint `python src/run_pipeline.py` with `--download`, `--days A-B` (PARTIAL), `--full`; config in `config/protocol.yaml`.
- **Dry run before any full run:** process days 1-2, record throughput and peak RSS, extrapolate to 58 days, and optimise if the estimate exceeds the budget set in config. A dry run is PARTIAL, labelled everywhere, and never upgrades STATUS.
- **Benchmark exception:** while `auth.txt.gz.part` is still downloading, the first N MB of the gzip stream may be read for throughput and memory timing only. Discard all output; never compute or report metrics from it.

---

## 6. TASK 4: FIGURES

**Measured** (COMPLETED, or PARTIAL with coverage labelled):

- **Figure A.** Class distribution over the 58-day timeline. Top panel: `legacy_sampling_replay` (real rows), malicious vs benign events per day (log y if needed); the caption states it replays the earlier flawed design. Bottom panel: the new time-stratified design on the same axes, with P3 train/validation/test boundaries. Third panel or inset: time-only-baseline PR-AUC under P1 to P4 with block-bootstrap CIs and the prevalence baseline as a dashed line.
- Further measured figures as needed: PR curves by protocol, P1-vs-P3/P4 gap per model, ablation bars, SHAP only if non-degenerate.
- Every measured figure reads numbers from files of the real run and `provenance.json`, and refuses to run if provenance is missing or marks the data partial or fixture without a matching label.

**Conceptual** (any status), filename prefix `concept_`:

- **Figure B.** Methodology diagram: data, time-stratified sampling, causal features, purge gap, chronological train/validation/test or rolling-origin folds, metrics with block-bootstrap CIs. Boxes, arrows, a time axis, the purge gap. No numbers that look like results. Caption begins "Conceptual overview of the proposed protocol (no data shown)."

**Format:** vector PDF plus 300 dpi PNG; `pdf.fonttype=42`, `ps.fonttype=42`; constrained layout; Okabe-Ito palette, legible in greyscale, with markers and linestyles as well as colour; font at least 8 pt at column width; axis labels with units; legend; no baked-in title; no watermark.

**Figure lint** (`src/figure_lint.py`, run at pipeline end and in pytest) fails on: no plotted artists beyond text; R4 strings in extracted text (`pdftotext`); a near-blank PNG (over 98% background); a measured figure without a provenance hash in `figure_manifest.csv` (columns: `filename, type, source_script, source_data_hash, status_at_generation`); figures referenced in `paper_revision/*.tex` that are missing from the manifest, or manifest figures that are unreferenced.

After generation, open every figure image and record in `revision_log.md` what it shows.

---

## 7. TASK 5: PAPER FRAMING

`paper_revision/`: `abstract.tex`, `introduction_contributions.tex`, `related_work.tex`, `methodology.tex`, `results.tex` (tables auto-generated from real CSVs; if PROPOSED, only the protocol and clearly marked hypotheses), `limitations.tex`, `conclusion.tex`, `reproducibility_statement.tex`, `refs.bib` (`[VERIFY]` until confirmed), `CHANGES.md`.

Working title: "Temporal Leakage in Insider-Threat Evaluation: A Chronological Protocol and Audit on the LANL Red-Team Data", plus two alternatives.

Contributions: (1) a documented case study of how time-correlated sampling inflates red-team metrics, with the legacy values as a candid motivating artefact; (2) a leakage-aware chronological protocol; (3) leakage probes as a reusable audit checklist; (4) real-data measurements, only if STATUS is COMPLETED.

Limitations: extreme imbalance; small positive count; single network; 2015-era data; authentication-only modality; red-team exercise is not insider behaviour; failed logons only for users with a successful logon; undisclosed real timeframe; sampling and re-weighting caveat; unmatched red-team events with counts per reason.

Cite Kent (2015) as the page instructs. The reproducibility statement lists data page and DOI, file hashes, commit, seeds and compute, and states that the data were obtained through the LANL download form (redacted link, retrieval date), never the token.

---

## 8. TASKS 6 TO 8: PROVENANCE, CLEAN-UP, PACKAGE

**Provenance** (`outputs/provenance.json`): dataset page URL and DOI; retrieval or placement date; acquisition mode (`local` or `signed_link_download`) with redacted URLs, HTTP status and Content-Length; file sizes; SHA-256; line counts; matched and unmatched counts per reason; per-day `N_d`/quota/fraction; window boundaries; git commit; library versions; status (COMPLETED | PARTIAL | PROPOSED | FIXTURE). Every generator reads it and refuses to run otherwise.

**Clean-up:** delete all legacy synthetic-derived artifacts; rewrite README (no "heavily subsampled", no "Synthetic imbalance ratio", no detector claims); rewrite `revision_log.md` plainly (what was wrong, what changed, every placeholder figure removed, every figure inspected). Grep for "synthetic", "illustrative", "schematic", "placeholder", "random.choice", "verify=False" and "data-fence"; justify or remove every match. The only allowed form of the data-fence host is the redacted one from R8.

**Package layout** (committed, not git-ignored):

```
deliverables/figures   (PDF + 300 dpi PNG)
deliverables/tables    (CSV + booktabs .tex)
deliverables/paper     (paper_revision copy, CHANGES.md, refs.bib)
deliverables/meta      (provenance.json, figure_manifest.csv, table_manifest.csv, STATUS.md, revision_log.md, bundle_sha256.txt)
deliverables/leakage_audit_bundle.zip
```

- Exclude raw LANL data, Parquet, model binaries, `.part` files, `.env`, any file containing a signed URL or token, and any file over 25 MB.
- Delete `deliverables/` before every rebuild. Copy only manifest-listed files that passed `figure_lint` and match `STATUS.md`. Refuse fixture files, legacy artifacts and anything lacking a provenance hash. Run a final token scan over the staged files and abort on any signed-URL pattern.
- `table_manifest.csv` columns: `filename, description, source_script, source_data_hash, status_at_generation, n_rows`.
- Deterministic zip ordering; store its SHA-256 in `bundle_sha256.txt`.
- **Contents by status:** COMPLETED = all measured tables and figures + Figure B. PARTIAL = measured items with coverage in the filename and caption + a PARTIAL banner. PROPOSED = Figure B, protocol tables and paper fragments only.
- Generate `downloads.md` from the actual `deliverables/` contents: status, commit hash and date at the top; the zip first; then Figures, Tables, Paper fragments, Metadata; each entry with filename, one-line description, MEASURED or CONCEPTUAL, size and relative link.

---

## 9. DECISION GATE

- **COMPLETED:** both files present locally (Mode A or successful Mode B), validated, full single pass finished, Sections 4 to 8 ran end to end. `STATUS.md`: `COMPLETED: genuine measurements`.
- **PROPOSED METHODOLOGY:** files absent; links expired or denied (401/403/404/410); download incomplete or corrupt; insufficient disk; no network access in the agent environment; or a full pass not feasible. `STATUS.md`: `PROPOSED METHODOLOGY: no validation performed`, with the exact blocker (HTTP code, byte offset reached, disk shortfall) and a pointer to `RESUME.md`. Delete stale results; ship only Figure B, the protocol tables and the paper fragments. No result figures and no expected curves.
- **PARTIAL:** reportable only as an explicitly labelled partial analysis, with time coverage in every caption and filename suffix (for example `_days01-05`). Fixture and partial runs never upgrade STATUS. A truncated or half-downloaded file is never analysed.

`RESUME.md` must give, in order: (1) re-submit the form and export fresh links as `LANL_AUTH_URL` and `LANL_REDTEAM_URL` (or Colab secrets); (2) `python src/run_pipeline.py --download`; (3) `python src/run_pipeline.py --full`; (4) how to continue from `run_state.json` after an interruption.

---

## 10. TESTS (pytest; all must pass)

- **a.** No `verify=False`, `--insecure` or `curl -k` anywhere in `src`; no label or feature assigned through `random.*`; network code exists only in `src/download.py`, is invoked only through the explicit download path (never by tests or default imports), contacts only `csr.lanl.gov`, and keeps TLS verification on.
- **a2.** Secret hygiene: a repo-wide scan (src, tests, config, docs, outputs, paper_revision, deliverables, STATUS.md, README.md, RESUME.md, and all git-tracked files, including history) finds no full signed URL and no token string. The redaction helper turns any data-fence URL into the redacted form.
- **b.** Ingest: schema validation rejects wrong field counts, a non-decreasing-time violation, and an epoch that does not start at 1; `?` is treated as missing.
- **c.** Labelling: exact-join logic on a fixture; each unmatched reason code is reachable and assigned by the stated precedence; no red-team row is force-matched.
- **d.** Sampling: per-day quotas are exact; weights equal `quota_d / N_d`; the hash selection is deterministic across runs; class balance does not vary with day.
- **e.** Causality: for every feature, changing any event at time `>= t` leaves the feature at `t` unchanged; training-window-only fitting is asserted for scalers, encoders, z-scores and thresholds.
- **f.** Protocols: P3 windows do not overlap; the P4 purge gap is at least the longest lookback; P2 has no user in both train and test; P1 is stratified.
- **g.** Evaluate: bootstrap is deterministic under a seed; the paired-difference CI is not computed by endpoint subtraction; windows below the minimum positives return `NA` with a reason and the INCONCLUSIVE flag, not 0.
- **h.** Provenance: every generator refuses to run when provenance is missing or its status mismatches; fixture files never reach `outputs/` or `deliverables/`.
- **i.** Figure lint: catches a text-only figure, a forbidden string, a near-blank PNG, a missing manifest hash, and unreferenced or missing figures.
- **j.** Packaging: the token scan aborts on a planted signed URL; files over 25 MB are excluded; zip ordering is deterministic; the contents match the status.
- **k.** Download: with a mocked transport, HTTP 401/403/404/410 stop without retrying and write the PROPOSED status; resume uses a range request; the redacted URL is the only form persisted.

---

## 11. FINAL DELIVERABLES AND SELF-CHECK

Deliver everything in `deliverables/` plus the zip and `downloads.md`, with updated `src/`, `tests/`, config, `requirements.txt`, `README.md`, `RESUME.md`, `STATUS.md` and `docs/links_checked.csv`, and a short summary covering:

- what was obtained (files, sizes, hashes, acquisition mode);
- what failed;
- the key leakage numbers (P1 vs P3/P4 vs time-only baseline vs legacy replay), if available;
- what the user must do manually (for example, fetch fresh links).

Before finishing: run pytest and `figure_lint`; open every figure; grep for forbidden strings and for any signed URL or token, and justify or remove each match; confirm that `STATUS.md`, `outputs/`, `deliverables/` and `downloads.md` agree.
