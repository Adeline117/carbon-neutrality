# Research Status — 2026-04-20 (Nature push)

## Thesis (one sentence)

BCT collapsed because a permissionless bridge self-selected low-quality renewable credits into a uniform-price pool, where a dual-margin Gresham dynamic operated: architectural on entry (bridge attracted low-value supply) and strategic on exit (distinct sophisticated actors extracted high-value credits).

## Honest Assessment: What's Strong, What's Weak, Where We Might Be Fooling Ourselves

### UNASSAILABLE (descriptive facts, on-chain verifiable)

| Finding | Strength | Why |
|---------|----------|-----|
| 69.1% renewable, 4.2% REDD+ | Rock solid | On-chain data, anyone can reproduce |
| 1.87× selection coefficient | Strong | Robust to clustering, sensitivity, base-rate assumptions |
| Redemption differential (REDD+ 99.8% vs Renewable 3.6%) | Strong | On-chain, trivially verifiable |
| Depositor ≠ Redeemer (1.4% overlap) | Strong | On-chain fact |
| 93.5% bridge pass-through | Strong | Factory enumeration is complete |

### SOLID BUT NEEDS HONEST FRAMING

| Finding | Assessment | Honest concern |
|---------|-----------|----------------|
| Granger causality (n=55 weeks) | Moderate | Low power. F=6.32 is significant but barely. And price→quality (F=16.08) is STRONGER than quality→price (F=6.32). If the dominant channel is price→quality, then quality didn't DRIVE the collapse — the crypto winter did, and quality just RESPONDED. |
| "Gresham's law" framing | Under strain | Bridge decomposition shows entry-side is NOT classical Gresham (bad driving out good). It's self-selection (only bad showed up). Gresham only cleanly applies to the EXIT margin. Are we stretching the analogy? |
| CCP validation (d=1.80) | Potentially circular | Removal-type dimension (weight 0.250) basically IS the CCP criterion. If CCP eligibility → high removal-type score → high composite → high d... that's not independent validation, it's tautology with extra steps. |

### WHERE WE MIGHT BE FOOLING OURSELVES

1. **"Price-quality feedback loop" as causal mechanism.** The paper frames bidirectional Granger as "the empirical signature of a uniform-price pooling collapse." But: (a) n=55 is tiny for Granger, (b) the stronger channel is price→quality, not quality→price, (c) the price collapse might be entirely explained by crypto contagion (Terra, FTX) with quality being a passive consequence. We haven't adequately ruled out: "BCT price collapsed because crypto collapsed, and low-quality credits kept depositing because they had nowhere else to go."

2. **The Gresham framing.** Post bridge-decomposition, we know 93.5% of bridged tokens went to BCT. There was no "diverse bridged universe" from which depositors strategically chose. On entry, it's not "bad money drives out good" — it's "only bad money arrived." Gresham requires both types coexisting and one driving out the other. That only happens on the EXIT side. The paper currently uses "architectural on entry, strategic on exit" which is honest, but the TITLE still says "Anatomy of a market failure" implying an active mechanism. Is "a bad pool design attracted bad credits" really a "market failure" in the Gresham/Akerlof sense, or just... bad design?

3. **Quality framework circularity.** The CCP validation is our crown jewel statistic. But if the removal-type dimension (25% of composite) maps directly onto CCP eligibility categories, then d=1.80 is measuring "our rubric agrees with CCP" which is BY CONSTRUCTION. The real test would be: remove removal-type dimension, recompute CCP separation. If d is still large → genuine validation. If d collapses → our framework is just a fancy CCP-proxy with extra dimensions for show.

## Resolved Questions (2026-04-20)

1. ✅ **CCP circularity: NOT CIRCULAR.** Removing removal_type (25% weight) and renormalizing produces a LARGER CCP/non-CCP gap (29.6 vs 29.1 points). The separation is driven by additionality + permanence + MRV, not by the removal_type dimension. Gap retention = 102%.

2. ✅ **Price exogeneity: NOT CONFOUNDED.** BCT vs ETH weekly log-return correlation = 0.200 (p=0.14, NOT significant). Only 4% of BCT's price variance co-moves with the crypto market. BCT's collapse is BCT-specific. The Granger quality→price result has independent power.

3. 🟡 **Gresham framing: ADEQUATE with current caveats.** Bridge decomposition shows entry is architectural, exit is strategic. The paper now explicitly says: (a) permissionless bridge created Gresham incentive structure, (b) exit is classical Gresham, (c) "lower bound by token count." This is an honest framing. No need to change title — "market failure" is accurate regardless of whether entry is strategic or architectural.

## Nature Upgrade: In Progress

**Core insight**: "Adverse selection emerges identically under full public information as under Akerlof's private information, because uniform pricing renders observable quality non-actionable."

**Done:**
- ✅ Formal model (Props 1, 1b, 2, 3 + design space + bridging cost)
- ✅ Nature hook / pitch document
- ✅ All 6 model predictions confirmed empirically
- 🔄 Theory-first restructure (agent running)
- 🔄 Out-of-domain validation search (agent running)

**Remaining:**
- ✅ ~~One non-carbon example~~ → NFTX (exact same mechanism in NFTs) + BendDAO + Chiu et al. 2023 (formal theory)
- ✅ ~~Restructured draft~~ → nature-restructure.md complete (~3,100 words)
- Title: "Adverse selection without private information: architectural failure in transparent tokenized markets"
