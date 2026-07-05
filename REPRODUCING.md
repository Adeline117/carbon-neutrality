# Reproducing the results

Paper: *Transparency without pricing: a credit-level forensic account of collapse
in the first tokenized carbon pool* (submitted to Environmental Research Letters).

All analyses run on cached on-chain data committed to this repository; no API
keys or network access are required for reproduction. Python >= 3.10.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Verify every headline number (10 seconds)

```bash
python3 tools/verify_headline_numbers.py
```

Asserts each headline claim in the manuscript against its cached analysis
output (exit 0 = all consistent): 69.1% renewable composition, +73.9 pp
within-token gap, 0.689 -> 0.506 quality-gate counterfactual (real deposit stream), $146M welfare-gap
median, early-warning trigger and lead time, framework-free early-warning
variant, and the entity-level independence audit.

## 3. Regenerate the figures

```bash
python3 tools/generate_figures.py
```

Figures are written to `docs/figures/` (the manuscript's copies live in `figures/`; the gating figure is `natcomms_fig5_quality_gating`, copied to `figures/fig6_quality_gating`). Most other generated figures belong to companion drafts. The manuscript build
(`docs/natcomms-draft/latex/manuscript.tex`, pdflatex x2) consumes them directly.

## Smart-contract reference implementation

```bash
git submodule update --init lib/forge-std
forge test --gas-report
```

94 tests across 7 suites (rating registry, gated pool, EAS adapter, cross-domain generalization, gas benchmarks).

## Where each headline number lives

| Claim | Analysis output |
|---|---|
| 69.1% renewable / 4.2% REDD+ composition | `data/depositor-analysis/bct_composition_complete.json` |
| 1.87x base-rate over-selection | `data/depositor-analysis/base_rate_analysis.json` |
| Redemption asymmetry (100% vs 3.7%) | `data/depositor-analysis/redemption_analysis.json` |
| Within-token +73.9 pp gap | `data/depositor-analysis/within_token_did.json` |
| Entity-level independence audit | `data/depositor-analysis/entity_funding_analysis.json` |
| $146M welfare gap | `data/statistical-analysis/welfare_quantification_results.json` |
| Quality-gate counterfactual (0.689 -> 0.506, admits 7.2%) | `data/statistical-analysis/quality_gate_real_results.json` |
| Early warning (Lemons Index, ~9-month lead) | `data/depositor-analysis/early_warning_results.json` |
| Framework-free early-warning variant | `data/depositor-analysis/early_warning_framework_free_results.json` |
| Within-type cross-pool check | `data/depositor-analysis/within_type_crosspool_results.json` |
| NFTX cross-asset replication | `data/cross-domain/nftx_dual_margin_results.json` (raw events/sales in `nftx_raw/`) |

Each `*_results.json` is produced by the same-named `*.py` script beside it;
scripts are pure Python with NumPy/SciPy as the only dependencies, except `within_token_did.py`, which additionally needs pandas and statsmodels for its supplementary mixed-effects fit (that fit is variational and run-to-run variable; the paper reports it as directional corroboration only, and the headline +73.9 pp bootstrap does not depend on it). On-chain
records carry transaction hashes for independent verification against the
public Polygon ledger. The placeholder-to-source mapping for every number in
the manuscript mirrors is `results/manifest.json`
(checked by `tools/living-paper/fill_manifest.py --check`).
