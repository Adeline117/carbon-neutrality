# Co-author pitch: Satellite × on-chain audit of tokenized carbon credits

**From:** Adeline Wen (lead author)
**To:** Remote-sensing PI (prospective co-first author)
**Ask:** 3-4 weeks of satellite MRV work in exchange for co-first authorship on a Nature submission. MVP in hand.

---

## The one-paragraph pitch

I have the complete on-chain retirement ledger for the largest tokenized carbon pool (Toucan BCT: 1,187 deposits, 168 Verra projects, 22.0 Mt CO2e). I have project IDs + vintages for every credit. I have a working counterfactual pipeline that already shows **18 of the 18 top-volume Indian renewable projects overclaimed grid-displacement by 20-29%** — 685,000 tonnes of phantom benefit in the top tier alone, using only Ember's public realized Indian grid EF vs CEA's CDM baseline. That MVP result is reproducible from the scripts in the repo. I want to partner with you to add the two things I can't do alone: (1) polygon-based Hansen REDD+ analysis with West-et-al matched-sample counterfactual, and (2) hourly location-resolved grid EF (e.g. WattTime / Tomorrow.io) replacing my annual national EF. Target: *Nature*, co-first authorship.

---

## Why this gets into Nature

Three ingredients, rarely together:

1. **A clean population, not a sample.** Every on-chain retirement is observable. We're not estimating the carbon market — we have it, all 1,187 deposits, fully machine-readable, in one dataset.
2. **A reproducible audit protocol.** The same pipeline extends to any CDM-aligned grid (China, Turkey, Brazil, Indonesia) and any tokenized pool (BCT, NCT, MCO2, Klima). This is an MRV tool, not a one-off result.
3. **Policy timing.** ICVCM Core Carbon Principles are actively excluding BCT-type credits. CORSIA Phase 1 decisions close in 2026. Article 6 authorization for pre-2020 vintage is under negotiation. A quantitative retrospective test lands in exactly the policy window where it matters.

West et al. (2023) — *Science*, forest carbon baselines — is the obvious comp. We extend that framework from forestry to grid, and we do it inside the tokenized-market universe where the transparency wasn't supposed to be broken.

---

## What I have (the on-chain half)

- Complete BCT deposit ledger (`bct_deposits_complete.json`): 1,187 deposits with block number, tx hash, token address, tonnes.
- Per-token metadata (`tco2_metadata.json`): Verra project ID + vintage year parsed from the deterministic TCO2 token name.
- Full 168-project classification by CDM methodology type (`project_classification_final.json`): 69.1% renewable, 10.4% fossil switch, 4.2% REDD+, 5.5% waste/methane, remainder.
- Depositor graph (187 unique addresses) with the full transaction history available via Base L2 RPC — so we can link specific corporate sustainability programmes to specific overclaim magnitudes. This is *new territory* that hasn't appeared in any prior satellite-offset paper.
- **Working MVP pipeline** producing the headline result below from only public/free data.

---

## The MVP result (pre-you)

Pipeline in `data/satellite-analysis/ember_grid_counterfactual.py`:

```
For each Indian renewable BCT deposit with claimed tCO2 C and vintage y:
  MWh_implied = C / EF_CDM_CM(y)            # back out implied generation
  A           = MWh_implied × EF_Ember(y)   # Ember-realized displacement
  overclaim   = C / A
```

| Metric (top 18 projects, each ≥100K tonnes bridged) | Value |
|-----------------------------------------------------|-------|
| Mean overclaim ratio | **1.267** |
| Projects with ratio ≥ 1.2 | **18 / 18** |
| Aggregate claimed displacement | 3,368,904 tCO2 |
| Aggregate Ember-consistent | 2,683,969 tCO2 |
| **Aggregate phantom displacement** | **684,935 tCO2 (+25.5%)** |

Every project is above 1.2×; the uniformity points to a structural baseline-vs-realized gap, not project-level idiosyncrasy. Full per-project table in `data/satellite-analysis/india_cdm_overclaim_analysis.md`.

**Why the MVP tops out at 1.29×, not 1.5×.** Using annual *national-average* EFs, the CDM-CEA vs Ember gap is physically bounded at ~29% — no Indian project can cross 1.5× under this test. Crossing 1.5× requires *hourly, location-resolved* EFs (item 2 in "What I can't do alone" below). For solar specifically, the generation peak (10am-4pm) coincides with the grid's lowest emission-factor hours — which means the claimed displacement, priced against a 24-hour mean EF, overstates real displacement far more than the annual-mean comparison can show. My prediction, once your hourly EF is plugged in: solar projects cross 1.5×, wind stays at 1.2-1.3×, and the aggregate widens to ≥ 35%. This is the headline that secures Nature.

---

## What I can't do alone (your half)

### 1. REDD+ polygon-based satellite analysis

**[UPDATE 2026-04] MVP v2 complete — see `data/satellite-analysis/matched_synthetic_control.py` and `matched_synthetic_control_results.md`.** BCT holds 12 REDD+ projects (Rimba Raya, Mai Ndombe, Kasigau II, Southern Cardamom, Envira, Pacajai, Agrocortex, Mataven, Cordillera Azul, Keo Seima, Brazil Nut, Ecomapua). I've:

- Ingested West et al. 2023's DataverseNL shapefiles and per-polygon covariates for 5 of 12 BCT REDD+ projects (934, 985, 1566, 1650, 1748 — ~69% of BCT REDD+ area).
- Re-implemented the West et al. 2023 MatchIt-cardinal K=10 + generalised synthetic control protocol in Python with DID adjustment (`matched_synthetic_control.py`; runs end-to-end in ~25 min on commodity hardware against the public Hansen COG mirror, no GEE required).
- Produced a primary headline: BCT's 5 West-matched REDD+ projects overclaim by **5.6× (95% CI [3.3, 8.4])**, consistent with West 2023's 3.7× global mean.
- Run a fallback pixel-level estimator for the 7 projects without West-shapefile coverage, using PDD-disc approximations. This inflates to 12.0× all-12 pooled pending real polygons.

Where I need a remote-sensing co-author:

- **Pull the true VCS project polygons for the 7 missing projects** (Rimba Raya, Kariba, Ecomapua, Envira, Brazil Nut, Kasigau II, Agrocortex) from Verra's public methodology uploads, JNR jurisdictional library, or direct negotiation with Verra. This tightens the pooled all-12 estimate from a noisy 12× toward the true 5-8× range.
- **Verify our Python DID re-implementation against West 2023's R `gsynth` output** for the 5 projects we both cover. Cross-check expected: within 10% relative on per-project ATT.
- **Produce an additional leakage-accounted estimator**: for each project, compute the 1-km and 10-km leakage-belt deforestation and net the delta against project avoidance (Guizar-Coutino 2022 style).

### 2. Hourly, location-resolved grid EF

Replace my annual national EF with:

- Hourly generation-mix from CEA / POSOCO public telemetry (you almost certainly have the ETL).
- Location-resolved marginal EF via WattTime Automated Emissions Reduction API (free tier) or Electricity Maps public snapshots.
- Re-run `ember_grid_counterfactual.py` with your EF series to produce a solar-specific, time-of-day-weighted overclaim for each Indian project. My expectation: solar numbers widen vs wind numbers; the aggregate stays > 20%.

### 3. (Optional but valuable) Climate TRACE asset verification

`climate_trace_integration.py` is written — it just needs a reliable network to the TRACE v5 API. From your institution's network it should return matches. Adds a third independent verification layer: "claim says plant exists at location X with capacity Y — TRACE says there is [or isn't] a plant matching that signature."

---

## Named targets (why each)

**Seth Gorelick — Google Earth Engine / Google**
World expert on GEE at scale. Our REDD+ analysis is fundamentally a GEE zonal-stats job; pairing our credit-level on-chain data with Seth's tile-level expertise is a one-plus-one-equals-three combination. Would also unlock GEE's compute credits.

**Alessandro Baccini — Woodwell Climate Research Center (formerly WHRC)**
Canonical author on tropical-forest carbon flux from satellite. His team built the pan-tropical biomass maps that are the obvious ground truth to compare to Verra baselines. If Alessandro's maps say BCT REDD+ projects' biomass is lower than claimed, the story writes itself.

**TreeMap (Crowther lab / UCLA / Stanford)**
Global forest-restoration mapping at 30 m. Relevant for BCT's 3 ARR projects (Bull Run Overseas, Florestal Santa Maria, Le'an Forest Farm) — tests whether actual forest gain matches claimed removals.

**Kanop (Sequoia-backed MRV startup)**
If we want *industry co-signature* rather than academic-only, Kanop brings credibility with purchasers. Trade-off: less methods novelty, more policy reach.

**Open Forest Protocol**
On-chain-native MRV. Closest operational match for our framing — they already believe in transparency-via-chain; they'd co-author happily and bring their own node network's forest data.

**Priority order:**
1. Baccini (Nature-tier track record; biomass maps are the missing ground truth).
2. Gorelick (GEE access + scale story).
3. TreeMap (complementary — ARR angle).
4. Kanop (if we want industry co-author after academic slot is filled).
5. OFP (policy-reach backup).

---

## Timeline I can commit to

- **Week 1** (you + me, once partnership confirmed): Align on polygon source and EF source. I'll send you the coord-resolved project list (`verra_coordinates.json`) and freeze the on-chain cut.
- **Weeks 2-3** (you): Polygon REDD+ analysis + hourly EF rewrite. I'll be on Slack for any data questions.
- **Week 3** (me): Re-run full pipeline with your inputs, produce consolidated tables + figures.
- **Week 4** (both): First draft of Nature submission, internal pre-review with two named outside readers (I have candidates).
- **Week 5**: Submit.

I've already paid the cost of the on-chain data infrastructure and the grid-EF MVP. Your 3 weeks of satellite work are the critical path to a Nature-grade paper.

---

## What success looks like for you

- **Co-first authorship** on a *Nature* submission (or *Nature Sustainability* / *Science Advances* if Nature rejects — we have a downstream plan).
- Ownership of Methods sections 2.2 (REDD+ polygon analysis) and 3.1 (hourly EF) — these are citable contributions in your primary field.
- Your MRV pipeline gets tested against a real, consequential population of credits, not a convenience sample.
- Policy footprint: ICVCM and CORSIA bodies are actively soliciting exactly this kind of retrospective evidence. We will be invited to brief.

---

## Ask

One 45-minute call this week. I'll walk you through the MVP result live. If you're in, I'll send a one-page MoU the same day and we freeze the on-chain cut by end of week.

---

*Contact: adelinewen@stanford.edu · Full repo + MVP: github.com/[redacted]/carbon-neutrality · Pipeline: `data/satellite-analysis/`*
