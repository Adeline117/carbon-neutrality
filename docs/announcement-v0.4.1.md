# v0.4.1 announcement (DRAFT, HELD)

*This is a pre-written 1-page announcement to be posted after the Base Sepolia deployment is live and the demo page works. Do NOT post it before the contracts are deployed, the MCC-* addresses are in `v0.4.1-deployment-notes.md`, and the demo page loads a real grade when opened. Posting early means readers follow a link to a contract that returns `Unrated` for everything.*

---

## An open, on-chain carbon credit quality rating framework — now deployable on Base Sepolia

I've been building a transparent, machine-readable quality rating framework for tokenized carbon credits. The motivation: when Toucan's BCT pool mixed credits of vastly different quality into a single fungible token, the pool degraded into a market for lemons (Akerlof 1970, formally modeled for VCM by Manshadi et al. 2025). Commercial rating agencies (Sylvera, BeZero, Calyx Global, MSCI) produce inconsistent off-chain ratings — Carbon Market Watch 2023 documented cases where the same REDD+ project received opposite ratings from two of them. None of the commercial agencies are composable with DeFi.

**v0.4.1 is a public, reproducible alternative.** The rubric, the scoring logic, the Solidity contract, and the pilot data are all in one repo: [Adeline117/carbon-neutrality](https://github.com/Adeline117/carbon-neutrality).

### What's in the box

1. **A 7-dimension rubric** (removal type, additionality, permanence, MRV grade, vintage year, co-benefits as a safeguards-gate, registry/methodology) with machine-readable JSON band definitions.
2. **A linear weighted composite** that produces a 6-tier grade (AAA → B) with 6 disqualifier caps (double counting, failed verification, sanctioned registry, no third party, human rights, community harm).
3. **A Solidity contract** (`CarbonCreditRating`) that stores per-credit attestations with freshness (`expiresAt`), methodology version (`methodologyVersion`), and evidence provenance (`evidenceHash`). Plus a `QualityGatedPool` that refuses deposits below a configured grade. 12 Foundry tests passing.
4. **Two pilot datasets**: a 29-credit illustrative pilot (spectrum-sampled across project types) and a 14-credit tokenized pilot scoring actual on-chain instruments (Toucan BCT/NCT, Moss MCO2, Nori NRT, Puro CDR, Heirloom DAC, Climeworks Orca, Charm Industrial, JPMorgan Kinexys, Open Forest Protocol, ...).
5. **A rank-correlation study** against BeZero/Calyx/Sylvera using the Carbon Market Watch 2023 Table 20 multi-rater overlap (the only public dataset). Under v0.4.1, our mean Spearman agreement with commercial raters is **+0.343** vs the commercial raters' agreement with each other of **+0.009** — i.e., we agree with them more than they agree among themselves on this REDD+ sample.
6. **A deployment on Base Sepolia** (PRELIMINARY AUTHOR ATTESTATIONS — see disclaimer) with a live demo:
   - Rating contract: `<fill in after deploy>`
   - Read API: `https://<user>.github.io/carbon-neutrality/api/v0.4.1/ratings.json`
   - Interactive demo: `https://<user>.github.io/carbon-neutrality/demo/`

### What the pilot shows

- **Oxford hierarchy is restored at the top of the scale.** Climeworks Orca, Heirloom DAC, and Charm Industrial all reach AAA under v0.4.1. Under v0.3 none of them did — co-benefits had a 10% weight that systematically penalized industrial CDR projects that have no SDG narrative. v0.4 dropped co_benefits from the composite entirely and made it a `communityHarm` safeguards-gate instead. See `docs/methodology-gate-v0.4.md` for the four alternative mechanisms we stress-tested before picking the safeguards-gate.
- **Toucan BCT scores 31.1 (BB), only 1.1 points above the B boundary.** BCT's lemons problem is quantifiable, not rhetorical.
- **The tokenized carbon market has no AA middle.** Engineered CDR (Puro/Isometric) occupies the high end, bridge-and-pool instruments cluster at BB/BBB. High-quality nature-based credits have not migrated on-chain.

### What I want from you

- **Try the demo** and tell me what's wrong. The fragility flags I already know: C004 Charm Industrial sits 0.15 points above the AAA boundary; small rescoring flips it. I'd rather you tell me what I missed.
- **Disagree with my scores.** Per-dimension scores are author judgment. If you think Pacific Biochar should be A not AA, or Toucan BCT should be B not BB, open an issue with your reasoning.
- **Tell me which registries would actually attest via EAS** per the design at `docs/decentralized-rater-design.md`. The v0.4.1 deployment uses a single-owner key precisely because I don't have registry buy-in. That is the main unlock.
- **If you're at CarbonPlan, Open Climate Initiative, ICVCM, or a commercial agency**, I'd appreciate 30 minutes of feedback — the full questionnaire is at `docs/v0.5-weight-calibration-questionnaire.md`.

### Known limitations (the parts I'm upfront about)

- The v0.4.1 ratings are **one author's judgment** applied to public documentation. No multi-rater reliability data yet. LLM panel IRR study is v0.5 workstream W1.
- The deployment is **single-owner on testnet**. v0.5 replaces this with EAS + registry allowlist.
- The pilot is **spectrum-sampled**, not VCM-representative. Do not read our 12% AAA share as "12% of the VCM is AAA".
- The rank-correlation sample is **n=6 REDD+ projects**. Other project types are untested against commercial agencies.
- MSCI per-project ratings are paywalled and excluded from the rank-correlation study.
- None of the named projects have been formally reviewed by the framework's author team; the scores are archetype judgments from public documentation.

### Where it is

- GitHub: https://github.com/Adeline117/carbon-neutrality
- Paper: `docs/workshop-paper.md`
- Methodology gate: `docs/methodology-gate-v0.4.md`
- Rank correlation: `data/rank-correlation/analysis.md`
- v0.4.1 changelog: `docs/v0.4.1-changelog.md`

MIT licensed. Issues and PRs welcome.

---

## Posting checklist

Before posting this to any venue, confirm:

- [ ] `script/Deploy.s.sol` has been run on Base Sepolia
- [ ] `script/SeedRatings.s.sol` has been run and MCC-* addresses are in `v0.4.1-deployment-notes.md`
- [ ] `tools/snapshot.py` has run at least once and `docs/api/v0.4.1/ratings.json` exists with 14 entries
- [ ] GitHub Pages is enabled on the repo, `/docs/` folder
- [ ] `docs/demo/index.html` loads successfully and shows real grades
- [ ] The disclaimer paragraph is visible above the fold on all surfaces: README, demo, read API metadata
- [ ] A trusted carbon-market reader has reviewed the announcement text before posting publicly (see `docs/decentralized-rater-design.md` §7.4 risk mitigation)

Target venues, in order of preference:

1. **CarbonPlan Slack or their contact form.** Highest-leverage audience, explicit carbon methodology focus.
2. **Open Climate Initiative forum** (openclimate.initiative).
3. **Ethereum Magicians "research" category**, if the post leads with the EAS design and treats carbon as the case study.
4. **A single tweet** from a known carbon-tech or ReFi account, linking the demo and one headline finding (e.g., "BCT scores 31.1, only 1.1 points above the B boundary").

Do NOT:

- Post to general crypto subreddits — the audience is wrong and the risk of being read as a shill token is high
- Cold-email registries before the technical audience has vetted the framework
- Post to Hacker News without being prepared for the comment thread (it's a high-scrutiny audience and carbon markets attract both serious skeptics and cranks)
