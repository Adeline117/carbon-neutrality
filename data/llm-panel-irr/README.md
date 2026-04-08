# LLM Panel Inter-Rater Reliability Study (v0.5 W1)

First empirical measurement of the v0.4.1 rubric's inter-rater reliability using an Anthropic-only LLM panel (Opus 4.6, Sonnet 4.6, Haiku 4.5).

## Files

| File | Purpose |
|------|---------|
| `prompt.md` | Canonical scoring prompt; identical across all raters |
| `evidence-packs/credits-redacted.json` | 29 credits from the illustrative pilot with author scores + disqualifiers REMOVED |
| `raw/<model>/scored.json` | Raw per-credit output from each rater |
| `extract_panel.py` | Parses subagent JSONL transcripts into `raw/<model>/scored.json` |
| `irr.py` | Computes Fleiss' κ, Cohen's κ per pair, ICC(2,k), per-dimension agreement, fragility validation, disqualifier recall |
| `irr_summary.json` | Machine-readable headline numbers |
| `panel_scores.csv` | Per-credit per-rater grades and composites |
| `analysis.md` | Full narrative analysis + v0.6 rubric refinement proposals |

## Headline results

- **Grade-level Fleiss' κ = +0.600** (substantial agreement, 3-rater LLM panel)
- **Composite ICC(2,k) = +0.993** (near-perfect on the continuous outcome)
- **Author vs LLM panel median exact agreement = 86%**, 100% within ±1 band
- **C004 Charm Industrial is not robust:** 0/3 LLMs put it at AAA; panel consensus is AA
- **Disqualifier recall: 4/4 stress tests × 3 raters = 12/12** (100%)
- **Weakest rubric dimensions**: registry_methodology (κ=0.168), co_benefits (κ=0.182). Both flagged as v0.6 refinement targets.

## Reproducing

```bash
python3 extract_panel.py   # re-parse rater transcripts if they exist
python3 irr.py             # recompute all statistics
```

Re-running the raters themselves requires the Claude Code subagent tool and the prompt in `prompt.md`.
