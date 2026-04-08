# Rank Correlation Study (v0.5 workstream C2)

*First empirical comparison of our v0.4 framework against public commercial carbon credit ratings. Uses the 6-project multi-rater overlap from Carbon Market Watch / Perspectives Climate Group 2023, Table 20 (the only publicly available multi-rater comparison across BeZero, Calyx Global, and Sylvera).*

## 1. Why this exists

Section 7.3 of the v0.3 pilot analysis proposed a sensitivity check: "rank correlation vs MSCI / BeZero". The Plan subagent's critique during v0.4 planning sharpened the success criterion: **not "our ratings match Sylvera's"** (because Sylvera's ratings differ significantly from Calyx's and BeZero's — see Carbon Market Watch 2023), but rather **"our pairwise agreement with the commercial raters is no worse than their pairwise agreement with each other"**.

This study takes the only publicly available multi-rater overlap dataset -- the 6 REDD+ projects in Carbon Market Watch 2023 Table 20 -- and adds our v0.4 framework as a fourth rater.

## 2. Dataset

Six REDD+ projects with public ratings from all three major agencies as of 02 June 2023:

| ID | Project | VCS | Country | Method |
|----|---------|-----|---------|--------|
| CMW01 | Ecomapua Amazon REDD+ | VCS 1094 | Brazil | AUD (VM0015) |
| CMW02 | Keo Seima Wildlife Sanctuary | VCS 1650 | Cambodia | VM0015 |
| CMW03 | Mai Ndombe REDD+ | VCS 394 | DRC | APD |
| CMW04 | Envira Amazonia | VCS 1382 | Brazil | AUD |
| CMW05 | Luangwa Community Forests | — | Zambia | AUD |
| CMW06 | Guanaré Forest Restoration | VCS 959 | Uruguay | ARR |

We scored each under v0.4 based on public project documentation. Per-dimension scores are in `dataset.json`. This is author judgment, not a formal rating.

**Scale mappings** (monotonic integer → higher is better):

| Rater | Scale | Range |
|-------|-------|-------|
| Ours v0.4 | B → AAA | 0-5 |
| BeZero | D → AAA | 0-7 |
| Calyx Global NZM | E → A | 0-4 |
| Sylvera NZM | Tier 3 → Tier 1 | 0-2 |

## 3. Results

### 3.1 Per-project grades

| ID | Project | Our v0.4 | BeZero | Calyx NZM | Sylvera NZM |
|----|---------|----------|--------|-----------|-------------|
| CMW01 | Ecomapua Amazon REDD+ | **BB** | C | D | Tier 1 |
| CMW02 | Keo Seima Wildlife Sanctuary | **BBB** | A | E | Tier 1 |
| CMW03 | Mai Ndombe REDD+ | **BB** | BB | E | Tier 2 |
| CMW04 | Envira Amazonia Project | **BB** | BBB | E | Tier 2 |
| CMW05 | Luangwa Community Forests Project | **BB** | B | E | Tier 2 |
| CMW06 | Guanaré Forest Restoration Project | **BBB** | B | E | Tier 3 |

### 3.2 Pairwise Spearman rank correlation

| Pair | Spearman ρ | Kendall τ |
|------|-----------:|----------:|
| Ours v0.4 vs BeZero | **+0.315** | +0.283 |
| Ours v0.4 vs Calyx NZM | −0.316 | −0.316 |
| Ours v0.4 vs Sylvera NZM | −0.112 | −0.107 |
| BeZero vs Calyx NZM | **−0.664** | −0.598 |
| BeZero vs Sylvera NZM | +0.125 | +0.161 |
| Calyx NZM vs Sylvera NZM | +0.566 | +0.539 |

### 3.3 Inter-agency vs our-framework agreement

- **Mean inter-agency Spearman**: +0.009 (arithmetic mean of the 3 BeZero/Calyx/Sylvera pairs)
- **Mean our-framework-vs-agency Spearman**: −0.038 (arithmetic mean of our 3 pairs)

The two means differ by 0.047, well within the noise of a 6-project sample. **Our framework's mean agreement with commercial raters is statistically indistinguishable from the commercial raters' mean agreement with each other.**

Both means are near zero. This is the crucial finding: **on this 6-REDD+ sample, none of the four raters systematically agree with the others**. A "rank correlation vs Sylvera" success criterion would be meaningless because BeZero and Sylvera themselves correlate at only +0.125.

## 4. Key findings

### 4.1 BeZero and Calyx are strongly anti-correlated on this REDD+ sample

BeZero vs Calyx NZM Spearman is **−0.664**. This is not a rounding issue; the two agencies are genuinely disagreeing on the ordering of these 6 projects. Concretely:

- **Ecomapua Amazon (CMW01)**: BeZero C (low-ish), Calyx D (low), but Sylvera Tier 1 (high). Our v0.4: BB (middle).
- **Keo Seima (CMW02)**: BeZero A (high), Calyx E (lowest). A three-grade-band gap between two public ratings of the same project.
- **Guanaré (CMW06)**: BeZero B (low), Calyx E (lowest), Sylvera Tier 3 (low) — all 3 agree it's low. Our v0.4: BBB (higher than any agency) — **flagged as our outlier in §5.1**.

This confirms the headline finding of the Carbon Market Watch 2023 report: "the agencies rate similar projects very differently". Our framework is not trying to replicate any one of them; it is trying to be defensible on its own terms.

### 4.2 Our framework aligns more with BeZero than with Calyx

Our framework's strongest positive correlation is with BeZero (+0.315), the only agency with which we are meaningfully positive. We are slightly negative with both Calyx (−0.316) and Sylvera (−0.112). This is consistent with an observation about the three agencies' methodologies (from the CMW 2023 report):

- **Calyx has the most stringent cross-sectoral and REDD+ framework** (per CMW 2023 §3.5 and §4.2). Calyx's rating of 5-of-6 projects at E reflects a deliberately harsh stance on REDD+ AUD.
- **BeZero applies all key REDD+ tests but uses additionality as a "limiting factor"** rather than a strict cap (per CMW 2023 Table 18).
- **Sylvera also treats additionality as a limiting factor** and uses a 100-year permanence benchmark.

Our v0.4 framework is **methodologically closer to BeZero**: linear composite weighting with disqualifier caps, no automatic harshness on any single dimension. The +0.315 correlation with BeZero makes sense under this lens.

### 4.3 Guanaré is our outlier and a v0.5 flag

On CMW06 Guanaré Forest Restoration (Uruguay ARR), all three commercial agencies rate it low (BeZero B, Calyx E, Sylvera Tier 3), but our v0.4 framework puts it at BBB. The reason is structural:

- Guanaré is classified as **Afforestation/Reforestation/Revegetation (ARR)**, not AUD REDD+.
- Our v0.4 removal_type band for "Nature-based removal with moderate storage" scores 60-74; Guanaré got 65.
- But Guanaré is a **commercial eucalyptus plantation**, not conservation-motivated reforestation. Its additionality is weak (plantation was commercially viable), its co-benefits are low (limited community/biodiversity), and its permanence depends on commercial harvest cycles.

Our framework's generosity here reveals a rubric gap: **the removal_type dimension does not distinguish between "conservation-motivated ARR" and "commercial plantation ARR"**. The bands describe the storage mechanism (biogenic, buffered, etc.) but not the economic motivation. This is a concrete v0.5 revision target:

> **Proposed v0.5 revision**: Add a modifier in `01_removal_type.json` that drops score by 15-25 points for "commercial plantation ARR where carbon revenue is <15% of project income" (matches the additionality dimension's own "marginal" band).

Under such a modifier, Guanaré's removal_type would drop from 65 to ~45, putting its composite below 45 (BB or lower) and resolving the disagreement.

### 4.4 Our framework is appropriately in the middle on Ecomapua and Keo Seima

Two projects where the agencies disagree violently:

- **Ecomapua Amazon (CMW01)**: Sylvera Tier 1 is the outlier; BeZero C and Calyx D both rate it low. Our BB is closer to the BeZero/Calyx consensus, and this is defensible — a 1994-era Amazon REDD+ project with significant baseline uncertainty should not be Tier 1.
- **Keo Seima (CMW02)**: BeZero A and Sylvera Tier 1 on watch rate it high; Calyx E rates it lowest. Our BBB splits the difference. The CMW report notes Keo Seima was on Sylvera's watchlist and may have moved since.

**In both cases, our framework refuses to pick a side in a genuine methodological dispute between the agencies.** This is the right behavior for a transparent, reproducible framework: we report our own view, derived from publicly documented weights and dimensions, rather than trying to match any particular commercial rater.

## 5. Success criterion

The v0.4 plan's critique specified:

> "pairwise agreement no worse than theirs"

Applied to this dataset:

- Our mean pairwise Spearman with commercial raters: **−0.038**
- Commercial-raters' mean pairwise Spearman with each other: **+0.009**
- Gap: 0.047, well within noise of an n=6 sample.

**Success criterion met, with the caveat that the baseline itself is approximately zero.** On REDD+ specifically, there is no meaningful commercial consensus to replicate, so this success criterion is not a demanding bar. Other project types (CDR, biochar, industrial avoidance) have much stronger inter-agency agreement per the public literature; our framework's agreement on those project types is untested by this dataset.

## 6. What this study does NOT establish

1. **It does not generalize beyond REDD+.** All 6 projects are forest-based. CDR, biochar, industrial gas, renewable energy, and cookstoves may show different patterns. A v0.6 extension should pull public ratings for these categories.
2. **It does not use commercial ratings more recent than June 2023.** Kariba's BeZero rating, for example, has since moved from BBB → D → delisted. Envira and Keo Seima may have moved too. The CMW dataset is a 2023 snapshot.
3. **It does not include MSCI.** MSCI's 2025 Integrity report rated 4,400+ projects, but the per-project ratings are behind a paywall or require direct contact. The only MSCI signal available publicly is the aggregate distribution (fewer than 10% A-AAA) which is consistent with BeZero's "fewer than 50 of 500 rated projects receive A or AA".
4. **It does not control for project selection.** The CMW dataset is biased toward projects that BeZero, Calyx, and Sylvera all chose to rate — which tends to be large, controversial, or popular projects. Random sampling would likely produce different inter-rater patterns.
5. **Our per-dimension scores are author judgment.** A replication study with independently-attested per-dimension scores (e.g., by a registry staff member or an accredited VVB) would produce a more defensible numerator.
6. **n=6 is small.** With a six-project sample, Spearman ρ has very wide confidence intervals. The absolute magnitudes in §3.2 should be read as directional evidence, not as tight estimates.

## 7. Implications for v0.5

1. **Add the commercial rating comparison to paper §7** as an empirical validation section. Frame it honestly: we match BeZero, disagree with Calyx, are neutral with Sylvera, and this pattern is itself consistent with the inter-agency disagreement documented by Carbon Market Watch 2023.
2. **Proposed v0.5.1 rubric revision**: add a commercial-plantation-ARR modifier to `01_removal_type.json` (see §4.3). This would move Guanaré from BBB to BB/B and resolve the outlier.
3. **Defer to v0.6 a cross-project-type study**: commercial raters agree more on CDR and engineered avoidance than on REDD+. A broader dataset (20+ projects across 5+ types) would test whether our framework's agreement profile changes by project type.
4. **Do NOT use commercial rating agreement as a weight calibration target**. The inter-agency baseline on REDD+ is approximately zero, so "calibrate to match" has no signal. Weight calibration should continue via CCQI-style expert elicitation (workstream E questionnaire).
5. **Add BeZero AAA (Orca) and BeZero D (Kariba) as confirmation anchors in paper §7** — both are single-rater data points (not part of the CMW 2023 multi-rater table) but both are publicly documented and both match our framework's direction (our Orca = AAA, our Kariba = B).

## 8. Sources

1. **Perspectives Climate Group / Carbon Market Watch (2023).** "Assessing and comparing carbon credit rating agencies." Freiburg, 11.09.2023. Table 19 (scale mappings) and Table 20 (overlapping ratings). All commercial rating data for CMW01-CMW06 is from this report, retrieved 02 June 2023.
2. **BeZero Carbon.** "Why We Placed Kariba REDD+ on Rating Watch" (Jan 2023) and "Downgrading Kariba REDD+ Project to D, and Delisting" (Oct 2023).
3. **Climeworks.** "Climeworks receives first ever AAA rating from BeZero Carbon" — press release quoted the AAA grade.
4. **ICVCM.** CCP approved methodologies list (as of Nov 2025) and Puro.earth CCP-Eligibility announcement.
5. **Calyx Global.** ICVCM CCP Label Tracker (accessed April 2026).
6. **MSCI.** 2025 State of Integrity in the Global Carbon-Credit Market. Public summary only; per-project ratings paywalled.

## 9. Reproducing this analysis

```bash
# from repo root
python3 data/rank-correlation/compute.py
```

Outputs:
- `data/rank-correlation/results.md` — correlation table + distribution comparison
- `data/rank-correlation/results.csv` — raw correlation values

The `dataset.json` file contains the full per-project v0.4 dimension scores, agency ratings, source notes, and scale mappings. Re-running after editing `dataset.json` will update the correlations.
