# Revision Templates for Nature Communications Submission

*Pre-written paragraph templates for integrating incoming empirical data.
Fill in the bracketed blanks when data arrives, then slot into the existing
Results structure in sections-1-2-intro-results.md.*

---

## Template A: Expert Weight Validation

**Target location:** Section 2, after the "Rating stability under weight perturbation" subsection (currently the last Results subsection). Insert as a new subsection titled "Expert weight validation confirms framework calibration" or similar.

---

### Expert weight validation confirms framework calibration

To test whether the framework's dimension weights reflect practitioner consensus, we conducted a Best-Worst Scaling (BWS) study with [N] experts spanning [ROLE_CATEGORIES, e.g., "registry staff, commercial raters, project developers, academics, and civil society representatives"] (mean experience: [MEAN_YEARS] years in voluntary carbon markets). Each expert completed 15 choice sets from a balanced incomplete block design (BIBD(6, 15, 10, 4, 6)), selecting the most and least important dimension in each set. BWS produces ratio-scale importance scores free from anchoring bias, addressing the methodological concern that direct weight elicitation tends to anchor on presented values.

The BWS-derived weight vector [was/was not] significantly different from the framework's current weights (chi-squared = [CHI2], df = 5, p = [P_VALUE]). The Spearman rank correlation between BWS-derived and current weight orderings was [RHO] ([INTERPRETATION: e.g., "indicating that experts endorse the same dimension hierarchy: removal type and additionality at the top, vintage year and registry methodology at the bottom"]). The maximum absolute deviation between any BWS-derived weight and its current value was [MAX_DELTA] (dimension: [DIM_NAME]), [within/exceeding] the 0.05 threshold we pre-registered as the criterion for weight revision.

[IF WEIGHTS ADOPTED:] We adopted the BWS-derived weights for the final framework version, producing [N_FLIPS] grade changes across the 29-credit pilot dataset ([LIST_FLIPS, e.g., "Plan Vivo agroforestry moved from A to BBB; Gold Standard cookstoves moved from BBB to BB"]). The rank correlation with BeZero ratings [increased/decreased/remained unchanged] from rho = +0.901 to rho = [NEW_RHO] (n = 27).

[IF WEIGHTS RETAINED:] Because the chi-squared test was non-significant and the rank ordering matched, we retained the current weights per our pre-registered decision rule. The expert consensus is consistent with the framework's existing calibration.

Bootstrap 95% confidence intervals (10,000 resamples) for each BWS-derived weight are reported in Extended Data Table [X]. [IF APPLICABLE: Fleiss' kappa across the [N] experts' BWS responses was [EXPERT_KAPPA], indicating [INTERPRETATION] agreement on dimension importance.]

---

## Template B: Multi-Provider IRR

**Target location:** Section 2, within the "Quality ratings are reproducible across independent raters" subsection, after the current Anthropic-only panel paragraph. Insert as a continuation paragraph.

---

We extended the inter-rater reliability analysis to a multi-provider panel of [N_PROVIDERS] LLM families ([PROVIDER_LIST, e.g., "Claude (Anthropic), GPT-5 (OpenAI), Gemini 2.5 Pro (Google), and Llama 4 Maverick (Meta)"]) with [N_TOTAL_RATERS] total raters, each scoring [N_CREDITS] credits independently using the same rubric and redacted evidence packs. This extension tests whether the Anthropic-only panel's agreement (Fleiss' kappa = 0.600) reflects genuine rubric clarity or provider-shared biases from common training data.

Grade-level Fleiss' kappa across all [N_TOTAL_RATERS] raters was [MULTI_KAPPA] ([INTERPRETATION, e.g., "moderate/substantial agreement"]), [higher than/lower than/comparable to] the Anthropic-only baseline of 0.600. Composite ICC(2,k) was [MULTI_ICC]. The [increase/decrease] of [DELTA_KAPPA] in kappa [supports/challenges] the hypothesis that within-family agreement inflates the Anthropic-only estimate.

Cross-provider pairwise agreement (using each provider's median grade as a single rater) ranged from kappa = [MIN_CROSS_KAPPA] ([PAIR_MIN]) to kappa = [MAX_CROSS_KAPPA] ([PAIR_MAX]). [ALL/N_OF_M] provider pairs achieved 100% agreement within plus-or-minus one grade band, confirming that the rubric produces consistent ordinal rankings across model families.

Per-dimension analysis identified [N_FLAGGED] dimensions where cross-provider mean absolute disagreement exceeded 10 points on the 0--100 scale: [FLAGGED_DIMS, e.g., "registry_methodology (mean |Delta| = 14.2) and co_benefits (mean |Delta| = 12.8)"]. [REMAINING_DIMS, e.g., "Permanence (mean |Delta| = 4.8) and removal type (mean |Delta| = 5.1)"] showed the strongest cross-provider consensus, consistent with the Anthropic-only findings. These results provide [partial/full] resolution of Limitation 1 (Anthropic-only panel) identified in the original submission.

---

## Template C: Depositor-Level Analysis

**Target location:** Section 2, within the "Quality degradation varies dramatically across carbon credit pools" subsection, after the current pool-level Lemons Index analysis. Insert as a new paragraph or sub-subsection.

---

### Depositor-level quality sorting within pools

The pool-level Lemons Index measures aggregate quality degradation but cannot distinguish whether low-quality pool composition reflects adverse selection (strategic depositor behaviour) or simply quality-blind pooling rules that attract low-quality supply. To disentangle these mechanisms, we analysed depositor-level behaviour for [N_DEPOSITORS] unique depositor addresses in [POOL_NAME, e.g., "Toucan BCT"], covering [N_DEPOSITS] deposit transactions from [DATE_RANGE].

Depositors who held credits both inside and outside the pool ("dual holders," n = [N_DUAL]) deposited credits with a mean composite score [DEPOSIT_MEAN] points [lower/higher] than their retained credits (mean retained composite = [RETAINED_MEAN], mean deposited composite = [DEPOSITED_MEAN]; paired t-test: t = [T_VALUE], p = [P_VALUE]; Cohen's d = [D_VALUE]). This [DEPOSIT_MEAN]-point gap is [consistent with/inconsistent with] the adverse selection prediction: depositors who can choose which credits to deposit systematically [deposit their lowest-quality credits / show no quality-based sorting].

[IF SIGNIFICANT:] The quality gap was most pronounced for depositors holding credits spanning multiple project types (n = [N_MULTI_TYPE], gap = [GAP_MULTI] points, p = [P_MULTI]), and smallest for depositors holding credits from a single project (n = [N_SINGLE], gap = [GAP_SINGLE] points, p = [P_SINGLE]). This pattern is consistent with informed selection: depositors with more heterogeneous portfolios have more room to sort by quality.

[IF NOT SIGNIFICANT:] The absence of a significant quality gap suggests that BCT's low-quality composition may be primarily attributable to the pool's quality-blind admission rules --- which attracted low-quality supply in aggregate --- rather than strategic within-depositor sorting. This is consistent with a "pooling equilibrium" interpretation: all depositors deposit all eligible credits without quality-based selection, but the eligible set is itself dominated by low-quality credits because high-quality credits have more attractive alternative channels (direct retirement, premium pools, forward contracts).

[EITHER WAY:] Across all depositors, the [top/bottom] quintile by deposit volume accounted for [SHARE]% of total deposited credits and exhibited a Lemons Index of [QUINTILE_LI], compared with [OTHER_QUINTILE_LI] for the remaining depositors. [INTERPRETATION, e.g., "Large depositors showed marginally worse quality profiles, consistent with institutional actors optimising portfolio quality by offloading low-quality credits into the fungible pool."]

---

## Usage Notes

1. **Brackets** (`[LIKE_THIS]`) are placeholders. Fill with actual values when data arrives.

2. **Conditional blocks** (`[IF SIGNIFICANT:]`, `[IF WEIGHTS ADOPTED:]`) are alternative paragraphs. Keep the one that matches the data; delete the other.

3. **Extended Data references** (`Extended Data Table [X]`) should be assigned the next available number in the existing sequence.

4. **Integration with existing text:**
   - Template A goes after the current last Results subsection ("Rating stability under weight perturbation").
   - Template B is inserted within the existing "Quality ratings are reproducible" subsection, extending the current Anthropic-only paragraph.
   - Template C is inserted within the existing "Quality degradation varies dramatically" subsection.

5. **Citation style:** Follow the existing superscript number convention (e.g., ^1^). Add new references to the bibliography in sections-5-figures-refs.md.

6. **Corresponding scripts:**
   - Template A data: `data/expert-panel/process_bws.py` -> `data/expert-panel/bws_results.md`
   - Template B data: `data/llm-panel-irr/process_multi_provider.py` -> `data/llm-panel-irr/multi_provider_results.md`
   - Template C data: Requires on-chain depositor analysis (not yet scripted; see project_state.md).
