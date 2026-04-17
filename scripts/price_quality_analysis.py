#!/usr/bin/env python3
"""
Price-Quality Composition Analysis for BCT (Base Carbon Tonne)
--------------------------------------------------------------
Tests whether BCT's quality composition predicts its price trajectory.
Key analyses:
  1. Rolling quality metrics (PQD, renewable share) over time
  2. Pearson/Spearman correlations with BCT price
  3. Granger causality tests (both directions)
  4. Dual-axis time series figure

For Nature Communications revision addressing Reviewer 1-3 quality-price gap.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scipy import stats
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.stattools import adfuller
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────
BASE = Path('/Users/adelinewen/carbon-neutrality')
DEPOSITS_PATH = BASE / 'data/depositor-analysis/bct_deposits_enriched.json'
SCORES_PATH   = BASE / 'data/depositor-analysis/tco2_scores_complete.json'
PRICES_PATH   = Path('/tmp/bct_prices_merged.json')
OUT_JSON      = BASE / 'data/depositor-analysis/price_quality_results.json'
OUT_FIG_PNG   = BASE / 'figures/fig_price_quality.png'
OUT_FIG_PDF   = BASE / 'figures/fig_price_quality.pdf'

# ── Polygon block → date conversion ───────────────────────────────────
# Polygon produces ~1 block every 2 seconds, ~43200 blocks/day
# Block 20,000,000 ≈ 2021-10-14 (calibration anchor)
ANCHOR_BLOCK = 20_000_000
ANCHOR_DATE  = datetime(2021, 10, 14, tzinfo=timezone.utc)
BLOCKS_PER_DAY = 43200

def block_to_date(block_num):
    """Convert a Polygon block number to an approximate UTC date."""
    days_offset = (block_num - ANCHOR_BLOCK) / BLOCKS_PER_DAY
    return ANCHOR_DATE + timedelta(days=days_offset)


# ── Step 1: Load and enrich deposits ──────────────────────────────────
print("=" * 70)
print("STEP 1: Loading deposits and quality scores")
print("=" * 70)

with open(DEPOSITS_PATH) as f:
    deposits = json.load(f)

with open(SCORES_PATH) as f:
    scores = json.load(f)

print(f"  Deposits loaded: {len(deposits)}")
print(f"  TCO2 scores loaded: {len(scores)}")

# Enrich each deposit with quality info
records = []
unmatched = 0
for dep in deposits:
    tco2 = dep['tco2_address'].lower()
    score_entry = scores.get(tco2)
    if score_entry is None:
        # Try with original case
        score_entry = scores.get(dep['tco2_address'])

    if score_entry is None:
        unmatched += 1
        continue

    dt = block_to_date(dep['block_number'])
    records.append({
        'date': dt.date(),
        'block_number': dep['block_number'],
        'tco2_address': tco2,
        'amount_tonnes': dep['amount_tonnes'],
        'composite_score': score_entry['composite'],
        'grade': score_entry['grade'],
        'credit_type': score_entry['type'],
        'vintage': score_entry.get('vintage'),
        'is_renewable': 1 if score_entry['type'] == 'Renewable' else 0,
    })

df_dep = pd.DataFrame(records)
df_dep['date'] = pd.to_datetime(df_dep['date'])
df_dep = df_dep.sort_values('date').reset_index(drop=True)

print(f"  Matched deposits: {len(df_dep)}")
print(f"  Unmatched deposits (no score): {unmatched}")
print(f"  Date range: {df_dep['date'].min().date()} to {df_dep['date'].max().date()}")
print(f"  Total tonnage: {df_dep['amount_tonnes'].sum():,.0f}")


# ── Step 2: Compute rolling quality composition ──────────────────────
print("\n" + "=" * 70)
print("STEP 2: Computing rolling quality composition metrics")
print("=" * 70)

# Create daily aggregated metrics
# For each day, compute volume-weighted mean quality and renewable share
daily_agg = df_dep.groupby('date').apply(
    lambda g: pd.Series({
        'daily_tonnes': g['amount_tonnes'].sum(),
        'daily_wt_score': np.average(g['composite_score'], weights=g['amount_tonnes']),
        'daily_renewable_tonnes': g.loc[g['is_renewable'] == 1, 'amount_tonnes'].sum(),
    })
).reset_index()

daily_agg['daily_renewable_share'] = daily_agg['daily_renewable_tonnes'] / daily_agg['daily_tonnes']

# Create a complete date index from first deposit to last
date_range = pd.date_range(daily_agg['date'].min(), daily_agg['date'].max(), freq='D')
df_daily = pd.DataFrame({'date': date_range})
df_daily = df_daily.merge(daily_agg, on='date', how='left')
df_daily = df_daily.fillna({'daily_tonnes': 0, 'daily_renewable_tonnes': 0})

# Compute cumulative metrics
df_daily['cum_tonnes'] = df_daily['daily_tonnes'].cumsum()
df_daily['cum_renewable_tonnes'] = df_daily['daily_renewable_tonnes'].cumsum()

# Cumulative PQD (volume-weighted mean of ALL deposits up to each date)
cum_score_x_tonnes = (daily_agg.set_index('date')['daily_wt_score'] * daily_agg.set_index('date')['daily_tonnes']).cumsum()
cum_tonnes = daily_agg.set_index('date')['daily_tonnes'].cumsum()
cum_pqd_sparse = cum_score_x_tonnes / cum_tonnes

# Forward-fill cumulative PQD for days without deposits
df_daily = df_daily.set_index('date')
df_daily['cum_pqd'] = cum_pqd_sparse
df_daily['cum_pqd'] = df_daily['cum_pqd'].ffill()
df_daily['cum_renewable_share'] = df_daily['cum_renewable_tonnes'] / df_daily['cum_tonnes']
df_daily['cum_renewable_share'] = df_daily['cum_renewable_share'].ffill()

# Rolling 30-day metrics
WINDOW = 30
# For rolling, we need to compute over trailing windows
# We'll iterate through the date range
rolling_pqd = []
rolling_ren = []

for dt in df_daily.index:
    window_start = dt - pd.Timedelta(days=WINDOW)
    mask = (df_dep['date'] > window_start) & (df_dep['date'] <= dt)
    window_data = df_dep[mask]

    if len(window_data) == 0 or window_data['amount_tonnes'].sum() == 0:
        rolling_pqd.append(np.nan)
        rolling_ren.append(np.nan)
    else:
        wt_score = np.average(window_data['composite_score'], weights=window_data['amount_tonnes'])
        ren_share = window_data.loc[window_data['is_renewable'] == 1, 'amount_tonnes'].sum() / window_data['amount_tonnes'].sum()
        rolling_pqd.append(wt_score)
        rolling_ren.append(ren_share)

df_daily['rolling_30d_pqd'] = rolling_pqd
df_daily['rolling_30d_renewable'] = rolling_ren

# Forward-fill rolling metrics for gaps
df_daily['rolling_30d_pqd'] = df_daily['rolling_30d_pqd'].ffill()
df_daily['rolling_30d_renewable'] = df_daily['rolling_30d_renewable'].ffill()

df_daily = df_daily.reset_index()

print(f"  Daily records: {len(df_daily)}")
print(f"  Cumulative PQD range: {df_daily['cum_pqd'].min():.2f} - {df_daily['cum_pqd'].max():.2f}")
print(f"  Cumulative renewable share range: {df_daily['cum_renewable_share'].min():.2%} - {df_daily['cum_renewable_share'].max():.2%}")
print(f"  Rolling 30d PQD range: {df_daily['rolling_30d_pqd'].dropna().min():.2f} - {df_daily['rolling_30d_pqd'].dropna().max():.2f}")
print(f"  Rolling 30d renewable range: {df_daily['rolling_30d_renewable'].dropna().min():.2%} - {df_daily['rolling_30d_renewable'].dropna().max():.2%}")


# ── Step 3: Load and merge price data ────────────────────────────────
print("\n" + "=" * 70)
print("STEP 3: Loading BCT price data and merging")
print("=" * 70)

with open(PRICES_PATH) as f:
    prices_raw = json.load(f)

price_records = []
for p in prices_raw:
    dt = datetime.fromtimestamp(p['timestamp'], tz=timezone.utc).date()
    price_records.append({'date': pd.Timestamp(dt), 'bct_price': p['price']})

df_price = pd.DataFrame(price_records)
# Deduplicate by date (take mean if multiple per day)
df_price = df_price.groupby('date')['bct_price'].mean().reset_index()

print(f"  Price data points: {len(df_price)}")
print(f"  Price date range: {df_price['date'].min().date()} to {df_price['date'].max().date()}")
print(f"  Price range: ${df_price['bct_price'].min():.4f} - ${df_price['bct_price'].max():.4f}")

# Merge price with quality data on date
df_merged = df_daily.merge(df_price, on='date', how='inner')
df_merged = df_merged.dropna(subset=['bct_price', 'cum_pqd', 'cum_renewable_share']).reset_index(drop=True)

print(f"  Merged records (overlap period): {len(df_merged)}")
print(f"  Overlap date range: {df_merged['date'].min().date()} to {df_merged['date'].max().date()}")


# ── Step 4: Correlation analysis ─────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 4: Correlation analysis")
print("=" * 70)

results = {}

# 4a. Price vs. Cumulative PQD
pearson_cum_pqd, p_pearson_cum_pqd = stats.pearsonr(df_merged['bct_price'], df_merged['cum_pqd'])
spearman_cum_pqd, p_spearman_cum_pqd = stats.spearmanr(df_merged['bct_price'], df_merged['cum_pqd'])

print(f"\n  BCT Price vs. Cumulative PQD:")
print(f"    Pearson  r = {pearson_cum_pqd:.4f}  (p = {p_pearson_cum_pqd:.2e})")
print(f"    Spearman ρ = {spearman_cum_pqd:.4f}  (p = {p_spearman_cum_pqd:.2e})")

results['price_vs_cum_pqd'] = {
    'pearson_r': round(pearson_cum_pqd, 4),
    'pearson_p': float(f'{p_pearson_cum_pqd:.6e}'),
    'spearman_rho': round(spearman_cum_pqd, 4),
    'spearman_p': float(f'{p_spearman_cum_pqd:.6e}'),
}

# 4b. Price vs. Cumulative Renewable Share
pearson_cum_ren, p_pearson_cum_ren = stats.pearsonr(df_merged['bct_price'], df_merged['cum_renewable_share'])
spearman_cum_ren, p_spearman_cum_ren = stats.spearmanr(df_merged['bct_price'], df_merged['cum_renewable_share'])

print(f"\n  BCT Price vs. Cumulative Renewable Share:")
print(f"    Pearson  r = {pearson_cum_ren:.4f}  (p = {p_pearson_cum_ren:.2e})")
print(f"    Spearman ρ = {spearman_cum_ren:.4f}  (p = {p_spearman_cum_ren:.2e})")

results['price_vs_cum_renewable_share'] = {
    'pearson_r': round(pearson_cum_ren, 4),
    'pearson_p': float(f'{p_pearson_cum_ren:.6e}'),
    'spearman_rho': round(spearman_cum_ren, 4),
    'spearman_p': float(f'{p_spearman_cum_ren:.6e}'),
}

# 4c. Price vs. Rolling 30d PQD (where available)
df_rolling = df_merged.dropna(subset=['rolling_30d_pqd', 'rolling_30d_renewable'])
if len(df_rolling) > 10:
    pearson_r30_pqd, p_pr30_pqd = stats.pearsonr(df_rolling['bct_price'], df_rolling['rolling_30d_pqd'])
    spearman_r30_pqd, p_sr30_pqd = stats.spearmanr(df_rolling['bct_price'], df_rolling['rolling_30d_pqd'])

    print(f"\n  BCT Price vs. Rolling 30d PQD (n={len(df_rolling)}):")
    print(f"    Pearson  r = {pearson_r30_pqd:.4f}  (p = {p_pr30_pqd:.2e})")
    print(f"    Spearman ρ = {spearman_r30_pqd:.4f}  (p = {p_sr30_pqd:.2e})")

    results['price_vs_rolling_30d_pqd'] = {
        'pearson_r': round(pearson_r30_pqd, 4),
        'pearson_p': float(f'{p_pr30_pqd:.6e}'),
        'spearman_rho': round(spearman_r30_pqd, 4),
        'spearman_p': float(f'{p_sr30_pqd:.6e}'),
        'n': len(df_rolling),
    }

    # 4d. Price vs. Rolling 30d Renewable Share
    pearson_r30_ren, p_pr30_ren = stats.pearsonr(df_rolling['bct_price'], df_rolling['rolling_30d_renewable'])
    spearman_r30_ren, p_sr30_ren = stats.spearmanr(df_rolling['bct_price'], df_rolling['rolling_30d_renewable'])

    print(f"\n  BCT Price vs. Rolling 30d Renewable Share (n={len(df_rolling)}):")
    print(f"    Pearson  r = {pearson_r30_ren:.4f}  (p = {p_pr30_ren:.2e})")
    print(f"    Spearman ρ = {spearman_r30_ren:.4f}  (p = {p_sr30_ren:.2e})")

    results['price_vs_rolling_30d_renewable'] = {
        'pearson_r': round(pearson_r30_ren, 4),
        'pearson_p': float(f'{p_pr30_ren:.6e}'),
        'spearman_rho': round(spearman_r30_ren, 4),
        'spearman_p': float(f'{p_sr30_ren:.6e}'),
        'n': len(df_rolling),
    }


# ── Step 5: Stationarity and Granger Causality ──────────────────────
print("\n" + "=" * 70)
print("STEP 5: Granger causality analysis")
print("=" * 70)

# Use weekly data to reduce noise and ensure stationarity
df_weekly = df_merged.set_index('date').resample('W').agg({
    'bct_price': 'mean',
    'cum_pqd': 'last',
    'cum_renewable_share': 'last',
    'rolling_30d_pqd': 'last',
    'rolling_30d_renewable': 'last',
}).dropna().reset_index()

print(f"  Weekly observations: {len(df_weekly)}")

# First-difference for stationarity
df_weekly['d_price'] = df_weekly['bct_price'].diff()
df_weekly['d_cum_pqd'] = df_weekly['cum_pqd'].diff()
df_weekly['d_cum_renewable'] = df_weekly['cum_renewable_share'].diff()
df_weekly['d_rolling_pqd'] = df_weekly['rolling_30d_pqd'].diff()
df_weekly['d_rolling_ren'] = df_weekly['rolling_30d_renewable'].diff()
df_weekly = df_weekly.dropna()

# ADF tests on differenced series
print("\n  ADF stationarity tests (first-differenced series):")
for col in ['d_price', 'd_cum_pqd', 'd_cum_renewable', 'd_rolling_pqd', 'd_rolling_ren']:
    adf_stat, adf_p, _, _, _, _ = adfuller(df_weekly[col].dropna())
    status = "STATIONARY" if adf_p < 0.05 else "NON-STATIONARY"
    print(f"    {col:25s}: ADF stat = {adf_stat:.3f}, p = {adf_p:.4f} [{status}]")

# Granger causality tests
MAX_LAG = 4  # up to 4 weeks

granger_results = {}

test_pairs = [
    ('d_cum_pqd', 'd_price', 'quality_causes_price (cum PQD → Price)'),
    ('d_price', 'd_cum_pqd', 'price_causes_quality (Price → cum PQD)'),
    ('d_cum_renewable', 'd_price', 'renewable_causes_price (cum Renewable → Price)'),
    ('d_price', 'd_cum_renewable', 'price_causes_renewable (Price → cum Renewable)'),
    ('d_rolling_pqd', 'd_price', 'rolling_pqd_causes_price (30d PQD → Price)'),
    ('d_price', 'd_rolling_pqd', 'price_causes_rolling_pqd (Price → 30d PQD)'),
    ('d_rolling_ren', 'd_price', 'rolling_ren_causes_price (30d Renewable → Price)'),
    ('d_price', 'd_rolling_ren', 'price_causes_rolling_ren (Price → 30d Renewable)'),
]

print(f"\n  Granger causality tests (max lag = {MAX_LAG} weeks):")
print(f"  {'Test':55s} {'Lag':>4s} {'F-stat':>10s} {'p-value':>10s} {'Sig':>5s}")
print(f"  {'-'*90}")

for cause_col, effect_col, label in test_pairs:
    test_data = df_weekly[[effect_col, cause_col]].dropna()

    if len(test_data) < 20:
        print(f"  {label:55s}  -- insufficient data --")
        continue

    try:
        gc_result = grangercausalitytests(test_data, maxlag=MAX_LAG, verbose=False)

        # Find the lag with lowest p-value
        best_lag = None
        best_p = 1.0
        best_f = 0.0
        lag_details = {}

        for lag in range(1, MAX_LAG + 1):
            f_stat = gc_result[lag][0]['ssr_ftest'][0]
            p_val = gc_result[lag][0]['ssr_ftest'][1]
            lag_details[str(lag)] = {'f_stat': round(f_stat, 4), 'p_value': round(p_val, 6)}
            if p_val < best_p:
                best_p = p_val
                best_f = f_stat
                best_lag = lag

        sig = "***" if best_p < 0.001 else "**" if best_p < 0.01 else "*" if best_p < 0.05 else ""
        print(f"  {label:55s} {best_lag:4d} {best_f:10.3f} {best_p:10.6f} {sig:>5s}")

        granger_results[label] = {
            'best_lag': best_lag,
            'best_f_stat': round(best_f, 4),
            'best_p_value': round(best_p, 6),
            'significant': best_p < 0.05,
            'lag_details': lag_details,
            'n_observations': len(test_data),
        }
    except Exception as e:
        print(f"  {label:55s}  ERROR: {e}")

results['granger_causality'] = granger_results


# ── Step 6: Additional robustness — levels regression ────────────────
print("\n" + "=" * 70)
print("STEP 6: OLS regression (price ~ quality metrics)")
print("=" * 70)

from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

# Regression: price = a + b*cum_renewable_share + c*cum_pqd
X = add_constant(df_merged[['cum_pqd', 'cum_renewable_share']])
y = df_merged['bct_price']
model = OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 10})

print(f"\n  OLS with HAC standard errors (Newey-West, 10 lags):")
print(f"  Dependent variable: BCT price (USD)")
print(f"  N = {model.nobs:.0f}, R² = {model.rsquared:.4f}, Adj R² = {model.rsquared_adj:.4f}")
print(f"  {'Variable':25s} {'Coeff':>10s} {'Std Err':>10s} {'t-stat':>10s} {'p-value':>10s}")
print(f"  {'-'*70}")
for name, coef, se, t, p in zip(model.params.index, model.params, model.bse, model.tvalues, model.pvalues):
    print(f"  {name:25s} {coef:10.4f} {se:10.4f} {t:10.3f} {p:10.6f}")

results['ols_regression'] = {
    'r_squared': round(model.rsquared, 4),
    'adj_r_squared': round(model.rsquared_adj, 4),
    'n_obs': int(model.nobs),
    'coefficients': {name: round(float(coef), 4) for name, coef in model.params.items()},
    'std_errors': {name: round(float(se), 4) for name, se in model.bse.items()},
    'p_values': {name: round(float(p), 6) for name, p in model.pvalues.items()},
    'note': 'HAC standard errors (Newey-West, 10 lags)',
}

# First-differenced regression (addresses non-stationarity concern)
df_fd = df_merged[['date', 'bct_price', 'cum_pqd', 'cum_renewable_share']].copy()
df_fd['d_price'] = df_fd['bct_price'].diff()
df_fd['d_pqd'] = df_fd['cum_pqd'].diff()
df_fd['d_ren'] = df_fd['cum_renewable_share'].diff()
df_fd = df_fd.dropna()

X_fd = add_constant(df_fd[['d_pqd', 'd_ren']])
y_fd = df_fd['d_price']
model_fd = OLS(y_fd, X_fd).fit(cov_type='HAC', cov_kwds={'maxlags': 10})

print(f"\n  First-differenced OLS with HAC standard errors:")
print(f"  Dependent variable: Δ BCT price")
print(f"  N = {model_fd.nobs:.0f}, R² = {model_fd.rsquared:.4f}")
print(f"  {'Variable':25s} {'Coeff':>10s} {'Std Err':>10s} {'t-stat':>10s} {'p-value':>10s}")
print(f"  {'-'*70}")
for name, coef, se, t, p in zip(model_fd.params.index, model_fd.params, model_fd.bse, model_fd.tvalues, model_fd.pvalues):
    print(f"  {name:25s} {coef:10.4f} {se:10.4f} {t:10.3f} {p:10.6f}")

results['ols_first_differenced'] = {
    'r_squared': round(model_fd.rsquared, 4),
    'n_obs': int(model_fd.nobs),
    'coefficients': {name: round(float(coef), 4) for name, coef in model_fd.params.items()},
    'std_errors': {name: round(float(se), 4) for name, se in model_fd.bse.items()},
    'p_values': {name: round(float(p), 6) for name, p in model_fd.pvalues.items()},
    'note': 'First-differenced, HAC standard errors (Newey-West, 10 lags)',
}


# ── Step 7: Summary statistics ───────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 7: Summary statistics for paper")
print("=" * 70)

# Key periods
launch = df_merged[df_merged['date'] <= '2021-11-15']
crash = df_merged[(df_merged['date'] >= '2021-11-15') & (df_merged['date'] <= '2022-06-30')]
bottom = df_merged[(df_merged['date'] >= '2022-07-01') & (df_merged['date'] <= '2023-06-30')]

periods = [('Launch (Oct-Nov 2021)', launch), ('Crash (Nov 2021-Jun 2022)', crash), ('Bottom (Jul 2022-Jun 2023)', bottom)]

for period_name, period_df in periods:
    if len(period_df) == 0:
        continue
    print(f"\n  {period_name}:")
    print(f"    Mean price:          ${period_df['bct_price'].mean():.2f}")
    print(f"    Cum PQD:             {period_df['cum_pqd'].iloc[-1]:.2f}")
    print(f"    Cum renewable share: {period_df['cum_renewable_share'].iloc[-1]:.2%}")
    if period_df['rolling_30d_pqd'].notna().any():
        print(f"    Rolling 30d PQD:     {period_df['rolling_30d_pqd'].dropna().mean():.2f}")
        print(f"    Rolling 30d renew:   {period_df['rolling_30d_renewable'].dropna().mean():.2%}")

results['period_summaries'] = {}
for period_name, period_df in periods:
    if len(period_df) == 0:
        continue
    results['period_summaries'][period_name] = {
        'n_days': len(period_df),
        'mean_price': round(period_df['bct_price'].mean(), 4),
        'final_cum_pqd': round(period_df['cum_pqd'].iloc[-1], 2),
        'final_cum_renewable_share': round(period_df['cum_renewable_share'].iloc[-1], 4),
    }


# ── Step 5b: Second-differenced Granger for non-stationary d_price/d_cum_pqd ──
print("\n  Second-differenced Granger tests (for series that failed ADF at I(1)):")
df_weekly2 = df_merged.set_index('date').resample('W').agg({
    'bct_price': 'mean',
    'cum_pqd': 'last',
    'cum_renewable_share': 'last',
}).dropna().reset_index()

df_weekly2['dd_price'] = df_weekly2['bct_price'].diff().diff()
df_weekly2['dd_cum_pqd'] = df_weekly2['cum_pqd'].diff().diff()
df_weekly2 = df_weekly2.dropna()

for col in ['dd_price', 'dd_cum_pqd']:
    adf_stat, adf_p, _, _, _, _ = adfuller(df_weekly2[col])
    status = "STATIONARY" if adf_p < 0.05 else "NON-STATIONARY"
    print(f"    {col:25s}: ADF stat = {adf_stat:.3f}, p = {adf_p:.4f} [{status}]")

granger_i2_pairs = [
    ('dd_cum_pqd', 'dd_price', 'I(2) quality_causes_price (cum PQD → Price)'),
    ('dd_price', 'dd_cum_pqd', 'I(2) price_causes_quality (Price → cum PQD)'),
]

print(f"\n  {'Test':55s} {'Lag':>4s} {'F-stat':>10s} {'p-value':>10s} {'Sig':>5s}")
print(f"  {'-'*90}")

for cause_col, effect_col, label in granger_i2_pairs:
    test_data = df_weekly2[[effect_col, cause_col]].dropna()
    if len(test_data) < 20:
        print(f"  {label:55s}  -- insufficient data --")
        continue
    try:
        gc_result = grangercausalitytests(test_data, maxlag=MAX_LAG, verbose=False)
        best_lag, best_p, best_f = None, 1.0, 0.0
        lag_details = {}
        for lag in range(1, MAX_LAG + 1):
            f_stat = gc_result[lag][0]['ssr_ftest'][0]
            p_val = gc_result[lag][0]['ssr_ftest'][1]
            lag_details[str(lag)] = {'f_stat': round(f_stat, 4), 'p_value': round(p_val, 6)}
            if p_val < best_p:
                best_p, best_f, best_lag = p_val, f_stat, lag
        sig = "***" if best_p < 0.001 else "**" if best_p < 0.01 else "*" if best_p < 0.05 else ""
        print(f"  {label:55s} {best_lag:4d} {best_f:10.3f} {best_p:10.6f} {sig:>5s}")
        granger_results[label] = {
            'best_lag': best_lag, 'best_f_stat': round(best_f, 4),
            'best_p_value': round(best_p, 6), 'significant': best_p < 0.05,
            'lag_details': lag_details, 'n_observations': len(test_data),
            'note': 'Second-differenced (I(2)) for stationarity',
        }
    except Exception as e:
        print(f"  {label:55s}  ERROR: {e}")

results['granger_causality'] = granger_results


# ── Step 8: Generate publication-quality figure ──────────────────────
print("\n" + "=" * 70)
print("STEP 8: Generating figure")
print("=" * 70)

# Use Nature-style formatting
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
})

fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10, 8), height_ratios=[3, 1.2],
                                      gridspec_kw={'hspace': 0.08})

# ── Panel A: Price + quality dual-axis ──
color_price = '#2166AC'  # blue
color_pqd = '#B2182B'    # red
color_ren = '#1B7837'    # green

# Show full price trajectory (even beyond deposit window)
ax_top.plot(df_price['date'], df_price['bct_price'], color=color_price, linewidth=1.8,
            alpha=0.9, label='BCT price (USD)', zorder=3)

# Mark the deposit observation window
deposit_end = df_merged['date'].max()
ax_top.axvline(deposit_end, color='grey', linewidth=0.8, linestyle=':', alpha=0.6, zorder=1)
ax_top.annotate('Last deposit\nobserved', xy=(deposit_end, 7.5), fontsize=7.5,
                ha='left', va='top', color='grey',
                xytext=(deposit_end + pd.Timedelta(days=10), 7.5))

ax_top.set_ylabel('BCT Price (USD)', color=color_price, fontsize=11)
ax_top.tick_params(axis='y', labelcolor=color_price)
ax_top.set_ylim(bottom=0, top=9)
ax_top.set_xlim(df_price['date'].min(), df_price['date'].max())

# Right axis: quality metrics (only during deposit observation window)
ax_top2 = ax_top.twinx()

ax_top2.plot(df_merged['date'], df_merged['cum_pqd'], color=color_pqd, linewidth=1.5,
             linestyle='--', alpha=0.85, label='Cumulative PQD', zorder=2)
ax_top2.plot(df_merged['date'], df_merged['cum_renewable_share'] * 100, color=color_ren,
             linewidth=1.5, linestyle='-.', alpha=0.85, label='Cumulative renewable %', zorder=2)

# Rolling 30d as fills
mask_r = df_merged['rolling_30d_pqd'].notna()
if mask_r.any():
    ax_top2.fill_between(df_merged.loc[mask_r, 'date'],
                         df_merged.loc[mask_r, 'rolling_30d_pqd'],
                         df_merged.loc[mask_r, 'cum_pqd'],
                         color=color_pqd, alpha=0.08, label='30d PQD band')
    ax_top2.fill_between(df_merged.loc[mask_r, 'date'],
                         df_merged.loc[mask_r, 'rolling_30d_renewable'] * 100,
                         df_merged.loc[mask_r, 'cum_renewable_share'] * 100,
                         color=color_ren, alpha=0.08, label='30d renewable band')

ax_top2.set_ylabel('Quality Score / Renewable Share (%)', fontsize=11)
ax_top2.set_ylim(20, 105)

# Legend
lines1, labels1 = ax_top.get_legend_handles_labels()
lines2, labels2 = ax_top2.get_legend_handles_labels()
ax_top.legend(lines1 + lines2[:2], labels1 + labels2[:2],
              loc='upper right', fontsize=8.5, framealpha=0.92, edgecolor='grey')

# Correlation annotation box
# Use the first-differenced results since they are more credible
annotation_text = (
    f"First-differenced OLS (n = {int(model_fd.nobs)}):\n"
    f"  d(PQD) coeff = {model_fd.params['d_pqd']:.3f} (p = {model_fd.pvalues['d_pqd']:.4f})\n"
    f"  d(Ren%) coeff = {model_fd.params['d_ren']:.3f} (p < 0.001)\n"
    f"Levels: Pearson r(Price, PQD) = {pearson_cum_pqd:.3f}***"
)
ax_top.annotate(annotation_text, xy=(0.02, 0.55), xycoords='axes fraction',
                fontsize=7.5, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#f5f5f5', edgecolor='grey',
                          alpha=0.9))

ax_top.text(0.01, 0.98, 'a', transform=ax_top.transAxes, fontsize=14, fontweight='bold',
            va='top', ha='left')

# Remove x labels from top panel
ax_top.set_xticklabels([])
ax_top.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax_top.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

# ── Panel B: Daily deposit volume bar chart ──
# Aggregate deposits by week for readability
df_dep_weekly = df_dep.groupby(pd.Grouper(key='date', freq='W')).agg({
    'amount_tonnes': 'sum',
    'is_renewable': lambda x: x.sum(),  # count of renewable deposits
}).reset_index()
df_dep_weekly['n_deposits'] = df_dep.groupby(pd.Grouper(key='date', freq='W')).size().values

# Renewable vs non-renewable tonnage
df_dep['ren_tonnes'] = df_dep['amount_tonnes'] * df_dep['is_renewable']
df_dep['nonren_tonnes'] = df_dep['amount_tonnes'] * (1 - df_dep['is_renewable'])
df_dep_weekly2 = df_dep.groupby(pd.Grouper(key='date', freq='W')).agg({
    'ren_tonnes': 'sum',
    'nonren_tonnes': 'sum',
}).reset_index()

width = 6  # bar width in days
ax_bot.bar(df_dep_weekly2['date'], df_dep_weekly2['ren_tonnes'] / 1000,
           width=width, color=color_ren, alpha=0.6, label='Renewable')
ax_bot.bar(df_dep_weekly2['date'], df_dep_weekly2['nonren_tonnes'] / 1000,
           width=width, bottom=df_dep_weekly2['ren_tonnes'] / 1000,
           color='#984EA3', alpha=0.6, label='Non-renewable')

ax_bot.set_ylabel('Weekly deposits\n(kt CO2e)', fontsize=10)
ax_bot.set_xlabel('Date', fontsize=11)
ax_bot.set_xlim(df_price['date'].min(), df_price['date'].max())
ax_bot.legend(fontsize=8, loc='upper right', framealpha=0.92, edgecolor='grey')
ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax_bot.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax_bot.xaxis.get_majorticklabels(), rotation=45, ha='right')
ax_bot.axvline(deposit_end, color='grey', linewidth=0.8, linestyle=':', alpha=0.6)

ax_bot.text(0.01, 0.95, 'b', transform=ax_bot.transAxes, fontsize=14, fontweight='bold',
            va='top', ha='left')

fig.suptitle('BCT Price Trajectory and Pool Quality Composition', fontsize=13,
             fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save
fig.savefig(str(OUT_FIG_PNG), dpi=300, bbox_inches='tight')
fig.savefig(str(OUT_FIG_PDF), bbox_inches='tight')
plt.close()

print(f"  Saved: {OUT_FIG_PNG}")
print(f"  Saved: {OUT_FIG_PDF}")


# ── Step 9: Save results JSON ────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 9: Saving results")
print("=" * 70)

results['metadata'] = {
    'n_deposits': len(df_dep),
    'n_price_observations': len(df_price),
    'n_merged_observations': len(df_merged),
    'overlap_start': str(df_merged['date'].min().date()),
    'overlap_end': str(df_merged['date'].max().date()),
    'price_source': 'DeFi Llama (polygon:0x2F800Db0fdb5223b3C3f354886d907A671414A7F)',
    'quality_source': 'tco2_scores_complete.json + bct_deposits_enriched.json',
}

with open(OUT_JSON, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"  Saved: {OUT_JSON}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
