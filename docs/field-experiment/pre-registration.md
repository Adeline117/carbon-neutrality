# Pre-Registration: Quality-Gated Retirement Field Experiment

*Format follows the AEA RCT Registry schema (https://www.socialscienceregistry.org/).
To be submitted prior to any mainnet deployment of `RandomizedGate.sol`.*

---

## Title

**Does on-chain quality gating of tokenized carbon credits raise the
pool-quality-distribution (PQD) of retired credits? A mainnet randomized
controlled trial.**

## Registration status

- **Status:** draft, pre-deployment
- **Intended registration date:** upon partner signature (Toucan / KlimaDAO 2.0 / Carbonmark / Isometric / Thallo / Senken)
- **Trial ID:** _to be assigned by AEA registry_
- **Primary investigator:** Adeline Wen
- **Affiliation:** _to be added at registration_
- **Contact:** _to be added at registration_

## Abstract

Tokenized carbon credit pools have historically suffered from adverse selection:
pool designs that treat every credit as fungible (most notably Toucan's BCT)
concentrate low-quality credits at the expense of high-quality ones, and the
market's buyer side exits when the pool's Lemons Index rises above a threshold.
Our earlier work (Wen, *Nature Communications* submission, 2026) estimates BCT's
terminal Lemons Index at ~0.72, against ~0.22 for the grade-gated CHAR pool.

This pre-registered mainnet field experiment tests whether quality gating
*causes* the observed pool-quality improvement by randomly assigning retirement
users to either a treatment arm (gate enforced) or a control arm (no gate) via
a verifiable on-chain randomizer (Chainlink VRF v2+). The randomizer contract,
`RandomizedGate.sol`, is deployed upstream of the partner pool's retirement
flow. The same user submitting the same credit has a 50% chance of being
subjected to the gate.

We commit in advance to three hypotheses (H1, H2, H3), one primary outcome,
three secondary outcomes, two robustness checks (RD, wallet-size heterogeneity),
and the full analysis pipeline
(`data/field-experiment/analysis_pipeline.py`). The code is deposited and
hash-pinned before randomization begins.

---

## 1. Hypotheses

**H1 (primary).** Users randomly assigned to the *treatment* arm (quality gate
enforced) will retire credits whose mean composite quality score (tonnes-
weighted, PQD) is strictly higher than users randomly assigned to the *control*
arm (no gate).

  - Formal statement: let $Q_i^{(retired)}$ be the composite quality (in basis
    points, 0–10000) of the credit that user $i$ ultimately retires, and let
    $T_i \in \{0, 1\}$ be the randomized arm. Then
    $E[Q_i^{(retired)} \mid T_i = 1] > E[Q_i^{(retired)} \mid T_i = 0]$.
  - Directional, one-sided prediction; two-sided test at α=0.05.

**H2 (secondary).** The per-tonne retirement price (USD-equivalent) in the
treatment arm is weakly higher than in the control arm. Conditional on retired
credits, we expect a positive, non-zero difference driven by the quality
composition of retirements.

**H3 (secondary).** The probability of using the treatment arm conditional on
*holding* a high-quality credit (final grade ≥ A) is higher than conditional
on holding a low-quality credit. That is, depositor heterogeneity: users
holding high-quality credits self-sort into quality-gated retirement when
given the option.
  - Note: randomization breaks direct self-sorting; H3 is tested on the subset
    of users who commit multiple retirements. For those users we observe the
    share of retirements in each arm that corresponded to their higher-quality
    vs lower-quality holdings.

## 2. Design

### Intervention

`RandomizedGate.sol` is a smart contract that interposes between a user's
retirement request and the underlying burn. Upon `commitRetire(creditToken,
tokenId, amount)`, the credit is transferred to the contract in escrow, and a
Chainlink VRF v2+ randomness request is submitted. When the VRF callback
(`rawFulfillRandomWords`) lands, the user is assigned to `TREATMENT` (lsb=1) or
`CONTROL` (lsb=0) in a 50/50 split, and the assignment is recorded in the
`TreatmentAssigned` event. Settlement (`settleRetire(requestId)`) then either
burns the credit (both arms, if control; treatment only if the credit meets
the configured minimum grade) or refunds the credit to the user (treatment
arm, below-grade credit or stale rating).

### Arms

- **Treatment:** retirement succeeds iff `CarbonCreditRating.meetsGrade(credit,
  tokenId, minGrade) == true` AND `isStale == false`. Otherwise the credit is
  refunded.
- **Control:** retirement succeeds regardless of grade (BCT-style behavior).

### Arm assignment (randomization)

- **Unit of randomization:** the individual retirement (not the user). A
  single user who commits multiple retirements receives an independent draw
  each time. This maximizes power and allows within-user variation.
- **Randomization ratio:** 50/50.
- **Randomization mechanism:** Chainlink VRF v2+ subscription. The VRF keyhash
  and subscription ID are pinned at deploy and visible on-chain. The
  randomness is un-forgeable given VRF's cryptographic assumptions.
- **Commit-reveal property:** because the user's credit is transferred into
  escrow BEFORE the VRF callback, the user cannot withdraw their retirement
  after learning which arm they were assigned to — they pre-commit to accept
  either outcome.

### Sample frame

All wallets that interact with the partner's retirement UI during the
experiment window. No participant solicitation; no PII; no consent form
(see IRB memo, `docs/field-experiment/irb-memo.md`). The deployment
announcement and smart-contract source are public, which satisfies the
disclosure requirement for deceptive-experiment exclusion.

### Experiment window

180 days from `experimentStart`. Both timestamps are immutable constructor
parameters of the gate contract.

## 3. Randomization verification

Upon deployment, we will publish the VRF transaction history and rerun the
off-chain chi-square check from `analysis_pipeline.balance_check` weekly
during the experiment. Any week in which the balance p-value falls below 0.01
triggers a mandated pause (via timelock multisig) and a publicly logged
diagnostic review.

## 4. Outcomes

### Primary outcome

- **Y1**: tonnes-weighted mean composite score (basis points, 0–10000) of
  retired credits, computed per arm of commitment.
  - Source: `composite_bps` emitted on the `RetirementCompleted` event,
    filtered to `retired == true`, weighted by the `amount` field.
  - Analysis: Welch two-sample test on the arm difference; 95% CI.
  - Pre-specified target direction: treatment > control.

### Secondary outcomes

- **Y2**: share of retirements with final grade ≥ A, per arm.
- **Y3**: mean grade ordinal (B=0, BB=1, BBB=2, A=3, AA=4, AAA=5), per arm.
- **Y4**: share of committed retirements that end in a successful burn (vs
  refund), per arm. Under the null of zero selection effect, Y4 in treatment
  is exactly the BCT-like pool's probability that an arbitrary committed
  credit meets the gate. Under H1 with depositor-side self-sorting, Y4 in
  treatment rises over time.
- **Y5 (H2)**: USD per tonne of retired credit, sourced from the partner's
  clearing-price log (off-chain appendix table, `prices.csv`).
- **Y6 (H3)**: arm share as a function of user-level credit-quality
  portfolio (tested on users with ≥2 retirements).

### Exploratory outcomes

- Retirement velocity: time between commit and settle, per arm.
- Project-type decomposition of retired credits, per arm.
- Per-registry composition of retired credits, per arm.

## 5. Randomization

- **Unit:** individual retirement.
- **Method:** Chainlink VRF v2+, committed before user reveals arm.
- **Ratio:** 50/50.
- **Stratification:** none at contract level; optional
  post-hoc stratification on `(grade, project_type, wallet_size)` is a
  robustness check, not an identification strategy.

## 6. Sample size & power

### Target

- **Primary outcome effect size:** shift in mean composite of retired credits.
- **Minimum detectable effect (MDE):** Δ = 1000 basis points (equivalent to a
  +10 point move on the 0–100 composite scale, or about half a grade).
  - Rationale: Wen et al. (Nat. Comms 2026 submission) estimates a ~3000 bps
    gap between BCT (mean 3211 bps) and CHAR (mean 7790 bps). A +1000 bps
    detection target is a third of that and plausibly conservative under
    incomplete self-sorting.
- **Assumed SD of composite within arm:** σ ≈ 1400 bps (BCT empirical).
- **α:** 0.05 (two-sided).
- **Power (1 − β):** 0.80.

### Calculation

Standard two-sample t, equal allocation:
$n_{per arm} = 2 \cdot (z_{1-\alpha/2} + z_{1-\beta})^2 \cdot (\sigma / \Delta)^2$
$n_{per arm} = 2 \cdot (1.96 + 0.84)^2 \cdot (1400 / 1000)^2$
$n_{per arm} = 2 \cdot 7.84 \cdot 1.96 = 30.7$

So ~31 retirements per arm for the marginal mean test. With the 0.1 effect
*on the 0–100 unit scale* (SI units) the requested task specifies — i.e.
Δ = 10 bps, σ = 14 bps — the required sample is
$n_{per arm} = 2 \cdot 7.84 \cdot (14/10)^2 = 30.7$ as well. (The ratio
σ/Δ=1.4 is invariant to scale.)

### Design inflation

The MDE above is for a simple mean comparison. Our design introduces:

1. **Attrition** (user aborts before VRF fulfillment): we budget 5% attrition.
2. **Compliance heterogeneity**: refunded treatment users still count toward
   ITT but not toward TOT; sample size is driven by the ITT pathway.
3. **Robustness tests** (RD, heterogeneity): we want ≥50 retirements in each
   (arm × wallet tercile) cell for the heterogeneity block, and ≥100
   retirements within a ±500 bps bandwidth of the cutoff for the RD jump.

### Target sample size

- **N = 1000 committed retirements** (500 per arm, expected).
- Accounts for attrition and dominates the heterogeneity requirement.
- With the observed BCT historical deposit rate (1187 deposits / ~9 months =
  ~132/month), 1000 retirements are feasible in 180 days on a partner pool
  of comparable scale.

We reserve the right to extend the experiment window if the deposit rate
falls below 100/month for two consecutive months. Any extension is announced
publicly before activation.

## 7. Analysis plan (pre-specified)

All analyses are implemented in `data/field-experiment/analysis_pipeline.py`
and validated against synthetic DGPs in
`data/field-experiment/mock_data_validation.py`. The analysis script is
hash-pinned in the pre-registration; any post-hoc change is reported as an
explicit deviation.

### Primary

Welch two-sample t-test on Y1 (tonnes-weighted mean composite of retired
credits, per arm), two-sided, α=0.05.

### Secondary

Welch t-tests on Y2–Y6; Bonferroni correction across the five secondary
outcomes (α=0.01 per test).

### Robustness

1. **RD at grade cutoff.** In the treatment arm, compare burn-rate for
   credits whose composite is in [cutoff − bw, cutoff) vs [cutoff,
   cutoff + bw), with bw = 500 bps. Under a valid RD, the jump is ~1 (a
   mechanical consequence of the gate) and provides a falsification test on
   the ITT: if we fail to see the jump, the gate itself is mis-wired.
2. **Heterogeneity by wallet size.** Tercile split on user-level total
   committed tonnes. Report separate ITTs; no formal interaction test (the
   tercile split is exploratory, not confirmatory).
3. **Stale-rating robustness.** Re-run primary ITT restricted to retirements
   where `isStale == false` at settlement. Under a stale-rating bias the
   treatment arm appears to reject more credits than it should; filtering
   for fresh ratings should move the point estimate only mildly.
4. **Re-rating robustness.** If any credit's grade is rewritten mid-
   experiment, we keep the first rating the user observed (using
   `lastUpdatedAt` timestamps). An appendix replay using the settlement-time
   rating is a sensitivity check.
5. **Cluster-robust SEs.** Cluster by user.

## 8. Units of analysis

- **Experimental unit:** individual committed retirement.
- **Observation unit:** (user, request_id) pair, joined across
  `TreatmentAssigned` and `RetirementCompleted` events.

## 9. IRB / ethics

See `docs/field-experiment/irb-memo.md`. We anticipate exemption under
45 CFR 46.104(d)(4) (publicly available, non-personally-identifiable data;
the randomizer contract's source is open and the design is disclosed before
enrolment).

## 10. Pre-registered changes log

This file is version-controlled in the repository. Any amendment after the
public registration timestamp is recorded in the trailing "Amendments"
section of this document and committed with the date of the change and a
one-sentence rationale.

## 11. Reproducibility

- **Contracts:** `contracts/experiment/RandomizedGate.sol`
- **Tests:** `contracts/experiment/test/RandomizedGate.t.sol`
- **Analysis pipeline:** `data/field-experiment/analysis_pipeline.py`
- **Synthetic validation:** `data/field-experiment/mock_data_validation.py`
- **Event schema:** see top of `analysis_pipeline.py`.
- **Deployment script:** `script/DeployRandomizedGate.s.sol` (to be added
  at partner signature).
- **Archive hashes:** contract bytecode (post-compilation) and analysis-
  pipeline script (SHA-256) will be published at the AEA registration
  alongside this document.

---

*End of pre-registration.*
