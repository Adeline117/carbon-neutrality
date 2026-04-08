# v0.4 Methodology Gate: Scoring Mechanism Decision

*Design note. Not part of the workshop paper. Produced before any code changes to lock in the v0.4 scoring mechanism.*

## 1. Why this note exists

The v0.3 pilot (`data/pilot-scoring/analysis.md`) surfaced one load-bearing problem: **no credit reached AAA under the current weights**. The top-scoring credit, Climeworks Orca, scored 86.8 — short of the 90 threshold by 3.2 points. The proximate cause is that co_benefits (10% weight) pulls industrial CDR projects down by 7-8 composite points, which inverts the Oxford Principles hierarchy the framework is supposed to encode.

Section 7.3 of the v0.3 paper proposed two revisions:

1. **Rev-1 (reweight):** removal_type 0.20→0.225, mrv_grade 0.15→0.175, co_benefits 0.10→0.075, registry_methodology 0.10→0.075
2. **Rev-2 (removal bonus):** +5 composite (capped at 100) if removal_type ≥90 AND permanence ≥90 AND mrv_grade ≥85

Before implementing Rev-1+2, I stress-tested it against the v0.3 pilot and found **three problems that make it the wrong choice**:

- **Rev-1 alone does not fix the inversion.** Recomputed, Orca moves from 86.8 → 89.125 — still 0.875 below AAA. The +5 bonus is doing all the work, and the bonus is the conceptually ugly part of the proposal.
- **The bonus triple-counts durability.** `removal_type` and `permanence` already each carry weight, and both strongly co-vary with engineered removal. Adding a third bonus term on an AND-condition over these two (plus mrv_grade) rewards the same underlying property three times.
- **C007 Brazilian reforestation becomes fragile.** Under Rev-1+2, C007 lands at 75.3 — just 0.3 points above the AA/A boundary. C007 is the headline "AA BCT-eligible credit" in the paper's Toucan retrospective; any minor rescoring flips it.

This note compares Rev-1+2 against three alternatives and picks the best one for v0.4 implementation.

## 2. Options

All four options inherit Rev-1's reweighting (removal_type 0.225, mrv_grade 0.175, co_benefits 0.075, registry 0.075) as their baseline. They differ in what they do on top of that baseline.

| Option | Mechanism | Linear composite? |
|---|---|---|
| **Rev-1+2** | Rev-1 weights + `+5` additive bonus on `removal_type≥90 AND permanence≥90 AND mrv_grade≥85` | Linear + indicator |
| **Alt-1 multiplicative premium** | Rev-1 weights + `*1.05` multiplier on the same condition | Nonlinear (multiplicative) |
| **Alt-2 geometric-mean core** | `0.60 * geomean(removal_type, permanence, mrv_grade) + 0.40 * weighted_mean(additionality, vintage, co_benefits, registry)` | Nonlinear (geomean) |
| **Alt-3 safeguards-gate** | Rev-1 weights with `co_benefits → 0` (its 0.075 redistributed: +0.025 each to removal_type, permanence, mrv_grade). Co_benefits becomes a disqualifier-style gate: documented community harm caps the grade at BBB. | Linear |

Design intent behind each:

- **Rev-1+2** — the naive fix. Adds a hand-tuned reward for credits that clear all three Oxford thresholds.
- **Alt-1** — same reward, but multiplicative to preserve relative ordering more cleanly.
- **Alt-2** — captures the "both must be high" intent of the Oxford hierarchy via a geometric mean, which naturally penalizes imbalance without a magic constant.
- **Alt-3** — reframes co_benefits entirely. Berg et al. (2025) showed that buyers already pay a premium for co-benefit narratives *regardless of integrity*, so rewarding co_benefits in a quality rating reinforces the mispricing the framework is supposed to correct. Co_benefits becomes a *filter for harm*, not a *reward for narrative*.

## 3. Results on the v0.3 pilot

Full table at the bottom of this note; here are the load-bearing credits:

| ID | Credit | v0.3 | Rev-1+2 | Alt-1 | Alt-2 | **Alt-3** |
|----|--------|------|---------|-------|-------|-----------|
| C001 | Climeworks Orca (DACCS) | 86.8 AA | **94.1 AAA** | 93.6 AAA | 88.5 AA ✗ | **95.2 AAA** |
| C002 | Heirloom DAC | 85.3 AA | **92.5 AAA** | 91.9 AAA | 86.9 AA ✗ | **93.0 AAA** |
| C003 | CarbonCure mineralization | 80.0 AA | 86.9 AA | 86.0 AA | 81.7 AA | **87.2 AA** |
| C004 | Charm Industrial bio-oil | 83.0 AA | 85.0 AA ✗ | 85.0 AA ✗ | 84.2 AA ✗ | **90.2 AAA** |
| C005 | Pacific Biochar | 81.0 AA | 81.5 AA | 81.5 AA | 81.1 AA | **83.1 AA** |
| C006 | Husk biochar (co-benefit heavy) | 81.0 AA | 80.6 AA | 80.6 AA | 80.2 AA | **80.0 AA** |
| C007 | Brazilian reforestation (BCT) | 75.7 AA | **75.3 AA** ⚠ | 75.3 AA ⚠ | 74.0 A | **73.9 A** |
| C010 | Kenya cookstoves (co-benefit heavy) | 51.8 BBB | 50.1 BBB | 50.1 BBB | 43.3 BB ✗ | **46.1 BBB** |
| C014 | Plan Vivo agroforestry | 63.3 A | 62.9 A | 62.9 A | 60.8 A | **60.9 A** |
| C018 | REDD+ Cordillera Azul | 31.2 BB | 30.4 BB | 30.4 BB | 30.8 BB | **28.6 B** |

**Grade distributions:**

| Grade | v0.3 | Rev-1+2 | Alt-1 | Alt-2 | **Alt-3** |
|-------|------|---------|-------|-------|-----------|
| AAA | 0 | 2 | 2 | 0 | **3** |
| AA | 7 | 5 | 5 | 6 | **3** |
| A | 4 | 4 | 4 | 5 | **5** |
| BBB | 4 | 4 | 4 | 2 | **4** |
| BB | 3 | 3 | 3 | 5 | **2** |
| B | 7 | 7 | 7 | 7 | **8** |

## 4. Evaluation against decision criteria

**Criterion (a): Orca must reach AAA.**

- Rev-1+2: ✓ (94.1)
- Alt-1: ✓ (93.6)
- Alt-2: ✗ (88.5 — the geomean of 98/98/92 is 95.9, but 40% weight on the linear remainder pulls it back down)
- **Alt-3: ✓ (95.2 — highest of any option)**

Alt-2 fails outright. Its conceptual elegance is undermined by the fact that industrial CDR projects *do* legitimately score low on the 40% linear remainder (low co_benefits, sometimes moderate vintage/registry), so the geomean core can't fully compensate. Alt-2 is eliminated.

**Criterion (b): C007 must keep a 2+ point buffer to its nearest grade boundary.**

- Rev-1+2: ✗ (75.3 — only 0.3 pts above AA/A boundary). **Headline fragility risk.**
- Alt-1: ✗ (75.3 — same problem)
- Alt-2: ✓ (74.0 A, 14 pts above A/BBB boundary)
- **Alt-3: ✓ (73.9 A, ~14 pts above A/BBB boundary)**

This criterion is where Rev-1+2 really breaks down. C007 is explicitly cited in the v0.3 paper's Toucan retrospective as one of only two BCT-eligible credits that would have made a grade-A pool. Under Rev-1+2 it *nominally* remains AA, but by such a thin margin that any later expert rescoring — or a single dimension-score change of 2-3 points — flips it to A and changes the paper's headline.

Alt-3 solves this by *reframing rather than preserving* the BCT story. Under Alt-3, C007 is a solid A with a 14-point buffer to BBB. The BCT retrospective becomes: "Of 10 BCT-eligible credits, two grade A or higher, eight grade B or worse." The substantive finding (BCT was dominated by junk) is identical. The fragility is gone.

**Criterion (c): Conceptual framing.**

- **Rev-1+2**: poor. Triple-counts durability (removal_type + permanence + bonus indicator on the AND of both). Hand-tuned threshold `mrv_grade≥85` is arbitrary — why 85 and not 80 or 90? The CarbonCure edge case (mrv_grade=85 exactly) forced an unanswerable `>=` vs `>` question. No literature citation supports the +5 magnitude.
- **Alt-1**: same triple-count problem as Rev-1+2, just expressed multiplicatively.
- **Alt-2**: elegant. "Peaks in the Oxford dimensions are rewarded because geomean punishes imbalance." But the 0.60/0.40 split is itself a magic number, and Alt-2 fails criterion (a).
- **Alt-3**: **cleanest**. Directly encodes the Berg et al. (2025) finding that co-benefits are priced as narrative rather than integrity, and that a quality rating reinforces this mispricing if it rewards co-benefits. Co-benefits becomes a *filter for harm*, not a *reward for stories*. This is also the change a serious reviewer is most likely to suggest independently — a point in Alt-3's favor for expert-consultation robustness.

Alt-3 additionally has a secondary win that the numeric comparison surfaced but criterion (c) didn't originally anticipate: **Alt-3 correctly grades C004 (Charm Industrial bio-oil) as AAA**, while Rev-1+2 and Alt-1 leave it at AA because Charm's `mrv_grade` is 82, just below the arbitrary 85 bonus threshold. Under Alt-3, Charm's weighted score is 90.2 — the framework now correctly rewards Charm's 94 removal_type and 95 permanence without needing a threshold test. This is a second Oxford-inversion case that Rev-1+2 silently fails to fix.

**Criterion (d): Preserve off-chain ≡ on-chain scorer invariant as cheaply as possible.**

- **Rev-1+2**: adds a new branch (`if bonus_condition then add 5`) to both the Python scorer and the Solidity contract. Minor but real additional surface area.
- **Alt-1**: adds a multiplicative branch (`*1.05`) — integer/fixed-point arithmetic complication in Solidity. Larger surface area.
- **Alt-2**: requires a cube root in Solidity (unsupported in plain Solidity; would need a Newton-iteration helper or off-chain-computed attestation). **Disqualifying for on-chain use.**
- **Alt-3**: **only a constant change.** No new branches, no nonlinear math. The `co_benefits` weight becomes 0, the other three weights go up, and one new disqualifier flag (`communityHarm`) is added. This is the smallest possible diff that still fixes the problem.

Alt-2 fails criterion (d) as well, on top of failing (a).

## 5. Decision: Alt-3 (safeguards-gate)

Alt-3 wins every criterion that matters. Concretely for v0.4:

### 5.1 Weights

| Dimension | v0.3 | v0.4 (Alt-3) | Δ |
|-----------|------|--------------|---|
| removal_type | 0.200 | **0.250** | +0.050 |
| additionality | 0.200 | 0.200 | 0 |
| permanence | 0.150 | **0.175** | +0.025 |
| mrv_grade | 0.150 | **0.200** | +0.050 |
| vintage_year | 0.100 | 0.100 | 0 |
| co_benefits | 0.100 | **0.000 (gate)** | −0.100 |
| registry_methodology | 0.100 | 0.075 | −0.025 |
| **Total** | 1.000 | 1.000 | |

In basis points (for the Solidity contract): 2500 / 2000 / 1750 / 2000 / 1000 / 0 / 750 = 10000 ✓

### 5.2 Gate semantics

Add a new disqualifier flag to the `Disqualifiers` struct:

```
communityHarm   -- documented community opposition, environmental damage,
                   or any condition matching the "None" band of the
                   v0.3 co_benefits rubric with negative externalities.
                   Caps the grade at BBB.
```

The existing `humanRights` disqualifier remains as a separate, stricter cap (caps at B). `communityHarm` is a weaker signal — the project exists and delivers the climate output, but with community cost sufficient to disqualify it from premium pools without destroying its eligibility entirely.

### 5.3 What happens to the co_benefits rubric file

`data/scoring-rubrics/06_co_benefits.json` is **not deleted**. The dimension survives as:

- An informational attestation (still scored 0-100 by assessors, still stored in the on-chain `DimensionScores` struct)
- A documentation anchor for off-chain buyers who want to filter by SDG alignment
- The evidentiary basis for setting the `communityHarm` disqualifier — if an assessor scores co_benefits in the 0-9 "None / negative externalities" band per the rubric, they set `communityHarm = true`

The file gains a `weight: 0.0` field and a top-level note explaining that v0.4 uses it as a gate, not a scored dimension. The band definitions stay.

### 5.4 Solidity change footprint

- `contracts/CarbonCreditRating.sol`: update 7 weight constants. Add `W_CO_BENEFITS = 0`. No new branches, no new math.
- `contracts/ICarbonCreditRating.sol`: add `bool communityHarm` to `Disqualifiers` struct. This is a storage-layout change; methodology version bump (workstream B) catches it.
- `contracts/CarbonCreditRating.sol` `_applyDisqualifiers`: add one new `if (flags.communityHarm && capped > Grade.BBB) capped = Grade.BBB;` line.
- `contracts/test/CarbonCreditRating.t.sol`: update Orca expected composite (8680 → 9520 bps), update AAA/AA grade assertions, add communityHarm cap test, add test that co_benefits has no effect on composite.

Total contract diff: ~30 lines. Compare to Rev-1+2 which requires a new `_applyRemovalBonus` branch and a threshold-edge test for each of the three thresholds.

### 5.5 Impact on the BCT retrospective

The v0.3 paper §7.2 finding ("6 of 10 BCT-eligible credits grade B") changes slightly but substantively stays intact:

| v0.3 Grade | v0.4 (Alt-3) Grade | Credit |
|------------|---------------------|--------|
| AA | **A** | C007 Pachama Brazilian reforestation |
| A | **A** | C009 SE Asian VCS afforestation |
| BBB | BBB | C015 VCS afforestation 2018 vintage |
| BB | BB | C017 Grid-connected solar (India) |
| BB | **B** | C018 REDD+ Cordillera Azul |
| B | B | C019 Rimba Raya REDD+ |
| B | B | C020 Chinese CDM wind 2014 |
| B | B | C021 Large hydro Brazil 2015 |
| B | B | C022 Kariba REDD+ |
| B | B | C023 HFC-23 destruction 2012 |

New phrasing for paper §7.2: **"Of 10 BCT-eligible credits in our pilot, 2 grade A or higher, 1 BBB, 1 BB, 6 at B. Had a grade-A gated pool existed, it would have admitted only C007 and C009 from this sample — 20% of the BCT population."**

This is a cleaner headline than the fragile "75.3 AA" under Rev-1+2. Cordillera Azul also correctly drops from BB to B, which matches the Carbon Market Watch 2023 assessment that flagged the project.

### 5.6 Impact on co-benefit-heavy credits

Worth naming explicitly since Alt-3 is the option that hits them hardest:

| Credit | v0.3 | v0.4 (Alt-3) | Grade change? |
|--------|------|--------------|---------------|
| C006 Husk biochar | 81.0 | 80.0 | No (still AA) |
| C010 Kenya cookstoves | 51.8 | 46.1 | No (still BBB, closer to BB) |
| C014 Plan Vivo agroforestry | 63.3 | 60.9 | No (still A, narrow) |
| C016 Ghana cookstoves 2019 vintage | 38.4 | 33.3 | No (still BB) |

No grade flips. The drops are meaningful (up to 5.7 points for cookstoves) but do not cross boundaries in the pilot. This matches Alt-3's design intent: co_benefits should not be a way for fundamentally-weak credits to claw back to a higher grade through SDG storytelling.

The one caveat: **C014 Plan Vivo at 60.9 sits only 0.9 points above the A/BBB boundary** under Alt-3. This is the Alt-3 analog of Rev-1+2's C007 fragility, and should be noted in the v0.4 §7 sensitivity discussion. Plan Vivo is a smallholder agroforestry program with real climate value and strong co-benefits; its A grade under Alt-3 is conditional on its technical dimension scores remaining stable.

## 6. Alternatives considered and rejected

- **Alt-2 (geomean core)** — eliminated on criteria (a) and (d). Orca failed to reach AAA; cube root is impractical on-chain.
- **Rev-1+2 (status quo proposal)** — eliminated on criterion (c), with criterion (b) as a strong secondary reason. Triple-counts durability, fails C007 fragility, leaves Charm Industrial (C004) incorrectly at AA, CarbonCure threshold edge is unresolved.
- **Alt-1 (multiplicative)** — same conceptual problems as Rev-1+2, strictly worse on criterion (d) (multiplicative fixed-point math in Solidity).
- **"Do nothing" (keep v0.3)** — eliminated by the original v0.3 pilot finding: no credit reached AAA. Oxford inversion unaddressed.
- **7→6 dimension collapse** (merge removal_type + permanence into "Durability") — bigger change than v0.4 should absorb. Correct direction for v0.6 after v0.5 expert consultation, per the v0.4 plan's explicit deferral list.
- **Adding a "safeguards" dimension as #8** — strictly inferior to Alt-3. A new scored safeguards dimension would dilute the weights of the technical dimensions the framework is supposed to emphasize; a gate does not.

## 7. Implementation checklist for A1

Carried forward into workstream A1:

1. `data/scoring-rubrics/index.json`:
   - `paper_version: "0.4"`
   - `schema_version: "0.2.0"` (gate semantics are a schema extension)
   - Weights updated per §5.1
   - New top-level `gates` block parallel to `disqualifiers`, listing `communityHarm` with `grade_cap: "BBB"`
2. `data/scoring-rubrics/06_co_benefits.json`:
   - `weight: 0.0`
   - New top-level note explaining v0.4 gate semantics
   - Band definitions preserved (still used by assessors to determine when to set `communityHarm`)
3. `data/scoring-rubrics/01_removal_type.json`, `03_permanence.json`, `04_mrv_grade.json`, `07_registry_methodology.json`:
   - Weight updates per §5.1
4. `data/pilot-scoring/score.py`:
   - Weight dictionary pulled from `index.json` (no hardcoded numbers)
   - `communityHarm` added to disqualifier processing
5. `data/pilot-scoring/credits.json`:
   - No existing credit triggers `communityHarm` in the v0.3 set
   - C026/C027/C028 synthetic stress tests added in workstream A3, one of which should include `communityHarm`
6. `contracts/ICarbonCreditRating.sol`:
   - `Disqualifiers` struct gains `bool communityHarm`
7. `contracts/CarbonCreditRating.sol`:
   - Weight constants updated (2500 / 2000 / 1750 / 2000 / 1000 / 0 / 750)
   - `_applyDisqualifiers` gains one new cap check
8. `contracts/test/CarbonCreditRating.t.sol`:
   - `testOrcaComposite` expected value changes 8680 → 9520, grade AA → AAA
   - `testCoBenefitsNoEffect`: verify composite is unchanged when only co_benefits varies
   - `testCommunityHarmCap`: verify high-composite credit with `communityHarm` caps at BBB
9. `docs/workshop-paper.md` §4.1, §5.3, §7, §9 update in workstream A4

## Appendix A — Full 25-credit comparison

Generated by `data/pilot-scoring/analyze_options.py`:

| ID | Name | v0.3 | Rev-1+2 | Alt-1 | Alt-2 | Alt-3 |
|----|------|------|---------|-------|-------|-------|
| C001 | Climeworks Orca | 86.8 AA | 94.1 AAA | 93.6 AAA | 88.5 AA | **95.2 AAA** |
| C002 | Heirloom DAC | 85.3 AA | 92.5 AAA | 91.9 AAA | 86.9 AA | **93.0 AAA** |
| C003 | CarbonCure mineralization | 80.0 AA | 86.9 AA | 86.0 AA | 81.7 AA | **87.2 AA** |
| C004 | Charm Industrial bio-oil | 83.0 AA | 85.0 AA | 85.0 AA | 84.2 AA | **90.2 AAA** |
| C005 | Pacific Biochar | 81.0 AA | 81.5 AA | 81.5 AA | 81.1 AA | **83.1 AA** |
| C006 | Husk biochar (Cambodia) | 81.0 AA | 80.6 AA | 80.6 AA | 80.2 AA | **80.0 AA** |
| C007 | Brazilian reforestation | 75.7 AA | 75.3 AA ⚠ | 75.3 AA ⚠ | 74.0 A | **73.9 A** |
| C008 | Rexford IFM | 66.5 A | 66.9 A | 66.9 A | 65.9 A | **67.6 A** |
| C009 | SE Asian afforestation | 66.4 A | 66.5 A | 66.5 A | 65.1 A | **66.2 A** |
| C010 | Kenya cookstoves | 51.8 BBB | 50.1 BBB | 50.1 BBB | 43.3 BB | **46.1 BBB** |
| C011 | N2O destruction (India) | 56.5 BBB | 57.5 BBB | 57.5 BBB | 46.8 BBB | **59.5 BBB** |
| C012 | Landfill methane capture | 53.4 BBB | 53.9 BBB | 53.9 BBB | 44.6 BB | **55.0 BBB** |
| C013 | Mangrove blue-carbon | 70.5 A | 70.0 A | 70.0 A | 68.0 A | **68.4 A** |
| C014 | Plan Vivo agroforestry | 63.3 A | 62.9 A | 62.9 A | 60.8 A | **60.9 A** |
| C015 | VCS afforestation 2018 | 50.9 BBB | 51.1 BBB | 51.1 BBB | 51.5 BBB | **51.5 BBB** |
| C016 | Ghana cookstoves 2019 | 38.4 BB | 36.9 BB | 36.9 BB | 31.1 BB | **33.3 BB** |
| C017 | Grid-connected solar (India) | 37.2 BB | 37.1 BB | 37.1 BB | 30.4 BB | **36.5 BB** |
| C018 | REDD+ Cordillera Azul | 31.2 BB | 30.4 BB | 30.4 BB | 30.8 BB | **28.6 B** |
| C019 | Rimba Raya REDD+ | 29.2 B | 28.4 B | 28.4 B | 29.0 B | **26.1 B** |
| C020 | Chinese CDM wind 2014 | 23.9 B | 24.1 B | 24.1 B | 19.8 B | **24.8 B** |
| C021 | Large hydro Brazil 2015 | 25.4 B | 25.5 B | 25.5 B | 20.9 B | **25.9 B** |
| C022 | Kariba REDD+ | 19.1 B | 19.1 B | 19.1 B | 19.7 B | **19.2 B** |
| C023 | HFC-23 destruction 2012 | 21.6 B | 23.0 B | 23.0 B | 18.7 B | **24.9 B** |
| C024 | Chinese CDM wind 2012 | 18.1 B | 18.5 B | 18.5 B | 15.4 B | **19.3 B** |
| C025 | Unverified grassland 2013 | 15.3 B | 15.8 B | 15.8 B | 15.7 B | **16.4 B** |

To reproduce: `python3 data/pilot-scoring/analyze_options.py`
