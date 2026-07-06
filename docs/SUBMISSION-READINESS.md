# Submission readiness: final handoff

*Status as of the latest `main`. The manuscript is ready to submit; what remains is a short list of human-only steps.*

## Verdict: READY TO SUBMIT

Recommended venue: **Environmental Research Letters (ERL)**, the honest best fit (carbon-integrity empirical work; reviewers who understand adverse selection without the crypto framing being a liability). Cover letter drafted at `docs/cover-letter-erl.md`.

## Automated checks (all pass)
- `manuscript.pdf` builds clean: **21 pages, 0 LaTeX errors**.
- All figures **300 DPI** (`figures/*.png`).
- Required sections present: Data availability, Code availability, Author contributions, Competing interests.
- No leftover TODO / placeholder / FLUID markers in the LaTeX.
- Abstract ~200 words (within ERL limits); main text **~4,000 words on ERL's counting basis** (Methods included; declarations excluded): Methods restructured to a compact summary with full detail relocated to Supplementary Methods, per ERL's explicit guidance to move detailed methods to supplementary materials.
- Living-paper audit: **CLEAR**; all `{{placeholders}}` resolve.
- One-command verification: `python3 tools/verify_headline_numbers.py` (exit 0, 15 checks); reproduction guide at `REPRODUCING.md` + pinned `requirements.txt`.
- Framework-free early-warning variant (cumulative renewable share) triggers the SAME DAY as the Lemons Index (Supplementary Methods); robustness summary at Supplementary Table 6.
- Loki agent-team audit (52 agents, 6 lenses + adversarial verification) complete: 43 findings dispositioned. Gating counterfactual now computed on the REAL deposit stream (0.689 -> 0.506 at BBB, 7.2% admitted; stylized-sim numbers retired); fabricated-input claims removed (BWS panel) or relabelled (BeZero non-blind); profit scripted (~\$10M midpoint); stranded corrected to 9.3M; five citation fixes.
- Cross-asset replication upgraded to quantitative: entry-margin lemons selection replicates in 6/6 NFTX vaults (each p<0.05; sign test p=0.016); exit-margin extraction absent, completing the margin decomposition. Old unreproducible NFTX aggregates (1.3%, 2-31x) superseded by a fully scripted pipeline.
- Remedy folded in from Paper #2 (sacrificed): open-source reference implementation (94 passing Foundry tests, measured gas) in Supplementary; main-text release sentence + ref 19 repointed.
- CarbonPlan-cluster citations added (Badgley 2022 GCB, Haya 2023 FFGC, refs 22-23); suggested-reviewer list at `docs/erl-suggested-reviewers.md`.

## What the paper is (set expectations)
An honest, reproducible credit-level forensic account of the first tokenized carbon-pool collapse:
- composition reversal (69% renewables/hydro, not 4% REDD+);
- account forensics with on-chain contract verification of the top extractor;
- a cross-pool design→quality gradient across 5 pools and 2 independent operators, reported as corroborative and largely definitional (screens are defined on credit type), not as an independent test;
- a real-time early-warning Lemons Index (~7-month lead) + a deployable quality-gating remedy;
- the within-token contrast reported honestly as *strongly suggestive, not causally identified*;
- an on-chain entity-level independence audit of the dual-margin claim (first-funder resolution of the top 20 accounts per margin; separation reported as account-level, not entity-level).

**Ceiling (be honest in the response-to-reviewers):** it is descriptive/cross-sectional, not causally identified. The only clean causal upgrade is the pre-registered mainnet RCT (turnkey: `contracts/experiment/RandomizedGate.sol`, `data/field-experiment/`).

## Known cosmetic figure items (deferred, non-blocking)
- Figs 1/3 use a red-green colormap (colorblind accessibility); their original generator scripts are not in the repo, so a fix requires re-plotting from the underlying JSONs. Panel labels, figure order, and fig5 in-figure stats have been fixed.

## Human-only steps before clicking submit
1. **Read the PDF once end to end**: final author eyes (esp. pp. 3–8: composition, forensics, cross-pool, within-token).
2. **Fill author/affiliation/ORCID/funding** placeholders in the ERL submission form; paste suggested reviewers from `docs/erl-suggested-reviewers.md` (verify emails first).
3. **(Optional, ~10 min) classify VCS-849** in the Verra registry to push C3 coverage 17/18 → 18/18 (does not change conclusions).
4. Confirm the GitHub repo is public (and optionally mint a Zenodo DOI for the release) (data/code availability links resolve).

## The two genuine forward upgrades (not for this paper)
- **Paper #2 (method/tool)**: the on-chain audit method + metadata recovery + early-warning Lemons Index + gating contracts, as a fintech/data/systems contribution. Sidesteps the n=1/causal ceiling. All artifacts already exist.
- **Paper #3 / long-line (RCT)**: run the pre-registered quality-gated retirement experiment for clean causal identification. Author-initiated (partner + IRB + ~6 months); analysis pipeline + power analysis already done.

**Recommendation: submit this paper now; develop Paper #2 next.**
