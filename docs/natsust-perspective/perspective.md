# The Convergence Paradox: Why Six Carbon Market Frameworks Chose the Same Binary Trap

*Adeline Wen*

*Target: Nature Sustainability, Perspective (~2,000 words, 30 references max)*

---

In November 2025, Singapore became the first sovereign government to mandate commercial carbon credit quality ratings for compliance-market purposes, appointing BeZero Carbon, Calyx Global, and Sylvera to assess credits under its International Carbon Credit Framework [1]. The appointment was not an isolated regulatory experiment. It was the sixth instance of the same institutional move: the Integrity Council's Core Carbon Principles (CCP) [2], the Paris Agreement's Article 6.4 Supervisory Body standards [3], ICAO's CORSIA Emissions Unit Eligibility Criteria [4], the EU Carbon Removal Certification Framework [5], and the VCMI Claims Code [6] had all, independently, converged on the same diagnosis --- that carbon credit quality must be assessed against integrity criteria spanning additionality, permanence, quantification, and safeguards. Six governance frameworks. The same integrity criteria. The same conclusion.

And the same blind spot. All six implemented their quality requirements as binary gates: a credit is eligible or ineligible, approved or rejected, CCP-labelled or not. None provides continuous quality scoring. None quantifies the uncertainty of its assessment. None offers an automated enforcement interface. The convergence proves the diagnosis is correct. The uniform binary implementation reveals that the solution is incomplete. Binary gates are necessary --- they prevent the worst credits from entering regulated markets --- but they are structurally insufficient to prevent the second-worst from crowding out the best within the approved tier.

## The binary gate problem

The strongest available evidence for binary gating's value comes from the ICVCM's CCP label, the most influential of the six frameworks. Scoring 318 credits across 17 methodology categories, we find that CCP eligibility produces a 1.99-grade separation between CCP-eligible and non-CCP credits (Cohen's *d* = 1.80, *p* < 10^-38), independently validated by Calyx Global's measurement of approximately two grade levels on their own scale [7,8]. No CCP-eligible credit scored in the lowest tier; no non-CCP credit scored in the highest. A randomly chosen CCP credit outranks a randomly chosen non-CCP credit 91% of the time. CCP works. It separates populations that should be separated.

But here is the number that should give every policymaker pause: the Lemons Index --- a metric of adverse selection severity bounded between 0 (no quality degradation) and 1 (complete quality failure) --- for the CCP-eligible pool is 0.419 [9]. Even after the most authoritative quality filter in the voluntary carbon market has done its work, 42% quality degradation persists. CCP reduces the aggregate Lemons Index from 0.667 (the non-CCP baseline) to 0.419 --- a 37% improvement. Significant, but not solved.

The reason is structural. Within the CCP-eligible tier, credit grades span from BBB (barely above the investment-grade threshold) to AAA (the highest tier). Forty-three percent of CCP-eligible credits score BBB --- the modal grade [8]. These credits dominate pooled pricing because they are the most numerous, dragging down the average price that all CCP-eligible credits receive. Meanwhile, the 8% that score AAA are undervalued in any pooled equilibrium. The quality gradient above the binary threshold is real, consequential, and invisible to any framework that stops at pass/fail.

The analogy to credit markets is precise. Bond ratings did not stop at "investment grade versus junk" because institutional buyers discovered that a BBB-rated corporate bond and an AAA-rated sovereign bond could not trade at the same price without destroying allocative efficiency. The carbon market has not yet learned this lesson. MSCI data shows that high-integrity credits already command a 4:1 price premium over low-integrity credits, up from 2:1 in 2024 [10]. The market is pricing quality when it can see it. The problem is that the dominant governance frameworks give it only one bit of quality information: approved or not.

[PLACEHOLDER: Danny Cullenward, University of Pennsylvania --- "Binary certification was the right first step, but the data are now clear that it creates a false equivalence within the approved tier that the market cannot resolve without finer-grained signals."]

## Evidence from tokenized markets

The consequences of binary-only quality information are not theoretical. The Toucan Base Carbon Tonne (BCT) pool --- launched in October 2021 to aggregate heterogeneous Verra credits into a single fungible DeFi token --- provides the canonical failure case. BCT's Lemons Index reached 0.724 at its 2022 peak: the average credit scored below the 28th percentile, with zero credits rated A or above [9]. BCT sat 6.2 standard deviations above the random-pool baseline in a null model of 10,000 simulated pools [9]. This was not bad luck. It was adverse selection operating exactly as Akerlof predicted [11] and as Manshadi, Monachou, and Morgenstern formalised for carbon markets specifically [12]: rational depositors retained their highest-quality credits for premium OTC markets and deposited their lowest-quality ones into the fungible pool. CarbonPlan found that 99.9% of BCT credits were ineligible for CORSIA [13]. The pool collapsed not because blockchain infrastructure failed, but because quality information was absent at the point of deposit.

The natural experiment is equally instructive. Toucan CHAR, a biochar-specific pool on the same blockchain infrastructure, restricts deposits to an allowlist of high-integrity biochar projects. CHAR's Lemons Index: 0.221 --- less than one-third of BCT's --- with 100% of credits scoring A or above [9]. Both pools operated on Base, drew from overlapping registries, and launched into the same market. The 0.503-point gap between them quantifies the value of quality curation. CHAR achieved its quality profile through type restriction rather than continuous scoring --- a blunt instrument that works for a single credit category but cannot generalise. A companion empirical study details the depositor-level evidence of strategic quality selection across these pools and the counterfactual simulations showing that an on-chain quality gate at the BBB threshold would have reduced BCT's Lemons Index from 0.724 to 0.405 by admitting only 5% of its historical inventory [14].

The lesson is stark: quality information must be as granular as price information. When the market can price a carbon credit to the cent but cannot assess its quality beyond a binary label, information asymmetry is guaranteed. The systematic scan across 34 pool segments --- stratified by project type, vintage, CCP status, and registry --- reveals that the Lemons Index varies by an order of magnitude, from 0.076 (DACCS-only pools) to 0.759 (renewable energy pools) [9]. The quality gradient exists. It is measurable. It is currently invisible to the governance infrastructure.

[PLACEHOLDER: Vahideh Manshadi, Yale University --- "Our model shows that when certification noise exceeds a threshold, adverse selection becomes inevitable. The empirical data from tokenized pools confirm that binary certification has not brought noise below that threshold."]

## What continuous quality infrastructure looks like

If binary gates are necessary but insufficient, what does sufficient look like? The empirical evidence points to four requirements.

First, quality scoring must be open and reproducible. Proprietary ratings from commercial agencies provide value to their subscribers but cannot serve as public infrastructure. When three agencies rate the same six REDD+ projects, their mean pairwise Spearman correlation is +0.009 --- effectively zero [15]. The same Amazon REDD+ project receives top marks from one agency and the lowest possible rating from another. Singapore's regulatory panel will confront this inter-agency disagreement directly when its three appointed raters deliver divergent assessments of the same project. Transparent methodologies with machine-readable rubrics and open-source scoring engines enable independent verification and reduce the certification noise that drives adverse selection in Manshadi et al.'s model.

Second, quality must be distributional, not a point estimate. A credit scored AAA with 96% confidence is fundamentally different from one scored AAA with 57% confidence [16]. Publishing P(grade) --- the posterior probability that a credit belongs to each grade tier given measurement uncertainty --- transforms a brittle point rating into an honest uncertainty statement. No carbon credit rating system, commercial or regulatory, currently provides this. Insurance underwriters pricing carbon credit invalidation risk need probability-of-loss estimates, not letter grades [17]. Distributional scoring translates directly into the actuarial inputs that the emerging carbon insurance market requires.

Third, quality signals must be composable with market infrastructure. The on-chain carbon market --- already processing hundreds of millions of dollars in tokenized credits --- needs quality gates that are callable at the smart contract level. A `meetsGrade()` view function that any pool or retirement contract can invoke at deposit time generalises CHAR's binary allowlist to continuous, parameterisable thresholds, and a companion technical paper describes the implementation and gas economics of this interface standard [18].

Fourth, and most consequentially, quality infrastructure must bridge the gap between what Singapore started and what the data says is needed. Singapore's mandate is a phase transition: the first sovereign regulator embedding commercial ratings into a compliance pipeline. But the appointed agencies produce proprietary, point-estimate ratings on incompatible scales. The gap between Singapore's institutional innovation and the quality infrastructure the data demands is the gap between recognising that quality matters and building infrastructure that makes quality actionable at market scale. Nine Article 6 bilateral partner countries --- Papua New Guinea, Ghana, Bhutan, Peru, Chile, Rwanda, Paraguay, Thailand, Vietnam --- will have their project credits assessed through this framework [1]. The scale of the quality assessment challenge is already beyond what proprietary, manually reviewed, binary systems can serve.

## The economic case for continuous quality infrastructure

The costs of quality opacity and the returns to quality transparency are not symmetric. The Toucan BCT collapse alone represented an estimated $64--122 million in adverse selection deadweight loss --- value transferred from buyers who assumed average pool quality to depositors of below-average credits [19]. More broadly, MSCI's 4:1 quality price ratio, applied to 2025 retirement volumes of approximately 160 million tCO2e, implies that quality-tiered pricing could unlock $76--278 million per year in price discovery value by allowing the 28% of credits that score A or above to trade at prices commensurate with their quality, rather than being dragged down by the 50% that score below investment grade [10,19]. Combining CCP's binary filter with continuous scoring above the threshold adds approximately $40 million per year in incremental price discovery within the CCP-eligible tier alone [19].

Against these benefits, the cost of quality infrastructure is vanishingly small. On-chain quality checks via a composable interface cost approximately $0.003--0.005 per query at current Layer 2 fee levels. Rating 160,000 unique credit vintages costs under $8,000 in gas. Total annual infrastructure cost, including off-chain computation: less than $1 million [19]. The benefit-cost ratio exceeds 100:1 under conservative assumptions. This is because quality gating is fundamentally an information intervention --- the cost is the cost of producing and distributing a signal, while the benefit accrues across the entire market volume that consumes that signal.

[PLACEHOLDER: Gregory Trencher, Kyoto University --- "The economic logic is overwhelming. The barrier to continuous quality infrastructure is not cost --- it is institutional inertia and the vested interest of incumbents in proprietary information advantages."]

## The convergence demands a response

Six governance frameworks independently arrived at the same integrity criteria. The convergence proves the diagnosis is right. All six chose binary implementation. The uniform choice proves the solution is incomplete. The punchline is a number: CCP-eligible pool LI = 0.419. Binary is necessary. Binary is insufficient.

The data, the infrastructure, and the first regulatory mandate now exist. Singapore has established the institutional precedent. The empirical evidence --- 318 credits, 34 pool segments, six tokenized pools, counterfactual simulations, depositor-level adverse selection data --- quantifies both the problem and the solution. Open-source scoring engines, composable on-chain interfaces, and distributional uncertainty quantification are not future technology; they are deployed and tested [14,18]. What remains is the policy choice: will the next generation of carbon market governance move from binary certification to continuous quality infrastructure, or will it accept that 42% quality degradation within the approved tier is an acceptable cost of institutional simplicity?

The voluntary carbon market channels over $2 billion annually toward climate mitigation [20]. Fewer than 16% of credits represent real emission reductions [21]. The gap between these two facts is an information gap. Closing it requires quality infrastructure that is as granular, as transparent, and as composable as the price infrastructure the market already possesses. The convergence paradox is not that six frameworks got the diagnosis wrong. It is that all six stopped one step short of the cure.

---

## References

1. Singapore National Environment Agency. Carbon rating panel: appointment of BeZero, Calyx Global, and Sylvera under the International Carbon Credit Framework. NEA Regulatory Notice (2025).
2. Integrity Council for the Voluntary Carbon Market. The Core Carbon Principles, Assessment Framework and Assessment Procedure. ICVCM (2023).
3. UNFCCC Article 6.4 Supervisory Body. Methodological standards for baselines, additionality, and monitoring. UNFCCC Decision 3/CMA.3 (2021); SB methodological tools (2025).
4. International Civil Aviation Organization. CORSIA Emissions Unit Eligibility Criteria. ICAO Document Series (2024).
5. European Union. Regulation (EU) 2024/3012 establishing a Union certification framework for carbon removals and carbon farming. *Off. J. Eur. Union* L series (2024).
6. Voluntary Carbon Markets Integrity Initiative. VCMI Claims Code of Practice v2. VCMI (2024).
7. Calyx Global. Are carbon credit quality indicators delivering? Calyx Global Research Report (2025).
8. Wen, A. CCP empirical weight validation: 1.99-grade separation on 318 credits. Companion dataset (2026).
9. Wen, A. Systematic Lemons Index scan: adverse selection severity across 34 VCM pool segments. Companion dataset (2026).
10. MSCI. State of integrity in the global carbon-credit market. MSCI ESG Research (2025).
11. Akerlof, G. A. The market for "lemons": quality uncertainty and the market mechanism. *Q. J. Econ.* **84**, 488--500 (1970).
12. Manshadi, V. H., Monachou, F. & Morgenstern, I. Offsetting carbon with lemons: adverse selection and certification in the voluntary carbon market. SSRN Working Paper (2025).
13. CarbonPlan. OffsetsDB: a comprehensive database of carbon offset projects. CarbonPlan (2024).
14. Wen, A. Quantifying adverse selection in tokenized carbon credit pools. Companion paper, *Nature Communications* (in preparation).
15. Carbon Market Watch & Perspectives Climate Group. Assessing and comparing carbon credit rating agencies. Carbon Market Watch Report (2023).
16. Wen, A. Distributional uncertainty quantification for carbon credit quality ratings. In Ref. 14, Methods.
17. Cabiyo, B. & Field, C. B. Embracing imperfection: carbon offset markets must learn to mitigate the risk of overcrediting. *PNAS Nexus* **4**, pgaf091 (2025).
18. Wen, A. Composable quality attestations for tokenized carbon credits. Companion paper, *Proc. WWW 2027* (in preparation).
19. Wen, A. Economic impact of quality gating on the voluntary carbon market. Companion analysis (2026).
20. Ecosystem Marketplace. State of the Voluntary Carbon Market 2025: Meeting the Moment. Ecosystem Marketplace (2025).
21. Calel, R., Colmer, J., Dechezlepretre, A. & Glachant, M. Systematic assessment of the achieved emission reductions of carbon crediting projects. *Nat. Commun.* **15**, 5535 (2024).
22. Trencher, G. et al. Demand for low-quality offsets by major companies undermines climate integrity of the voluntary carbon market. *Nat. Commun.* **15**, 10890 (2024).
23. Coglianese, C. & Giles, C. Auditors can't save carbon offsets. *Science* **389**, 6733 (2025).
24. Allen, M. et al. The Oxford Principles for Net Zero Aligned Carbon Offsetting. University of Oxford (2020).
25. Berg, F., Kolbel, J., Pavlova, A. & Rigobon, R. The market for voluntary carbon offsets. SSRN Working Paper (2025).
26. Integrity Council for the Voluntary Carbon Market. CCP Impact Report. ICVCM (2025).
27. Haya, B. K. et al. Are carbon offsets fixable? *Annu. Rev. Environ. Resour.* (2025).
28. Zeng, Y. et al. Limitations of carbon markets for biodiversity conservation. *Nat. Rev. Biodivers.* (2026).
29. Sylvera. State of Carbon Credits 2025: From Volume to Value. Sylvera Research Report (2025).
30. Battocletti, V., Caldwell, L. & Macey, J. The voluntary carbon market: market failures and policy implications. *Colo. Law Rev.* **95**, 889--960 (2024).
