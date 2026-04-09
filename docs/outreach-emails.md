# Expert Outreach Emails — v0.5 Weight Calibration

*Drafted 2026-04-09. Five personalized emails for priority reviewers 1-5.*

---

## Sending Instructions

### Finding contact information

| # | Recipient | Email | Source |
|---|-----------|-------|--------|
| 1 | Lambert Schneider | l.schneider@oeko.de | Oeko-Institut profile |
| 2 | Jeremy Freeman + Danny Cullenward | jeremy@carbonplan.org, danny@carbonplan.org | CarbonPlan team page |
| 3 | Vahideh Manshadi | vahideh.manshadi@yale.edu | Yale SOM profile |
| 4 | Nan Ransohoff | buyers@frontierclimate.com (or via LinkedIn DM) | Frontier website |
| 5 | Spencer Meyer | commercial@bezerocarbon.com (or via LinkedIn) | BeZero leadership page |

### Subject line

Use a consistent subject line across all five emails:

> **Subject: Expert review request — open-source carbon credit quality rating framework (60-90 min)**

### Attachments / links to include

1. **GitHub repo:** https://github.com/Adeline117/carbon-neutrality
2. **Executive summary (in-repo):** `docs/v0.4-executive-summary.md` — link directly: https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.4-executive-summary.md
3. **Questionnaire (in-repo):** `docs/v0.5-weight-calibration-questionnaire.md` — link directly: https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.5-weight-calibration-questionnaire.md

Do not attach PDFs unless the recipient asks. The repo links keep everything versioned and let reviewers see the code, rubrics, and pilot data alongside the documents.

### Timing

Send all five within the same 24-hour window. Follow up after 7 calendar days if no response. A second follow-up at 14 days is acceptable; do not follow up a third time.

---

## Email 1: Lambert Schneider (Oeko-Institut / CCQI / ICVCM Expert Panel)

**To:** l.schneider@oeko.de

**Subject:** Expert review request — open-source carbon credit quality rating framework (60-90 min)

---

Dear Dr. Schneider,

I am writing to request your expert review of an open-source, on-chain carbon credit quality rating framework that we are developing. Your dual role as co-architect of the CCQI scoring methodology and Co-Chair of the ICVCM Expert Panel makes you the single most qualified person to evaluate what we have built — and, more importantly, where it is wrong.

Our framework scores carbon credits across seven dimensions on a 0-100 composite scale, maps them to six letter grades (AAA through B), and enforces quality-gated deposit rules via a Solidity smart contract. The design is deliberately transparent: rubrics, scoring logic, and pilot data are all public. In v0.4 we made a significant structural change: we removed co-benefits from the weighted composite and converted it into a safeguards-gate that caps grades when community harm is detected. This decision rests on Berg et al. (2025), who found that buyers pay a 2x premium for co-benefit narratives regardless of underlying integrity — a dynamic we believe a quality rating should correct rather than reinforce.

Your perspective on this is essential because CCQI uses a different weight structure, and we want to understand where our rebalancing diverges from CCQI's design choices and whether that divergence is defensible. The questionnaire sections most relevant to your expertise are S2 (dimension weights), S3 (the safeguards-gate mechanism), S4 (disqualifier calibration), and S8.2 (whether our framework should merge with or complement CCQI and the ICVCM CCP label).

The full repo is at https://github.com/Adeline117/carbon-neutrality. The two-page executive summary is at [docs/v0.4-executive-summary.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.4-executive-summary.md), and the structured questionnaire is at [docs/v0.5-weight-calibration-questionnaire.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.5-weight-calibration-questionnaire.md). We estimate 60-90 minutes for review and questionnaire completion. We are happy to receive written responses or to schedule a 30-minute call instead — whichever suits you.

I understand your ICVCM role may impose confidentiality constraints. We are approaching you via your Oeko-Institut affiliation, and any feedback you provide would be attributed solely in that capacity unless you indicate otherwise.

Thank you for considering this request.

Best regards,
[Your name]

P.S. All findings and scores in the current version reflect preliminary author attestations only. They have not been endorsed by any external expert, registry, or standards body. Your review would be among the first independent evaluations.

---

## Email 2: CarbonPlan (Jeremy Freeman + Danny Cullenward)

**To:** jeremy@carbonplan.org, danny@carbonplan.org

**Subject:** Expert review request — open-source carbon credit quality rating framework (60-90 min)

---

Dear Jeremy and Danny,

I am writing to ask whether CarbonPlan would be willing to review a structured questionnaire on an open-source carbon credit quality rating framework we are building. CarbonPlan's commitment to transparent, reproducible methodology — from the California forest offsets over-crediting analysis to the CDR verification framework — is the closest precedent in the field to what we are trying to do, and your critical eye is exactly what we need.

The framework scores carbon credits on seven dimensions (removal type, additionality, permanence, MRV grade, vintage, co-benefits, registry/methodology), produces a 0-100 composite mapped to letter grades, and runs identically as a Python scorer and a Solidity smart contract. In our pilot, Toucan's BCT pool scores 31.1 (BB) — 1.1 points above the B boundary — which we believe is a stronger quantitative statement about BCT's quality composition than any existing public analysis. CarbonPlan's own analysis of Toucan crypto-offsets explored the same problem space, and we would value your assessment of whether our scoring gets the right answer for the right reasons.

The questionnaire sections most relevant to your work are S2 (dimension weights, especially how your CDR verification work informs removal_type and MRV weighting), S3 (the safeguards-gate decision), S6 (pilot scoring — you have analyzed many of the same projects), and S7.2 (the off-chain/on-chain invariant constraint — Danny, you may argue that on-chain is the wrong venue entirely, and we want to hear that case). Section S8.3 on failure modes is one where CarbonPlan's experience with methodology critique would be particularly valuable.

Everything is at https://github.com/Adeline117/carbon-neutrality. Start with the two-page executive summary at [docs/v0.4-executive-summary.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.4-executive-summary.md). The questionnaire is at [docs/v0.5-weight-calibration-questionnaire.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.5-weight-calibration-questionnaire.md). Time commitment is 60-90 minutes; we can also do a 30-minute call if that works better. You are welcome to respond individually or as a team.

Thank you for your time.

Best regards,
[Your name]

P.S. All findings and scores in the current version reflect preliminary author attestations only. They have not been endorsed by any external expert, registry, or standards body. PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED.

---

## Email 3: Vahideh Manshadi (Yale School of Management)

**To:** vahideh.manshadi@yale.edu

**Subject:** Expert review request — open-source carbon credit quality rating framework (60-90 min)

---

Dear Professor Manshadi,

Your paper with Monachou and Morgenstern on adverse selection and certification in the voluntary carbon market is foundational to the framework I am writing to ask you about. We cite it directly, and the core design problem we are trying to solve — quality differentiation in fungible on-chain carbon pools — is precisely the market-for-lemons dynamic your model formalizes. I want to make sure we have interpreted your work correctly, and I would value your assessment of whether our proposed solution actually reduces the certification noise your model identifies.

Concretely: our framework scores carbon credits on seven dimensions, produces a 0-100 composite, and enforces quality-gated pool deposits via a smart contract. In v0.4, we moved co-benefits out of the scoring composite and into a harm-based disqualifier gate, because Berg et al. (2025) showed that buyers pay a 2x narrative premium that a quality rating should not reinforce. The empirical result is that Toucan's BCT pool — the canonical adverse-selection example — scores 31.1 (BB), just 1.1 points above the lowest-but-one grade boundary. Your model's prediction about pool degradation under minimal eligibility criteria is exactly what our pilot data confirms.

The questionnaire sections where your expertise is most needed are S2 (dimension weights), S3 (the safeguards-gate mechanism — your model formalizes the certification-noise threshold our scoring addresses), and S8 (whether this framework actually mitigates the adverse selection your paper identifies, or merely rearranges it).

The repo is at https://github.com/Adeline117/carbon-neutrality. The executive summary (2 pages) is at [docs/v0.4-executive-summary.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.4-executive-summary.md), and the questionnaire is at [docs/v0.5-weight-calibration-questionnaire.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.5-weight-calibration-questionnaire.md). We estimate 60-90 minutes for review and questionnaire completion. Written responses or a 30-minute call both work.

Thank you for considering this.

Best regards,
[Your name]

P.S. All findings and scores in the current version reflect preliminary author attestations only. They have not been endorsed by any external expert, registry, or standards body. PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED.

---

## Email 4: Nan Ransohoff (Frontier / Stripe Climate)

**To:** buyers@frontierclimate.com (or via LinkedIn DM to Nan Ransohoff)

**Subject:** Expert review request — open-source carbon credit quality rating framework (60-90 min)

---

Dear Nan,

Frontier has done more than any other institution to define what "high-quality carbon removal" means in practice — through purchasing criteria, due diligence on hundreds of suppliers, and the signal that a $1B+ advance market commitment sends to the field. I am writing because we are building an open-source quality rating framework for carbon credits, and the buyer perspective that Frontier represents is one we cannot calibrate without.

The framework scores credits across seven dimensions (removal type, additionality, permanence, MRV grade, vintage, co-benefits, registry/methodology) and maps the composite to letter grades. In our pilot, Climeworks Orca, Heirloom DAC, and Charm Industrial bio-oil all reach AAA — the top grade — while Toucan's BCT pool lands at BB (31.1/100). Frontier has purchased from Charm Industrial and Climeworks, among others in our pilot set, so you are positioned to tell us whether our scoring aligns with how Frontier actually evaluates these suppliers on permanence, MRV rigor, and cost trajectory.

The questions we most want your input on are S2 (how would you weight our seven dimensions, given Frontier's evaluation criteria?), S5 (what quality threshold would Frontier require for pool eligibility — is our AAA/AA/A boundary structure useful?), S6 (are there credits in our pilot where the per-dimension scores are clearly wrong?), and S8.1 (would Frontier or Stripe Climate ever integrate an on-chain quality rating into procurement workflows?).

Everything is public at https://github.com/Adeline117/carbon-neutrality. The two-page executive summary is at [docs/v0.4-executive-summary.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.4-executive-summary.md), and the structured questionnaire is at [docs/v0.5-weight-calibration-questionnaire.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.5-weight-calibration-questionnaire.md). We estimate 60-90 minutes for the full questionnaire, but even a partial response focusing on the sections above would be very helpful. We can also schedule a 30-minute call if that is more practical.

Thank you for your time.

Best regards,
[Your name]

P.S. All findings and scores in the current version reflect preliminary author attestations only. They have not been endorsed by any external expert, registry, or standards body. PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED.

---

## Email 5: Spencer Meyer (BeZero Carbon, Chief Ratings Officer)

**To:** commercial@bezerocarbon.com (attention: Dr. Spencer Meyer)

**Subject:** Academic peer review request — open-source carbon credit quality methodology (60-90 min)

---

Dear Dr. Meyer,

I am reaching out to request your review of an open-source carbon credit quality rating methodology, in your capacity as Chief Ratings Officer at BeZero. BeZero publishes more openly than any other commercial rater — the BCMA Framework and your September 2024 safeguards paper ("First Do No Harm") are two of the few public-facing methodological documents in the field — and that openness is why your feedback would be particularly valuable.

Our framework is not a commercial product. It is an open-source, on-chain scoring system designed for a different market segment: DeFi protocols that need machine-readable quality gates for tokenized carbon credit pools. We score credits across seven dimensions on a 0-100 composite, and in v0.4 we converted co-benefits from a scored dimension into a safeguards-gate disqualifier — a decision directly relevant to your safeguards work. Our `communityHarm` flag, which caps grades at BBB when negative community impacts are detected, was designed with the same "first do no harm" principle your paper articulates, and we want to know whether we have implemented it correctly.

The questionnaire sections most relevant to your expertise are S2 (dimension weights — BeZero uses a different dimensional structure, and a direct comparison would be informative), S3 (the safeguards-gate mechanism), S6 (pilot scoring — you rate many of the same projects; we are specifically interested in cases where your ratings and ours disagree), and S8.2 (whether our framework complements or conflicts with BeZero's work).

The repo is at https://github.com/Adeline117/carbon-neutrality. The executive summary is at [docs/v0.4-executive-summary.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.4-executive-summary.md), and the questionnaire is at [docs/v0.5-weight-calibration-questionnaire.md](https://github.com/Adeline117/carbon-neutrality/blob/main/docs/v0.5-weight-calibration-questionnaire.md). We estimate 60-90 minutes for the full questionnaire. Written responses or a 30-minute call both work.

Thank you for considering this.

Best regards,
[Your name]

P.S. All findings and scores in the current version reflect preliminary author attestations only. They have not been endorsed by any external expert, registry, or standards body. PRELIMINARY AUTHOR ATTESTATIONS — NOT ENDORSED.
