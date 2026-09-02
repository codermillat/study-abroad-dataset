# v5 Stratified Causal Test (Audit Material)

This drop adds the v5 §3 pre-registered stratified causal test artifacts
to the dataset repository, so the audit is reproducible from the dataset
side independently of the paper repository.

## Files

| File | Purpose |
|---|---|
| `v5-audit-catalog-template.csv` | 85-row audit template (60 random + 25 high-risk-keyword) generated from the 2,954-row Gemini 1.0 Pro training corpus. Fill in `label` (`verified_correct` / `verified_wrong` / `unclear`), `source_url`, `notes`. |
| `STRATIFIED-TEST-PREREGISTRATION.md` | Frozen 2026-09-02 analysis plan: hypothesis, stratification (C/W/M), sample size, McNemar's test, decision rules. |
| `audit_training_neighbors.py` | Source-verification sampling script. Run with `python3 audit_training_neighbors.py generate --training-data dataset/study_abroad_dataset.jsonl --output v5-audit-catalog.csv --mode mixed --n-random 60 --n-keyword 25 --seed 42`. |
| `V4-DATASET-FACTUALITY-CATALOG.md` | The 4 source-verified dataset D-Cases that anchor the method-vs-data attribution in v4 §4.4. These four rows should be appended to the filled `v5-audit-catalog.csv` as positive controls. |

## Pre-registration

The stratified causal test (loosely §3 of the v5 paper) is pre-registered
to upgrade the v4 "data attribution supported" claim to "established,"
*if* LoRA error rate exceeds base error rate **only** in Stratum W (wrong
neighbors), not in Stratum C (clean neighbors). Full protocol and decision
rules in `STRATIFIED-TEST-PREREGISTRATION.md`.

## Reproducibility

The v5 audit catalog is reproducible from this repo alone:

```bash
python3 audit_training_neighbors.py generate \
  --training-data dataset/study_abroad_dataset.jsonl \
  --output v5-audit-catalog.csv \
  --mode mixed --n-random 60 --n-keyword 25 --seed 42
```

The 4 v4 D-Cases from `V4-DATASET-FACTUALITY-CATALOG.md` are then appended
to the CSV as positive controls before source-verification.
