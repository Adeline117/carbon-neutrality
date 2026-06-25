# Feasibility: causal identification of the pool-design effect *without* a partner platform

*Checked 2026-06-25 against the existing BCT on-chain dataset. Verdict: no usable
quasi-experiment exists in this data; the only no-partner path to true causal
evidence is a self-recruited incentivized RCT.*

We assessed whether the pool-design effect can be identified causally from
existing data, avoiding both the within-token pseudo-replication problem (a
two-pool contrast re-labelled 14 times) and the need for a cooperating retirement
platform. Two quasi-experimental strategies were evaluated.

## 1. Regression discontinuity at NCT's vintage ≥ 2012 eligibility cutoff — INFEASIBLE

NCT admits only AFOLU credits with vintage ≥ 2012, a sharp administrative cutoff.
The treatment (NCT-eligibility) only "bites" for AFOLU credits, so the running
variable (vintage) must be evaluated within the AFOLU subset.

- AFOLU tokens by vintage near the cutoff: **2011 → 1 token, 2012 → 7 tokens**
  (38 AFOLU tokens total, spread 2009–2019).
- A regression discontinuity needs substantial mass on both sides of the cutoff.
  One token immediately below the threshold provides no identification.

**Verdict: infeasible (no mass at the boundary).**

## 2. Difference-in-differences around the January 2023 REDD+ scandal — INFEASIBLE

The Guardian / Die Zeit / SourceMaterial REDD+ investigation (18 Jan 2023) is a
clean, type-specific exogenous quality shock (it hit REDD+ credibility, not
renewables), which would in principle support a REDD+-vs-renewables DiD on
redemption behaviour.

- But **all BCT redemption activity ends by 2022-12-28** (last REDD+ redemption
  2022-12-23; last event of any type 2022-12-28). The pool was effectively dead
  before the shock.
- There are **zero post-shock outcome events**, so the DiD has no treated
  post-period. The market-wide crypto shocks that *are* inside the window
  (Terra, May 2022; FTX, Nov 2022) hit every credit type and provide no clean
  control, so they cannot serve as a type-specific quality shock.

**Verdict: infeasible (the market died before the only clean shock landed).**

## Conclusion

The existing BCT dataset contains no exogenous variation that cleanly separates
the pool-design effect from confounds. The honest options are therefore:

1. **Accept the descriptive framing** (current manuscript): the within-token
   contrast is reported as strongly suggestive, not causal. No partner needed.
2. **Run a self-recruited incentivized RCT** (`RandomizedGate.sol` +
   `analysis_pipeline.py` + `power_analysis.py`): recruit participants directly
   (no third-party platform), randomize via the contract, pay small real or
   testnet stakes. This is a true RCT and the only no-partner path to causal
   identification, but it requires recruitment, a small budget, and IRB.

There is no free quasi-experimental lunch in this data.
