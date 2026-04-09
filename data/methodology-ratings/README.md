# Methodology-Level Archetype Ratings

**318 carbon credit archetypes rated across 17 methodology categories** -- the first
open, machine-readable, uncertainty-quantified quality database for the voluntary
carbon market.

## Overview

This module scales the framework's credit coverage from 45 hand-scored credits to
318 methodology-derived ratings by applying archetype scoring: each project inherits
the typical score profile of its methodology category, adjusted for vintage year.

| Metric | Value |
|--------|-------|
| Total projects rated | 318 |
| Methodology categories | 17 |
| Grade levels | 6 (AAA, AA, A, BBB, BB, B) |
| Registries covered | Verra VCS, Gold Standard, ACR, CAR, CDM, ART TREES, Puro, Isometric |
| Countries represented | 70+ |
| Vintage range | 2012-2026 |

## Grade Distribution

| Grade | Count | Pct | Description |
|-------|-------|-----|-------------|
| AAA | 14 | 4.4% | Premium: engineered removal, high permanence, rigorous MRV |
| AA | 40 | 12.6% | High quality: nature-based removal or strong avoidance with robust verification |
| A | 34 | 10.7% | Standard quality: meets ICVCM Core Carbon Principles |
| BBB | 72 | 22.6% | Acceptable: legacy methodology, adequate verification |
| BB | 77 | 24.2% | Below standard: questionable additionality or weak MRV |
| B | 81 | 25.5% | Low quality: significant integrity concerns |

The distribution is bottom-heavy: ~50% of projects grade BB or below. This reflects
the real VCM, where renewable energy credits (ICVCM-rejected), legacy REDD+ (not
CCP-approved), and HFC-23 projects together constitute a large share of issuances.

## Per-Category Summary

| Category | Archetype ID | N | Typical Grade | Mean Composite | CCP Status |
|----------|-------------|---|---------------|----------------|------------|
| DACCS (geological) | daccs_geological | 14 | AAA | 92.4 | CCP-eligible |
| Bio-oil geological | bio_oil_geological | 8 | AA | 88.1 | CCP-eligible |
| Enhanced weathering | enhanced_weathering | 12 | AA | 83.5 | Under assessment |
| Biochar | biochar | 20 | AA | 78.0 | CCP-eligible |
| ARR (conservation) | arr_conservation | 25 | A | 64.7 | CCP-eligible |
| IFM | ifm | 20 | BBB | 59.8 | CCP-eligible |
| ODS destruction | ods_destruction | 10 | BBB | 54.2 | CCP-eligible |
| Sustainable agriculture | sustainable_agriculture | 16 | BBB | 52.9 | CCP-eligible |
| N2O abatement | n2o_abatement | 10 | BBB | 51.9 | CCP-eligible |
| Landfill gas | landfill_gas | 16 | BBB | 48.6 | CCP-eligible |
| Rice methane | rice_methane | 12 | BB | 44.8 | CCP-eligible |
| REDD+ jurisdictional | redd_jurisdictional | 14 | BB | 44.6 | CCP-eligible |
| Cookstoves | cookstoves | 36 | BB | 41.9 | CCP-eligible (with conditions) |
| ARR (commercial plantation) | arr_commercial_plantation | 12 | BB | 40.6 | Varies |
| REDD+ (project-level) | redd_project | 45 | B | 28.8 | Not CCP |
| Grid renewable energy | grid_renewable_energy | 40 | B | 25.1 | REJECTED |
| HFC-23 destruction | hfc23_destruction | 8 | B | 25.9 | REJECTED |

## Dataset Construction

### Project Sources

The 318 projects are drawn from public registry data and published market reports:

1. **Verra VCS Registry** (registry.verra.org) -- 2,300+ registered projects as of
   2024. We sampled named projects from REDD+, ARR, IFM, renewable energy, cookstoves,
   and other AFOLU categories with realistic geographic and vintage distributions.

2. **Gold Standard Impact Registry** (registry.goldstandard.org) -- 3,362 projects as
   of 2024. Primary source for cookstove and rice methane projects.

3. **CDR.fyi** (cdr.fyi) -- Tracks all durable CDR purchases. Source for DACCS
   (Climeworks, 1PointFive, Heirloom), biochar (Exomad, Oregon Biochar Solutions,
   NetZero, Carbofex), enhanced weathering (UNDO, Lithos, Eion, Mati Carbon), and
   bio-oil (Charm Industrial, BioCirc) projects.

4. **ICVCM CCP Assessment Status** (icvcm.org) -- 7 programs and 36 methodologies
   approved as of November 2025. Used to set CCP status flags.

5. **ACR / CAR registries** -- Source for IFM, landfill gas, ODS, and N2O projects.
   68 ACR IFM projects and 24 CAR IFM projects registered to date.

6. **CDM Registry** -- Source for legacy HFC-23, N2O, and renewable energy CDM projects.

### Distribution Rationale

The category distribution mirrors real VCM retirement patterns (Ecosystem Marketplace
2024, Climate Focus 2025 VCM Review):

- **REDD+ (project + jurisdictional): 18.6%** -- Historically ~18% of credits issued;
  project-level REDD+ graded B (not CCP-approved) while jurisdictional REDD+ grades BB
  (CCP-eligible under ART TREES).
- **Grid renewable energy: 12.6%** -- 31% of retirements in 2024 but declining; ICVCM
  rejected for lack of additionality.
- **Cookstoves: 11.3%** -- 15% of retirements in 2024, growing 67% year-on-year.
- **Nature-based removal (ARR + IFM): 14.2%** -- Emerging CCP-eligible category.
- **Engineered CDR (DACCS + biochar + ERW + bio-oil): 17.0%** -- Over-represented
  vs VCM-wide (~5%) because the framework specifically targets the CDR segment.
  Includes named companies from CDR.fyi supplier leaderboards.
- **Industrial gas (N2O + ODS + HFC-23): 8.8%** -- Legacy avoidance projects.
- **Soil carbon / rice methane: 8.8%** -- Growing CCP-eligible categories.

### Vintage Distribution

Projects span 2012-2026 with methodology-appropriate vintage distributions:
- Legacy categories (HFC-23, renewable energy): 2012-2022 (older vintages)
- Traditional VCM (REDD+, cookstoves, landfill gas): 2015-2024
- Nature-based removal (ARR, IFM): 2018-2024
- Engineered CDR (DACCS, biochar, ERW): 2023-2026 (newer vintages)

## Scoring Methodology

### Archetype Scoring

Each of the 17 methodology categories has a pre-scored archetype profile in
`archetypes.json` with scores across 6 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| removal_type | 0.250 | Is this genuine CO2 removal vs avoidance? |
| additionality | 0.200 | Would this have happened without carbon finance? |
| permanence | 0.175 | How durable is the storage? |
| mrv_grade | 0.200 | Measurement, reporting, verification quality |
| co_benefits | 0.000 | Safeguards gate (informational, not scored) |
| registry_methodology | 0.075 | Registry and methodology rigor |
| vintage_year | 0.100 | Recency of credit issuance |

### Vintage Adjustment

Each project's vintage year overrides the archetype default using:
```
vintage_score = max(0, min(100, 100 - (2026 - vintage_year) * 12))
```
Newer vintages score higher; credits older than 8 years score 0.

### Composite and Grade

```
composite = sum(dimension_score_i * weight_i)
grade = lookup(composite, grade_bands)
```

Grade bands: AAA (90-100), AA (75-89), A (60-74), BBB (45-59), BB (30-44), B (0-29).

### Uncertainty Quantification

Each grade includes a posterior probability P(grade) computed under a Gaussian
approximation using empirically-derived per-dimension standard deviations from the
LLM panel inter-rater reliability study (see `data/llm-panel-irr/`).

## Files

| File | Description |
|------|-------------|
| `archetypes.json` | 17 methodology archetype score profiles |
| `realistic_projects.csv` | 318 projects with registry, vintage, country data |
| `batch_scorer.py` | Scoring engine (reads CSV, outputs graded results) |
| `batch_scores.csv` | Full scored output (composite, grade, P(grade), CCP status) |
| `batch_summary.json` | Grade distribution and category summary |

## Usage

```bash
# Score the realistic project database
python3 batch_scorer.py --input realistic_projects.csv

# Score a custom project list (same CSV format)
python3 batch_scorer.py --input your_projects.csv
```

## Limitations

1. **Archetype-level, not project-level**: All projects in a category receive the same
   base scores. Individual project quality varies significantly within categories.
   This is a scalable approximation, not a substitute for per-project expert assessment.

2. **Vintage is the only per-project adjustment**: Future versions could adjust for
   specific registry, country risk, verification body, and buffer pool adequacy.

3. **CDR over-represented**: Engineered CDR is 17% of this dataset vs ~5% of VCM
   retirements. This is intentional -- the framework targets the CDR segment -- but
   the distribution should not be interpreted as representative of the full VCM.

4. **Named projects are illustrative**: While project names reference real registry
   entries, the scores are archetype-derived and do not reflect project-specific
   assessments by the named registries or third-party raters.

## Comparison to Commercial Agencies

| Agency | Credits Rated | Methodology |
|--------|--------------|-------------|
| Sylvera | ~800 | Per-project expert + satellite |
| BeZero Carbon | ~500 | Per-project expert panel |
| Calyx Global | ~4,400 | Per-project automated + expert |
| MSCI (Trove) | ~1,200 | Per-project quantitative |
| **This framework** | **318** | **Archetype-derived, open, uncertainty-quantified** |

Our dataset is smaller than commercial agencies but uniquely offers:
- **Open source**: All scores, rubrics, and code are public
- **Machine-readable**: CSV/JSON output for programmatic consumption
- **Uncertainty-quantified**: Every grade includes P(grade) posterior probability
- **Reproducible**: Deterministic scoring from published archetype profiles
