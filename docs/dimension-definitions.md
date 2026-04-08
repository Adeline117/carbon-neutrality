# Rating Dimension Definitions

Detailed scoring criteria for each dimension of the on-chain carbon credit quality rating.

## Overview

| # | Dimension | Weight | Data Source | On-Chain Feasibility |
|---|-----------|--------|-------------|---------------------|
| 1 | Removal Type Hierarchy | 20% | Methodology category | High (mapping table) |
| 2 | Additionality | 20% | Project analysis | Low (oracle needed) |
| 3 | Permanence | 15% | Project type + commitments | Medium (type-based defaults + attestation) |
| 4 | MRV Grade | 15% | Verification reports | Low (oracle needed) |
| 5 | Vintage Year | 10% | Token metadata | High (on-chain native) |
| 6 | Co-benefits | 10% | SDG certifications | Medium (attestation) |
| 7 | Registry & Methodology | 10% | Token metadata | High (mapping table) |

---

## 1. Removal Type Hierarchy

**Rationale**: The Oxford Principles establish that carbon removal is more valuable than avoidance for achieving net zero. Engineered removal with durable storage represents the highest-integrity intervention.

### Scoring Rubric

| Score | Category | Examples | Key Criteria |
|-------|----------|----------|-------------|
| 95-100 | Engineered removal + geological storage | DACCS, BECCS with geological injection | Captures CO2 from atmosphere; stores in geological formations (>10,000 yr) |
| 85-94 | Engineered removal + durable storage | Enhanced weathering with mineralization, ocean alkalinity enhancement | Captures CO2; converts to stable mineral form (>1,000 yr) |
| 75-84 | Nature-based removal + long storage commitment | Biochar, afforestation with >100yr legal covenant | Biogenic CO2 removal; contractual/legal permanence mechanisms |
| 60-74 | Nature-based removal + moderate storage | Reforestation (standard buffer pool), blue carbon | Biogenic removal; standard registry permanence mechanisms |
| 45-59 | Avoidance with high certainty | Industrial fuel switching, N2O destruction, methane capture from landfill | Prevents emissions that would otherwise certainly occur |
| 30-44 | Avoidance with moderate certainty | Renewable energy (grid-connected), efficient cookstoves | Displaces emissions based on baseline calculations |
| 15-29 | Avoidance with baseline uncertainty | REDD+ (avoided deforestation), avoided conversion | Depends heavily on counterfactual baseline accuracy |

### Implementation Notes
- Scoring can be automated via methodology-to-category mapping table
- Edge cases (e.g., hybrid projects) scored by primary intervention type

---

## 2. Additionality

**Rationale**: A credit that represents an emission reduction that would have happened anyway has zero climate value. Additionality is the most contested yet most important integrity dimension.

### Scoring Rubric

| Score | Level | Indicators |
|-------|-------|-----------|
| 90-100 | Very High | Carbon revenue is >50% of project income; technology is pre-commercial; no regulatory mandate; financial analysis shows negative NPV without carbon finance |
| 75-89 | High | Carbon revenue is 30-50% of income; clear investment barrier documented; regulatory surplus demonstrated |
| 60-74 | Moderate | Carbon revenue is 15-30% of income; multiple revenue streams; common practice analysis supports not-yet-standard |
| 45-59 | Marginal | Carbon revenue <15% of income; project type is becoming standard practice; relies primarily on barrier analysis |
| 30-44 | Low | Project type is common in jurisdiction; weak barrier analysis; regulatory requirements approaching project standard |
| 0-29 | Questionable | Project type is mandated or standard practice; no credible barrier analysis; free-rider concerns |

### Red Flags (score cap at 40)
- Project was already under construction before carbon finance was secured
- Government subsidies cover >80% of project costs
- Technology is cheapest available option regardless of carbon revenue

---

## 3. Permanence

**Rationale**: A tonne of CO2 removed for 10 years has far less climate value than a tonne removed for 10,000 years.

### Scoring Rubric

| Score | Storage Duration | Mechanism | Examples |
|-------|-----------------|-----------|---------|
| 95-100 | >10,000 years | Geological / mineralization | CO2 geological injection, mineral carbonation |
| 80-94 | 1,000-10,000 years | Stable organic / mineral | Biochar (lab-verified stability), basalt weathering |
| 65-79 | 100-1,000 years | Structural / legal | Timber in buildings (>100yr design life), legally protected forests |
| 50-64 | 40-100 years | Biological with buffer | AFOLU with >=20% buffer pool, managed plantation with replanting covenant |
| 35-49 | 20-40 years | Biological with monitoring | Standard reforestation, soil carbon with monitoring commitment |
| 15-34 | <20 years | Short-term biological | Short rotation crops, grassland management |
| 0-14 | No storage | N/A (avoidance only) | Renewable energy, cookstoves, avoided emissions |

### Adjustment Factors
- **Insurance/buffer mechanism**: +5 if project has dedicated permanence insurance beyond registry buffer
- **Reversal history**: -10 to -30 if project type has documented reversal events (e.g., forest fires in buffer pool region)

---

## 4. MRV Grade

**Rationale**: The credibility of the claimed emission reduction depends entirely on how well it is measured, reported, and independently verified.

### Scoring Rubric

| Score | Grade | Monitoring | Reporting | Verification |
|-------|-------|-----------|-----------|-------------|
| 90-100 | Digital MRV | Continuous IoT/sensor data; satellite imagery with <10m resolution; automated anomaly detection | Real-time or near-real-time automated reporting; uncertainty quantified | Independent third-party + automated cross-validation; dispute mechanism |
| 75-89 | Enhanced | Regular sensor data or high-res satellite; defined monitoring protocol | Standardized reporting with uncertainty bounds | Independent third-party with methodology-specific competence |
| 60-74 | Standard+ | Periodic sampling per methodology; some remote sensing | Meets registry requirements; conservative default factors | Standard VVB verification per registry rules |
| 45-59 | Standard | Meets minimum registry monitoring requirements | Template-based reporting; limited uncertainty analysis | Standard verification; no red flags |
| 30-44 | Basic | Minimum monitoring; reliance on default emission factors | Basic reporting; significant reliance on estimates | Verification completed but with findings/CARs |
| 0-29 | Deficient | Known monitoring gaps; self-reported only | Late or incomplete reporting | Failed verification; unresolved material findings |

---

## 5. Vintage Year

**Rationale**: Older credits may not reflect current project performance, and their continued availability may indicate low demand (negative signal).

### Scoring Formula

```
vintage_score = max(0, 100 - (current_year - vintage_year) * 12)
```

Capped at 100, floor at 0. Approximately:
- Current year: 100
- 1 year old: 88
- 3 years: 64
- 5 years: 40
- 8 years: 4
- 9+ years: 0

### Override Conditions
- **Pre-2016 vintage**: Automatic cap at 20 (pre-Paris Agreement baselines may not align with current standards)

---

## 6. Co-benefits

**Rationale**: Carbon credits that also deliver verified social and environmental benefits beyond climate mitigation are more valuable to buyers and more aligned with holistic sustainability.

### Scoring Rubric

| Score | Level | Requirements |
|-------|-------|-------------|
| 90-100 | Verified High Impact | SD VISta or Gold Standard SDG certification; >= 3 SDGs with quantified, third-party verified metrics; community engagement documented |
| 70-89 | Verified Moderate | 1-2 SDGs with third-party verified metrics; or CCB (Climate, Community & Biodiversity) Gold/Silver |
| 50-69 | Partially Verified | Self-reported SDG contributions with some third-party evidence; CCB standard certification |
| 30-49 | Self-Reported | Project documentation claims SDG contributions without independent verification; reasonable plausibility |
| 10-29 | Minimal | Limited co-benefit claims; primarily industrial/technological project |
| 0-9 | None | No co-benefits identified or project has documented negative externalities |

### Negative Adjustments
- **Documented community opposition**: -20
- **Environmental damage allegations**: -30
- **Human rights concerns**: Score capped at 0

---

## 7. Registry & Methodology

**Rationale**: The crediting program (registry) and specific methodology determine the rules and rigor under which credits are generated.

### Registry Tier

| Tier | Registries | Base Score |
|------|-----------|-----------|
| 1 | Verra VCS, Gold Standard, ACR, CAR (ICVCM-assessed) | 70-100 |
| 2 | Plan Vivo, Cercarbono, Global Carbon Council | 40-69 |
| 3 | Emerging / regional registries with limited track record | 10-39 |
| 4 | Unrecognized / no registry | 0-9 |

### Methodology Modifier

Within each registry tier, methodology-specific adjustments:

| Modifier | Criteria | Adjustment |
|----------|---------|-----------|
| CCP-eligible | Methodology category approved under ICVCM CCP | +15 |
| Conservative baseline | Demonstrated conservative crediting baseline | +10 |
| Methodology under review | Active integrity review or revision process | -15 |
| Known overcrediting | Published research demonstrates systematic overcrediting | -25 |

---

## Composite Calculation Example

**Example: Afforestation project in Southeast Asia, Verra VCS, 2024 vintage**

| Dimension | Raw Score | Weight | Weighted |
|-----------|----------|--------|---------|
| Removal Type (NBS removal, moderate storage) | 65 | 20% | 13.0 |
| Additionality (carbon revenue ~25% of income) | 62 | 20% | 12.4 |
| Permanence (40-yr commitment, 20% buffer) | 52 | 15% | 7.8 |
| MRV (standard VVB verification + satellite) | 68 | 15% | 10.2 |
| Vintage (2024, current year) | 100 | 10% | 10.0 |
| Co-benefits (CCB Gold, 2 verified SDGs) | 75 | 10% | 7.5 |
| Registry (Verra VCS, standard methodology) | 65 | 10% | 6.5 |
| **Composite** | | | **67.4** |

**Grade: A** (Standard quality; meets baseline integrity expectations)

No disqualifiers triggered. Eligible for A-grade pool.
