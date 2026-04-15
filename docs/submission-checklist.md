# Submission Checklists -- All Four Papers

---

## Paper 1: ERL Letter

**Target:** Environmental Research Letters (Letter format)
**Status:** Ready to submit

### Format Compliance
- [ ] Word count: ERL Letters allow up to ~4,000 words (excluding abstract, methods, references). Current draft is within range.
- [ ] Abstract: <= 250 words (current: ~180 words -- within limit)
- [ ] Reference count: no strict limit for ERL, but current 29 references is appropriate
- [ ] Figures: 4 main-text figures planned; ERL allows supplementary without limit
- [ ] ERL requires structured sections (Introduction, Methods, Results, Discussion) -- confirmed present
- [ ] Author affiliations and ORCID prepared
- [ ] LaTeX or Word submission -- confirm ERL template compliance

### Data Availability
- [ ] GitHub repo (https://github.com/Adeline117/carbon-neutrality) is public
- [ ] Assign DOI via Zenodo for the repository snapshot at time of submission
- [ ] 318-credit batch dataset with per-dimension scores included in repo
- [ ] Machine-readable JSON rubrics included in `data/scoring-rubrics/`
- [ ] Bootstrap analysis scripts included and documented
- [ ] LLM panel raw outputs included

### Code Availability
- [ ] Python scoring engine (`score.py`) documented and dependency-free
- [ ] Analysis scripts for CCP calibration, rank correlation, IRR, weight sensitivity documented
- [ ] Requirements file or environment specification present
- [ ] README with reproduction instructions

### Figure Preparation
- [ ] Figure 1 (CCP calibration violin plot): render from data -- currently placeholder description
- [ ] Figure 2 (Spearman correlation heatmap + scatter inset): render from data
- [ ] Figure 3 (34-segment Lemons Index bar chart): render from data
- [ ] Figure 4 (Weight robustness summary): render from data
- [ ] All figures at >= 300 DPI for publication
- [ ] Figure source data files prepared for journal deposit

### Cross-Reference Consistency
- [ ] ERL mentions companion empirical paper (Nat Comms) -- currently present in Section 4.3
- [ ] ERL mentions companion systems paper (WWW) -- NEEDS ADDING
- [ ] Reference list entries for companion papers use consistent format: "Wen, A. [Title]. Companion paper, [journal] (in preparation/submitted)."
- [ ] Companion paper references do not create circular dependency at review time

### Supplementary Materials
- [ ] Supplementary outline (docs/erl-draft/supplementary-outline.md) finalized
- [ ] All supplementary tables and figures rendered
- [ ] Supplementary materials PDF compiled

### Cover Letter
- [ ] Cover letter (docs/erl-draft/cover-letter.md) finalized
- [ ] Three suggested reviewers included (Schneider, Haya, Calel)
- [ ] None of the suggested reviewers are in the 20-expert candidates list (verified: Schneider is in the list -- see note below)

> **NOTE:** Lambert Schneider appears in both the suggested reviewer list and the v0.5 expert candidates list. If he has already been contacted for the BWS questionnaire, replace him with an alternative. Suggested replacement: **Robert Huber** (TU Berlin), author of the systematic review of quality criteria in carbon crediting (J. Environ. Manage., 2024).

### Preprint Strategy
- [ ] Submit to arXiv (q-fin.GN or econ.GN) simultaneously with journal submission
- [ ] arXiv submission uses the same version as journal submission
- [ ] arXiv ID noted in cover letter if available before journal review

---

## Paper 2: Nature Communications Article

**Target:** Nature Communications
**Status:** NOT ready -- depositor-level on-chain data collection pending (placeholder values throughout)

### Format Compliance
- [ ] Word count: Nat Comms Articles allow up to ~5,000 words main text. Check current length after placeholder filling.
- [ ] Abstract: <= 150 words (Nat Comms limit). Current abstract has placeholders -- will need word count check after filling.
- [ ] Reference count: no strict limit; current ~42 references is appropriate
- [ ] Figures: 5 main-text figures planned (Nat Comms allows up to 8 display items)
- [ ] Methods section can be placed at end or in Supplementary -- currently at end
- [ ] Reporting Summary and Data Availability Statement required
- [ ] Author contributions statement required

### Data Availability
- [ ] GitHub repo public with DOI via Zenodo
- [ ] 318-credit batch dataset included
- [ ] **BLOCKING:** Depositor-level event logs and portfolio reconstructions -- NOT YET COLLECTED
- [ ] Depositor analysis scripts present in `data/depositor-analysis/`
- [ ] On-chain data extraction scripts documented

### Code Availability
- [ ] Python scoring engine documented
- [ ] Depositor-level analysis pipeline documented
- [ ] Statistical analysis scripts (Wilcoxon, permutation, bootstrap) documented

### Figure Preparation
- [ ] Figure 1 (representative depositor portfolio): BLOCKED -- needs on-chain data
- [ ] Figure 2 (quality differential distribution): BLOCKED -- needs on-chain data
- [ ] Figure 3 (34-segment Lemons Index): can be rendered now
- [ ] Figure 4 (time-stratified adverse selection): BLOCKED -- needs on-chain data
- [ ] Figure 5 (counterfactual quality gating): can be rendered now

### Cross-Reference Consistency
- [ ] Nat Comms cites ERL as "companion methods paper" -- present (ref ^6^ in sections-1-2, ref [41] in sections-5)
- [ ] Nat Comms cites WWW as "companion systems paper" -- present (ref ^8^ in sections-1-2, ref [42] in sections-5)
- [ ] Nat Comms mentions Nat Sust Perspective -- NEEDS ADDING
- [ ] Reference format for companion papers is consistent

### Placeholder Resolution
- [ ] All [BRACKETED_PLACEHOLDERS] filled with real data from on-chain extraction
- [ ] Statistical tests rerun with real data
- [ ] Effect sizes recomputed
- [ ] Figures regenerated

### Preprint Strategy
- [ ] Submit to arXiv simultaneously with journal submission
- [ ] Coordinate arXiv timing with ERL preprint to avoid confusion

---

## Paper 3: Nature Sustainability Perspective

**Target:** Nature Sustainability (Perspective format)
**Status:** Ready for editorial review; placeholders for expert quotes remain

### Format Compliance
- [ ] Word count: Nat Sust Perspectives allow ~2,000 words. Current draft appears within range.
- [ ] Reference count: maximum 30 references. Current: 30 references exactly -- at limit.
- [ ] Figures: Perspectives typically allow 1--2 display items. None currently in draft -- check if figure needed.
- [ ] No Methods section required for Perspectives
- [ ] Nat Sust requires a "Competing Interests" statement

### Data Availability
- [ ] Companion datasets referenced via the ERL and Nat Comms repos
- [ ] No independent dataset for the Perspective itself

### Cross-Reference Consistency
- [ ] Perspective cites ERL framework results -- present via ref [8] (CCP data) and ref [9] (Lemons Index data)
- [ ] Perspective cites Nat Comms depositor-level evidence -- present via ref [14]
- [ ] Perspective cites WWW systems paper -- present via ref [18]
- [ ] All four self-citations use "companion paper" or "companion analysis" phrasing -- verified
- [ ] Cross-references use consistent titles

### Content Items
- [ ] Three expert quote placeholders (Cullenward, Manshadi, Trencher) -- resolve before submission
  - Option A: obtain actual quotes from named experts
  - Option B: remove placeholders and rephrase as author assertions
- [ ] Ensure no new data claims beyond what ERL and Nat Comms report

### Preprint Strategy
- [ ] Nature Sustainability does NOT allow preprints posted after submission (check current policy)
- [ ] If preprinting, must be done BEFORE submission
- [ ] Alternative: no preprint for Perspective piece

---

## Paper 4: WWW 2027 Conference Paper

**Target:** The Web Conference 2027 (WWW 2027)
**Status:** Ready to submit

### Format Compliance
- [ ] Page count: WWW full papers typically 12 pages (ACM two-column format). Verify current draft fits.
- [ ] ACM conference template (acmart, sigconf format) compliance
- [ ] Abstract: <= 250 words (ACM limit)
- [ ] CCS concepts and keywords prepared
- [ ] ACM Reference Format citation block at bottom of first page
- [ ] References in ACM format (numbered, bracketed)

### Data Availability
- [ ] GitHub repo public
- [ ] All Foundry test files reproducible via `forge test`
- [ ] Smart contract source code in `contracts/`
- [ ] Gas benchmark data reproducible

### Code Availability
- [ ] Foundry test suite fully documented
- [ ] Contract deployment scripts present
- [ ] Python scoring engine for off-chain/on-chain equivalence validation
- [ ] Base Sepolia deployment addresses documented (if applicable)

### Figure Preparation
- [ ] Figure 1 (ERC-CCQR architecture diagram -- three compliance levels): render from description
- [ ] Figure 2 (sequence diagrams -- three composability patterns): render from description
- [ ] Figure 3 (gas cost breakdown -- stacked bar chart): render from benchmark data
- [ ] Figure 4 (CCP calibration violin plot): render from data
- [ ] Figure 5 (per-dimension kappa bar chart): render from IRR data
- [ ] Figure 6 (Lemons Index comparison): render from data
- [ ] All figures compatible with ACM two-column format

### Cross-Reference Consistency
- [ ] WWW cites ERL for framework validation -- NEEDS ADDING (currently references validation data inline without explicit companion citation)
- [ ] WWW mentions Nat Comms for depositor-level adverse selection -- NEEDS ADDING
- [ ] Reference entries for companion papers added to reference list

### Preprint Strategy
- [ ] WWW typically does NOT allow public preprints during review (double-blind)
- [ ] Do NOT post to arXiv before WWW notification
- [ ] Ensure GitHub repo does not reveal author identity if double-blind review required
- [ ] Check WWW 2027 specific anonymity policy

### Submission Logistics
- [ ] Track selection: "Web3 and Decentralized Systems" (primary)
- [ ] Submission via conference management system (likely OpenReview or HotCRP)
- [ ] Submission deadline confirmed
- [ ] Author registration on submission platform completed
- [ ] Reviewer suggestions prepared (see submission-notes.md)

---

## Cross-Cutting Items (All Papers)

### Cross-Reference Matrix

| Paper | Cites ERL? | Cites Nat Comms? | Cites WWW? | Cites Nat Sust? |
|-------|-----------|-----------------|-----------|----------------|
| ERL | -- | Yes (Sec 4.3, as "companion paper in preparation") | **MISSING** | N/A |
| Nat Comms | Yes (ref ^6^/[41]) | -- | Yes (ref ^8^/[42]) | **MISSING** |
| Nat Sust Perspective | Yes (ref [8],[9]) | Yes (ref [14]) | Yes (ref [18]) | -- |
| WWW | **MISSING** | **MISSING** | -- | N/A |

### GitHub Repository Preparation
- [ ] README updated with paper titles, submission status, and reproduction instructions
- [ ] Repository cleaned of any draft-stage comments or internal notes
- [ ] MIT licence file present
- [ ] Zenodo DOI reserved and linked

### Figure Rendering Pipeline
- [ ] Identify all placeholder figures across all four papers
- [ ] Create rendering scripts (matplotlib/seaborn) for each figure
- [ ] Render at publication quality (300+ DPI, vector where possible)
- [ ] Ensure consistent colour scheme and typography across papers
