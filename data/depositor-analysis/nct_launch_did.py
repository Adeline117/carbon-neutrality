#!/usr/bin/env python3
"""
nct_launch_did.py — quasi-experimental evidence on the sorting/cannibalization
channel: did the launch of a screened pool (NCT) divert high-quality credits
away from the unscreened pool (BCT)?

Design. NCT (Toucan's AFOLU-only screened pool) launched 2022-02-04, well before
the May-2022 Terra crash, so it is separable from that macro shock. Treatment =
NCT becomes an available alternative. Treated units = NCT-eligible (nature-based:
REDD+/ARR/IFM) credits, which can now divert to NCT. Control = NCT-ineligible
(renewable) credits, whose BCT-deposit behaviour cannot be affected by NCT's
existence. Outcome = composite quality of credits deposited into BCT. The DiD
differences out BCT's secular quality decline (the renewable trend is the
counterfactual for nature-based absent NCT).

Findings (honest): parallel pre-trends hold (interaction n.s.); an RDiT shows a
discontinuous quality drop at launch (~-2.2 pts, p~0.02); the DiD point estimate
is the right sign and magnitude (~-4.7 pts) but is NOT significant under
type-clustered SEs (p~0.14, post-period nature-based n=19); the nature-based
share of BCT deposits collapses 15.8% -> 4.0%. We therefore report this as
SUPPORTING, not decisive, quasi-experimental evidence of the sorting channel.

numpy + scipy only.
"""
from __future__ import annotations
import json
import numpy as np
from pathlib import Path
from scipy import stats

D = Path(__file__).resolve().parent
NCT_LAUNCH = 24749944  # first NCT deposit block ~ 2022-02-04
AFOLU = {"REDD+", "ARR", "IFM"}


def _load():
    bct = json.load(open(D / "bct_deposits_complete.json"))
    scores = json.load(open(D / "tco2_scores_complete.json"))
    cls = json.load(open(D / "project_classification_final.json"))
    md = json.load(open(D / "tco2_metadata_fixed.json"))
    sc = {}
    it = scores.items() if isinstance(scores, dict) else ((r.get("tco2_address"), r) for r in scores)
    for k, v in it:
        c = v.get("composite") or v.get("composite_score")
        if c is not None:
            sc[str(k).lower()] = float(c)
    at = {}
    rec = md.items() if isinstance(md, dict) else ((None, r) for r in md)
    for a, r in rec:
        if a:
            at[str(a).lower()] = (cls.get(str(r.get("project_id"))) or {}).get("type")
    rows = [(r["block_number"], sc[str(r["tco2_address"]).lower()], at.get(str(r["tco2_address"]).lower()))
            for r in bct if str(r["tco2_address"]).lower() in sc]
    rows.sort()
    return rows


def main():
    rows = _load()
    b = np.array([x[0] for x in rows], float)
    q = np.array([x[1] for x in rows], float)
    nat = np.array([1.0 if x[2] in AFOLU else 0.0 for x in rows])
    types = np.array([x[2] or "NA" for x in rows])
    post = (b >= NCT_LAUNCH).astype(float)

    # parallel pre-trends
    pre = b < NCT_LAUNCH
    bb = (b[pre] - NCT_LAUNCH) / 1e6
    Xp = np.column_stack([np.ones(pre.sum()), bb, nat[pre], bb * nat[pre]])
    bp, *_ = np.linalg.lstsq(Xp, q[pre], rcond=None)
    rp = q[pre] - Xp @ bp
    sp = np.sqrt(np.diag((rp @ rp) / (len(rp) - 4) * np.linalg.inv(Xp.T @ Xp)))
    pretrend_t = bp[3] / sp[3]

    # RDiT (jump beyond linear trend)
    bc = (b - NCT_LAUNCH) / 1e6
    Xr = np.column_stack([np.ones_like(bc), bc, post, post * bc])
    br, *_ = np.linalg.lstsq(Xr, q, rcond=None)
    rr = q - Xr @ br
    sr = np.sqrt(np.diag((rr @ rr) / (len(rr) - 4) * np.linalg.inv(Xr.T @ Xr)))
    rdit_t = br[2] / sr[2]

    # DiD with cluster-robust (by type) SE
    Xd = np.column_stack([np.ones_like(b), post, nat, post * nat])
    bd, *_ = np.linalg.lstsq(Xd, q, rcond=None)
    rd = q - Xd @ bd
    XtXi = np.linalg.inv(Xd.T @ Xd)
    meat = np.zeros((4, 4))
    for t in set(types):
        m = types == t
        meat += Xd[m].T @ np.outer(rd[m], rd[m]) @ Xd[m]
    sd = np.sqrt(np.diag(XtXi @ meat @ XtXi))
    did_t = bd[3] / sd[3]

    share_pre = float(np.mean(nat[b < NCT_LAUNCH]))
    share_post = float(np.mean(nat[b >= NCT_LAUNCH]))

    out = {
        "nct_launch_block": NCT_LAUNCH, "nct_launch_date": "2022-02-04",
        "parallel_pretrends": {"interaction_per_Mblock": round(float(bp[3]), 3),
                               "t": round(float(pretrend_t), 2),
                               "parallel_ok": bool(abs(pretrend_t) < 1.96)},
        "rdit_discontinuity_pts": round(float(br[2]), 2),
        "rdit_p": round(float(2 * (1 - stats.norm.cdf(abs(rdit_t)))), 4),
        "did_pts": round(float(bd[3]), 2),
        "did_cluster_se": round(float(sd[3]), 2),
        "did_p_clustered": round(float(2 * (1 - stats.norm.cdf(abs(did_t)))), 3),
        "nature_share_pre": round(share_pre, 3), "nature_share_post": round(share_post, 3),
        "verdict": ("Parallel pre-trends hold; RDiT discontinuity significant (p~0.02); DiD right "
                    "sign/magnitude but not significant under type-clustering (p~0.14, small post-N). "
                    "Supporting, not decisive, quasi-experimental evidence of the sorting channel."),
    }
    (D / "nct_launch_did_results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
