# Adversarial Review: New Claims (2026-04-20)

## Claim 1: "93.5% pass-through means selection is at bridge level"

**Potential attack**: "369 tokens is the COUNT of unique TCO2 contracts. But what about TONNAGE? Maybe the 24 non-BCT tokens represent a huge volume of high-quality credits that weren't deposited."

**Assessment**: VALID CONCERN. We report token count (369 vs 345) but not tonnage. If those 24 non-BCT tokens represent millions of tonnes of nature-based credits, the bridge universe by VOLUME could be more diverse than by count.

**Mitigation needed**: Query total tonnage bridged vs BCT-deposited tonnage. If BCT's 22M tonnes is also ~93% of total bridged tonnage, claim stands. If not, needs reframing.

**Priority**: HIGH — run follow-up Dune query on tonnage.

**Follow-up query**:
```sql
-- Tonnage comparison: bridged vs deposited
SELECT
    CASE WHEN b.erc20Addr IS NOT NULL THEN 'BCT' ELSE 'not_BCT' END AS status,
    COUNT(*) AS n_deposits,
    SUM(b.amount / 1e18) AS total_tonnes
FROM toucan_protocol_polygon.basecarbontonne_evt_deposited b
GROUP BY 1
```
(Note: this only gets BCT tonnage, not total bridged tonnage — would need Transfer events from factory-created tokens to get total bridged volume)

---

## Claim 2: "Depositor ≠ Redeemer (1.4% overlap) rules out round-trip arbitrage"

**Potential attack**: "1.4% is address overlap, but addresses are cheap on Polygon. Same entity could use different addresses for depositing vs redeeming."

**Assessment**: VALID but hard to fully counter. However:
- The QUALITY signature is different: depositors put in low quality (31.7), redeemers take out high quality (38.7). Same entity using different addresses would still need to first deposit low-quality AND have access to high-quality credits already in the pool.
- The TIMING is asymmetric: 509 depositors over 14 months vs 28,897 redeemers, top 10 = 85%. The population sizes alone suggest different actor types.
- Gini coefficients differ: depositor Gini 0.94 vs redeemer Gini 0.999.

**Mitigation**: Already partially addressed — note in paper that address-level separation is a lower bound on population separation. The quality differential and asymmetric population sizes provide additional support.

**Priority**: LOW — acknowledgeable but not fatal.

---

## Claim 3: "Redemption temporal ordering (ρ = -0.095) shows exit is price-responsive"

**Potential attack**: "ρ = -0.095 is tiny. It's only significant because n = 35,432. Practically, this explains < 1% of variance."

**Assessment**: VALID. R² ≈ 0.009. The PHASE breakdown is more compelling (pre-Terra quality 42 vs post-Terra 32 is a 10-point gap). The aggregate ρ is diluted by the 35K renewable micro-redemptions at the end.

**Mitigation**: Lead with phase breakdown (10-point gap), use ρ as a supporting statistic. Current paper text does this correctly — mentions both.

**Priority**: LOW — already well-framed.

---

## Claim 4: "CV = 17.1 indicates bot/MEV behavior"

**Potential attack**: "Burstiness could just be batch processing by the pool contract, not strategic behavior."

**Assessment**: PARTIALLY VALID. Some batch processing is mechanical (e.g., a user redeeming multiple TCO2 types in one session). But:
- Median gap = 2 blocks (4.6 seconds) means consecutive transactions, not batch calls
- Combined with top-10 = 85% concentration, this is consistent with automated strategies
- "Consistent with" is the right framing (not "proves")

**Mitigation**: Current paper uses "consistent with automated smart contract execution" — correct hedge.

**Priority**: NONE — already correctly hedged.

---

## Claim 5: "Gresham is asymmetric: architectural on entry, strategic on exit"

**Potential attack**: "If selection is at bridge level, then the 1.87× selection coefficient vs VCS base rate is NOT a Gresham finding — it's just Toucan's architecture. You can't call it Gresham at all on the entry side."

**Assessment**: THIS IS THE MOST DANGEROUS ATTACK. The paper's title mentions "market failure" and the framing is Gresham. If entry-side selection is architectural (bridge design) rather than strategic (depositor behavior), the Gresham framing only applies to the exit margin.

**Current mitigation**: The paper already says "architectural on entry... strategic on exit" in Discussion. The Gresham framing applies specifically to the DUAL-margin pattern and the exit-side strategic behavior. The base-rate selection coefficient (1.87×) still holds as a descriptive finding even if the mechanism is architectural.

**Additional consideration**: The bridge being permissionless means that the TYPES of actors who chose to bridge were self-selected. It's not that Toucan designed the bridge to attract renewables — it's that renewable credit holders had the strongest incentive to bridge (their credits had the lowest OTC value and the most to gain from uniform-price pooling). This IS Gresham reasoning — it's just operating at the bridge level.

**Priority**: MEDIUM — consider adding one sentence to Discussion clarifying that the bridge's permissionless design creates the SAME incentive structure as Gresham (low-value assets flow toward uniform-price mechanisms).

---

## Summary

| Claim | Risk | Action |
|-------|------|--------|
| 93.5% pass-through (token count) | HIGH | Need tonnage verification |
| Depositor ≠ Redeemer | LOW | Acknowledge address ≠ entity |
| ρ = -0.095 temporal ordering | LOW | Already well-framed |
| CV = 17.1 bot behavior | NONE | Correctly hedged |
| Asymmetric Gresham | MEDIUM | Add bridge incentive sentence |
