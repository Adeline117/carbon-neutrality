# Figure and Table Specifications for All Papers

This document provides detailed rendering specifications for every figure and table placeholder across the four-paper submission pipeline.

---

## Paper 1: ERL Draft (Environmental Research Letters)

**File**: `docs/erl-draft/full-paper.md`

The ERL draft contains no explicit `[Figure N]` or `[Table N]` placeholders. However, the following figures are implied by the results sections and would strengthen the paper. They are specified here for completeness.

### ERL-Fig-1: CCP Calibration Grade Distribution

- **Paper**: ERL
- **Figure number**: 1 (implied)
- **Type**: Grouped bar chart (side-by-side)
- **Data source**: `data/statistical-analysis/ccp_effect_size_results.json` + `data/methodology-ratings/batch_summary.json`
- **X axis**: Grade tier (B, BB, BBB, A, AA, AAA)
- **Y axis**: Count (number of credits)
- **Color coding**: Blue = CCP-eligible (n=165), Orange = non-CCP (n=153)
- **Key annotations**: Annotate 1.99-grade gap, Cohen's d = 1.80, CLES = 91.4%, Mann-Whitney z = 13.06. Dashed vertical separator between BB and BBB marking approximate quality threshold. Mean ordinal grades labeled: CCP = 2.69, non-CCP = 0.70.
- **Size**: Single column (89 mm)
- **Tool**: matplotlib + seaborn

### ERL-Fig-2: Rank Correlation Scatter (Framework vs. BeZero, n=27)

- **Paper**: ERL
- **Figure number**: 2 (implied)
- **Type**: Scatter plot with ordinal axes
- **Data source**: `data/rank-correlation/expanded_correlation.json`
- **X axis**: BeZero grade (D, C, B, BB, BBB, A, AA, AAA) -- mapped to numeric 0-7
- **Y axis**: Framework grade (B, BB, BBB, A, AA, AAA) -- mapped to numeric 0-5
- **Color coding**: Points colored by project category -- CDR/removal (blue), avoidance (red), industrial (green)
- **Key annotations**: Spearman rho = +0.901, 95% CI [+0.783, +0.959], p < 0.0001. Diagonal identity line. Label notable projects (Climeworks Orca at AAA/AAA, Kariba at B/D, Keo Seima at BBB/A). Jitter overlapping points.
- **Size**: Single column (89 mm)
- **Tool**: matplotlib

### ERL-Fig-3: Lemons Index Across 34 Market Segments

- **Paper**: ERL
- **Figure number**: 3 (implied)
- **Type**: Horizontal bar chart, sorted by LI descending
- **Data source**: `data/lemons-index/systematic_scan_results.json`
- **X axis**: Lemons Index (0.0 to 1.0)
- **Y axis**: Pool segment name (34 segments)
- **Color coding**: Continuous red-to-green gradient (red = high LI, green = low LI)
- **Key annotations**: Vertical dashed line at LI = 0.51 (null model). Label specific pools: DACCS (0.076), BCT-like renewable energy (0.759), CCP-eligible (0.419), full market (0.510).
- **Size**: Double column (183 mm), tall format
- **Tool**: matplotlib

### ERL-Fig-4: Monte Carlo Weight Sensitivity Per-Credit Stability

- **Paper**: ERL
- **Figure number**: 4 (implied)
- **Type**: Horizontal lollipop / dot plot
- **Data source**: `data/statistical-analysis/monte_carlo_sensitivity_results.json`
- **X axis**: Grade stability (0% to 100%)
- **Y axis**: Credit name (29 credits, sorted by stability)
- **Color coding**: Color by baseline grade (AAA=dark blue, AA=blue, A=teal, BBB=yellow, BB=orange, B=red)
- **Key annotations**: Vertical dashed line at 90% stability threshold. Label the 5 fragile credits below 90%. Mark Climeworks Orca (100%) and Kariba (100%) as reference extremes. Report global robustness = 93.7% at concentration=50.
- **Size**: Single column (89 mm), tall
- **Tool**: matplotlib

### ERL-Fig-5: Inter-Rater Reliability Per-Dimension Kappa

- **Paper**: ERL
- **Figure number**: 5 (implied)
- **Type**: Horizontal bar chart with Landis-Koch interpretation bands
- **Data source**: `data/llm-panel-irr/irr_summary.json`
- **X axis**: Fleiss' kappa value (0.0 to 1.0)
- **Y axis**: Dimension name (7 dimensions)
- **Color coding**: Bars colored by Landis-Koch threshold: slight (<0.20, red), fair (0.21-0.40, orange), moderate (0.41-0.60, yellow), substantial (0.61-0.80, green), almost perfect (>0.80, dark green)
- **Key annotations**: Vertical lines at kappa = 0.20, 0.40, 0.60, 0.80. Label overall grade kappa = 0.600, ICC = 0.993. Weight annotations next to each dimension name.
- **Size**: Single column (89 mm)
- **Tool**: matplotlib

---

## Paper 2: Nature Communications Draft

**File**: `docs/natcomms-draft/sections-1-2-intro-results.md` and `docs/natcomms-draft/sections-5-figures-refs.md`

### NatComms-Fig-1: Single Depositor Portfolio (Adverse Selection Mechanism)

- **Paper**: Nature Communications
- **Figure number**: 1
- **Type**: (a) Grouped bar chart + (b) Schematic diagram
- **Data source**: Depositor-level on-chain data (NOT YET AVAILABLE -- requires Dune Analytics query)
- **Panel (a)**: Bar chart of TCO2 token types held by one representative depositor. X = TCO2 type, Y = composite quality score. Red bars = deposited into BCT, blue bars = retained. Horizontal dashed lines at grade boundaries (AAA >= 90, AA >= 75, A >= 60, BBB >= 45, BB >= 30, B < 30).
- **Panel (b)**: Schematic of Akerlof mechanism at depositor level (information advantage -> strategic selection -> quality arbitrage). This is a conceptual diagram.
- **Size**: Double column (183 mm)
- **Tool**: Panel (a) matplotlib (when data available); Panel (b) draw.io or tikz
- **STATUS**: BLOCKED -- awaiting on-chain depositor data

### NatComms-Fig-2: Distribution of Quality Differentials Across Depositors

- **Paper**: Nature Communications
- **Figure number**: 2
- **Type**: Histogram with KDE overlay and permutation null
- **Data source**: Depositor-level on-chain data (NOT YET AVAILABLE)
- **X axis**: Quality differential Delta_d = Q_retained - Q_deposited
- **Y axis**: Count / density
- **Color coding**: Blue histogram = observed, grey shading = permutation null distribution (KDE). Inset box plot.
- **Key annotations**: Vertical dashed line at Delta = 0. Label selection rate %, mean Delta, median Delta, p-value.
- **Size**: Single column (89 mm)
- **Tool**: matplotlib + seaborn
- **STATUS**: BLOCKED -- awaiting on-chain depositor data

### NatComms-Fig-3: Lemons Index Across 34 Market Segments (Quality Atlas)

- **Paper**: Nature Communications
- **Figure number**: 3
- **Type**: (a) Horizontal bar chart + (b) Null model histogram
- **Data source**: `data/lemons-index/systematic_scan_results.json`
- **Panel (a)**:
  - X axis: Lemons Index (0.0 to 1.0)
  - Y axis: 34 pool segment names, sorted by LI descending
  - Color: Continuous red-to-green gradient
  - Highlight BCT (0.724), MCO2 (0.713), NCT (0.601), kVCM (0.519), CHAR (0.221), AAA-only (0.100) with bold outlines
  - Vertical dashed line at LI = 0.51 (null expectation)
- **Panel (b)**:
  - Histogram of 10,000 Monte Carlo null LI values for n=43 (mean=0.51, SD=0.026)
  - Mark BCT observed at 6.2 SD with arrow
- **Size**: Double column (183 mm)
- **Tool**: matplotlib

### NatComms-Fig-4: Temporal Stratification of Adverse Selection

- **Paper**: Nature Communications
- **Figure number**: 4
- **Type**: (a) Bar chart (early vs late selection rates), (b) scatter + LOESS, (c) price overlay
- **Data source**: Depositor-level on-chain data (NOT YET AVAILABLE)
- **STATUS**: BLOCKED -- awaiting on-chain depositor data

### NatComms-Fig-5: Counterfactual Quality Gating

- **Paper**: Nature Communications
- **Figure number**: 5
- **Type**: Line plot with dual Y-axis
- **Data source**: `data/statistical-analysis/counterfactual_simulation_results.json`
- **X axis**: Minimum grade threshold (B, BB, BBB, A, AA, AAA)
- **Y axis (primary)**: Lemons Index (0.0 to 1.0)
- **Y axis (secondary)**: Number of credits admitted (annotation track)
- **Lines**: BCT (red), kVCM (blue), NCT (orange)
- **Key annotations**: Horizontal dashed line at CHAR LI = 0.221. Highlight BBB "sweet spot". Shade area between baseline and gated trajectories. Label admission rates at BBB threshold.
- **Size**: Single column (89 mm)
- **Tool**: matplotlib

### NatComms-Table-1: Depositor-Level Adverse Selection Summary Statistics

- **Paper**: Nature Communications
- **Table number**: 1
- **Column headers**: Metric | Full Sample | Excl. KlimaDAO | Early Period | Late Period
- **Data source**: Depositor-level on-chain data (NOT YET AVAILABLE)
- **Rows**: N depositors, N multi-type, Selection rate (%), Mean Delta (95% CI), Median Delta, Cohen's d, Wilcoxon z, Wilcoxon p, Permutation p
- **Key formatting**: Bold the full-sample row. P-values in scientific notation. CIs in brackets.
- **STATUS**: BLOCKED -- awaiting on-chain depositor data

### NatComms-Table-2: Pool-Level Lemons Index for Six Tokenized Pools

- **Paper**: Nature Communications
- **Table number**: 2
- **Column headers**: Pool | Chain | n | Mean Composite | Lemons Index | % >= A | SD from Null
- **Data source**: `data/statistical-analysis/counterfactual_simulation_results.json`
- **Rows**: Toucan BCT (0.724, n=43), Moss MCO2 (0.713, n=30), Toucan NCT (0.601, n=28), Klima kVCM (0.519, n=20), Toucan CHAR (0.221, n=12), Hypothetical AAA-only (0.100, n=13)
- **Key formatting**: Sort by LI descending. Color-code LI cells (red for high, green for low). Null model row at bottom: LI = 0.51, SD = 0.026 for n=43.

---

## Paper 3: Nature Sustainability Perspective

**File**: `docs/natsust-perspective/perspective.md`

### NatSust-Fig-1: The Convergence-Gap Diagram (Six Frameworks)

- **Paper**: Nature Sustainability
- **Figure number**: 1 (implied -- perspective papers typically have 1-2 figures)
- **Type**: Schematic / conceptual diagram
- **Data source**: Text-based (six governance frameworks enumerated in intro)
- **Content**: Six horizontal rows (CCP, Article 6.4, CORSIA, EU CRCF, VCMI Claims Code, Singapore NEA), each with the same four integrity dimensions (additionality, permanence, quantification, safeguards) checked. Right column shows "Binary gate" for all six. Arrow pointing to "Gap: no continuous scoring within approved tier."
- **Key annotations**: CCP-eligible LI = 0.419 annotated at the gap.
- **Size**: Double column (183 mm)
- **Tool**: draw.io or tikz (conceptual, not data-driven)

### NatSust-Fig-2: CCP-Eligible Pool Still Has 42% Quality Degradation

- **Paper**: Nature Sustainability
- **Figure number**: 2 (implied)
- **Type**: Stacked or split bar comparing CCP-eligible (LI=0.419) vs non-CCP (LI=0.667) vs full market (LI=0.510)
- **Data source**: `data/lemons-index/systematic_scan_results.json` (CCP-eligible, Non-CCP, Full 318-credit entries)
- **X axis**: Pool segment (Non-CCP, Full Market, CCP-eligible)
- **Y axis**: Lemons Index (0.0 to 1.0)
- **Color coding**: Red (Non-CCP), Grey (Full market), Green (CCP-eligible)
- **Key annotations**: 37% improvement arrow from 0.667 to 0.419. "0.419 = 42% quality degradation persists" annotation. Null model baseline at 0.51.
- **Size**: Single column (89 mm)
- **Tool**: matplotlib

### NatSust-Placeholder-1: Danny Cullenward Quote

- **Paper**: Nature Sustainability
- **Location**: After "The binary gate problem" section
- **Type**: Pull quote / text placeholder
- **Content**: Expert quote from Danny Cullenward, University of Pennsylvania
- **STATUS**: PLACEHOLDER -- awaiting expert interview/permission

### NatSust-Placeholder-2: Vahideh Manshadi Quote

- **Paper**: Nature Sustainability
- **Location**: After "Evidence from tokenized markets" section
- **Type**: Pull quote / text placeholder
- **Content**: Expert quote from Vahideh Manshadi, Yale University
- **STATUS**: PLACEHOLDER -- awaiting expert interview/permission

### NatSust-Placeholder-3: Gregory Trencher Quote

- **Paper**: Nature Sustainability
- **Location**: After "The economic case" section
- **Type**: Pull quote / text placeholder
- **Content**: Expert quote from Gregory Trencher, Kyoto University
- **STATUS**: PLACEHOLDER -- awaiting expert interview/permission

---

## Paper 4: WWW 2027 Draft (ACM Web Conference)

**File**: `docs/www2027-draft/full-paper.md`

### WWW-Fig-1: ERC-CCQR Architecture Diagram

- **Paper**: WWW 2027
- **Figure number**: 1
- **Type**: Architecture schematic (concentric layers)
- **Data source**: Text-based (specification in Section 3)
- **Content**: Three concentric layers. Inner: Level 1 (meetsGrade/isStale). Middle: Level 2 (Rating struct, ratingOf). Outer: Level 3 (EAS relay, trusted-attester allowlist). Integration arrows from consuming contracts: QualityGatedPool, KlimaRetirementGate, CHARQualityOverlay.
- **Size**: Single column (ACM standard: 84 mm)
- **Tool**: draw.io or tikz (conceptual, not data-driven)

### WWW-Fig-2: Composability Pattern Sequence Diagrams

- **Paper**: WWW 2027
- **Figure number**: 2
- **Type**: Three UML sequence diagrams
- **Data source**: Text-based (Section 4)
- **Panels**:
  - (a) QualityGatedPool: user -> pool -> meetsGrade staticcall -> rating contract -> bool -> transferFrom
  - (b) KlimaRetirementGate: buyer -> gate -> isStale + meetsGrade -> burn
  - (c) CHARQualityOverlay: depositor -> CHAR checkEligible -> overlay -> ratingOf -> fee calculation
- **Size**: Double column (177 mm)
- **Tool**: draw.io, PlantUML, or tikz

### WWW-Fig-3: Gas Cost Breakdown (Stacked Bar)

- **Paper**: WWW 2027
- **Figure number**: 3
- **Type**: Stacked bar chart
- **Data source**: Gas benchmarks from Table 2 (hardcoded values from Section 6.1)
- **X axis**: Operation (ERC-20 transfer, Uniswap swap, Aave supply, QualityGatedPool deposit)
- **Y axis**: Gas cost
- **Stacked segments**: Base operation cost (grey) + meetsGrade overhead (blue, ~19,244 gas)
- **Key annotations**: Percentage overhead labels. Label meetsGrade as "quality gate: ~19k gas".
- **Size**: Single column (84 mm)
- **Tool**: matplotlib

### WWW-Fig-4: CCP Calibration Dual Violin Plot

- **Paper**: WWW 2027
- **Figure number**: 4
- **Type**: Dual violin plot
- **Data source**: `data/statistical-analysis/ccp_effect_size_results.json` + `data/lemons-index/systematic_scan_results.json` (CCP-eligible and Non-CCP pools for distribution reconstruction)
- **X axis**: Two groups (CCP-eligible, Non-CCP)
- **Y axis**: Composite score (0-100) or ordinal grade (B=0 to AAA=5)
- **Color coding**: Green (CCP-eligible), Red (Non-CCP)
- **Key annotations**: 1.99-grade gap annotated with bracket. Cohen's d = 1.80. Means marked with white diamond. Horizontal grade boundary lines.
- **Size**: Single column (84 mm)
- **Tool**: matplotlib + seaborn

### WWW-Fig-5: Per-Dimension Fleiss' Kappa Bar Chart

- **Paper**: WWW 2027
- **Figure number**: 5
- **Type**: Horizontal bar chart with Landis-Koch bands
- **Data source**: `data/llm-panel-irr/irr_summary.json`
- **X axis**: Fleiss' kappa (0.0 to 1.0)
- **Y axis**: Dimension names (7 dimensions, sorted by kappa descending)
- **Color coding**: Bars colored by Landis-Koch interpretation: slight (red), fair (orange), moderate (yellow), substantial (green)
- **Key annotations**: Background color bands at 0.20, 0.40, 0.60, 0.80 boundaries. Overall grade kappa = 0.600, ICC = 0.993 as text annotation.
- **Size**: Single column (84 mm)
- **Tool**: matplotlib

### WWW-Fig-6: Lemons Index Comparison Across Pool Types

- **Paper**: WWW 2027
- **Figure number**: 6
- **Type**: Horizontal bar chart (6 pools)
- **Data source**: `data/statistical-analysis/counterfactual_simulation_results.json`
- **X axis**: Lemons Index (0.0 to 1.0)
- **Y axis**: Pool name (BCT, MCO2, NCT, kVCM, CHAR, AAA-only)
- **Color coding**: Red-to-green gradient by LI value
- **Key annotations**: Null model baseline at 0.51 (dashed line). Labels with n and mean composite.
- **Size**: Single column (84 mm)
- **Tool**: matplotlib

### WWW-Table-1: Weight Vector, Grade Bands, and Disqualifier Cap Lattice

- **Paper**: WWW 2027
- **Table number**: 1
- **Column headers**: Dimension | Weight (bps) | Score Range | Data Source
- **Data source**: Hardcoded from specification (Section 3.3)
- **Rows**: Removal type (2500), Additionality (2000), MRV grade (2000), Permanence (1750), Vintage year (1000), Co-benefits/safeguards (0), Registry/methodology (750)
- **Additional sections**: Grade bands (AAA>=9000 through B<3000), Disqualifier caps (7 flags with cap targets)
- **Key formatting**: Two-part table. Bold the zero-weight co-benefits row. Footnote explaining safeguards-gate design.

### WWW-Table-2: Gas Benchmarks

- **Paper**: WWW 2027
- **Table number**: 2
- **Column headers**: Operation | Measured Gas | Notes
- **Data source**: Foundry gas-report (hardcoded values in Section 6.1)
- **Rows**: setRating cold (167,720), setRating warm (30,308), meetsGrade (19,244), ratingOf (20,823), isStale (19,057), isStale unrated (7,097), EAS relay (250,086), QualityGatedPool deposit (57k-162k)
- **Key formatting**: Right-align gas values. Bold the view functions. Footnote on L2 costs.

### WWW-Table-3: On-Chain Carbon Protocol Comparison

- **Paper**: WWW 2027
- **Table number**: 3
- **Column headers**: Protocol | Chain | Quality Mechanism | Limitation
- **Data source**: Text-based (Section 2.1)
- **Rows**: Toucan BCT (Polygon), Toucan CHAR (Base), Moss MCO2 (Ethereum/Polygon), Nori NRT (Polygon), Klima 2.0 (Base), Carbonmark (Polygon), Regen Network (Cosmos)
- **Key formatting**: Highlight limitation column in italic.

### WWW-Table-4: Spearman Rank Correlation Matrix

- **Paper**: WWW 2027
- **Table number**: 4
- **Column headers**: Rater pair | Dataset | n | Spearman rho | p-value
- **Data source**: `data/rank-correlation/expanded_correlation.json` + `data/rank-correlation/bootstrap_expanded_results.json`
- **Rows**: Ours vs BeZero (REDD+ n=6: +0.664; cross-type n=27: +0.901), Ours vs Sylvera (+0.566), Ours vs Calyx (-0.200), BeZero vs Calyx (-0.664), BeZero vs Sylvera (+0.600), Calyx vs Sylvera (+0.091), Inter-agency mean (+0.009), Framework-agency mean (+0.343)
- **Key formatting**: Bold the cross-type n=27 row. Color-code negative correlations red.

### WWW-Table-5: Positioning Matrix (ERC-CCQR vs Related Systems)

- **Paper**: WWW 2027
- **Table number**: 5
- **Column headers**: System | Credit-level rating | Continuous threshold | Uncertainty quantification | EVM composability | Published IRR | DeFi pool integration
- **Data source**: Text-based (Section 2.5)
- **Rows**: CATchain-R, PACT, Toucan CHAR, Hypercerts, ERC-CCQR
- **Key formatting**: Checkmark/cross symbols. ERC-CCQR row highlighted (all checks).

### WWW-Table-6: Oracle and Compliance Interface Comparison

- **Paper**: WWW 2027
- **Table number**: 6
- **Column headers**: System | Core Query | Query Semantic | Return Type | Staleness Model | Update Model | Composability
- **Data source**: Text-based (Section 2.6)
- **Rows**: Chainlink AggregatorV3, UMA OptimisticOracleV3, Pyth Network, ERC-3643 T-REX, ERC-CCQR
- **Key formatting**: Multi-row. Bold ERC-CCQR row. Footnotes for novel vs adapted elements.

---

## Summary: Figures Generatable from Existing Data

| ID | Paper | Type | Can Generate Now? |
|----|-------|------|-------------------|
| ERL-Fig-1 | ERL | CCP calibration bar chart | YES |
| ERL-Fig-2 | ERL | Rank correlation scatter | YES |
| ERL-Fig-3 | ERL | LI 34-segment bar | YES |
| ERL-Fig-4 | ERL | MC weight sensitivity | YES |
| ERL-Fig-5 | ERL | IRR per-dimension kappa | YES |
| NatComms-Fig-1 | Nat Comms | Depositor portfolio | NO (needs Dune data) |
| NatComms-Fig-2 | Nat Comms | Quality differential histogram | NO (needs Dune data) |
| NatComms-Fig-3 | Nat Comms | LI 34-segment + null model | YES |
| NatComms-Fig-4 | Nat Comms | Temporal adverse selection | NO (needs Dune data) |
| NatComms-Fig-5 | Nat Comms | Counterfactual quality gating | YES |
| NatSust-Fig-1 | Nat Sust | Six-framework schematic | NO (conceptual/draw.io) |
| NatSust-Fig-2 | Nat Sust | CCP vs non-CCP LI bars | YES |
| WWW-Fig-1 | WWW 2027 | Architecture diagram | NO (conceptual/draw.io) |
| WWW-Fig-2 | WWW 2027 | Sequence diagrams | NO (conceptual/draw.io) |
| WWW-Fig-3 | WWW 2027 | Gas cost stacked bar | YES |
| WWW-Fig-4 | WWW 2027 | CCP dual violin | YES |
| WWW-Fig-5 | WWW 2027 | IRR per-dimension kappa | YES |
| WWW-Fig-6 | WWW 2027 | Pool LI comparison | YES |
