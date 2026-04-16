# Partnership Proposal: First Randomized Field Experiment on Carbon Credit Quality

*A 3-page pitch for tokenized-VCM protocol teams. Sent as a PDF attachment
to a personalized cover email (see `docs/outreach-emails.md` for templates).*

---

## Page 1 — Problem and Opportunity

**Tokenized carbon credit pools are stuck.** BCT collapsed because every
credit was fungible regardless of quality: our measurement (Wen 2026, under
review at *Nature Communications*) puts BCT's terminal Lemons Index at 0.72,
versus 0.22 for the quality-gated CHAR pool. Between those two numbers lies
the entire crypto-native carbon market: buyers left BCT because they couldn't
tell the good credits from the bad, and the market thinned until the pool
stopped clearing.

Every team building an on-chain retirement product today is working around
this problem by hand — allowlists, curated inventories, off-chain quality
checks. These are all reasonable, but they are also all **observational**.
We do not yet have a causal estimate of how much a quality gate actually
changes retirement behaviour, what the price elasticity of demand is for
graded credits, or who the marginal buyers of premium credits are.

**What we propose.** Run a pre-registered, mainnet, randomized field
experiment that inserts a quality gate — randomly, and reversibly — into
your retirement flow. The gate uses our open-source on-chain rating contract
(`CarbonCreditRating.sol`, audited, deployed on Base Sepolia since v0.4) and
the randomizer (`RandomizedGate.sol`, in this repository, 7 passing tests,
chi-square validated on 2,000 simulated users). Chainlink VRF provides the
randomness; commit-reveal stops users from cherry-picking an arm.

**Why this matters to your product.** The most credible critique of your
retirement flow is that you cannot prove, post-hoc, that the gate is
*doing* anything versus how your buyers would have behaved anyway. A
pre-registered RCT gives you that proof. It also positions you as the first
DeFi protocol to run a peer-reviewed, on-chain field experiment — the kind
of methodological credibility institutional buyers ask for before onboarding.

---

## Page 2 — What we bring, what you bring

### What our team provides (already built)

| Asset | Status | Path |
|---|---|---|
| Rating contract (6-dimension composite, grade tiers, disqualifier flags) | Deployed Base Sepolia | `contracts/CarbonCreditRating.sol` |
| Randomizer contract (commit-reveal, VRF v2+) | Implemented, 7 tests passing | `contracts/experiment/RandomizedGate.sol` |
| Test suite (randomization, treatment enforcement, event contract) | 56 tests, all pass | `contracts/experiment/test/RandomizedGate.t.sol` |
| Pre-registration (AEA RCT format) | Draft, ready to submit | `docs/field-experiment/pre-registration.md` |
| Analysis pipeline (ITT, TOT, RD, heterogeneity) | Tested on 6,000 synthetic events | `data/field-experiment/analysis_pipeline.py` |
| Synthetic-data validation | Passing; recovers planted effects within 1% | `data/field-experiment/mock_data_validation.py` |
| IRB exemption memo | Draft, 45 CFR 46.104(d)(4) | `docs/field-experiment/irb-memo.md` |
| Security review of contracts | In progress; independent audit quote obtained | — |
| Academic paper draft (WWW 2027 / SIGMOD 2026 target) | Skeleton committed | `docs/field-experiment/draft.md` |

### What we ask of you

| Item | Details |
|---|---|
| **Deployment slot** | One production retirement endpoint that we can route through the randomizer for 6 months. Your users continue to use your UI; the gate is transparent. |
| **Initial liquidity** | A seed inventory of at least 1,000 tonnes of rated credits, mixed across grades. (We rate via our existing rubric; optionally your team co-rates.) |
| **Governance sign-off** | Your DAO / board / foundation confirms willingness to honour the experiment window (180 days) without interrupting randomization. |
| **UI disclosure** | A one-sentence notice in the retirement flow: "This pool is running a randomized research experiment — see [link] for details." Matches the AEA registry deposition. |
| **Price log access** | Per-retirement clearing price, timestamped. Either pushed to a public endpoint or shared via a read-only S3/postgres link. |

### What you get back

1. **Co-authorship** on the Distinguished Paper submission to WWW 2027 or
   SIGMOD 2026 — your protocol's name in the title, your engineering lead
   as a named author.
2. **First-mover position** on quality DeFi: you are the protocol that
   shipped the experiment that settled the question.
3. **Usable TOT / ITT estimates** for your own pricing, demand forecasts,
   and investor decks — we hand you the CSV, the code, and the interpretive
   write-up.
4. **No downside** on governance: the gate is configurable, the experiment
   window is bounded, and either party can pause via a publicly announced
   timelock.

### Timeline

| Week | Milestone |
|---|---|
| 0–4 | Partner sign-off; KYC/legal paperwork; audit of randomizer against the chain we target |
| 4–8 | Testnet deployment on partner infra; joint dry-run of retirement UX |
| 8 | Pre-registration deposited with AEA; randomizer goes live on mainnet |
| 8–34 | Experiment runs (180 days) |
| 34–36 | Analysis against pipeline; results posted to partner Discord / forum 24 hours before paper submission |
| 36–38 | Paper finalized; joint press release timed with submission |

---

## Page 3 — Named contacts and next step

### Teams we would most like to partner with

We are pitching in parallel to the following teams; the first to sign
locks in exclusive co-authorship for the Distinguished submission.

- **Toucan Protocol** — Raphaël Haupt (Co-founder & CEO). CHAR pool on
  Base is the closest existing quality-gated product; extending CHAR to
  an RCT is the most natural fit.
- **KlimaDAO 2.0** — Marcus Aurelius (Head of Protocol). kVCM retirement
  inventory on Base already clears via a burn; dropping `RandomizedGate`
  in front of kVCM retirements is a ~1-week engineering effort.
- **Carbonmark** — Bram Bailey (Founder & CEO). Marketplace aggregator;
  their retirement-by-wallet UX is well-suited to a user-level RCT.
- **Isometric, Thallo, Senken** — engineering-side conversations pending;
  priority depends on which stack has a live retirement endpoint by
  mid-2026.

### Common objections, answered

- *"Will this slow down retirements?"* No: VRF callback is 2–3 blocks (≈
  5 seconds on Base). User sees a confirmation screen for the arm;
  settlement is a second transaction, batchable. Total latency < 30
  seconds.
- *"What if the gate rejects a paying customer?"* The customer's credit is
  refunded, they are logged as treatment-refused, and they can retry on
  our non-gated inventory immediately. No net UX cost; we gain an
  observation.
- *"Can we trust the randomization?"* Chainlink VRF is cryptographically
  verifiable; the assignment is published on-chain; a pre-registered
  chi-square is re-run weekly and published. If the balance test fails,
  the experiment pauses.
- *"What if our users don't consent?"* The design is disclosed in the UI
  and in a public README. There is no deception. The data collected is
  already on-chain and already public. See the IRB memo for the formal
  case (45 CFR 46.104(d)(4) exemption).

### Next step

Reply to this email with one of three words:

- **"Interested"** — we schedule a 30-minute technical call with your
  engineering lead within a week.
- **"Later"** — we keep you on the shortlist; no commitment.
- **"Pass"** — we remove you from follow-up.

Happy to share the audit quote, the security review, or any of the eight
linked documents on request.

— *The Carbon Rating Research Team, April 2026*

---

*Hard-copy prefix: `docs/field-experiment/` in the repository carbon-neutrality
(private, share on request). All code and documents MIT licensed upon
partner agreement.*
