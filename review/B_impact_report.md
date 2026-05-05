# Agent B Impact Report — 2026-04-20T12:00

## Run Summary
- Trigger: New experiment `redemption_price_timing_results.json`
- Source: `data/depositor-analysis/redemption_price_timing.py` (first run)
- Status: **NEW FINDINGS — narrative enhancement opportunity**

## New Results (redemption_timing_v1)

| Metric | Value | Significance |
|--------|-------|--------------|
| Temporal quality correlation | ρ = -0.095, p < 10⁻⁷⁰ | Higher-quality credits redeemed earlier |
| Pre-Terra weighted quality | 42.02 | vs post-Terra 32.35 (10-point gap) |
| Depositor-redeemer overlap | 1.4% (399/28,897) | Different populations on each side |
| Redeemer concentration | Gini 0.999, top 10 = 85% | Small group of sophisticated actors |
| Burst coefficient | CV = 17.1 | Programmatic/bot-driven redemptions |
| Pre-Terra tonnage | 1.69M (65% of total redemptions) | Most exit happened early when price was high |

## Narrative Impact Assessment

### **FLAG**: Enhancement opportunity (not direction change)

The existing paper says:
> "Non-renewable credits were preferentially redeemed out of the pool: industrial gas 100% redeemed, REDD+ 99.8%, IFM 93.0%..."

The NEW data adds three dimensions not currently in the paper:

1. **Temporal ordering of exit** — High-quality credits exited FIRST (pre-Terra = quality 42 vs later = 32). The Gresham exit isn't just a static composition difference; it's temporally ordered by price regime.

2. **Population separation** — Only 1.4% of redeemer addresses were also depositors. This kills the "same speculators gaming both sides" counter-narrative. Depositors (509 wallets, low quality) ≠ Redeemers (28,897 addresses, high quality). The Gresham mechanism operates through two distinct populations.

3. **Sophisticated actors drove exit** — Top 10 redeemers = 85% of tonnage, Gini 0.999. Redemption events are extremely bursty (CV = 17.1, median gap = 2 blocks ≈ 4.6 seconds). This is MEV/bot behavior — automated smart contracts cherry-picking high-value credits the moment it's profitable.

### Claims that should be STRENGTHENED (not weakened):

Current paper: "high-quality credits were deposited and then removed because they had greater value outside the uniform-price pool"

Proposed enhancement: Add temporal structure + population separation evidence. This transforms the Gresham claim from descriptive ("high quality exited") to mechanistic ("high quality exited first, driven by a distinct concentrated group of sophisticated actors, not round-trip arbitrage by depositors").

## Action Items

- [ ] **Agent C**: Add 2-3 sentences to Results §2.3 (redemption-side evidence) with temporal and population findings
- [ ] **Agent C**: Add brief mention in Discussion (depositor ≠ redeemer population)
- [ ] No direction change → no human confirmation needed
- [ ] Bridge decomposition experiment pending (needs Dune API — saved as `bridge_decomposition_dune.sql`)

## Figure Impact
- Existing Fig 6 should be UPDATED to show redemption temporal structure (or add supplementary panel)
- No existing figures invalidated
