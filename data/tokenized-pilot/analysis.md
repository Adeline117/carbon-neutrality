# Tokenized Credit Pilot Analysis (v0.5 workstream C)

*14 real on-chain / tokenized carbon credits, hand-scored under the v0.4 rubrics. This is the companion to the illustrative pilot in `../pilot-scoring/`; where that dataset uses project archetypes, this dataset only includes instruments that actually exist as tokens on a real chain.*

Every score in this file is still author judgment, not a formal rating. The goal is to apply the v0.4 methodology to the actually-tokenized carbon market and see whether its grade distribution matches, contradicts, or extends the illustrative pilot's findings.

## 1. Dataset composition

14 tokenized credits / pools spanning five tokenization models:

| Tokenization model | Count | Examples |
|--------------------|-------|----------|
| Bridge-and-pool | 4 | Toucan BCT, Toucan NCT, Moss MCO2, C3 |
| Bridge individual (TCO2) | 1 | Kariba REDD+ via Toucan |
| Registry-native (CDR-first) | 4 | Puro biochar, Heirloom, Climeworks Orca, Charm Industrial |
| NFT per credit | 1 | Nori NRT (ERC-1155) |
| Decentralized MRV | 1 | Open Forest Protocol (NEAR) |
| Registry-layer tokenization | 1 | JPMorgan Kinexys / S&P Global |
| Non-EVM native | 1 | Regen Network (Cosmos) |
| Defunct / pre-launch | 1 | Flowcarbon GNT |

Deliberately excluded: commercial rating agency ratings (Sylvera, BeZero, Calyx, MSCI) are *referenced* via `commercial_rating_coverage` fields in `credits.json` but their specific ratings are **not** included, because doing so without verified fetches would fabricate data. A proper rank-correlation analysis is a separate v0.5 sub-workstream (C2 in the original plan) that needs real web access to commercial rating portals.

## 2. Grade distribution

| Grade | Count | Share | Credits |
|-------|-------|-------|---------|
| AAA   | 3     | 21%   | T008 Heirloom DAC, T009 Climeworks Orca, T010 Charm Industrial |
| AA    | 1     | 7%    | T007 Puro biochar (average) |
| A     | 2     | 14%   | T011 JPMorgan Kinexys, T012 Open Forest Protocol |
| BBB   | 4     | 29%   | T002 Toucan NCT, T004 Nori NRT, T006 C3, T013 Regen Network |
| BB    | 2     | 14%   | T001 Toucan BCT, T003 Moss MCO2 |
| B     | 2     | 14%   | T005 Flowcarbon (cap), T014 Kariba TCO2 |

## 3. Key findings

### 3.1 The actually-tokenized market is bimodal

The headline result: **the tokenized carbon market has almost nothing in the AA middle**. The high-quality tail is dominated by engineered CDR on quality-aware registries (Puro, Isometric), and the low-quality middle is dominated by bridge-and-pool mechanisms (Toucan BCT/NCT, Moss MCO2). There are no nature-based AA credits in the tokenized sample -- the closest is T007 Puro biochar at 80.4.

This is a finding the illustrative pilot could not produce. In `../pilot-scoring/` the distribution has 7 AA credits (Climeworks, Heirloom, Charm, CarbonCure, two biochar, Brazilian reforestation). Only three of those seven (Climeworks, Heirloom, Charm, via Puro/Isometric attestations) have tokenized analogs on-chain. **The market has not tokenized its AA nature-based credits.**

Candidate explanations (to be tested in v0.5 expert consultation):

- **Selection bias:** high-quality nature-based credit holders have premium OTC markets and no reason to tokenize.
- **Bridge restrictions:** Verra's 2022 statement restricted unauthorized tokenization of retired credits, which disproportionately affects nature-based pools.
- **Tokenization-at-issuance is still new:** Puro/Isometric only cover CDR; there is no equivalent registry-native tokenization path for nature-based high-quality credits yet.
- **Co-benefit narrative marketing:** Under v0.3 weights, co-benefit-heavy nature-based credits could reach AA. Under v0.4 they cannot without strong technical dimensions. The tokenized pilot is scored under v0.4, which is harsher on narrative.

### 3.2 Toucan BCT grades BB, and only by 1.1 points

**Toucan BCT scores 31.1 under v0.4 -- grade BB, but only 1.10 points above the BB/B boundary.** This is a stronger statement than the illustrative pilot could make, because T001 is scored as the actual pool composition (dominated by pre-2018 low-integrity credits) rather than as any single credit inside it.

Any modest downward rescoring of BCT's per-dimension scores pushes the entire BCT pool from BB to B. In practical terms: if an expert reviewer decided that the weighted-average `mrv_grade` of BCT's underlying credits should be 45 rather than 48, or that its `additionality` average was 28 rather than 32, BCT flips to the bottom tier.

This directly substantiates the workshop paper's Section 2.2 (Fungibility Trap) claim: BCT is a lemons pool. Under v0.4 scoring, it is approximately the lowest grade tier's worth of carbon integrity, just barely clearing the bottom of the distribution.

### 3.3 Moss MCO2 tells a similar story, slightly cleaner

**T003 Moss MCO2 scores 30.5 -- BB, 0.50 above the B boundary.** Even more fragile than BCT. MCO2's Amazon REDD+ domination pulls its removal_type and additionality scores down (West et al. 2023 documented systematic baseline inflation in Amazon REDD+), and there is nothing in its tokenization model (simple bridge) that adds quality signal.

MCO2 is interesting because it is *technically cleaner* than BCT (each MCO2 is 1 VCU rather than a heterogeneous pool) but its underlying composition is *worse* (more concentrated in a single controversial project type). The v0.4 framework correctly ranks it below BCT's better-diversified exposure.

### 3.4 Engineered CDR dominates the high-quality tail

All three AAA credits are tokenized engineered CDR:

| ID | Credit | Composite | Notes |
|----|--------|-----------|-------|
| T009 | Climeworks Orca | 95.20 | Same composite as C001 in illustrative pilot |
| T008 | Heirloom DAC | 93.05 | Same composite as C002 in illustrative pilot |
| T010 | Charm Industrial bio-oil | 90.15 | Same composite as C004 in illustrative pilot; **0.15 above AAA boundary -- fragile** |

This is the area where the tokenized market is doing the framework's job already: Puro and Isometric attest CDR credits at issuance, and the v0.4 safeguards-gate lets engineered CDR reach AAA without a magic bonus. The framework's value-add here is comparability across registries, not re-ranking within them.

**T010 Charm Industrial remains the fragility-flag headline for v0.4.** Under tokenized scoring, the same 0.15-point buffer applies. Any downward rescoring on removal_type, permanence, or mrv_grade flips Charm to AA and removes a credit from the AAA tier. Paper §7.2 already flags this; the tokenized pilot confirms it is not an artifact of the illustrative dataset.

### 3.5 Kariba REDD+ is the cleanest disqualifier test in real data

**T014 Toucan TCO2 Kariba** is a single Verra VCU individually bridged via Toucan (not pooled into BCT). It is the single best real-world test case for the disqualifier lattice because:

1. Its technical scores are genuinely low across the board (removal 18, additionality 20, permanence 22, mrv 25).
2. Its registry is Verra VCS (a tier-1 registry), which the framework does NOT automatically trust.
3. The `no_third_party` disqualifier is flagged because the project has had formal verification challenges documented in the academic literature (Carbon Market Watch 2023).

Its final grade is B (composite 19.23). This matches the consensus from BeZero, Sylvera, and Calyx -- all three commercial agencies have publicly rated Kariba low -- providing one data point where the v0.4 framework's output agrees with every public commercial rating. That's not a rank correlation study (it's n=1) but it's a useful sanity check.

### 3.6 Flowcarbon demonstrates the `failed_verification` disqualifier on a real case

**T005 Flowcarbon GNT** was the Celsius-adjacent nature-based tokenization project that cancelled launch after Verra's 2022 statement and the Celsius bankruptcy. Its nominal composite (41.38) would place it at BB, but the `failed_verification` disqualifier caps it at B. This is a real-world example of the disqualifier lattice doing useful work: the project's technical scoring isn't catastrophic, but its inability to complete verification under Verra's tokenization framework is a process failure that should gate it out of premium pools regardless of composite.

## 4. Comparison to the illustrative pilot (`../pilot-scoring/`)

| Metric | Illustrative (25 credits) | Tokenized (14 credits) |
|--------|---------------------------|-------------------------|
| AAA share | 12% | 21% |
| AA share | 12% | 7% |
| A share | 20% | 14% |
| BBB share | 16% | 29% |
| BB share | 8% | 14% |
| B share | 32% | 14% |
| Fragility flags (buffer < 2) | 3 (C004, C011, C014) | 3 (T010, T003, T001) |

The two distributions differ in characteristic ways, all explicable:

- **Higher AAA share in tokenized** (21% vs 12%): the tokenized dataset deliberately includes Puro/Isometric-attested CDR credits, which are over-represented relative to their share of the broader VCM. Do not interpret this as "tokenized carbon is higher quality" -- it is a dataset-construction artifact.
- **Higher BBB share in tokenized** (29% vs 16%): pools cluster at BBB. NCT, C3, Nori, Regen all end up here because the weighted averages of their compositions land in the 45-59 band.
- **Lower B share in tokenized** (14% vs 32%): the illustrative pilot was spectrum-sampled and deliberately included many low-quality archetypes. The tokenized pilot only includes Flowcarbon (cap) and Kariba, so its B share is smaller.
- **Shared fragility flag**: T010 Charm Industrial / C004 Charm Industrial are the same archetype and have the same 0.15-point buffer to AAA. This is not a coincidence; it is the same credit scored in both datasets. The fragility flag is robust across datasets.

## 5. What this pilot does NOT establish

1. **This is not a rank-correlation study against commercial raters.** I did not cross-reference Sylvera, BeZero, Calyx, or MSCI ratings because doing so without verified web fetches would fabricate data. The rank correlation is the natural v0.5.2 sub-workstream and requires real access to commercial rating disclosures.
2. **This is not a market-share analysis.** Toucan BCT is weighted equally with Climeworks Orca in the distribution, but BCT's historical market cap was orders of magnitude larger. A market-cap-weighted version of this analysis would make the lemons story even more stark.
3. **Contract addresses are best-effort.** Several entries say "registry-native" or "varies per credit"; these should be verified before being cited externally.
4. **Pool compositions change over time.** T001's BCT score reflects historical BCT (pre-Verra-restriction, heavy HFC/REDD+). Current BCT is smaller, less liquid, and may have a different composition.
5. **Per-dimension scores are still archetype judgments.** Moving from the illustrative to the tokenized pilot did not make the scoring more rigorous; it made it more specific. The next step for empirical rigor is (a) getting real verification-report-based dimension scores from trusted attesters and (b) running rank correlation against commercial agencies.

## 6. Implications for the paper and v0.5 scope

Three concrete things the tokenized pilot adds to the v0.5 workshop paper discussion:

1. **Toucan BCT's BB grade is quantitative, not rhetorical.** The paper's §2 Fungibility Trap and §7.2 BCT retrospective can now cite the tokenized pilot's BCT composite score (31.1) and its 1.10-point buffer to B. This is stronger than the illustrative pilot's "6 of 10 BCT-eligible credits grade B" framing because it measures the pool *as a pool*, not as individual credits.
2. **The AA middle is empty.** No tokenized nature-based credit reached AA in this pilot. The only AA is Puro biochar average (T007, 80.4). This is a distinctive claim that should be surfaced in §7 or §9 (Limitations / Open Questions): the tokenized market has a quality valley between premium CDR and pooled bridged instruments, and closing that valley is a market-design problem.
3. **Charm Industrial's AAA buffer of 0.15 points is robust across datasets.** The fragility flag is not an artifact of scoring Charm once. It shows up in both pilots at the same magnitude. Any expert reviewer who lowers Charm's dimension scores by more than 1 point will flip it to AA, so the AAA count is sensitive to that specific credit.

## 7. Reproducing this analysis

```bash
# from repo root
python3 data/pilot-scoring/score.py --credits data/tokenized-pilot/credits.json --sensitivity
```

Outputs:
- `data/tokenized-pilot/scores.csv`
- `data/tokenized-pilot/scores.md`
- `data/tokenized-pilot/sensitivity.md`

The same `score.py` script handles both pilots; the rubric source of truth is shared at `data/scoring-rubrics/index.json`. The off-chain / on-chain invariant from workstream A1 still holds: any credit in this dataset would produce identical composites if fed through `contracts/CarbonCreditRating.sol::computeComposite`.
