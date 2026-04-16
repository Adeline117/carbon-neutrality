#!/usr/bin/env python3
"""Counterfactual QRX replay over the 1,187 Toucan BCT deposits.

Question
--------
If BCT had required the QRX bond schedule, how many deposits would have been
deterred or downgraded — and what would aggregate pool quality have looked like?

Data sources
------------
  - data/depositor-analysis/bct_deposits_complete.json
      [{"tco2_address": ..., "amount_tonnes": ...}, ...]
      One row per deposit. 1,187 rows.
  - data/depositor-analysis/tco2_scores_final.json
      {tco2_address: {"composite": float, "grade": str, "type": str, "vintage": int}}
      Per-credit true quality (composite 0-100 and letter grade).

Reference QRX parameters (matches contracts/test/QRX.t.sol):
  bondRatePerTonne (USDC / tonne):
    B=1, BB=2, BBB=4, A=7, AA=10, AAA=15
  slash(bond, claimed, true) = bond * max(0, rank(claimed)-rank(true)) / 5

Counterfactual strategy assumptions
-----------------------------------
Under QRX, a depositor chooses (claimedGrade, bond) to maximise
    E[payoff] = a * (WTP(claimed) - cost) - p * slash(bond, claimed, true)
where:
  a         = tonnage,
  WTP(g)    = buyer willingness-to-pay per tonne at claimed grade g,
  cost      = depositor's reservation price per tonne,
  p         = probability the claim is challenged and the true grade revealed,
  bond      = BONDS[claimed] * a (depositors post the minimum).

We model two depositor strategies for each of the 1,187 deposits:

  (1) TRUTHFUL:    claim = trueGrade   → zero slash expectation.
  (2) OPTIMISTIC:  claim = AAA, regardless of trueGrade → maximum surplus but
                   maximum slash.

For each deposit we compute:
  - TruthBondCost      = BONDS[trueGrade] * amount_tonnes
  - OvercClaimBond     = BONDS[AAA] * amount_tonnes
  - ExpectedSlash(p)   = p * slash(OvercClaimBond, AAA, trueGrade)
  - NetOvercVsTruth(p) = (WTP_gap - cost_difference) * amount_tonnes - ExpectedSlash

Under plausible WTP assumptions (derived from spot pricing gaps between BCT
and premium pools like Puro.earth — ~$50/tonne premium for AAA vs <$1 for B),
the overclaim expected payoff is negative at any detection probability
p > p*, where p* = (WTP_gap × amount) / slash. We report p* per deposit and
count how many deposits are deterred given p = 5% (a conservative MRV scan
rate).

We also report:
  - Deposits downgraded: number where trueGrade != AAA (deterred AAA claim).
  - Aggregate tonnage by claimed grade under (a) full truthful equilibrium
    and (b) naive pooling (all claim AAA, bond slashed).
  - Expected slash revenue the treasury / challengers would collect under
    naive pooling, as a % of total BCT turnover.

Usage
-----
  python3 data/qrx/counterfactual_replay.py
  python3 data/qrx/counterfactual_replay.py --detection-prob 0.1 --wtp-gap 30

Outputs
-------
  data/qrx/counterfactual_replay_results.json
  stdout: summary table
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

# ---------------------------------------------------------------------------
# Repository layout (resolved relative to this file)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPOSITS_PATH = REPO_ROOT / "data" / "depositor-analysis" / "bct_deposits_complete.json"
SCORES_PATH = REPO_ROOT / "data" / "depositor-analysis" / "tco2_scores_final.json"
OUT_PATH = REPO_ROOT / "data" / "qrx" / "counterfactual_replay_results.json"

# ---------------------------------------------------------------------------
# QRX parameters (must match contracts/test/QRX.t.sol rates)
# ---------------------------------------------------------------------------

GRADES = ["B", "BB", "BBB", "A", "AA", "AAA"]
GRADE_RANK = {g: i for i, g in enumerate(GRADES)}

# Bond rate per tonne (USDC) — see contracts/test/QRX.t.sol RATE_*.
BONDS = {
    "B": 1.0,
    "BB": 2.0,
    "BBB": 4.0,
    "A": 7.0,
    "AA": 10.0,
    "AAA": 15.0,
}


def slash(bond: float, claimed: str, true_grade: str) -> float:
    """Linear slash schedule: bond * max(0, rank(claimed) - rank(true)) / 5."""
    gap = max(0, GRADE_RANK[claimed] - GRADE_RANK[true_grade])
    return bond * gap / 5.0


# ---------------------------------------------------------------------------
# Core counterfactual
# ---------------------------------------------------------------------------


def run_counterfactual(
    detection_prob: float, wtp_gap_aaa_vs_b: float, bond_scale: float = 1.0
) -> dict:
    """Replay the 1,187 BCT deposits under a QRX bond regime.

    Parameters
    ----------
    detection_prob : float
        Assumed probability that any given overclaimed deposit is challenged
        and resolved against the claimant. 0.05 is the conservative default;
        higher values strengthen deterrence.
    wtp_gap_aaa_vs_b : float
        USD per tonne gap between buyer WTP at each adjacent claimed grade.
        Observed spot spreads: BCT at ~$0.50/t vs Puro.earth at ~$100-200/t
        imply a ~$40/t gap between adjacent grades for a linear schedule.
        We use $50/t as the default; so AAA vs B surplus is 5 * wtp_gap.
    bond_scale : float
        Multiplicative scale on the reference BONDS schedule. The reference
        schedule {B:1..AAA:15}/t is illustrative; calibrating QRX to actual
        BCT economics requires bond_scale * RATE_AAA >= wtp_gap * 5 / p
        (i.e. expected slash exceeds WTP surplus). Default 1.0 reproduces
        the on-chain reference rates.
    """
    with open(DEPOSITS_PATH) as f:
        deposits = json.load(f)
    with open(SCORES_PATH) as f:
        scores = json.load(f)

    scaled_bonds = {g: BONDS[g] * bond_scale for g in GRADES}
    per_grade_wtp = {g: i * wtp_gap_aaa_vs_b for i, g in enumerate(GRADES)}

    results = {
        "parameters": {
            "detection_prob": detection_prob,
            "wtp_gap_per_adjacent_grade_usd": wtp_gap_aaa_vs_b,
            "bond_scale": bond_scale,
            "bond_rate_per_tonne": scaled_bonds,
        },
        "n_deposits_total": len(deposits),
        "n_deposits_with_score": 0,
        "n_deposits_missing_score": 0,
        "per_deposit": [],
    }

    # Aggregates.
    total_tonnes = 0.0
    tonnes_by_true_grade: dict[str, float] = defaultdict(float)
    truthful_bond_cost_total = 0.0
    overclaim_bond_total = 0.0
    expected_slash_total = 0.0
    deterred_deposits = 0
    downgraded_tonnes_if_truthful = 0.0  # tonnes where trueGrade != AAA
    deterred_tonnes = 0.0
    truthful_net_payoff_total = 0.0

    per_grade_tonnes_truthful: dict[str, float] = defaultdict(float)

    for d in deposits:
        addr = d["tco2_address"]
        amt = float(d["amount_tonnes"])
        total_tonnes += amt

        meta = scores.get(addr)
        if meta is None:
            results["n_deposits_missing_score"] += 1
            continue
        results["n_deposits_with_score"] += 1

        true_grade = meta["grade"]
        tonnes_by_true_grade[true_grade] += amt

        # Strategy 1: TRUTHFUL.
        truth_bond = scaled_bonds[true_grade] * amt
        truth_wtp = per_grade_wtp[true_grade] * amt
        truthful_bond_cost_total += truth_bond
        truthful_net_payoff_total += truth_wtp  # bond returned in full
        per_grade_tonnes_truthful[true_grade] += amt

        # Strategy 2: OVERCLAIM (always AAA).
        overc_bond = scaled_bonds["AAA"] * amt
        overc_slash = slash(overc_bond, "AAA", true_grade)
        overc_expected_slash = detection_prob * overc_slash
        overc_wtp = per_grade_wtp["AAA"] * amt
        overc_net_payoff = overc_wtp - overc_expected_slash

        overclaim_bond_total += overc_bond
        expected_slash_total += overc_expected_slash

        # Detection-probability threshold above which overclaim is strictly
        # dominated by truthful reporting:
        #   p* = (WTP(AAA) - WTP(true)) * amt / slash
        wtp_gap = (per_grade_wtp["AAA"] - per_grade_wtp[true_grade]) * amt
        p_star = (wtp_gap / overc_slash) if overc_slash > 0 else float("inf")

        deterred_here = overc_net_payoff < truth_wtp  # truthful dominates
        if deterred_here:
            deterred_deposits += 1
            deterred_tonnes += amt
        if true_grade != "AAA":
            downgraded_tonnes_if_truthful += amt

        results["per_deposit"].append(
            {
                "tco2_address": addr,
                "amount_tonnes": amt,
                "true_grade": true_grade,
                "truth_bond_cost": truth_bond,
                "overclaim_bond_cost": overc_bond,
                "overclaim_slash_if_detected": overc_slash,
                "overclaim_expected_slash": overc_expected_slash,
                "truthful_wtp": truth_wtp,
                "overclaim_wtp": overc_wtp,
                "overclaim_net_payoff": overc_net_payoff,
                "truthful_dominates": deterred_here,
                "p_star_detection_threshold": p_star,
            }
        )

    # Summary block.
    matched_tonnes = sum(tonnes_by_true_grade.values())
    results["summary"] = {
        "total_tonnes_deposited": total_tonnes,
        "total_tonnes_with_known_grade": matched_tonnes,
        "tonnes_by_true_grade": dict(tonnes_by_true_grade),
        "pct_tonnes_by_true_grade": {
            g: (tonnes_by_true_grade[g] / matched_tonnes * 100.0)
            if matched_tonnes > 0
            else 0.0
            for g in GRADES
        },
        "truthful_total_bond_locked": truthful_bond_cost_total,
        "overclaim_total_bond_locked": overclaim_bond_total,
        "bond_overhead_ratio_overclaim_vs_truth": (
            overclaim_bond_total / truthful_bond_cost_total
            if truthful_bond_cost_total > 0
            else float("inf")
        ),
        "expected_slash_revenue_at_p": expected_slash_total,
        "expected_slash_as_pct_of_pool_turnover_at_50usd": (
            expected_slash_total / (matched_tonnes * 50.0) * 100.0
            if matched_tonnes > 0
            else 0.0
        ),
        "n_deposits_overclaim_deterred": deterred_deposits,
        "pct_deposits_deterred": (
            deterred_deposits / results["n_deposits_with_score"] * 100.0
            if results["n_deposits_with_score"] > 0
            else 0.0
        ),
        "tonnes_overclaim_deterred": deterred_tonnes,
        "pct_tonnes_deterred": (
            deterred_tonnes / matched_tonnes * 100.0 if matched_tonnes > 0 else 0.0
        ),
        "tonnes_downgraded_vs_aaa_under_truthful": downgraded_tonnes_if_truthful,
        "pct_tonnes_downgraded_vs_aaa_under_truthful": (
            downgraded_tonnes_if_truthful / matched_tonnes * 100.0
            if matched_tonnes > 0
            else 0.0
        ),
        "per_grade_tonnes_truthful_equilibrium": dict(per_grade_tonnes_truthful),
    }

    # Per-grade p_star averages (diagnostic).
    per_grade_p_star: dict[str, list[float]] = defaultdict(list)
    for r in results["per_deposit"]:
        if r["overclaim_slash_if_detected"] > 0:
            per_grade_p_star[r["true_grade"]].append(r["p_star_detection_threshold"])
    results["summary"]["mean_p_star_by_true_grade"] = {
        g: (mean(per_grade_p_star[g]) if per_grade_p_star[g] else None) for g in GRADES
    }

    return results


def print_summary(results: dict) -> None:
    s = results["summary"]
    p = results["parameters"]
    print("=" * 78)
    print("QRX Counterfactual Replay — Toucan BCT 1,187 Deposits")
    print("=" * 78)
    print()
    print(f"Assumptions:")
    print(f"  detection_prob p            = {p['detection_prob']:.3f}")
    print(f"  WTP gap per grade           = ${p['wtp_gap_per_adjacent_grade_usd']:.2f}/t")
    print(f"  bond schedule (USDC/t)      = {p['bond_rate_per_tonne']}")
    print()
    print(f"Deposit coverage:")
    print(f"  total deposits              = {results['n_deposits_total']}")
    print(f"  with known tCO2 grade       = {results['n_deposits_with_score']}")
    print(f"  missing score metadata      = {results['n_deposits_missing_score']}")
    print(f"  total tonnes                = {s['total_tonnes_deposited']:,.0f}")
    print(f"  tonnes with known grade     = {s['total_tonnes_with_known_grade']:,.0f}")
    print()
    print("Tonnes by true grade:")
    for g in GRADES:
        t = s["tonnes_by_true_grade"].get(g, 0)
        pct = s["pct_tonnes_by_true_grade"].get(g, 0)
        print(f"  {g:>4s}                       {t:>14,.0f}  ({pct:5.1f}%)")
    print()
    print("Bond economics:")
    print(f"  truthful bond locked (total) = ${s['truthful_total_bond_locked']:,.0f}")
    print(f"  overclaim bond locked        = ${s['overclaim_total_bond_locked']:,.0f}")
    print(f"  overhead ratio (oc/tr)       = {s['bond_overhead_ratio_overclaim_vs_truth']:.2f}x")
    print(f"  expected slash at p={p['detection_prob']:.0%}       = ${s['expected_slash_revenue_at_p']:,.0f}")
    print()
    print("Mechanism effectiveness:")
    print(f"  deposits where truthful dominates overclaim")
    print(
        f"      n                       = {s['n_deposits_overclaim_deterred']:>6} "
        f"({s['pct_deposits_deterred']:.1f}%)"
    )
    print(
        f"      tonnes                  = {s['tonnes_overclaim_deterred']:>14,.0f} "
        f"({s['pct_tonnes_deterred']:.1f}%)"
    )
    print()
    print("Claimed-grade distribution under truthful equilibrium:")
    per_grade_tr = s["per_grade_tonnes_truthful_equilibrium"]
    matched = s["total_tonnes_with_known_grade"]
    for g in GRADES:
        t = per_grade_tr.get(g, 0)
        pct = (t / matched * 100.0) if matched > 0 else 0.0
        print(f"  claim={g:<4s}                  {t:>14,.0f}  ({pct:5.1f}%)")
    print()
    print("Interpretation:")
    if s["pct_tonnes_deterred"] >= 95.0:
        print(
            "  At these parameters, QRX deters overclaim on >95% of tonnage.\n"
            "  The BCT pool would compress to a genuine mixture of claimed grades\n"
            "  that matches the underlying distribution — i.e. no AAA-dominant\n"
            "  pooling equilibrium."
        )
    elif s["pct_tonnes_deterred"] >= 50.0:
        print(
            "  QRX deters overclaim on the majority of tonnage but residual\n"
            "  pooling remains. Raising the bond schedule or detection rate would\n"
            "  close the gap."
        )
    else:
        print(
            "  At these parameters, QRX underprices quality misrepresentation.\n"
            "  Recommendation: raise AAA bond rate or detection probability."
        )


def run_sweep(wtp_gap: float, out_dir: Path) -> None:
    """Grid-sweep (bond_scale, detection_prob) to find the deterrence frontier.

    Reports a 2-D table of pct_tonnes_deterred. A cell is 100% when truthful
    reporting weakly dominates overclaim for every deposit.
    """
    bond_scales = [1, 2, 5, 10, 20, 50, 100, 200]
    detection_probs = [0.01, 0.05, 0.10, 0.25, 0.50, 1.00]

    print("Deterrence frontier — pct of tonnage where truthful dominates overclaim")
    print(f"  WTP gap per grade: ${wtp_gap:.0f}/t")
    print()
    header = "  bond_scale \\ p  | " + " ".join(f"{p:>6.2%}" for p in detection_probs)
    print(header)
    print("  " + "-" * (len(header) - 2))

    rows = []
    for scale in bond_scales:
        row = f"  {scale:>6.1f}x         | "
        cells = []
        for p in detection_probs:
            r = run_counterfactual(p, wtp_gap, bond_scale=scale)
            pct = r["summary"]["pct_tonnes_deterred"]
            cells.append(pct)
            row += f"{pct:>5.1f}% "
        rows.append({"bond_scale": scale, "detection_probs": detection_probs, "pct_deterred": cells})
        print(row)

    out_path = out_dir / "counterfactual_sweep.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(
            {
                "wtp_gap_per_adjacent_grade_usd": wtp_gap,
                "bond_schedule_base_usd_per_tonne": BONDS,
                "rows": rows,
            },
            f,
            indent=2,
        )
    print()
    print(f"Wrote {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument(
        "--detection-prob",
        type=float,
        default=0.05,
        help="Assumed probability an overclaimed deposit is challenged (default 0.05).",
    )
    ap.add_argument(
        "--wtp-gap",
        type=float,
        default=50.0,
        help="USD per tonne WTP gap between adjacent claimed grades (default $50).",
    )
    ap.add_argument(
        "--bond-scale",
        type=float,
        default=1.0,
        help="Multiplicative scale on the reference bond schedule (default 1.0).",
    )
    ap.add_argument(
        "--out",
        type=str,
        default=str(OUT_PATH),
        help=f"Output JSON path (default {OUT_PATH}).",
    )
    ap.add_argument(
        "--sweep",
        action="store_true",
        help="Sweep (bond_scale, detection_prob) to locate the deterrence frontier.",
    )
    args = ap.parse_args()

    if args.sweep:
        run_sweep(args.wtp_gap, Path(args.out).parent)
        return

    results = run_counterfactual(args.detection_prob, args.wtp_gap, args.bond_scale)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Trim per-deposit detail from the JSON to keep file size reasonable; keep
    # summary as the primary artefact.
    compact = {
        "parameters": results["parameters"],
        "n_deposits_total": results["n_deposits_total"],
        "n_deposits_with_score": results["n_deposits_with_score"],
        "n_deposits_missing_score": results["n_deposits_missing_score"],
        "summary": results["summary"],
        "per_deposit_sample": results["per_deposit"][:20],
    }
    with open(out_path, "w") as f:
        json.dump(compact, f, indent=2)

    print_summary(results)
    print()
    print(f"Wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
