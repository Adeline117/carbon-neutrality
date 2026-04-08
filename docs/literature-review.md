# Literature Review: On-Chain Carbon Credit Quality Rating

*Comprehensive survey of academic papers, industry reports, and existing frameworks (2022-2026)*

---

## 1. The Quality Crisis: Empirical Evidence

### 1.1 Less Than 16% of Credits Represent Real Reductions

**"Systematic assessment of the achieved emission reductions of carbon crediting projects"**
*Nature Communications, 2024*

Synthesized 14 studies covering 2,346 projects and ~1 billion tCO2e (one-fifth of total credit volume). Findings by project type:
- Cookstoves: **11%** real reductions
- SF6 destruction: **16%**
- Avoided deforestation (REDD+): **25%**
- HFC-23 abatement: **68%**
- Wind power, improved forest management: **no statistically significant reductions**

**Implication for our framework**: Quality rating is not optional -- it's existentially important. The majority of issued credits have no real climate impact, and the market currently cannot distinguish them.

### 1.2 Offsets Overestimate Impact by 5-10x

**"Are Carbon Offsets Fixable?"**
*Annual Review of Environment and Resources, 2025*

Most comprehensive review to date. Found most widely used offset programs overestimate climate impact by **5-10x or more**. Concludes offsets are "ineffective and riddled with intractable problems." Recommends offsets should no longer substitute for direct emission cuts.

**Implication**: Our framework should not position quality rating as "fixing" offsets, but as enabling honest differentiation between the small fraction that works and the majority that doesn't.

### 1.3 Major Buyers Choose Low Quality

**"Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market"**
*Trencher et al., Nature Communications, 2024*

Examined 20 largest offset-purchasing companies (2020-2023). **87% of offsets carry high risk of not providing real/additional reductions**. Most come from forest conservation and renewable energy projects. None of the 20 companies could claim a substantial portion met well-known quality standards.

**Implication**: Demand-side incentives alone won't fix quality. On-chain quality gates that make it *impossible* to buy below a threshold could shift behavior.

---

## 2. Existing Quality Assessment Frameworks

### 2.1 Carbon Credit Quality Initiative (CCQI)

**Organizations**: Environmental Defense Fund, WWF-US, Oeko-Institut
**Methodology**: 7 quality objectives scored 1-5 by domain experts not employed by developers/programs. Free, user-friendly scoring tool.

| # | Quality Objective |
|---|------------------|
| 1 | Robust GHG emissions impact quantification |
| 2 | Additionality |
| 3 | No over-estimation |
| 4 | Permanence |
| 5 | No double counting |
| 6 | Safeguards (environmental and social) |
| 7 | Contribution to sustainable development |

**Comparison with our approach**: CCQI evaluates at the methodology level, not project level. Our framework operates at the individual credit/project level. CCQI's 7 objectives map well to our 7 dimensions but we add granularity (0-100 vs 1-5) and on-chain enforcement.

### 2.2 Commercial Rating Agencies

#### Sylvera
- Scale: AAA to D
- Method: Bottom-up, project-type-specific (1,500-2,500 hours per framework). ML-based remote sensing + expert review.
- Coverage: ~70% of ARR credits by end of 2023
- Key finding (State of Carbon Credits 2025): High-quality (BB+) credits grew to 50% of retirements; market shifting from volume to value.

#### BeZero Carbon
- Scale: 8-point (AAA to D)
- Method: 6 risk factors -- additionality, over-crediting, non-permanence, leakage, perverse incentives, policy/political environment
- Distinction: All ratings publicly available
- Also developed BeZero Carbon Methodology Assessment (BCMA) framework

#### Calyx Global
- Method: Three-part (program-, methodology-, project-level). 6 risk factors. Scores are **additive** (positive in one area cannot overcome risk in another). Peer-reviewed frameworks.
- Program screening: 31 best-practice criteria rated gold/silver/bronze/fail
- Separate SDG impact rating

#### MSCI Carbon Project Ratings
- 2025 State of Integrity report: 4,400+ projects assessed. Fewer than 10% rated AAA-A.
- High-integrity index trades at **4x** the level of the low-integrity index (up from 2x in 2024).
- BBB+ retirements rose to 35% (from 25% in 2022).

#### Cross-Agency Inconsistency (Carbon Market Watch, 2023)
Significant rating disagreements. Same Amazon REDD+ project received high marks from Sylvera but low ratings from Calyx and BeZero. **None of the four agencies** incorporate safeguards preventing negative impacts on local communities. This inconsistency is a strong argument for an open, transparent methodology.

### 2.3 ICVCM Core Carbon Principles (CCP)

- **5 programs approved**: ACR, ART, Climate Action Reserve, Gold Standard, Verra VCS
- **36 methodologies** approved as of late 2025
- **~101 million credits** approved for CCP label; 4% of 2024 market volume
- **25% price premium** for CCP-labelled credits
- Binary (meets/doesn't meet) rather than granular scoring

**Implication**: CCP provides a baseline threshold. Our framework builds on CCP as a minimum eligibility requirement while adding granular quality differentiation above the threshold.

---

## 3. On-Chain Carbon Market Lessons

### 3.1 Zhou et al. (2023) -- Nori Case Study

**"Harnessing Web3 on Carbon Offset Market for Sustainability: Framework and A Case Study"**
*Chenyu Zhou, Hongzhou Chen, Shiman Wang, Xinyao Sun, Abdulmotaleb El Saddik, Wei Cai*
*IEEE Wireless Communications, October 2023*

Three-layer framework (physical/technological/societal) with four blockchain utilities:
1. **Recording & Tracking**: IoT/sensors + blockchain for lifecycle data
2. **Wide Verification**: Smart contracts for decentralized verification certificates
3. **Value Trading**: Token incentives for environmental stewardship
4. **Concept Disseminating**: NFTs as public-facing carbon offset certificates

Nori case study findings:
- **NFT-based model** (NRT = Nori Removal Tonne) on Polygon -- each credit is unique, non-fungible, preventing the double-counting and mixing problems of fungible pool models (Toucan)
- **Buyer clustering** (SOM, 4 clusters):
  - Experiential buyers (87.9%) -- one-time, small purchases
  - Voluntary offset individuals (7.6%) -- regular purchasers aligned with annual emissions
  - Investors & SMEs (4%) -- larger volume, profit-driven or annual offset accounting
  - Large carbon offset organizations (4%) -- institutional reconciliation (e.g., The Sandbox computing monthly emissions)
- **Granger causality**: Public opinion has significant causal impact (p<0.01 at 3 lags); energy prices affect with delay; crypto-ecological prosperity does NOT significantly impact -- Nori is decoupled from crypto cycles
- **Sentiment analysis**: Nori sentiment is *not* correlated with broader crypto/NFT sentiment -- a positive signal for real-world utility

**Key insight for our framework**: The NFT (non-fungible) approach inherently preserves per-credit identity, making quality rating more natural than in fungible pool models. Our rating can attach to each individual NFT/token. Zhou et al.'s buyer segmentation also suggests that the "experiential" majority (87.9%) may not value quality differentiation, but the institutional buyers (4%) who drive 58.3% of transaction volume would strongly benefit from quality-gated pools.

### 3.2 Toucan Protocol / KlimaDAO Post-Mortem

**Key papers:**
- *"Tokenized carbon credits in voluntary carbon markets: the case of KlimaDAO"* (Frontiers in Blockchain, 2024) -- growth stagnated from Feb 2023; governance participation dropped from 10% to <4%
- *"Klima DAO: a crypto answer to carbon markets"* (Jirasek, Springer, 2023) -- whale governance concentration; limited transparency
- CarbonPlan analysis: 99.9% of BCT credits were ineligible for CORSIA; 85% ineligible for Article 6. 600,000+ HFC-23 credits dumped before blocklisting.

**"Carbon credits meet blockchain -- cryptocarbon projects and the algorithmic financialisation of voluntary carbon markets"** (Finance and Space, 2024): Blockchain financialization worsens VCM governance by "untethering the spatial linkages between carbon credits and their underlying conservation projects."

### 3.3 Verra's Response
- Banned tokenization of retired credits (May 2022)
- Proposed "immobilization" framework (credits locked in registry subaccounts before tokenization)
- 71 stakeholder responses to public consultation
- As of 2026: **still no implemented framework for tokenizing live credits**

---

## 4. Frontier On-Chain Quality Differentiation

### 4.1 CATchain-R: Blockchain Carbon Registry with Credibility Index

**Gao & Liu, Cornell University (npj Climate Action, 2026)**

Introduces a **carbon credibility index** comparing organizations' carbon reduction goals vs achievements, assigning/updating credibility ratings similar to a credit rating agency. Registry-mediated auditor selection + automated smart contracts. Applied to NYC transportation systems 2005-2050.

**Relevance**: Closest existing work to our approach. Key difference: CATchain-R rates *organizations'* credibility, while we rate *individual credits'* quality.

### 4.2 PACT Carbon Stablecoin

**Jaffer et al., Cambridge (IEEE ICBC, 2024)**

Proposes combining remote sensing + econometric techniques + on-chain certification. Uses **global, comparable baselines** via econometric techniques measurable digitally. Distinct PACT tokens backed by pools with similar co-benefits (biodiversity, jurisdiction). Implemented on Tezos.

**Relevance**: The PACT approach to attribute-preserving pooling is complementary -- credits could be quality-rated first, then pooled by both quality grade AND co-benefit attributes.

### 4.3 JPMorgan Kinexys Carbon Tokenization (2025)

**"Carbon Markets Reimagined: Scale, Resiliency, and Transparency"**

Registry-layer tokenization via API (credits tokenized at issuance, not bridged after the fact). Partners: S&P Global Commodity Insights, EcoRegistry, International Carbon Registry.

**Relevance**: Registry-layer tokenization solves the provenance problem that plagued Toucan. Quality rating could be integrated at the tokenization step.

---

## 5. Adverse Selection: Formal Models

### 5.1 The Lemons Problem in Carbon Markets

**"Offsetting Carbon with Lemons: Adverse Selection and Certification in the Voluntary Carbon Market"**
*Manshadi, Monachou, Morgenstern (SSRN, November 2025)*

First rigorous economic model showing:
- When certification noise exceeds a threshold → **market-for-lemons collapse** (no trade)
- Measures targeting only demand or supply side can actually **reduce** climate benefit without certification improvements
- Both certification quality AND market design matter

**Implication**: Our quality rating is essentially a certification mechanism. The model validates that *reducing certification noise* (= more granular, transparent, multi-dimensional scoring) is necessary to prevent market collapse.

### 5.2 Empirical Price Analysis

**"The Market for Voluntary Carbon Offsets"**
*Berg et al. (SSRN, December 2025)*

Using proprietary dealer data: prices range from cents to $100/tonne. Credits from **least reliable technologies but with positive non-carbon externalities are 2x more expensive** than trusted industrial solutions. This suggests buyers value *stories* (co-benefits) over *integrity* (real reductions) -- precisely the mispricing that quality rating should correct.

---

## 6. Digital MRV Advances

| Initiative | Approach | Status |
|-----------|----------|--------|
| **Verra-Pachama DMRV** | AI + satellite imagery for dynamic forest carbon measurement | Pilot phase; could reduce credit issuance from years to days |
| **ESA SatMRV** | Sentinel-2/1 + ML for soil organic carbon monitoring | 9 global pilots; 67% conversion to paid |
| **Open Forest Protocol** | Decentralized MRV on NEAR Protocol; distributed verifier network | Operational in 20 countries |
| **Isometric** | AI-native CDR registry; durable removal only (centuries/millennia) | Issued first verified Enhanced Weathering credits (Dec 2024) |
| **RMI Carbon Crediting Data Framework** | Open-source framework for standardizing carbon credit data | Published; addresses data opacity |

**Implication for MRV dimension**: Digital MRV is advancing rapidly enough that by 2027, satellite/sensor-based verification could provide automated, continuous MRV scoring inputs for our framework -- reducing reliance on subjective oracle attestation.

---

## 7. Consensus Methodology Options

### 7.1 Neutrosophic Delphi-DEMATEL

*Nguyen (2025)* applied to Vietnam's carbon credit systems. Two-phase: (1) Neutrosophic Delphi for expert consensus; (2) DEMATEL for inter-factor influence assessment. Handles uncertainty through neutrosophic logic (truth, indeterminacy, falsity).

**Assessment**: Rigorous but complex. May be over-engineered for our initial needs.

### 7.2 CCQI Expert Panel

Structured expert assessment (not formally Delphi) with domain specialists scoring criteria 1-5. Iterative methodology refinement based on feedback.

**Assessment**: Pragmatic and proven. Good model for Phase 2.

### 7.3 Recommendation

Start with **structured expert elicitation** (CCQI-style) for initial weight calibration. Consider formal Delphi for subsequent revisions if expert panel is large enough (15+). The key is to start collecting expert input early -- methodology can be refined.

---

## 8. Key Takeaways for Framework Design

1. **Quality crisis is empirically confirmed**: <16% of credits are real reductions. Rating is not optional.

2. **Price premiums validate demand**: ICVCM CCP gets 25% premium; MSCI high-integrity index at 4x. Market will pay for verified quality.

3. **Rating agency inconsistency creates opportunity**: An open, transparent, reproducible methodology addresses the trust gap that proprietary ratings cannot.

4. **NFT model > fungible pool model**: Zhou et al.'s analysis of Nori shows per-credit identity enables quality attribution. Our rating should attach to individual credits, not pools.

5. **Institutional buyers drive volume**: Zhou et al.'s clustering shows 4% of buyers (large organizations) drive 58.3% of transactions. These are the primary users of quality-gated pools.

6. **Registry-layer tokenization is the future**: JPMorgan Kinexys approach (tokenize at issuance) is more robust than bridge-and-pool (Toucan). Quality rating should integrate at issuance.

7. **Digital MRV will automate the hardest dimension**: Pachama, OFP, SatMRV show that MRV scoring inputs can be increasingly automated, reducing oracle dependence.

8. **Adverse selection is formally modeled**: Manshadi et al. (2025) proves that certification noise above a threshold causes market collapse. This validates the need for granular quality signals.

---

## References

1. Zhou, C., Chen, H., Wang, S., Sun, X., El Saddik, A., & Cai, W. (2023). Harnessing Web3 on Carbon Offset Market for Sustainability: Framework and A Case Study. *IEEE Wireless Communications*, 30(5), 104-111.
2. Nature Communications. (2024). Systematic assessment of the achieved emission reductions of carbon crediting projects.
3. Annual Review of Environment and Resources. (2025). Are Carbon Offsets Fixable?
4. Trencher, G., et al. (2024). Demand for low-quality offsets by major companies. *Nature Communications*.
5. Carbon Credit Quality Initiative. (2024). Methodology. carboncreditquality.org.
6. Sylvera. (2025). State of Carbon Credits 2025.
7. BeZero Carbon. (2023). Rating Methodology.
8. Calyx Global. (2024). Ratings Explained.
9. MSCI. (2025). State of Integrity in the Global Carbon-Credit Market.
10. Carbon Market Watch / Perspectives Climate Group. (2023). Assessing and comparing carbon credit rating agencies.
11. ICVCM. (2025). CCP Impact Report.
12. Frontiers in Blockchain. (2024). Tokenized carbon credits in VCM: the case of KlimaDAO.
13. Jirasek, M. (2023). Klima DAO: a crypto answer to carbon markets. *Springer*.
14. Finance and Space. (2024). Carbon credits meet blockchain.
15. Gao, H.O. & Liu, X. (2026). CATchain-R: A blockchain-based carbon registry platform. *npj Climate Action*.
16. Jaffer, S., et al. (2024). Global, robust and comparable digital carbon assets. *arXiv/IEEE ICBC*.
17. JPMorgan Kinexys. (2025). Carbon Markets Reimagined.
18. Manshadi, V., et al. (2025). Offsetting Carbon with Lemons. *SSRN*.
19. Berg, F., et al. (2025). The Market for Voluntary Carbon Offsets. *SSRN*.
20. Battocletti, V., et al. (2024). The Voluntary Carbon Market: Market Failures and Policy Implications. *Colorado Law Review*.
21. ScienceDirect. (2025). Addressing scandals and greenwashing in carbon offset markets.
22. Berkeley Carbon Trading Project. (2023). Quality Assessment of REDD+ Carbon Credit Projects.
23. Nguyen, T. (2025). Neutrosophic Delphi-DEMATEL for carbon credit systems.
24. Verra-Pachama. DMRV Pilot. verra.org.
25. Open Forest Protocol. openforestprotocol.org.
26. Isometric. isometric.com.
27. RMI. Carbon Crediting Data Framework.
