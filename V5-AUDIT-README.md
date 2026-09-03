# v5 §4.5 Stratified Test — Audit Artifacts (mirror)

This directory mirrors the v5 §4.5 stratified causal test artifacts from the
main paper repo (`codermillat/StudyAbroadGPT`). See the main repo for the
upstream copies; this is the supplementary release.

## Files

- `v5-audit-results.csv` — per-prompt base/LoRA labels + source URLs (input to analyze)
- `v5-audit-catalog.csv` — 149 audited training neighbors (43 verified-wrong)
- `v5-audit-catalog-template.csv` — empty template
- `v5-stratified-prompts.csv` — 50 held-out prompts → 30 C/W/M + 20 excluded
- `v5-stratified-merge-summary.md` — merge coverage + contingency
- `v5-analysis/` — per_stratum, per_prompt, excluded CSVs + summary.txt
- `V5-SECTION-4-5-RESULTS.md` — full results writeup
- `STRATIFIED-TEST-PREREGISTRATION.md` — pre-registered protocol (frozen 2026-09-02)
- `V5-AUDIT-README.md` — this file
- `merge_stratified_audits.py` — helper: 6 batch JSONs → v5-audit-results.csv

## Headline

§4.5 stratified test ran on 30 stratifiable held-out prompts (15 C, 14 W, 1 M);
2 excluded as `unclear` → 28 analyzable pairs.

- **Stratum C (n=14)**: base 0% / LoRA 14.3% error rate; McNemar p=0.4795 (CC).
- **Stratum W (n=13)**: base 38.5% / LoRA 46.2%; McNemar p=1.0 (CC); OR=2.0.
- **Decision rule (§6.4)**: LoRA worse in BOTH strata → "uniformly worse" branch fires,
  but with only 2-3 discordant pairs per stratum, statistical power is far below the
  pre-reg n>=30 "indicative" threshold. We report the test as **direction-consistent
  but under-powered**; data-attribution claim remains **SUPPORTED, NOT ESTABLISHED**.

See `V5-SECTION-4-5-RESULTS.md` for the full writeup.
