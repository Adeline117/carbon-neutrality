# Supplementary Note 1: Regulatory convergence across governance frameworks

Six major carbon market governance frameworks now in force or under development require overlapping integrity criteria, yet none provides continuous quality scoring, uncertainty quantification, or automated enforcement.

## Table S8. Mapping of framework dimensions to provisions in six regulatory frameworks

| Dimension | ICVCM CCP | Paris Art. 6.4 | CORSIA | Singapore ICC | EU CRCF | VCMI Claims Code |
|-----------|-----------|----------------|--------|---------------|---------|-------------------|
| Removal type | -- | -- | -- | -- | Art. 4 (4 categories) | Defers to CCP |
| Additionality | Principle 8 | SB standard | EUC Criterion 3 | "Additional" | Art. 4(1)(b) | Defers to CCP |
| MRV grade | Principles 4, 5 | SB standard | EUC monitoring | "Quantified and verified" | Art. 4(1)(a) | Defers to CCP |
| Permanence | Principle 9 | Reversal provisions | EUC permanence | "Permanent" | Art. 4 (4-category) | Defers to CCP |
| Vintage year | -- | -- | -- | -- | -- | -- |
| Safeguards gate | Principle 10 | -- | "Do no net harm" | "No net harm" | Art. 4(1)(d) | Defers to CCP |
| Registry/methodology | Principles 7, 10 | SB standard | TAB approval | Seven principles | CRCF certification | Defers to CCP |
| **Novel capabilities** | | | | | | |
| Continuous 0--100 scoring | No | No | No | No | No | No |
| Distributional P(grade) | No | No | No | No | No | No |
| On-chain meetsGrade() | No | No | No | No | No | No |

## Singapore ICC principle-by-principle alignment

Singapore's seven ICC eligibility principles map to our framework as follows:

1. **Not double-counted.** Registry and methodology scoring + `doubleCounting` disqualifier (cap at B). Full coverage.
2. **Additional.** Additionality dimension (weight 0.200), six-tier continuous assessment. Exceeding coverage (Singapore requires binary compliance; we provide gradient).
3. **Real.** Removal type hierarchy (0.250) + MRV grade (0.200). Full coverage via joint assessment of methodological pathway and measurement rigour.
4. **Quantified and verified.** MRV grade (0.200), differentiating traditional verification (45--59) from digital MRV with continuous sensor data (90--100). Exceeding coverage.
5. **Permanent.** Permanence dimension (0.175), seven-tier rubric mapping storage duration. Full coverage. CCP Principle 9's 40-year/20% buffer threshold corresponds to approximately score 50--55 (lower BBB range).
6. **No net harm.** Safeguards gate: `communityHarm`, `biodiversityHarm`, and `humanRightsViolation` disqualifiers. Exceeding coverage (extends beyond Singapore's requirement of host-country law compliance to include documented biodiversity harm and community opposition).
7. **No leakage.** Partially captured in additionality and removal-type assessments. Not scored as independent dimension. Gap.

Coverage summary: 6/7 full or exceeding, 1/7 partial.

## Policy implications by framework

**CORSIA Phase 2 (2027--2029).** IATA projects demand of 146--236 million units. The quality atlas demonstrates that programme-level TAB approval does not ensure credit-level quality: CarbonPlan found that 99.9% of BCT credits were CORSIA-ineligible. Grade thresholds could function as a second-layer eligibility filter within TAB-approved programmes.

**Paris Agreement Article 6.4.** The CDM-to-PACM transition risks importing CDM-era quality problems. Our CDM-era pool PQD = 0.718 quantifies the legacy quality burden. The vintage gradient (pre-2020 PQD 0.687, 2024+ PQD 0.273) provides a measurable target for transition quality monitoring.

**VCMI Claims Code.** Silver, Gold, and Platinum claim tiers are defined by retirement *volume* but not *quality gradient* within the CCP-eligible set. Quality-weighted retirement accounting could prevent companies from achieving Platinum status with high volumes of marginally CCP-eligible BBB credits.

**EU CRCF.** The CRCF's four-category structure (permanent removal, temporary carbon farming, carbon storage in products, carbon farming) maps to our removal-type hierarchy. The CRCF uniquely requires positive biodiversity impact for carbon farming --- a stronger standard than our current safeguards gate, which penalises documented harm but does not require demonstrated benefit.
