# Submission readiness — final handoff

*Status as of the latest `main`. The manuscript is ready to submit; what remains is a short list of human-only steps.*

## Verdict: READY TO SUBMIT

Recommended venue: **Environmental Research Letters (ERL)** — the honest best fit (carbon-integrity empirical work; reviewers who understand adverse selection without the crypto framing being a liability). Cover letter drafted at `docs/cover-letter-erl.md`.

## Automated checks (all pass)
- `manuscript.pdf` builds clean: **23 pages, 0 LaTeX errors**.
- All figures **300 DPI** (`figures/*.png`).
- Required sections present: Data availability, Code availability, Author contributions, Competing interests.
- No leftover TODO / placeholder / FLUID markers in the LaTeX.
- Abstract **245 words** (within ERL's ~250 limit).
- Living-paper audit: **CLEAR**; all `{{placeholders}}` resolve.

## What the paper is (set expectations)
An honest, reproducible credit-level forensic account of the first tokenized carbon-pool collapse:
- composition reversal (69% renewables/hydro, not 4% REDD+);
- account forensics with on-chain contract verification of the top extractor;
- **cross-pool design→quality relationship across 5 pools and 2 independent operators** (the n=1 answer);
- a real-time early-warning Lemons Index (~9-month lead) + a deployable quality-gating remedy;
- the within-token contrast reported honestly as *strongly suggestive, not causally identified*.

**Ceiling (be honest in the response-to-reviewers):** it is descriptive/cross-sectional, not causally identified. The only clean causal upgrade is the pre-registered mainnet RCT (turnkey: `contracts/experiment/RandomizedGate.sol`, `data/field-experiment/`).

## Human-only steps before clicking submit
1. **Read the PDF once end to end** — final author eyes (esp. pp. 3–8: composition, forensics, cross-pool, within-token).
2. **Fill author/affiliation/ORCID/funding** placeholders in the ERL submission form.
3. **(Optional) trim abstract to 200 words** if the chosen ERL article type requires it (currently 245).
4. **(Optional, ~10 min) classify VCS-849** in the Verra registry to push C3 coverage 17/18 → 18/18 (does not change conclusions).
5. Confirm the GitHub repo is public (data/code availability links resolve).

## The two genuine forward upgrades (not for this paper)
- **Paper #2 — method/tool**: the on-chain audit method + metadata recovery + early-warning Lemons Index + gating contracts, as a fintech/data/systems contribution. Sidesteps the n=1/causal ceiling. All artifacts already exist.
- **Paper #3 / long-line — RCT**: run the pre-registered quality-gated retirement experiment for clean causal identification. Author-initiated (partner + IRB + ~6 months); analysis pipeline + power analysis already done.

**Recommendation: submit this paper now; develop Paper #2 next.**
