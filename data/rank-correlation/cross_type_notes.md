# Cross-Type Rank Correlation Analysis (v0.6 W4)

*Extension of the rank correlation study beyond REDD+ to 11 non-REDD+ projects across 7 project types, testing whether our framework's agreement with commercial raters changes by project type.*

## 1. Motivation

The original rank correlation study (v0.4, analysis.md) used 6 REDD+ projects from the Carbon Market Watch 2023 multi-rater table. The key finding was that inter-agency agreement on REDD+ is near zero, and our framework was no worse. Section 6 explicitly noted: "It does not generalize beyond REDD+. CDR, biochar, industrial gas, renewable energy, and cookstoves may show different patterns."

This extension (v0.6 workstream W4) tests that hypothesis by assembling publicly documented agency ratings for non-REDD+ project types and scoring each under our v0.6 framework using methodology archetypes.

## 2. Data collection methodology

We searched for projects where BeZero, Calyx Global, or Sylvera have published specific letter-grade ratings in press releases, case studies, sector snapshots, or project developer announcements. We did NOT scrape paywalled rating platforms. All data points are sourced from publicly accessible URLs documented in dataset.json.

### Search coverage

| Agency | Projects found | Notes |
|--------|---------------|-------|
| BeZero | 9 of 11 | Most extensive public disclosure via case studies, testimonials, and press releases |
| Calyx | 2 of 11 | Published A/AA ratings for CCP-aligned cookstove projects; aggregate distributions for others |
| Sylvera | 1 of 11 | Published AA for Exomad Green biochar; most project-level ratings behind paywall |

The asymmetry reflects disclosure practices, not rating coverage. BeZero publishes all ratings publicly; Calyx and Sylvera are more selective with public disclosure.

## 3. Projects collected (11 data points)

| ID | Project | Type | Country | Our v0.6 | BeZero | Calyx | Sylvera |
|----|---------|------|---------|----------|--------|-------|---------|
| CT01 | Climeworks Orca (DACCS) | CDR | Iceland | AAA | AAA | - | - |
| CT02 | Novocarbo Rhine (Biochar) | Biochar | Germany | AA | A | - | - |
| CT03 | Exomad Green Concepcion | Biochar | Bolivia | AA | AA | - | AA |
| CT04 | EcoSafi Clean Cooking | Cookstoves | Kenya | BBB | A | - | - |
| CT05 | BURN/Key Carbon Cookstoves | Cookstoves | Kenya | BBB | - | AA | - |
| CT06 | Arborify Cookstoves Togo | Cookstoves | Togo | BBB | - | A | - |
| CT07 | Rebellion Heartland Methane | Methane abatement | US | A | A | - | - |
| CT08 | Family Forest Carbon (IFM) | IFM | US | BBB | BBB | - | - |
| CT09 | Southern Cardamom REDD+ | REDD+ | Cambodia | B* | B | - | - |
| CT10 | Qnergy Weber County LFG | Landfill gas | US | BBB | A | - | - |
| CT11 | Chinese Onshore Wind VCS 1188 | Renewable energy | China | B | C | - | - |

*CT09: composite yields BB but human_rights disqualifier caps at B.

## 4. Scoring methodology

Each project was scored under v0.6 using the closest methodology archetype from `data/methodology-ratings/archetypes.json` as a baseline, then adjusted per-project based on:

1. **Vintage recency** -- recent projects (2023-2024 vintages) score higher on vintage_year
2. **MRV specifics** -- projects with IoT/metered monitoring (EcoSafi, Arborify) receive higher mrv_grade than the archetype default
3. **Additionality evidence** -- orphan well plugging (Rebellion) has stronger counterfactual than generic methane abatement; adjusted up
4. **Registry/methodology status** -- CCP-approved methodologies score 80 on registry_methodology; ICVCM-rejected (renewables) score 25
5. **Disqualifiers** -- Southern Cardamom triggered human_rights disqualifier based on Human Rights Watch allegations and Verra suspension

The v0.6 composite formula: `sum(dimension_score * weight)` with weights from `data/scoring-rubrics/index.json`.

## 5. Results

### 5.1 Overall cross-type: Our v0.6 vs BeZero

On the 9 projects where both our framework and BeZero have ratings:

- **Spearman rho: +0.906**
- **Kendall tau: +0.853**
- **n = 9**

This is dramatically stronger than the REDD+-only correlation (+0.664 under v0.4.1). The cross-type dataset spans the full quality spectrum from B (renewable energy / REDD+) to AAA (DACCS), and both our framework and BeZero track this ordering closely.

### 5.2 Per-type breakdown

Most project types have only 1 data point, so per-type Spearman is not computable. Biochar has n=2 but our grades are tied (both AA), making correlation undefined.

What we can observe qualitatively:

| Type | Agreement pattern |
|------|-------------------|
| CDR (DACCS) | **Exact match**: AAA = AAA |
| Biochar | **Near-match**: AA vs A/AA (1 exact, 1 one-notch gap) |
| Cookstoves | **Systematic divergence**: BBB vs A (2-grade gap with BeZero); BBB vs A/AA (with Calyx) |
| Methane abatement | **Exact match**: A = A |
| IFM | **Exact match**: BBB = BBB |
| REDD+ (S. Cardamom) | **Exact match**: B = B (after disqualifier cap) |
| Landfill gas | **One-notch gap**: BBB vs A |
| Renewable energy | **Directional match**: B vs C (both low; one-grade gap) |

### 5.3 The cookstove divergence

The most notable pattern: our framework consistently rates cookstove projects BBB, while BeZero rates the best cookstove (EcoSafi) at A and Calyx rates top cookstoves at A-AA.

**Root cause**: our composite is structurally bounded by two dimensions that penalize avoidance projects:
- `removal_type = 38` (avoidance, not removal -- capped by rubric)
- `permanence = 8` (no durable storage -- inherent to the project type)

These two dimensions carry combined weight 0.425 (0.250 + 0.175) and together contribute only ~17.5 points to the composite. For a cookstove project to reach grade A (>=60), the remaining weighted dimensions would need to average ~81, which is near-impossible for any avoidance project.

This is a structural design choice, not a scoring error. Our framework deliberately privileges durable removals over avoidance. BeZero and Calyx do not apply this structural penalty. Whether this is a feature or a bug depends on one's philosophy of credit quality:

- **If quality = likelihood of delivering the claimed tonne**: cookstoves with IoT monitoring can score very high, and BeZero/Calyx's A ratings are justified.
- **If quality = contribution to net-zero alignment**: avoidance credits are inherently less aligned than removal credits, and our BBB ceiling is justified.

Our framework adopts the second philosophy (consistent with Oxford Principles, ICVCM guidance on removals, and the CCP+ label trajectory). This is documented and transparent; users who disagree can re-weight.

### 5.4 The landfill gas gap

Qnergy Weber County: our BBB vs BeZero A. Similar to the cookstove divergence but less extreme. Our framework gives `permanence = 10` and `removal_type = 50` for landfill gas, reflecting that methane destruction is avoidance. BeZero's A reflects the high measured-MRV and additionality of the small-landfill niche.

## 6. Comparison with REDD+-only study

| Metric | REDD+ only (v0.4.1) | Cross-type (v0.6) |
|--------|--------------------:|------------------:|
| n (vs BeZero) | 6 | 9 |
| Spearman vs BeZero | +0.664 | **+0.906** |
| Kendall vs BeZero | +0.598 | **+0.853** |
| Exact grade matches | 0 of 6 | 5 of 9 |
| Max grade gap | ~2 grades | 1 grade (on common scale) |

The cross-type agreement is substantially stronger. This confirms the hypothesis from analysis.md section 6: "Other project types have much stronger inter-agency agreement per the public literature; our framework's agreement on those project types is untested by this dataset."

**Key insight**: the near-zero inter-rater agreement on REDD+ is a property of REDD+, not of rating frameworks. When the underlying project type has clearer quality signals (engineered CDR, methane abatement, IFM), raters converge -- and our framework converges with them.

## 7. Structural observations

### 7.1 Our framework agrees most with BeZero on engineered removals and industrial avoidance

On CDR, biochar, and methane abatement (5 projects), we have 3 exact matches and 2 one-notch gaps. This is because both frameworks reward high permanence, strong MRV, and measurable additionality.

### 7.2 Our framework systematically rates cookstoves lower than commercial agencies

This is the only systematic bias in the cross-type dataset. All 3 cookstove projects show our BBB vs agency A or above. This is a deliberate design choice (see 5.3 above).

### 7.3 Calyx data is sparse but directionally interesting

We only have 2 Calyx data points (both cookstoves). Both show Calyx rating higher than our framework. This is consistent with the REDD+ finding: Calyx rates REDD+ much harsher than our framework, but rates CCP-approved cookstoves much higher. Calyx appears to weight CCP approval more than our framework does.

## 8. Limitations

1. **Selection bias**: publicly documented ratings skew toward high-profile, high-quality projects. The low end of the quality spectrum (D-rated renewables, E-rated projects) is underrepresented because those projects do not issue press releases about their ratings.
2. **Agency asymmetry**: 9 of 11 projects have BeZero ratings, but only 2 have Calyx and 1 has Sylvera. The Spearman is driven primarily by the BeZero relationship.
3. **Scoring from archetypes**: our v0.6 scores are archetype-based with per-project adjustments, not full independent assessments. This is less rigorous than the v0.4 REDD+ scoring which used detailed project documentation.
4. **Small n per type**: no project type has enough data points for a statistically meaningful per-type correlation. The per-type table is qualitative, not statistical.
5. **Temporal mismatch**: agency ratings span 2023-2025; our v0.6 archetypes are a single snapshot. Some ratings may have changed.

## 9. Implications

1. **The cross-type Spearman (+0.906) should be reported alongside the REDD+-only Spearman (+0.664) in the paper.** Together they tell a clear story: our framework tracks commercial consensus closely when project types have clear quality signals, and refuses to pick sides when the underlying science is disputed (REDD+).

2. **The cookstove divergence should be documented as a known, deliberate bias.** Users who want to use the framework for cookstove credits should understand that BBB is the effective ceiling for avoidance projects, and this is by design.

3. **Future data collection should target low-quality non-REDD+ projects** (D/C-rated renewables from India, E-rated cookstoves from C-Quest Capital) to test whether our framework tracks the low end of the quality spectrum as accurately as the high end.

4. **A combined dataset of 17+ projects** (6 REDD+ + 11 cross-type) could support a pooled correlation analysis, though the heterogeneous scales (v0.4 for REDD+, v0.6 for cross-type) require care.

## 10. Sources

All source URLs are recorded per-project in `dataset.json` under `cross_type_projects.projects[].source_urls`. Key references:

- BeZero Carbon public listings: https://bezerocarbon.com/ratings/listings
- BeZero case studies: https://bezerocarbon.com/case-studies/novocarbo, https://bezerocarbon.com/case-studies/ecosafi
- BeZero sector snapshots: cookstoves, renewables, landfill, IFM reviews
- Calyx Global research: https://calyxglobal.com/research-hub/
- Sylvera blog: https://www.sylvera.com/blog/
- Climeworks press release: https://climeworks.com/news/climeworks-receives-first-ever-aaa-rating-from-bezero-carbon
- Exomad Green: https://www.exomadgreen.com/post/achievement-unlocked-exomad-green-earns-aa-sylvera-rating
- Rebellion Energy: https://rebellionenergy.com/bezero-carbon-a-rating/
- American Forest Foundation: https://www.forestfoundation.org/why-we-do-it/family-forest-blog/family-forest-carbon-program-receives-bbbe-rating-from-carbon-ratings-agency/
- Carbon Herald: https://carbonherald.com/ecosafi-receives-a-rating-from-bezaro-carbon/
- Arborify: https://www.arborify.com/blog/the-first-carbon-core-principles-icvcm-cookstove-project-in-the-world-gs12069
- BURN/Key Carbon: https://www.burnstoves.com/media/newsroom/newsroom-13
- Qnergy: https://qnergy.com/2025/10/09/a-rated-carbon-credits-generated-from-methane-mitigation-project-at-weber-county-landfill/
