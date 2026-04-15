# Multi-Provider LLM Panel IRR Results

*3 providers, 3 total raters, 5 credits.*

## 1. Per-Provider IRR Statistics

| Provider | Model | N raters | Fleiss' kappa | ICC(2,k) |
|----------|-------|--------:|-------------:|--------:|
| openai | gpt-5 | 1 | N/A (1 rater) | N/A (1 rater) |
| google | gemini-2.5-pro | 1 | N/A (1 rater) | N/A (1 rater) |
| meta | llama-4-maverick | 1 | N/A (1 rater) | N/A (1 rater) |

## 2. Cross-Provider Pairwise Agreement (Median Grade)

| Provider 1 | Provider 2 | Cohen's kappa | Exact agreement | Within +/-1 band |
|------------|------------|-------------:|----------------:|----------------:|
| google | meta | +0.500 | 60% | 100% |
| google | openai | +0.737 | 80% | 100% |
| meta | openai | +0.737 | 80% | 100% |

**Mean cross-provider kappa:** +0.658
**Mean cross-provider exact agreement:** 73%

## 3. Overall Multi-Provider Statistics (All Raters Pooled)

| Metric | Anthropic-only (baseline) | Multi-provider (all pooled) | Delta |
|--------|-------------------------:|---------------------------:|------:|
| Grade-level Fleiss' kappa | +0.600 | +0.647 | +0.047 |
| Composite ICC(2,k) | +0.993 | +1.000 | +0.007 |

**Finding:** Multi-provider kappa is HIGHER than Anthropic-only baseline, suggesting the rubric produces consistent results even across model families.

## 4. Per-Dimension Cross-Provider Disagreement

| Dimension | Mean |Delta| | Worst credit | Worst |Delta| | Flagged? |
|-----------|---------------:|-------------|----------------:|----------|
| removal_type | 2.7 | C010 | 5.3 |  |
| additionality | 3.6 | C010 | 6.7 |  |
| permanence | 2.1 | C022 | 4.7 |  |
| mrv_grade | 3.6 | C022 | 5.3 |  |
| vintage_year | 0.0 | C001 | 0.0 |  |
| co_benefits | 4.1 | C010 | 5.3 |  |
| registry_methodology | 5.2 | C001 | 8.0 |  |

**No dimensions exceeded the |Delta| > 10 disagreement threshold.**

## 5. Provider Bias Detection

Mean composite score by provider (systematic bias check):

| Provider | Mean composite | Std composite | vs Grand mean |
|----------|---------------:|--------------:|-------------:|
| google | 68.3 | 33.4 | +1.0 |
| meta | 65.8 | 32.7 | -1.5 |
| openai | 67.8 | 33.3 | +0.5 |

## 6. Interpretation and Paper Integration Notes

### For the Nature Communications revision:

1. **Section 2 (Results), 'Quality ratings are reproducible'**: Update the Fleiss' kappa paragraph to report multi-provider kappa (+0.647) alongside the Anthropic-only baseline (+0.600).

2. **Table 1 (Per-dimension reliability)**: Add a column for multi-provider mean |Delta| per dimension.

3. **Discussion**: If multi-provider kappa < Anthropic kappa, this validates Limitation 1 (Anthropic-only panel). If multi-provider kappa >= Anthropic kappa, Limitation 1 is partially resolved.
