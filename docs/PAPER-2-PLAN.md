# Paper #2 plan — the method/standard paper (sidesteps the n=1 / causal ceiling)

*Purpose: the empirical paper (#1) is capped at descriptive/cross-sectional. Paper #2 changes the contribution type to **method + standard**, which is judged on usefulness and reproducibility — not causal identification or n. It reuses artifacts that already exist.*

## Key fact: a draft already exists
`docs/www2027-draft/full-paper.md` — **"ERC-CCQR: The Missing Composability Primitive for Real-World Asset Quality"** (target WWW 2027). It already frames the contribution as a composable on-chain quality standard (`meetsGrade()`), validates on carbon credits, generalizes to biodiversity + RECs, and cites the empirical paper as companion `[52]`. **Paper #2 is ~70% written.** The task is to fold in the new audit-method work and tighten — not to start over.

## The gap to fill: a coherent "on-chain RWA quality audit method"
My recent work added three method pieces that are NOT yet in the ERC-CCQR draft and are its strongest novel methods content:

1. **On-chain metadata recovery** (`data/depositor-analysis/c3_metadata_recovery.py`): tokenized credits encode registry+project+vintage in the ERC-20 symbol; recover via `eth_call`, classify via public registry. Turns "unrecoverable" pools into auditable ones.
2. **Cross-pool design→quality measurement** (`crosspool_design_outcome.json`): score N pools by a common framework, rank by screening design. Result: monotone design→quality across **5 pools / 2 operators**.
3. **Real-time early-warning Lemons Index** (`early_warning.py`): prospective composition audit flags a pool ~9 months before price repricing.

Together these are a **measurement/method contribution**: *how to audit the quality of any tokenized RWA pool from public chain data, in real time, and gate on it.* That framing is publishable on its own merits regardless of n=1.

## Reusable artifacts (all already in the repo)
| Component | Artifact |
|---|---|
| Standard + interface | `docs/erc-ccqr.md`, `contracts/ICarbonCreditRating.sol`, `CarbonCreditRating.sol` |
| Gating / composability demos | `contracts/QualityGatedPool.sol`, `examples/{KlimaRetirementGate,CHARQualityOverlay,BiodiversityCreditGate,RenewableEnergyCertGate}.sol` + 7 Foundry tests |
| Metadata recovery | `data/depositor-analysis/c3_metadata_recovery.py` |
| Cross-pool measurement | `crosspool_design_outcome.json`, `score_alt_pools.py` |
| Early warning | `early_warning.py`, `early_warning_results.json` |
| Scoring framework + validation | `data/methodology-ratings/` (Cohen's d=1.87, BeZero ρ=+0.901, κ=0.600) |
| EAS attestation adapter | `CarbonCreditRatingEASAdapter.sol` |

## Recommended contribution structure (5 contributions, all evidenced)
1. **ERC-CCQR standard** — the `meetsGrade()` composability primitive (existing draft §3–4).
2. **On-chain audit method** — metadata recovery + common-framework scoring → audit any RWA pool from public data (NEW; fold in piece 1–2).
3. **Cross-pool evidence it matters** — monotone design→quality across 5 pools/2 operators (NEW; piece 2).
4. **Real-time early warning** — prospective Lemons Index, ~9-month lead (NEW; piece 3).
5. **Generalization** — zero-modification reuse across carbon / biodiversity / RECs (existing, 7 passing tests).

## Concrete next actions
1. Decide venue: **WWW 2027** (web/systems, the existing target) or a measurement/data venue (e.g., a fintech/▷data-systems track) if you want the audit-method framing to lead.
2. Insert a **"Method: auditing tokenized RWA pools from public data"** section into `full-paper.md` drawing on the three scripts above (pull numbers from the JSONs).
3. Add the cross-pool table (Paper #1's `crosspool_design_outcome.json`) as the empirical-utility evidence.
4. Reconcile the companion-paper reference `[52]` with Paper #1's final title.
5. Run the 7 Foundry tests + the three method scripts; pin results.

## What NOT to do
- Do not re-litigate causal identification here — a method/standard paper is not judged on it.
- Do not duplicate Paper #1's forensics; cite it as companion and keep Paper #2 about the *method and standard*.

**Bottom line: Paper #2 is mostly drafted and all its artifacts exist. The remaining work is folding in three method pieces and one cross-pool table, then tightening — a far better use of effort than further increments on Paper #1.**
