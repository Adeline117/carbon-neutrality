# Bootstrap Rank Correlation Analysis

Seed: 42 | Bootstrap resamples: 10,000 | Permutations: 10,000

## REDD+ only (n=6)

| Pair | n | Spearman rho | 95% CI | Boot SE | Perm p | Sig? |
|------|---|------------:|--------|--------:|-------:|------|
| bezero vs calyx_nzm | 6 | -0.6642 | [-0.9798, -0.6642] | +0.1030 | +0.3258 | no |
| bezero vs sylvera_nzm | 6 | +0.1252 | [-0.8944, +1.0000] | +0.5618 | +0.8131 | no |
| calyx_nzm vs sylvera_nzm | 6 | +0.5657 | [+0.3162, +1.0000] | +0.1898 | +0.4973 | no |
| ours vs bezero | 6 | +0.6642 | [+0.6642, +1.0000] | +0.1047 | +0.3323 | no |
| ours vs calyx_nzm | 6 | -0.2000 | [-0.7071, -0.2000] | +0.1275 | +1.0000 | no |
| ours vs sylvera_nzm | 6 | +0.5657 | [+0.3162, +1.0000] | +0.1898 | +0.5026 | no |
## Full dataset (REDD+ + cross-type)

| Pair | n | Spearman rho | 95% CI | Boot SE | Perm p | Sig? |
|------|---|------------:|--------|--------:|-------:|------|
| bezero vs calyx | 6 | -0.6642 | [-1.0000, -0.6642] | +0.1050 | +0.3241 | no |
| bezero vs sylvera | 7 | +0.4720 | [-0.6417, +1.0000] | +0.4449 | +0.2918 | no |
| calyx vs sylvera | 6 | +0.5657 | [+0.3162, +1.0000] | +0.1875 | +0.4987 | no |
| ours vs bezero | 15 | +0.9134 | [+0.7803, +0.9696] | +0.0489 | +0.0000 | yes |
| ours vs calyx | 8 | +0.5809 | [-0.2182, +1.0000] | +0.3254 | +0.2891 | no |
| ours vs sylvera | 7 | +0.7702 | [+0.4320, +1.0000] | +0.1571 | +0.0470 | yes |

## Summary

**REDD+ only (n=6)**: mean ours-vs-agency rho = +0.343
  mean inter-agency rho = +0.009

**Full dataset (REDD+ + cross-type)**: mean ours-vs-agency rho = +0.755
  mean inter-agency rho = +0.124

## Notes

- Bootstrap CI uses the percentile method (10,000 resamples).
- Permutation p-value is two-sided: P(|rho_perm| >= |rho_obs|).
- With n=6 (REDD+ only), wide CIs and non-significant p-values are expected.
- The full dataset adds cross-type projects, increasing statistical power.
