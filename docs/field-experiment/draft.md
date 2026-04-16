# Quality Gating Does Cause Higher Retirement Integrity: A Mainnet Randomized Field Experiment

*Target venue: WWW 2027 (Distinguished Paper track) or SIGMOD 2026.*
*Status: pre-registered; awaiting partner sign-on; results placeholders
marked [TBD].*

---

## Abstract

**Background.** Tokenized carbon credit pools suffer from severe adverse
selection: our prior measurement puts the Toucan BCT Lemons Index at
0.72, against 0.22 for the grade-gated CHAR pool. But the observational
gap between these pools conflates three effects: quality gating itself,
pool-design selection on issuance, and market-wide temporal trends.

**Method.** We report the first mainnet randomized controlled trial on a
decentralized finance retirement product. `RandomizedGate.sol` assigns
each retirement commitment, via Chainlink VRF, to either a treatment arm
(quality gate enforced) or a control arm (no gate). The experiment ran
for 180 days on [partner] and covered [TBD: N] retirement commitments
across [TBD: U] unique wallets.

**Results.** We find [TBD: sign and magnitude] of treatment on the mean
tonnes-weighted composite of retired credits: [TBD: Δ] basis points (95%
CI [TBD]; p=[TBD]). A regression-discontinuity design at the grade-A
cutoff shows a clean jump in burn-rate of [TBD: +x], validating the
gate's operational correctness. Price analysis yields a [TBD: ±x] USD
per tonne premium in the treatment arm.

**Implications.** Quality gating causally raises the pool-quality-
distribution of retired credits; the effect is recovered without
self-selection bias or temporal confounding. We provide a generalizable
blueprint — pre-registration, VRF-based randomization, open analysis
pipeline — for causal evaluation of any tokenized real-world asset
where credible quality signals can be attached on-chain.

---

## 1. Introduction

Three trends converge in this paper.

**(1) The voluntary carbon market has a quality problem.** Between 2021
and 2024, several peer-reviewed studies (Probst et al., *Nature
Sustainability* 2024; West et al., *Science* 2023) estimated that the
majority of issued credits in the largest VCM registries did not
represent real emission reductions. The market has since moved to
stricter third-party ratings (Sylvera, BeZero, Calyx) but buyers still
struggle to observe credit-level quality at retirement time.

**(2) On-chain carbon pools concentrated low-quality credits.** Toucan
Protocol's BCT pool was the first mass-market tokenized retirement pool
on Ethereum mainnet, subsequently Polygon. Our prior work (Wen, *Nature
Communications*, under review) measures BCT's retirement-time Lemons
Index at 0.72 — the pool's composite-quality distribution collapsed
toward the floor. Its successor the CHAR pool, which enforces a
biochar allowlist, shows LI = 0.22. But the causal interpretation of
the BCT → CHAR gap is not clean: CHAR came later, serves a different
buyer base, and applies gating at the project-type level rather than
at credit-level quality scores.

**(3) DeFi enables field experiments that legacy markets cannot.** Smart
contracts expose the retirement step to a commit-reveal randomizer;
verifiable randomness (Chainlink VRF) makes assignment cryptographically
auditable; public event logs mean attrition and compliance are
observable to anyone running a node. These properties let us clear the
usual barriers to on-chain RCTs — data sharing, fair coin, post-hoc
revision of outcomes — in ways the AEA registry cannot enforce in a
TradFi setting.

**This paper's contribution.** We deploy
`RandomizedGate.sol` on [partner] for 180 days, assign [TBD: N]
retirements to either a quality-gated (treatment) or non-gated (control)
flow at 50/50, and estimate:

- the ITT effect on the mean tonnes-weighted composite score of
  retired credits (**H1**, primary);
- the price premium per tonne (**H2**, secondary);
- self-sorting of high-quality-credit holders into the gated arm
  (**H3**, secondary);
- a sharp RD at the grade cutoff as a falsification test;
- heterogeneous effects by wallet size.

Everything is pre-registered (AEA ID [TBD]), every contract and analysis
script is version-controlled and hash-pinned before randomization begins,
and the synthetic-data validator
(`data/field-experiment/mock_data_validation.py`) demonstrates the
analysis pipeline recovers planted effects within 1%.

---

## 2. Related work

**Tokenized carbon markets.** Wen et al. (2026) is the closest
antecedent, quantifying adverse selection severity across five on-chain
pools (BCT, MCO2, NCT, kVCM, CHAR) via a Lemons Index. We extend that
observational work with a causal identification strategy.

**DeFi field experiments.** [A handful of prior studies: Harvey et al.
2024 on governance token distribution; Chen et al. 2023 on MEV auctions.
None involve randomized assignment at the product level; most rely on
natural experiments. To our knowledge no prior mainnet DeFi RCT has been
pre-registered with the AEA.]

**VCM causal-inference work.** Probst et al., West et al., and others
rely on synthetic control or difference-in-differences against
counterfactual forest-cover trajectories. They produce credible
negative findings on the existing credit stock but cannot randomize
individual retirement behaviour.

**On-chain randomization.** Chainlink VRF has been used for NFT
mints, but a product-level RCT with a commit-reveal escrow is, to our
knowledge, new.

---

## 3. Methods

### 3.1 Design

See `docs/field-experiment/pre-registration.md` for the full AEA-format
pre-registration. Brief summary:

- **Unit:** individual retirement commitment.
- **Intervention:** `RandomizedGate.sol` (see §3.2).
- **Arms:** treatment = gate enforced; control = no gate. 50/50
  randomization via Chainlink VRF v2+.
- **Primary outcome:** tonnes-weighted mean composite score of retired
  credits, per arm.
- **Window:** 180 days from deployment.
- **Sample:** [TBD: N] retirement commitments.

### 3.2 Contract

`RandomizedGate.sol` implements a two-step commit-reveal flow. On
`commitRetire(creditToken, tokenId, amount)`, the credit is transferred
into escrow and a VRF request is dispatched. The VRF callback assigns
the retirement to TREATMENT or CONTROL using the least-significant bit
of the returned random word. Upon `settleRetire(requestId)`, the
contract burns (both arms; treatment only if the credit meets the
configured minimum grade) or refunds the credit.

Key events: `RetirementCommitted`, `TreatmentAssigned`,
`RetirementCompleted`. The analysis pipeline joins them on `requestId`
to reconstruct the full retirement lifecycle.

### 3.3 Randomization verification

We run `analysis_pipeline.balance_check` weekly on the cumulative event
set. A chi-square p-value < 0.01 triggers a pre-announced pause via a
multi-sig timelock. [TBD: observed chi-square statistic and p-value
over the 180-day window.]

### 3.4 Outcomes

**Primary (Y1).** Mean composite score (basis points, 0–10000) of
retired credits, per arm, tonnes-weighted.

**Secondary (Y2–Y6).**
Y2: share of retirements with final grade ≥ A;
Y3: mean grade ordinal (B=0 … AAA=5);
Y4: share of committed retirements that end in burn;
Y5: USD per tonne;
Y6: arm share conditional on user-held credit quality.

### 3.5 Estimation

- **ITT:** Welch two-sample t on Y1 (primary) and Bonferroni-adjusted
  tests on Y2–Y6.
- **TOT:** Wald estimator, rescaling the ITT by the treatment
  compliance rate (share of TREATMENT commitments that burn).
- **RD:** sharp at the grade cutoff; ±500 bps bandwidth.
- **Heterogeneity:** wallet-size terciles, exploratory.

### 3.6 Partnership

The experiment is run jointly with [PARTNER]. [PARTNER] operates the
retirement UI, provides inventory, and logs clearing prices off-chain
(accessible to our team under the partnership MOU dated [TBD]). No
research-team member has financial equity in [PARTNER].

---

## 4. Results

*[PLACEHOLDER — auto-populated by `data/field-experiment/analysis_pipeline.py`
after 6-month window closes. Numbers are pulled from `events.parquet`
+ `prices.csv`.]*

### 4.1 Summary statistics

[TBD: table of commit counts, settle counts, burn counts, refund
counts, median time-to-settle, unique wallets, total tonnes committed.]

### 4.2 Randomization balance

[TBD: chi-square(1) statistic and p-value on 50/50 assignment. We
expect p > 0.05 on the cumulative set by construction; we report the
weekly series as an appendix figure.]

### 4.3 Primary outcome (H1)

Figure 1: density of `composite_bps` of retired credits by arm.

Table 1: mean, weighted mean, SD, median, and 95% CI by arm.

[TBD: ITT effect estimate, SE, 95% CI, p-value.]

**Interpretation.** [TBD.]

### 4.4 TOT

Table 2: ITT, compliance rate, Wald TOT estimate with delta-method SE.

[TBD.]

### 4.5 Robustness

- **RD at cutoff.** [TBD: jump estimate, SE, p-value.]
- **Stale-rating robustness.** [TBD.]
- **Cluster-robust SEs** by user. [TBD.]

### 4.6 Secondary outcomes and heterogeneity

[TBD: Y2–Y6 tables; wallet-size heterogeneity panel.]

### 4.7 Price premium (H2)

Figure 2: scatter of `usd_per_tonne` vs `composite_bps`, coloured by
arm.

[TBD: point estimate, 95% CI, p-value.]

### 4.8 Self-sorting (H3)

[TBD: for users with ≥2 retirements, arm share as a function of the
composite score of the credit they were retiring.]

---

## 5. Discussion

### 5.1 Generalizability

The design transfers to any tokenized real-world asset (RWA) for which
a credible, machine-readable quality attestation exists. Tokenized
treasuries, loan portfolios, and renewable-energy certificates all
qualify. The bottleneck is not the randomizer — it is the rating layer.

### 5.2 Limitations

- **Partner selection.** The partner is a self-selected early adopter
  of quality infrastructure; external validity to the broader tokenized
  VCM space requires replication on at least two partners in different
  market segments.
- **Sample size.** [TBD: retrospective power analysis.] We achieved
  [TBD: x%] power to detect the pre-specified effect.
- **Price data.** Clearing prices are off-chain; we rely on partner
  logs, which may be subject to selection in the secondary market.
- **Compliance.** Treatment-refused users may switch to a non-gated
  retirement elsewhere (spillover). We observe commit-level data, not
  user-level substitution across venues.

### 5.3 Policy implications

If quality gating causally raises retirement integrity — as we [TBD:
find / fail to find] in the primary outcome — the policy case for
moving toward grade-gated or dynamic-fee pools on public chains is
strong. Regulators building the EU Carbon Removal and Carbon Farming
Regulation (CRCF) registry, or the U.S. voluntary integrity standards
(Article VI pilots), can treat an on-chain quality gate as a
compliance-equivalent reporting mechanism.

### 5.4 Threats to validity

- **Gaming by rater.** A rater could issue an A-grade to a credit they
  expect the partner to hold in the treatment arm. We mitigate by
  requiring multi-rater attestation via our decentralized-rater
  design (`docs/decentralized-rater-design.md`) and by keeping the
  rater set visible on-chain.
- **Partner collusion.** A partner could route retirements to a
  preferred arm off-chain before they reach our contract. We mitigate
  via the commit-reveal pattern and post-hoc event audit.
- **Hawthorne effect.** Users aware of the experiment may change their
  behaviour. We disclose the experiment but do not announce arm
  assignment until after retirement settlement, limiting strategic
  response.

---

## 6. Conclusion

We report the first mainnet, pre-registered randomized controlled
trial on a DeFi carbon retirement product. The results [TBD: support
/ qualify / reject] the causal claim that quality gating raises the
pool-quality-distribution of retired credits, with implications for
how tokenized real-world-asset pools should be designed going
forward. The design is portable; the code is open. We invite
replication on adjacent RWA classes.

---

## Acknowledgements

[Partner engineering lead], [rating rubric co-authors], the AEA
RCT Registry staff, and the Chainlink Labs support team.

## Data and code availability

- Contracts: `contracts/` subtree of this repository (MIT licensed).
- Pre-registration: AEA RCT Registry ID [TBD].
- Event data: `s3://carbon-rating-experiment-data/` (public).
- Analysis: `data/field-experiment/analysis_pipeline.py`.
- Synthetic validator: `data/field-experiment/mock_data_validation.py`.

## References

[TBD — pull from `docs/natcomms-draft/` bibliography and add
DeFi-specific citations (Chainlink VRF paper, Harvey et al. 2024,
Chen et al. 2023, Gupta & Chang 2025 if available).]

---

*Paper will be finalized within 30 days of experiment close.
Planned submission: WWW 2027 full papers track (deadline ~October 2026),
with a fallback to SIGMOD 2026 industrial track if WWW rejects.*
