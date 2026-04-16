# IRB Memo — Quality-Gated Retirement Field Experiment

*Prepared for submission to the home-institution IRB prior to the public
AEA registration of the pre-registered trial. Intended to support an
exemption determination; a full expedited review will be requested if the
IRB disagrees.*

---

## Principal investigator

_Adeline Wen (adelinewen@…)_
_Co-investigators: listed in the partnership agreement once signed._

## Study title

"Does on-chain quality gating raise the pool-quality-distribution of
retired carbon credits? A mainnet randomized controlled trial."

Companion pre-registration: `docs/field-experiment/pre-registration.md`.

## Summary of the study

The research team has deployed (or will deploy, on partner sign-off) a
smart contract, `RandomizedGate.sol`, that sits in front of a
carbon-credit retirement endpoint on a public blockchain. When a user
submits a retirement request, the contract randomly assigns them to one
of two arms:

- **TREATMENT**: the retirement is subject to a quality gate (only
  succeeds if the credit is rated at or above a pre-specified grade).
- **CONTROL**: the retirement is not subject to the gate (succeeds
  regardless of grade, matching the default behaviour of existing
  tokenized-carbon pools like Toucan's BCT).

Randomization is performed on-chain using Chainlink VRF. The analysis
uses only data that are automatically written to the public blockchain
by the contract (event logs emitted by `RandomizedGate`), plus off-chain
per-retirement clearing prices that the partner protocol already logs
for its own internal accounting.

## Why we are asking for an exemption determination

We believe the study qualifies for exemption under U.S. federal Common
Rule **45 CFR 46.104(d)(4)** (secondary research for which consent is
not required, involving the collection or study of information that is
publicly available, or of information recorded by the investigator in
such a manner that the identity of the human subjects cannot readily be
ascertained directly or through identifiers linked to the subjects).

Our reasoning:

1. **No private identifiable information is collected.** The unit of
   observation is a wallet address (hexadecimal string) and the
   associated on-chain events. Wallet addresses are pseudonymous by
   design. The research team does not collect names, email addresses,
   phone numbers, IP addresses, KYC documents, or any other identifier
   that would let us re-associate a wallet with a natural person. The
   partner protocol may, independently, hold KYC information on some
   users to comply with its own regulatory regime; we neither request
   nor store such information.

2. **All event data are public.** Blockchain events are, by construction,
   broadcast to every node on the network and are permanently available
   via any RPC endpoint. A third-party researcher with no institutional
   affiliation could download the identical dataset.

3. **The intervention is disclosed.** The contract's source code is
   open-source under MIT license; the partner's retirement UI displays
   a one-sentence notice that the pool is running a randomized research
   study; and the pre-registration is deposited with the AEA RCT
   Registry before randomization begins. There is no deception and no
   withholding of material information from participants.

4. **Subjects are economic decision-makers, not research subjects in the
   conventional sense.** The intervention (a gate that either succeeds
   or refunds a user's tokenized carbon credit) is identical to the
   kind of product-design change any DeFi protocol may roll out
   unilaterally. We are merely randomizing *which* users receive the
   change, and for what window of time, to support causal inference.

5. **No incentive structure targets subjects directly.** The gate's
   outcome (burn or refund) is already part of the space of behaviours
   a non-research partner would observe. Treatment-arm users whose
   credits are below-grade are refunded and can resubmit through the
   partner's non-gated inventory at no additional cost.

## Risks to human subjects

- **Financial risk.** The gate may refund a user's credit in the
  treatment arm, introducing a small timing inconvenience (the user
  must re-submit through a non-gated path). The credit itself is not
  destroyed; no loss of value results from assignment to the treatment
  arm. Gas costs for the extra transaction are bounded by Base (or
  equivalent L2) gas economics — estimated median $0.10 per retry.
  The partner protocol has pre-committed to reimburse any gas costs
  that exceed $1.00 for a treatment-refused user, on request.

- **Reputational risk.** Wallet addresses are pseudonymous but not
  private. A motivated adversary could correlate wallet activity with
  other public-chain behaviour and attempt to identify the natural
  person behind a wallet. This risk exists regardless of our study —
  our intervention does not increase it, because the `TreatmentAssigned`
  event we add does not record any information beyond what is already
  inferable from the retirement events the partner protocol emits.

- **Privacy risk.** Minimal. We do not collect, derive, or attempt to
  link off-chain identifiers to wallets.

## Benefits

- Better evidence on whether quality gating meaningfully changes
  retirement behaviour on public chains, which in turn informs the
  design of tokenized-VCM products that could shift real-world
  retirements toward higher-integrity credits.
- A public, peer-reviewed pre-registration and analysis pipeline that
  other researchers can replicate or extend.

## Informed consent

Given the exemption determination we are seeking, informed consent is
not required. The intervention is disclosed in the retirement UI and
in the publicly registered pre-registration; users can opt out by
simply not using the partner protocol. No separate consent document
is served to users.

If the IRB determines that exemption is not appropriate, we will
propose an expedited review under 45 CFR 46.110 Category 7 (research
on individual or group characteristics or behaviour), with waiver of
documented informed consent under 45 CFR 46.117(c)(1)(ii) on the basis
that the research involves no more than minimal risk and could not
practicably be carried out without the waiver (every retirement would
otherwise require a separate UI flow).

## Data management

- All event data are stored on public blockchains and mirrored to an
  S3 archive (`s3://carbon-rating-experiment-data/`) for long-term
  reproducibility. No access control is applied to the archive.
- The analysis code is version-controlled in this repository; a
  post-experiment final commit hash is appended to the AEA
  registration.
- Clearing-price data from the partner protocol are pseudonymized at
  source (wallet addresses only); they are merged with the event data
  on `request_id` and stored in the same public archive.
- Retention: indefinite, as the data are already public.

## Investigator training

All investigators have completed the NIH human-subjects research
training (CITI Program) within the past three years; certificates on
file with the office of research compliance.

## Conflicts of interest

The rating contract (`CarbonCreditRating.sol`) is developed by the PI
as part of an academic research programme; the PI holds no equity in
any of the partner protocols. The partnership agreement, once signed,
will be added as an appendix to this memo and flagged to the IRB for
a financial-conflict review.

## Requested IRB action

Determination of **EXEMPT** under 45 CFR 46.104(d)(4) for the study as
described above, contingent on the UI-disclosure language being
reviewed and approved by the IRB before deployment.

If the IRB finds that the research does not meet the exemption
criteria, we respectfully request an **EXPEDITED** review under
category 7 (45 CFR 46.110).

---

*Prepared April 2026. Revisions will be appended in a dated amendments
section rather than by overwriting the text above.*
