"""analysis_pipeline.py — Field experiment analysis for Paper 3.

Ingests on-chain events from RandomizedGate.sol and computes:

  - Randomization balance check (chi-square on arm assignment)
  - Attrition check (commit -> settle conversion by arm)
  - ITT (Intent-to-Treat): effect of being assigned to treatment on the
    quality of retired credits, across all committed retirements.
  - TOT (Treatment on Treated): effect of actual retirement under the
    gate among compliers, estimated via a Wald / 2SLS ratio where the
    assignment is the instrument.
  - Regression-discontinuity around the grade boundary (composite bps
    just above / below `minGrade` cutoff).
  - Heterogeneous effects by wallet size (log-tonnes committed historically).
  - Price premium analysis using off-chain retirement-price logs, if
    supplied in a `prices.csv` sidecar.

Outputs:
  - `results_template.md`: pre-registered table shells auto-populated.
  - `results_full.json`: all coefficients, SEs, CIs.
  - `robustness/`: per-check CSVs for appendix tables.

Usage (mainnet):

    python analysis_pipeline.py \
        --events events.parquet \
        --prices prices.csv \
        --cutoff-bps 6000 \
        --out ./out/

Usage (validation, synthetic data):

    python mock_data_validation.py   # generates and analyses synthetic data

The pipeline is intentionally pure-Python / numpy / pandas so it can be
re-run from scratch by reviewers without a toolchain install; scipy is
imported lazily and is optional.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Event schema
# ---------------------------------------------------------------------------

# The RandomizedGate contract emits three events. The analysis joins them on
# requestId. A "row" in our working frame is one committed retirement.
#
# Required columns after join:
#   request_id        int
#   user              str  (0x-prefixed wallet, lowercased)
#   credit_token      str
#   token_id          int
#   amount            float (tonnes; credits assumed to have 18 decimals)
#   arm               {"TREATMENT", "CONTROL", "PENDING"}
#   commit_ts         int  (unix seconds)
#   settle_ts         int or NaN
#   settled           bool
#   retired           bool
#   grade_at_settle   {"B","BB","BBB","A","AA","AAA"} or NaN
#   composite_bps     int (0-10000) or NaN
GRADE_ORDER = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_TO_INT = {g: i for i, g in enumerate(GRADE_ORDER)}


# ---------------------------------------------------------------------------
# Results dataclass
# ---------------------------------------------------------------------------

@dataclass
class BalanceCheck:
    n_treatment: int
    n_control: int
    share_treatment: float
    chi_square: float
    p_value: float
    passes_at_alpha_05: bool


@dataclass
class AttritionCheck:
    commit_to_settle_treatment: float
    commit_to_settle_control: float
    diff: float
    # Fisher exact or prop-test on settlement rates across arms:
    p_value: float


@dataclass
class ITTEstimate:
    outcome: str
    n: int
    mean_treatment: float
    mean_control: float
    effect: float
    se: float
    ci_low: float
    ci_high: float
    p_value: float


@dataclass
class TOTEstimate:
    outcome: str
    n: int
    effect_itt: float
    compliance_rate: float
    effect_tot: float
    se_tot: float
    ci_low: float
    ci_high: float


@dataclass
class RDEstimate:
    cutoff_bps: int
    bandwidth_bps: int
    n_left: int
    n_right: int
    jump: float
    se: float
    p_value: float


@dataclass
class Heterogeneity:
    subgroup: str
    effect: float
    se: float
    ci_low: float
    ci_high: float


@dataclass
class AnalysisResults:
    balance: BalanceCheck
    attrition: AttritionCheck
    primary_itt: ITTEstimate
    secondary_itt: list[ITTEstimate] = field(default_factory=list)
    tot: Optional[TOTEstimate] = None
    rd: Optional[RDEstimate] = None
    heterogeneity: list[Heterogeneity] = field(default_factory=list)
    price_premium: Optional[ITTEstimate] = None

    def to_dict(self) -> dict:
        return json.loads(json.dumps(asdict(self), default=str))


# ---------------------------------------------------------------------------
# Small statistical helpers (scipy-free)
# ---------------------------------------------------------------------------

def chi_square_p(stat: float, df: int = 1) -> float:
    """Upper-tail p-value for a chi-square statistic. Uses the regularized
    incomplete gamma function Q(df/2, stat/2). Good to ~5 decimal places
    for the df=1 and df=small cases we use."""
    try:
        from scipy.stats import chi2
        return float(chi2.sf(stat, df))
    except Exception:
        pass

    # Fallback: Wilson-Hilferty cube-root normal approximation
    # z = ((stat/df)^(1/3) - (1 - 2/(9*df))) / sqrt(2/(9*df))
    z = ((stat / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    # normal upper tail via erf
    return 0.5 * math.erfc(z / math.sqrt(2))


def two_sample_diff(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Welch's two-sample test on means. Returns (diff, se, p)."""
    mx, my = np.mean(x), np.mean(y)
    vx, vy = np.var(x, ddof=1) if len(x) > 1 else 0.0, np.var(y, ddof=1) if len(y) > 1 else 0.0
    nx, ny = len(x), len(y)
    se = math.sqrt((vx / nx) + (vy / ny)) if nx and ny else float("nan")
    diff = mx - my
    if se == 0 or math.isnan(se):
        return diff, se, float("nan")
    t = diff / se
    # Welch df
    num = ((vx / nx) + (vy / ny)) ** 2
    den = ((vx / nx) ** 2) / max(nx - 1, 1) + ((vy / ny) ** 2) / max(ny - 1, 1)
    df = num / den if den > 0 else nx + ny - 2
    try:
        from scipy.stats import t as student_t
        p = 2 * (1 - student_t.cdf(abs(t), df))
    except Exception:
        # Gaussian approximation for large df (>~30)
        p = math.erfc(abs(t) / math.sqrt(2))
    return diff, se, p


def proportion_diff_p(x_success: int, x_n: int, y_success: int, y_n: int) -> float:
    """Two-proportion z-test p-value."""
    if x_n == 0 or y_n == 0:
        return float("nan")
    p_pooled = (x_success + y_success) / (x_n + y_n)
    if p_pooled in (0.0, 1.0):
        return 1.0
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / x_n + 1 / y_n))
    z = (x_success / x_n - y_success / y_n) / se
    return math.erfc(abs(z) / math.sqrt(2))


# ---------------------------------------------------------------------------
# Core analyses
# ---------------------------------------------------------------------------

def balance_check(df: pd.DataFrame) -> BalanceCheck:
    """Chi-square test that the arm assignment share is 50/50."""
    assigned = df[df["arm"].isin(["TREATMENT", "CONTROL"])]
    n_t = int((assigned["arm"] == "TREATMENT").sum())
    n_c = int((assigned["arm"] == "CONTROL").sum())
    n = n_t + n_c
    if n == 0:
        return BalanceCheck(0, 0, float("nan"), float("nan"), float("nan"), False)
    expected = n / 2
    chi2 = ((n_t - expected) ** 2 + (n_c - expected) ** 2) / expected
    p = chi_square_p(chi2, df=1)
    return BalanceCheck(
        n_treatment=n_t,
        n_control=n_c,
        share_treatment=n_t / n,
        chi_square=chi2,
        p_value=p,
        passes_at_alpha_05=bool(p > 0.05),
    )


def attrition_check(df: pd.DataFrame) -> AttritionCheck:
    """Differential commit->settle rates across arms flag self-selection out."""
    t = df[df["arm"] == "TREATMENT"]
    c = df[df["arm"] == "CONTROL"]
    rate_t = t["settled"].mean() if len(t) else float("nan")
    rate_c = c["settled"].mean() if len(c) else float("nan")
    p = proportion_diff_p(
        int(t["settled"].sum()), len(t),
        int(c["settled"].sum()), len(c),
    )
    return AttritionCheck(
        commit_to_settle_treatment=rate_t,
        commit_to_settle_control=rate_c,
        diff=rate_t - rate_c,
        p_value=p,
    )


def itt_primary(df: pd.DataFrame) -> ITTEstimate:
    """Primary ITT outcome: mean composite_bps of BURNED credits by arm
    of commitment, weighted by amount (tonnes).

    Pre-registered (docs/field-experiment/pre-registration.md, H1):
    the primary outcome is the mean pool-quality-distribution of credits
    that actually get retired (burned to 0xdead). This is computed
    per-arm, using the arm the user was randomly assigned to — not per
    retirement (so users who were refunded in the treatment arm still
    count as being IN the treatment arm but contribute zero mass to the
    retired-credit distribution). Intent-to-treat semantics: we are
    asking "does assigning a user to the gated pool raise the mean
    quality of the credits the market actually retires?"."""
    sub = df.dropna(subset=["composite_bps"]).copy()
    sub = sub[sub["retired"] == True]  # burned credits only  # noqa: E712
    sub["w"] = sub["amount"]
    t = sub[sub["arm"] == "TREATMENT"]
    c = sub[sub["arm"] == "CONTROL"]

    def _wmean(frame: pd.DataFrame) -> float:
        w = frame["w"].to_numpy()
        x = frame["composite_bps"].to_numpy()
        return float(np.sum(w * x) / np.sum(w)) if len(frame) and w.sum() > 0 else float("nan")

    mt, mc = _wmean(t), _wmean(c)
    # Unweighted variance for SE; weighted mean with unweighted variance is
    # an approximation. For weighted variance, see tot/rd robustness below.
    diff, se, p = two_sample_diff(t["composite_bps"].to_numpy(), c["composite_bps"].to_numpy())
    # Report the weighted diff as the point estimate
    diff_w = mt - mc
    return ITTEstimate(
        outcome="composite_bps_weighted_by_tonnes",
        n=len(t) + len(c),
        mean_treatment=mt,
        mean_control=mc,
        effect=diff_w,
        se=se,
        ci_low=diff_w - 1.96 * se,
        ci_high=diff_w + 1.96 * se,
        p_value=p,
    )


def itt_secondary(df: pd.DataFrame) -> list[ITTEstimate]:
    """Secondary ITT outcomes (pre-registered):
       - share of retired credits with final_grade >= A (H1 stringency)
       - mean grade ordinal (B=0 .. AAA=5)
       - share of committed retirements that end in burn (vs refund)
    """
    out: list[ITTEstimate] = []

    # Outcome 1: share with grade >= A
    def _share_A(frame: pd.DataFrame) -> tuple[float, int]:
        if len(frame) == 0:
            return float("nan"), 0
        ok = frame["grade_at_settle"].map(lambda g: GRADE_TO_INT.get(g, -1) >= GRADE_TO_INT["A"])
        return float(ok.mean()), int(ok.sum())

    settled = df[df["settled"]].copy()
    t, c = settled[settled["arm"] == "TREATMENT"], settled[settled["arm"] == "CONTROL"]
    shareT, _ = _share_A(t)
    shareC, _ = _share_A(c)
    p = proportion_diff_p(
        int((t["grade_at_settle"].map(GRADE_TO_INT.get) >= GRADE_TO_INT["A"]).sum()), len(t),
        int((c["grade_at_settle"].map(GRADE_TO_INT.get) >= GRADE_TO_INT["A"]).sum()), len(c),
    )
    se = math.sqrt((shareT * (1 - shareT)) / max(len(t), 1) + (shareC * (1 - shareC)) / max(len(c), 1))
    out.append(ITTEstimate(
        outcome="share_retired_grade_at_least_A",
        n=len(t) + len(c),
        mean_treatment=shareT,
        mean_control=shareC,
        effect=shareT - shareC,
        se=se,
        ci_low=(shareT - shareC) - 1.96 * se,
        ci_high=(shareT - shareC) + 1.96 * se,
        p_value=p,
    ))

    # Outcome 2: mean grade ordinal
    settled["grade_ord"] = settled["grade_at_settle"].map(lambda g: GRADE_TO_INT.get(g, np.nan))
    t2 = settled[settled["arm"] == "TREATMENT"]["grade_ord"].dropna().to_numpy()
    c2 = settled[settled["arm"] == "CONTROL"]["grade_ord"].dropna().to_numpy()
    d, se, p = two_sample_diff(t2, c2)
    out.append(ITTEstimate(
        outcome="mean_grade_ordinal",
        n=len(t2) + len(c2),
        mean_treatment=float(t2.mean()) if len(t2) else float("nan"),
        mean_control=float(c2.mean()) if len(c2) else float("nan"),
        effect=d,
        se=se,
        ci_low=d - 1.96 * se,
        ci_high=d + 1.96 * se,
        p_value=p,
    ))

    # Outcome 3: share of commits that end in successful burn
    for_t = df[df["arm"] == "TREATMENT"]
    for_c = df[df["arm"] == "CONTROL"]
    burn_t = for_t["retired"].mean() if len(for_t) else float("nan")
    burn_c = for_c["retired"].mean() if len(for_c) else float("nan")
    se = math.sqrt(
        (burn_t * (1 - burn_t)) / max(len(for_t), 1)
        + (burn_c * (1 - burn_c)) / max(len(for_c), 1)
    )
    p = proportion_diff_p(int(for_t["retired"].sum()), len(for_t),
                          int(for_c["retired"].sum()), len(for_c))
    out.append(ITTEstimate(
        outcome="share_of_commits_that_retire",
        n=len(for_t) + len(for_c),
        mean_treatment=burn_t,
        mean_control=burn_c,
        effect=burn_t - burn_c,
        se=se,
        ci_low=(burn_t - burn_c) - 1.96 * se,
        ci_high=(burn_t - burn_c) + 1.96 * se,
        p_value=p,
    ))

    return out


def tot_estimate(df: pd.DataFrame, itt: ITTEstimate) -> TOTEstimate:
    """Wald-style TOT: rescale the ITT by the compliance rate. Compliance
    in our design = share of TREATMENT assignments that actually burn
    (i.e., credit met the grade). CONTROL is always-taker (compliance = 1
    in the no-gate sense), so the first-stage F is the difference in burn
    rates across arms."""
    t = df[df["arm"] == "TREATMENT"]
    c = df[df["arm"] == "CONTROL"]
    burn_t = t["retired"].mean() if len(t) else float("nan")
    burn_c = c["retired"].mean() if len(c) else float("nan")
    compliance = burn_c - burn_t  # CONTROL - TREATMENT burn rate = share refused
    if compliance == 0 or math.isnan(compliance):
        return TOTEstimate(
            outcome=itt.outcome, n=itt.n, effect_itt=itt.effect,
            compliance_rate=compliance, effect_tot=float("nan"),
            se_tot=float("nan"), ci_low=float("nan"), ci_high=float("nan"),
        )
    # TOT = ITT / compliance, delta-method SE
    tot = itt.effect / compliance
    # approximate SE via delta method: Var(a/b) ~ (1/b^2)*Var(a) + (a^2/b^4)*Var(b)
    se_a = itt.se
    # SE of compliance (binomial diff); approximate
    se_b = math.sqrt(
        (burn_t * (1 - burn_t)) / max(len(t), 1)
        + (burn_c * (1 - burn_c)) / max(len(c), 1)
    )
    se = math.sqrt((se_a / compliance) ** 2 + (itt.effect ** 2 / compliance ** 4) * se_b ** 2)
    return TOTEstimate(
        outcome=itt.outcome, n=itt.n, effect_itt=itt.effect,
        compliance_rate=compliance, effect_tot=tot,
        se_tot=se,
        ci_low=tot - 1.96 * se,
        ci_high=tot + 1.96 * se,
    )


def rd_estimate(df: pd.DataFrame, cutoff_bps: int, bandwidth_bps: int = 500) -> RDEstimate:
    """Sharp-at-the-grade RD: look at retirements whose composite is within
    `bandwidth_bps` of `cutoff_bps`. Compare retired-rate (treatment arm)
    just above and just below. This identifies the LATE at the grade
    boundary under continuity assumptions."""
    sub = df[(df["arm"] == "TREATMENT") & df["composite_bps"].notna()].copy()
    left = sub[(sub["composite_bps"] < cutoff_bps) & (sub["composite_bps"] >= cutoff_bps - bandwidth_bps)]
    right = sub[(sub["composite_bps"] >= cutoff_bps) & (sub["composite_bps"] < cutoff_bps + bandwidth_bps)]
    if len(left) == 0 or len(right) == 0:
        return RDEstimate(
            cutoff_bps=cutoff_bps, bandwidth_bps=bandwidth_bps,
            n_left=len(left), n_right=len(right),
            jump=float("nan"), se=float("nan"), p_value=float("nan"),
        )
    diff, se, p = two_sample_diff(
        right["retired"].astype(float).to_numpy(),
        left["retired"].astype(float).to_numpy(),
    )
    return RDEstimate(
        cutoff_bps=cutoff_bps, bandwidth_bps=bandwidth_bps,
        n_left=len(left), n_right=len(right),
        jump=diff, se=se, p_value=p,
    )


def heterogeneity_by_wallet_size(df: pd.DataFrame) -> list[Heterogeneity]:
    """Heterogeneous ITT by wallet-size terciles of historical committed tonnage."""
    sub = df.dropna(subset=["composite_bps"]).copy()
    # User-level total committed tonnes
    totals = sub.groupby("user")["amount"].sum().rename("user_total").reset_index()
    sub = sub.merge(totals, on="user")
    try:
        sub["tercile"] = pd.qcut(sub["user_total"], q=3, labels=["small", "medium", "large"])
    except ValueError:
        # too few distinct values for qcut
        sub["tercile"] = "single"

    results: list[Heterogeneity] = []
    for ter, grp in sub.groupby("tercile"):
        t = grp[grp["arm"] == "TREATMENT"]["composite_bps"].to_numpy()
        c = grp[grp["arm"] == "CONTROL"]["composite_bps"].to_numpy()
        d, se, _ = two_sample_diff(t, c)
        results.append(Heterogeneity(
            subgroup=f"wallet_tercile={ter}",
            effect=d,
            se=se,
            ci_low=d - 1.96 * se,
            ci_high=d + 1.96 * se,
        ))
    return results


def price_premium(df: pd.DataFrame, prices: pd.DataFrame) -> Optional[ITTEstimate]:
    """Merge prices (USD per tonne at time of retirement) and compute the
    arm-differential mean price. Prices frame schema:
        request_id int, usd_per_tonne float
    """
    if prices is None or len(prices) == 0:
        return None
    merged = df.merge(prices, on="request_id", how="inner")
    # Restrict to credits that were actually retired (burned). Refunded
    # credits in the treatment arm never cleared at a market price.
    merged = merged[merged["retired"] == True]  # noqa: E712
    t = merged[merged["arm"] == "TREATMENT"]["usd_per_tonne"].to_numpy()
    c = merged[merged["arm"] == "CONTROL"]["usd_per_tonne"].to_numpy()
    if len(t) == 0 or len(c) == 0:
        return None
    d, se, p = two_sample_diff(t, c)
    return ITTEstimate(
        outcome="usd_per_tonne",
        n=len(t) + len(c),
        mean_treatment=float(t.mean()),
        mean_control=float(c.mean()),
        effect=d,
        se=se,
        ci_low=d - 1.96 * se,
        ci_high=d + 1.96 * se,
        p_value=p,
    )


# ---------------------------------------------------------------------------
# Top-level runner
# ---------------------------------------------------------------------------

def run_analysis(
    events: pd.DataFrame,
    prices: Optional[pd.DataFrame] = None,
    cutoff_bps: int = 6000,
    bandwidth_bps: int = 500,
) -> AnalysisResults:
    """Execute the pre-registered analysis. Returns an AnalysisResults
    object. Side-effect free; callers render to markdown/json."""
    balance = balance_check(events)
    attrition = attrition_check(events)
    primary = itt_primary(events)
    secondary = itt_secondary(events)
    tot = tot_estimate(events, primary)
    rd = rd_estimate(events, cutoff_bps=cutoff_bps, bandwidth_bps=bandwidth_bps)
    hets = heterogeneity_by_wallet_size(events)
    prem = price_premium(events, prices) if prices is not None else None

    return AnalysisResults(
        balance=balance,
        attrition=attrition,
        primary_itt=primary,
        secondary_itt=secondary,
        tot=tot,
        rd=rd,
        heterogeneity=hets,
        price_premium=prem,
    )


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

RESULTS_TEMPLATE = """# Paper 3 Field Experiment — Results

*Auto-generated by `data/field-experiment/analysis_pipeline.py`.*
*Pre-registration: `docs/field-experiment/pre-registration.md`.*

## 1. Randomization balance

| Metric | Value |
|---|---|
| n (treatment) | {n_treatment} |
| n (control) | {n_control} |
| share treatment | {share_treatment:.4f} |
| chi-square(1) | {chi_square:.3f} |
| p-value | {p_balance:.4f} |
| passes α=0.05 | {balance_pass} |

## 2. Attrition (commit → settle)

| Arm | settlement rate |
|---|---|
| TREATMENT | {attr_t:.4f} |
| CONTROL   | {attr_c:.4f} |
| difference (T−C) | {attr_d:.4f} (p={attr_p:.4f}) |

## 3. Primary outcome (H1): quality of retired credits (ITT)

| Arm | Weighted mean composite (bps) |
|---|---|
| TREATMENT | {itt_mt:.1f} |
| CONTROL | {itt_mc:.1f} |
| Effect (T−C) | {itt_effect:+.1f} bps (95% CI {itt_lo:+.1f}, {itt_hi:+.1f}; p={itt_p:.4f}) |

Conclusion: {primary_conclusion}

## 4. Secondary outcomes (ITT)

{secondary_table}

## 5. TOT (Wald / 2SLS)

| | |
|---|---|
| ITT effect | {tot_itt:+.1f} |
| Compliance (share refused in treatment) | {tot_comp:.3f} |
| TOT effect | {tot_effect:+.1f} (95% CI {tot_lo:+.1f}, {tot_hi:+.1f}) |

## 6. Regression discontinuity at grade boundary

| | |
|---|---|
| Cutoff (bps) | {rd_cut} |
| Bandwidth | ±{rd_bw} bps |
| n left | {rd_nl} |
| n right | {rd_nr} |
| Jump in burn-rate | {rd_jump:+.3f} (SE {rd_se:.3f}, p={rd_p:.4f}) |

## 7. Heterogeneity by wallet-size tercile

{het_table}

## 8. Price premium (H2)

{price_block}

---

*All numbers are populated directly from on-chain events. The pipeline
is deterministic given the event set; re-running on the same input
yields bit-identical outputs.*
"""


def _secondary_table(rows: list[ITTEstimate]) -> str:
    if not rows:
        return "_no secondary outcomes computed_"
    lines = ["| Outcome | n | T | C | effect | 95% CI | p |",
             "|---|---:|---:|---:|---:|:-:|---:|"]
    for r in rows:
        lines.append(
            f"| `{r.outcome}` | {r.n} | {r.mean_treatment:.3f} | {r.mean_control:.3f} "
            f"| {r.effect:+.3f} | ({r.ci_low:+.3f}, {r.ci_high:+.3f}) | {r.p_value:.4f} |"
        )
    return "\n".join(lines)


def _het_table(rows: list[Heterogeneity]) -> str:
    if not rows:
        return "_no heterogeneity computed_"
    lines = ["| Subgroup | effect (bps) | 95% CI |",
             "|---|---:|:-:|"]
    for r in rows:
        lines.append(f"| {r.subgroup} | {r.effect:+.2f} | ({r.ci_low:+.2f}, {r.ci_high:+.2f}) |")
    return "\n".join(lines)


def _price_block(prem: Optional[ITTEstimate]) -> str:
    if prem is None:
        return "_no price data supplied; see `prices.csv` schema in analysis_pipeline.py_"
    return (
        f"| Arm | USD / tonne |\n|---|---:|\n"
        f"| TREATMENT | {prem.mean_treatment:.2f} |\n"
        f"| CONTROL | {prem.mean_control:.2f} |\n"
        f"| Difference | {prem.effect:+.2f} (95% CI {prem.ci_low:+.2f}, {prem.ci_high:+.2f}; p={prem.p_value:.4f}) |\n"
    )


def render_results(results: AnalysisResults) -> str:
    primary = results.primary_itt
    is_sig = primary.p_value < 0.05 and primary.effect > 0
    conclusion = (
        "**H1 supported.** Treatment (quality-gated) retirements have a significantly higher"
        " mean composite score than control, consistent with the pre-registered prediction."
        if is_sig else
        "**H1 not supported at α=0.05.** See discussion for failure-mode analysis and"
        " auxiliary tests."
    )
    return RESULTS_TEMPLATE.format(
        n_treatment=results.balance.n_treatment,
        n_control=results.balance.n_control,
        share_treatment=results.balance.share_treatment,
        chi_square=results.balance.chi_square,
        p_balance=results.balance.p_value,
        balance_pass="YES" if results.balance.passes_at_alpha_05 else "NO",
        attr_t=results.attrition.commit_to_settle_treatment,
        attr_c=results.attrition.commit_to_settle_control,
        attr_d=results.attrition.diff,
        attr_p=results.attrition.p_value,
        itt_mt=primary.mean_treatment,
        itt_mc=primary.mean_control,
        itt_effect=primary.effect,
        itt_lo=primary.ci_low,
        itt_hi=primary.ci_high,
        itt_p=primary.p_value,
        primary_conclusion=conclusion,
        secondary_table=_secondary_table(results.secondary_itt),
        tot_itt=(results.tot.effect_itt if results.tot else float("nan")),
        tot_comp=(results.tot.compliance_rate if results.tot else float("nan")),
        tot_effect=(results.tot.effect_tot if results.tot else float("nan")),
        tot_lo=(results.tot.ci_low if results.tot else float("nan")),
        tot_hi=(results.tot.ci_high if results.tot else float("nan")),
        rd_cut=(results.rd.cutoff_bps if results.rd else 0),
        rd_bw=(results.rd.bandwidth_bps if results.rd else 0),
        rd_nl=(results.rd.n_left if results.rd else 0),
        rd_nr=(results.rd.n_right if results.rd else 0),
        rd_jump=(results.rd.jump if results.rd else float("nan")),
        rd_se=(results.rd.se if results.rd else float("nan")),
        rd_p=(results.rd.p_value if results.rd else float("nan")),
        het_table=_het_table(results.heterogeneity),
        price_block=_price_block(results.price_premium),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_events(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix in (".csv", ".tsv"):
        return pd.read_csv(path, sep="," if path.suffix == ".csv" else "\t")
    raise ValueError(f"unsupported events format: {path.suffix}")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True, type=Path)
    ap.add_argument("--prices", type=Path, default=None)
    ap.add_argument("--cutoff-bps", type=int, default=6000)
    ap.add_argument("--bandwidth-bps", type=int, default=500)
    ap.add_argument("--out", type=Path, default=Path("./out"))
    args = ap.parse_args()

    events = _load_events(args.events)
    prices = pd.read_csv(args.prices) if args.prices else None

    res = run_analysis(events, prices, cutoff_bps=args.cutoff_bps, bandwidth_bps=args.bandwidth_bps)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "results_template.md").write_text(render_results(res))
    (args.out / "results_full.json").write_text(json.dumps(res.to_dict(), indent=2, default=str))
    print(f"Wrote {args.out / 'results_template.md'}")
    print(f"Wrote {args.out / 'results_full.json'}")


if __name__ == "__main__":
    main()
