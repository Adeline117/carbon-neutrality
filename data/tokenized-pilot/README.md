# Tokenized Credit Pilot (v0.5 workstream C)

Hand-scored dataset of 14 real tokenized carbon credits, applied to the v0.4 safeguards-gate rubrics. Companion to the illustrative pilot at `../pilot-scoring/`.

## Files

| File | Purpose |
|------|---------|
| `credits.json` | 14 real on-chain / tokenized carbon credits with per-dimension scores, contract addresses (best-effort), chain, token standard, tokenization model, and commercial rating coverage notes |
| `scores.csv` | Generated: composite scores and grades per credit |
| `scores.md` | Generated: markdown summary table |
| `sensitivity.md` | Generated: weight perturbation, leave-one-out, and key-credit boundary buffer analysis |
| `analysis.md` | Qualitative analysis and comparison to the illustrative pilot |

## Running

```bash
# from repo root
python3 data/pilot-scoring/score.py --credits data/tokenized-pilot/credits.json --sensitivity
```

## Important disclaimers

- Per-dimension scores are author judgment based on public project documentation. They are **not** formal ratings of the named projects or tokens.
- Contract addresses are best-effort from literature; verify before relying on them.
- Pool compositions (BCT, NCT, MCO2, C3) are scored as historical weighted averages. Current compositions may differ.
- Commercial rating agency ratings are referenced in `credits.json` but **not** quoted. A rank-correlation study against Sylvera / BeZero / Calyx / MSCI is a separate v0.5 sub-workstream.
