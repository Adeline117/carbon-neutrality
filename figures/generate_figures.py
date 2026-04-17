#!/usr/bin/env python3
"""
Generate publication-quality figures for Nature Communications paper on
adverse selection in tokenized carbon credits.

Figure 1: BCT Pool Composition (horizontal bar chart)
Figure 6: Four-panel depositor-level evidence (2x2)
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch
import warnings
warnings.filterwarnings('ignore')

# ── Style setup ──────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif', 'Times New Roman', 'serif'],
    'font.size': 9,
    'axes.linewidth': 0.6,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.edgecolor': 'white',
    'mathtext.fontset': 'dejavuserif',
    'pdf.fonttype': 42,  # TrueType for editability
    'ps.fonttype': 42,
})

DATA_DIR = '/Users/adelinewen/carbon-neutrality/data/depositor-analysis'
FIG_DIR  = '/Users/adelinewen/carbon-neutrality/figures'

# ── Load data ────────────────────────────────────────────────────────────
with open(f'{DATA_DIR}/bct_composition_complete.json') as f:
    comp = json.load(f)

with open(f'{DATA_DIR}/bct_deposits_enriched.json') as f:
    deposits = json.load(f)

with open(f'{DATA_DIR}/tco2_scores_complete.json') as f:
    scores = json.load(f)

with open(f'{DATA_DIR}/tco2_scores_novintage.json') as f:
    scores_nv = json.load(f)

with open(f'{DATA_DIR}/event_study_results.json') as f:
    events = json.load(f)

with open(f'{DATA_DIR}/base_rate_analysis.json') as f:
    base_rate = json.load(f)

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — BCT Pool Composition (horizontal bar chart)
# ═══════════════════════════════════════════════════════════════════════════

by_type = comp['by_type']

# Build sorted list (descending by tonnage)
types_sorted = sorted(by_type.keys(), key=lambda t: by_type[t]['tonnes'])
pcts = [by_type[t]['pct'] for t in types_sorted]

# Mean composite score per type from scores data
type_scores = {}
for addr, info in scores.items():
    t = info['type']
    type_scores.setdefault(t, []).append(info['composite'])
mean_scores = {t: np.mean(v) for t, v in type_scores.items()}

# Normalise scores to [0, 1] for colour mapping
all_means = list(mean_scores.values())
smin, smax = min(all_means), max(all_means)
norm_scores = {t: (mean_scores.get(t, smin) - smin) / (smax - smin)
               for t in types_sorted}

# Red-to-green gradient
cmap = LinearSegmentedColormap.from_list('rg', ['#c0392b', '#f0c040', '#27ae60'])
colors = [cmap(norm_scores[t]) for t in types_sorted]

fig1, ax1 = plt.subplots(figsize=(3.5, 3.0), dpi=300)

bars = ax1.barh(range(len(types_sorted)), pcts, color=colors, edgecolor='none',
                height=0.65, zorder=3)

ax1.set_yticks(range(len(types_sorted)))
ax1.set_yticklabels(types_sorted, fontsize=8)
ax1.set_xlabel('Share of BCT pool tonnage (%)', fontsize=8.5)
ax1.set_xlim(0, 82)

# Light horizontal gridlines
ax1.xaxis.grid(True, linewidth=0.3, color='#cccccc', zorder=0)
ax1.set_axisbelow(True)

# Percentage labels at end of each bar
for i, (pct, t) in enumerate(zip(pcts, types_sorted)):
    label = f'{pct:.1f}%'
    if t == 'Renewable':
        # annotate with selection coefficient
        label = f'{pct:.1f}%'
        ax1.annotate(f'  {label}   1.87× over-selection',
                     xy=(pct, i), xytext=(pct + 0.8, i),
                     fontsize=7, va='center', color='#333333',
                     fontstyle='italic')
    else:
        ax1.text(pct + 0.8, i, label, va='center', fontsize=7, color='#555555')

# Vertical dashed line at 37% VCS base rate — draw only near the Renewable bar
renewable_idx = types_sorted.index('Renewable')
ax1.vlines(37, renewable_idx - 0.45, renewable_idx + 0.45,
           linestyle='--', linewidth=0.9, color='#555555', zorder=4)
ax1.text(37, renewable_idx + 0.55, 'VCS base\nrate (37%)', fontsize=6,
         ha='center', va='bottom', color='#555555')

# Colour bar legend
sm = plt.cm.ScalarMappable(cmap=cmap, norm=matplotlib.colors.Normalize(
    vmin=round(smin, 0), vmax=round(smax, 0)))
sm.set_array([])
cbar = fig1.colorbar(sm, ax=ax1, location='bottom', fraction=0.06, pad=0.18,
                     aspect=30)
cbar.set_label('Mean composite quality score', fontsize=7)
cbar.ax.tick_params(labelsize=6.5)

fig1.tight_layout(rect=[0, 0.08, 1, 1])
fig1.savefig(f'{FIG_DIR}/fig1_composition.pdf', bbox_inches='tight')
fig1.savefig(f'{FIG_DIR}/fig1_composition.png', dpi=300, bbox_inches='tight')
plt.close(fig1)
print('Figure 1 saved.')

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 6 — Four-panel depositor-level evidence (2×2)
# ═══════════════════════════════════════════════════════════════════════════

# ── Merge deposits with scores ──────────────────────────────────────────
dep_blocks = []
dep_scores_full = []
dep_scores_nv = []
dep_amounts = []
for d in deposits:
    addr = d['tco2_address']
    if addr in scores:
        dep_blocks.append(d['block_number'])
        dep_scores_full.append(scores[addr]['composite'])
        dep_amounts.append(d['amount_tonnes'])
        nv = scores_nv.get(addr)
        dep_scores_nv.append(nv['composite_novintage'] if nv else None)

dep_blocks = np.array(dep_blocks, dtype=float)
dep_scores_full = np.array(dep_scores_full, dtype=float)
dep_amounts = np.array(dep_amounts, dtype=float)

# Block → approximate date mapping
# block 20M ≈ Oct 2021, block 37M ≈ Dec 2022
# Linear interpolation
from datetime import datetime, timedelta
date_20M = datetime(2021, 10, 1)
date_37M = datetime(2022, 12, 23)
sec_per_block = (date_37M - date_20M).total_seconds() / (37e6 - 20e6)

def block_to_date(b):
    dt = date_20M + timedelta(seconds=(b - 20e6) * sec_per_block)
    return dt

dates_num = matplotlib.dates.date2num([block_to_date(b) for b in dep_blocks])

# Quartile assignment
q_edges = np.percentile(dep_scores_full, [25, 50, 75])
def quartile_label(s):
    if s <= q_edges[0]: return 'Q1 (lowest)'
    elif s <= q_edges[1]: return 'Q2'
    elif s <= q_edges[2]: return 'Q3'
    else: return 'Q4 (highest)'

q_labels = [quartile_label(s) for s in dep_scores_full]
q_colors_map = {'Q1 (lowest)': '#c0392b', 'Q2': '#e67e22', 'Q3': '#3498db', 'Q4 (highest)': '#27ae60'}

# LOESS-like smoothing via rolling mean (sorted by block)
sort_idx = np.argsort(dep_blocks)
blocks_s = dep_blocks[sort_idx]
scores_s = dep_scores_full[sort_idx]
dates_s = np.array(dates_num)[sort_idx]

# Simple LOWESS using scipy if available, else rolling mean
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    loess_result = lowess(scores_s, dates_s, frac=0.25, return_sorted=True)
    loess_x, loess_y = loess_result[:, 0], loess_result[:, 1]
except ImportError:
    # Fallback: rolling mean
    window = 50
    loess_y = np.convolve(scores_s, np.ones(window)/window, mode='valid')
    loess_x = dates_s[window//2:window//2+len(loess_y)]

# Event study blocks → dates
block_terra = events['event_calibration']['block_terra']
block_ftx = events['event_calibration']['block_ftx']
date_terra = matplotlib.dates.date2num(block_to_date(block_terra))
date_ftx = matplotlib.dates.date2num(block_to_date(block_ftx))

# Period assignment for panel (c)
def period_label(b):
    if b < block_terra: return 'Pre-Terra'
    elif b < block_ftx: return 'Terra–FTX'
    else: return 'Post-FTX'

period_labels = [period_label(b) for b in dep_blocks]
period_colors_map = {'Pre-Terra': '#3498db', 'Terra–FTX': '#e67e22', 'Post-FTX': '#c0392b'}

# ── Create 2×2 figure ───────────────────────────────────────────────────
fig6, axes = plt.subplots(2, 2, figsize=(7.2, 5.8), dpi=300)
((ax_a, ax_b), (ax_c, ax_d)) = axes

# Format dates on x-axes
import matplotlib.dates as mdates

# ── Panel (a): Temporal quality decline ──────────────────────────────────
for ql in ['Q1 (lowest)', 'Q2', 'Q3', 'Q4 (highest)']:
    mask = np.array([l == ql for l in q_labels])
    ax_a.scatter(np.array(dates_num)[mask], dep_scores_full[mask],
                 s=4, alpha=0.35, c=q_colors_map[ql], label=ql,
                 edgecolors='none', zorder=2, rasterized=True)

ax_a.plot(loess_x, loess_y, color='#2c3e50', linewidth=1.5, zorder=3,
          label='LOESS')
ax_a.axhline(32.1, color='#888888', linewidth=0.7, linestyle=':', zorder=1)
ax_a.text(dates_num[-1], 32.5, 'VWM = 32.1', fontsize=6.5, ha='right',
          color='#666666')

# Compute overall rho from all 1,187 deposits (not the 877-subset in event study)
from scipy.stats import spearmanr as _spearmanr
rho_overall, p_overall = _spearmanr(dep_blocks, dep_scores_full)
ax_a.text(0.05, 0.92,
          f'$\\rho$ = {rho_overall:.2f}, $p$ < 10$^{{-16}}$',
          transform=ax_a.transAxes, fontsize=7.5, fontweight='bold',
          bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                    edgecolor='#cccccc', alpha=0.9))

ax_a.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax_a.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax_a.set_ylabel('Composite quality score', fontsize=8)
ax_a.set_xlabel('')
ax_a.legend(fontsize=5.5, loc='upper right', frameon=True, framealpha=0.9,
            edgecolor='#cccccc', ncol=2, markerscale=2.5, handletextpad=0.3,
            columnspacing=0.5)
ax_a.tick_params(labelsize=7)
ax_a.text(-0.12, 1.05, 'a', transform=ax_a.transAxes, fontsize=12,
          fontweight='bold', va='top')

# ── Panel (b): Base-rate selection ───────────────────────────────────────
top_types = ['Renewable', 'Fossil switch', 'Waste/Methane', 'REDD+']
bct_shares = [comp['by_type'][t]['pct'] for t in top_types]
vcs_shares_map = base_rate['vcs_universe']['shares_pct']
vcs_shares = [vcs_shares_map.get(t, 0) for t in top_types]

x_pos = np.arange(len(top_types))
bar_w = 0.35

bars_bct = ax_b.bar(x_pos - bar_w/2, bct_shares, bar_w, color='#c0392b',
                    label='BCT pool', edgecolor='none', zorder=3)
bars_vcs = ax_b.bar(x_pos + bar_w/2, vcs_shares, bar_w, color='#95a5a6',
                    label='VCS universe', edgecolor='none', zorder=3)

# Labels on bars
for bar, val in zip(bars_bct, bct_shares):
    ax_b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.2,
              f'{val:.1f}%', ha='center', fontsize=6, color='#c0392b')
for bar, val in zip(bars_vcs, vcs_shares):
    ax_b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.2,
              f'{val:.0f}%', ha='center', fontsize=6, color='#666666')

# Selection coefficients
sel_coefs = base_rate['selection_coefficients']
annotations = {
    'Renewable': f'1.87×',
    'REDD+': f'0.20×'
}
for i, t in enumerate(top_types):
    if t in annotations:
        y_annot = max(bct_shares[i], vcs_shares[i]) + 4
        ax_b.annotate(annotations[t],
                     xy=(i, y_annot),
                     fontsize=7.5, ha='center', fontweight='bold',
                     fontstyle='italic', color='#2c3e50')

ax_b.set_xticks(x_pos)
ax_b.set_xticklabels(top_types, fontsize=7)
ax_b.set_ylabel('Share of tonnage (%)', fontsize=8)
ax_b.legend(fontsize=6.5, loc='upper right', frameon=True, framealpha=0.9,
            edgecolor='#cccccc')
ax_b.set_ylim(0, 82)
ax_b.tick_params(labelsize=7)
ax_b.yaxis.grid(True, linewidth=0.3, color='#cccccc', zorder=0)
ax_b.set_axisbelow(True)
ax_b.text(-0.12, 1.05, 'b', transform=ax_b.transAxes, fontsize=12,
          fontweight='bold', va='top')

# ── Panel (c): Event study ───────────────────────────────────────────────
for pl in ['Pre-Terra', 'Terra–FTX', 'Post-FTX']:
    mask = np.array([l == pl for l in period_labels])
    ax_c.scatter(np.array(dates_num)[mask], dep_scores_full[mask],
                 s=4, alpha=0.35, c=period_colors_map[pl], label=pl,
                 edgecolors='none', zorder=2, rasterized=True)

# LOESS line
ax_c.plot(loess_x, loess_y, color='#2c3e50', linewidth=1.3, zorder=3)

# Vertical event lines
ax_c.axvline(date_terra, color='#555555', linewidth=0.8, linestyle='--', zorder=4)
ax_c.axvline(date_ftx, color='#555555', linewidth=0.8, linestyle='--', zorder=4)

# Event labels (inside plot area, near top)
ax_c.set_ylim(22, 58)
ax_c.text(date_terra, 56, 'Terra\ncollapse', fontsize=6, ha='center',
          color='#555555', va='top')
ax_c.text(date_ftx, 56, 'FTX\ncollapse', fontsize=6, ha='center',
          color='#555555', va='top')

# Period statistics — recompute from full 1187-deposit data
from scipy.stats import spearmanr as _sp
pre_mask = dep_blocks < block_terra
mid_mask = (dep_blocks >= block_terra) & (dep_blocks < block_ftx)
post_mask = dep_blocks >= block_ftx
pre_rho, pre_p = _sp(dep_blocks[pre_mask], dep_scores_full[pre_mask])
mid_rho, mid_p = _sp(dep_blocks[mid_mask], dep_scores_full[mid_mask]) if mid_mask.sum() >= 3 else (0, 1)
post_rho, post_p = _sp(dep_blocks[post_mask], dep_scores_full[post_mask]) if post_mask.sum() >= 3 else (0, 1)

stats_text = (
    f'Pre: $\\rho$={pre_rho:.2f}, p={pre_p:.4f}\n'
    f'Mid: $\\rho$={mid_rho:.2f}, p={mid_p:.4f}\n'
    f'Post: $\\rho$={post_rho:.2f}, p={post_p:.2f}'
)
ax_c.text(0.03, 0.05, stats_text, transform=ax_c.transAxes, fontsize=6,
          va='bottom', fontfamily='monospace',
          bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                    edgecolor='#cccccc', alpha=0.9))

ax_c.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax_c.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax_c.set_ylabel('Composite quality score', fontsize=8)
ax_c.set_xlabel('')
ax_c.legend(fontsize=6, loc='upper right', frameon=True, framealpha=0.9,
            edgecolor='#cccccc', markerscale=2.5)
ax_c.tick_params(labelsize=7)
ax_c.text(-0.12, 1.05, 'c', transform=ax_c.transAxes, fontsize=12,
          fontweight='bold', va='top')

# ── Panel (d): Vintage-free robustness (sign reversal) ──────────────────

# Compute temporal correlations: full composite vs vintage-free composite
# Using the same merged deposits
from scipy.stats import spearmanr

blocks_for_nv = []
scores_full_for_nv = []
scores_novintage_for_nv = []

for d in deposits:
    addr = d['tco2_address']
    if addr in scores and addr in scores_nv:
        blocks_for_nv.append(d['block_number'])
        scores_full_for_nv.append(scores[addr]['composite'])
        scores_novintage_for_nv.append(scores_nv[addr]['composite_novintage'])

blocks_for_nv = np.array(blocks_for_nv, dtype=float)
scores_full_for_nv = np.array(scores_full_for_nv, dtype=float)
scores_novintage_for_nv = np.array(scores_novintage_for_nv, dtype=float)

rho_full, p_full = spearmanr(blocks_for_nv, scores_full_for_nv)
rho_nv, p_nv = spearmanr(blocks_for_nv, scores_novintage_for_nv)

# Connected dot plot showing vintage confound
metrics = ['Full composite\n(with vintage)', 'Vintage-free\ncomposite']
rhos = [rho_full, rho_nv]
rho_colors = ['#c0392b', '#27ae60']  # negative=red, near-zero=green

ax_d.scatter([0, 1], rhos, s=140, c=rho_colors, zorder=5, edgecolors='white',
             linewidth=1.8)

# Connecting arrow
ax_d.annotate('', xy=(1, rho_nv), xytext=(0, rho_full),
              arrowprops=dict(arrowstyle='->', color='#555555', lw=1.8,
                              connectionstyle='arc3,rad=-0.15'))

# Zero line
ax_d.axhline(0, color='#888888', linewidth=0.7, linestyle='-', zorder=1)

# Background shading
ax_d.axhspan(-0.5, 0, color='#fdedec', alpha=0.35, zorder=0)
ax_d.axhspan(0, 0.35, color='#eafaf1', alpha=0.35, zorder=0)

# Value labels
ax_d.text(0, rho_full - 0.045, f'$\\rho$ = {rho_full:.2f}', ha='center',
          fontsize=9, fontweight='bold', color='#c0392b')
nv_sign = '+' if rho_nv >= 0 else ''
ax_d.text(1, rho_nv + 0.035, f'$\\rho$ = {nv_sign}{rho_nv:.2f}', ha='center',
          fontsize=9, fontweight='bold', color='#27ae60')

# p-value annotations
ax_d.text(0, rho_full - 0.085, f'$p$ < 10$^{{-16}}$', ha='center',
          fontsize=6.5, color='#888888')
p_nv_str = f'$p$ = {p_nv:.2f}' if p_nv > 0.01 else f'$p$ = {p_nv:.1e}'
ax_d.text(1, rho_nv + 0.075, p_nv_str, ha='center',
          fontsize=6.5, color='#888888')

# Annotation box
ax_d.text(0.5, 0.22, 'Vintage confound:\nremoving vintage score\ncollapses temporal signal',
          ha='center', fontsize=7, fontstyle='italic', color='#2c3e50',
          bbox=dict(boxstyle='round,pad=0.4', facecolor='#fef9e7',
                    edgecolor='#f0c040', alpha=0.9))

# Side region labels
ax_d.text(-0.35, -0.15, 'Declining\nquality', fontsize=6, ha='center',
          color='#c0392b', fontstyle='italic', rotation=90)
ax_d.text(-0.35, 0.10, 'No trend', fontsize=6, ha='center',
          color='#27ae60', fontstyle='italic', rotation=90)

ax_d.set_xticks([0, 1])
ax_d.set_xticklabels(metrics, fontsize=7.5)
ax_d.set_ylabel('Spearman $\\rho$ (quality vs. time)', fontsize=8)
ax_d.set_xlim(-0.55, 1.55)
ax_d.set_ylim(-0.38, 0.30)
ax_d.tick_params(labelsize=7)
ax_d.text(-0.12, 1.05, 'd', transform=ax_d.transAxes, fontsize=12,
          fontweight='bold', va='top')

# ── Final layout ─────────────────────────────────────────────────────────
fig6.tight_layout(h_pad=2.5, w_pad=2.0)
fig6.savefig(f'{FIG_DIR}/fig6_depositor_evidence.pdf', bbox_inches='tight')
fig6.savefig(f'{FIG_DIR}/fig6_depositor_evidence.png', dpi=300, bbox_inches='tight')
plt.close(fig6)
print('Figure 6 saved.')

print('Done — all figures generated.')
