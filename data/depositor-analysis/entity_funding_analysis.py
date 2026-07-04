#!/usr/bin/env python3
"""Entity-level independence check for the dual-margin claim.

Tests whether the top BCT deposit accounts and top redemption accounts are
plausibly independently controlled entities, via a first-funder analysis:
for each EOA, fetch its earliest incoming native-MATIC transaction and record
the funder. Cross-side common funders (excluding likely exchange/disperser
addresses) or direct transfers between the two sides would indicate entity
overlap; their absence is evidence (not proof) of independence.

Stages:
  1. nodes    -- build the top-20 deposit and top-20 redemption account lists
                 (local data only: klima_overlap_results.json + transfer_cache/)
  2. code     -- classify each account EOA vs contract (eth_getCode, public RPC)
  3. direct   -- check direct TCO2 transfers between the two sides (local cache)
  4. funders  -- fetch each EOA's first incoming native tx (Etherscan v2 API,
                 needs ETHERSCAN_API_KEY in env; chainid=137)
  5. verdict  -- cross-side common-funder analysis with exchange discounting

Usage:
  python3 entity_funding_analysis.py --stage nodes,code,direct   # keyless
  ETHERSCAN_API_KEY=... python3 entity_funding_analysis.py --stage funders,verdict
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "entity_funding_analysis.json"
CACHE_DIR = HERE / "transfer_cache"
BCT_POOL = "0x2f800db0fdb5223b3c3f354886d907a671414a7f"
RPCS = ["https://polygon-bor-rpc.publicnode.com", "https://polygon-rpc.com",
        "https://polygon.drpc.org"]
ETHERSCAN_V2 = "https://api.etherscan.io/v2/api"
TOP_N = 20
# A funder that funds >= this many analyzed wallets is tagged a likely
# exchange / disperser; shared exchange funding is NOT same-entity evidence.
EXCHANGE_FANOUT_THRESHOLD = 3


def load_state():
    if OUT.exists():
        return json.loads(OUT.read_text())
    return {
        "method": {
            "nodes": "top-20 depositors (klima_overlap_results.json) + top-20 redeemers "
                     "aggregated from transfer_cache pool->wallet TCO2 logs",
            "code_check": f"eth_getCode @ {RPCS[0]} (fallbacks: {RPCS[1:]})",
            "direct_transfers": "TCO2 ERC-20 transfers between the two account sets, from transfer_cache",
            "first_funder": "earliest incoming native-MATIC tx per EOA, Etherscan v2 (chainid=137)",
            "exchange_rule": f"funder of >= {EXCHANGE_FANOUT_THRESHOLD} analyzed wallets tagged "
                             "likely-exchange/disperser; common exchange funding treated as inconclusive, "
                             "not as same-entity evidence",
        },
        "accounts": {},
        "direct_transfers": None,
        "verdict": None,
    }


def save_state(state):
    OUT.write_text(json.dumps(state, indent=2))
    print(f"  saved -> {OUT.name}")


# ---------------------------------------------------------------- stage: nodes

def stage_nodes(state):
    print("[nodes] top-20 depositors from klima_overlap_results.json")
    overlap = json.loads((HERE / "klima_overlap_results.json").read_text())
    for rec in overlap["top_20_depositors_all_time"][:TOP_N]:
        addr = rec["depositor"].lower()
        acct = state["accounts"].setdefault(addr, {})
        acct.update({"side": acct.get("side", "deposit"), "deposit_tonnes": rec["tonnes"],
                     "deposit_count": rec["count"]})
        if acct["side"] == "redeem":
            acct["side"] = "both"

    print("[nodes] aggregating redemptions (pool->wallet) from transfer_cache/")
    redeemed = defaultdict(float)
    n_events = 0
    for f in sorted(CACHE_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        for ev in data.get("events", []):
            if ev["from"].lower() == BCT_POOL:
                redeemed[ev["to"].lower()] += int(ev["value_wei"]) / 1e18
                n_events += 1
    print(f"  {n_events} pool->wallet transfer events, {len(redeemed)} distinct redeemer addresses")
    top_redeemers = sorted(redeemed.items(), key=lambda kv: -kv[1])[:TOP_N]
    for addr, tonnes in top_redeemers:
        acct = state["accounts"].setdefault(addr, {})
        prev_side = acct.get("side")
        acct["redeem_tonnes"] = round(tonnes, 1)
        acct["side"] = "both" if prev_side == "deposit" else "redeem"

    sides = defaultdict(int)
    for a in state["accounts"].values():
        sides[a["side"]] += 1
    print(f"  accounts: {dict(sides)}")

    # merge prior EOA/contract verdicts for the known top-5 redeemers
    known = json.loads((HERE / "redeemer_contract_check.json").read_text())["results"]
    for addr, rec in known.items():
        a = state["accounts"].get(addr.lower())
        if a is not None:
            a["is_contract"] = rec["is_contract"]
            a["desc"] = rec.get("desc")


# ----------------------------------------------------------------- stage: code

def rpc_call(method, params):
    last_err = None
    for rpc in RPCS:
        try:
            req = urllib.request.Request(
                rpc, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                                      "params": params}).encode(),
                headers={"Content-Type": "application/json",
                         "User-Agent": "carbon-neutrality-research/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())["result"]
        except Exception as e:  # try next endpoint
            last_err = e
    raise last_err


def stage_code(state):
    todo = [a for a, rec in state["accounts"].items() if "is_contract" not in rec]
    print(f"[code] eth_getCode for {len(todo)} addresses")
    for addr in todo:
        code = rpc_call("eth_getCode", [addr, "latest"])
        state["accounts"][addr]["is_contract"] = len(code) > 2
        time.sleep(0.25)
    n_contract = sum(1 for r in state["accounts"].values() if r["is_contract"])
    print(f"  contracts: {n_contract} / {len(state['accounts'])}")


# --------------------------------------------------------------- stage: direct

def stage_direct(state):
    """Direct TCO2 transfers between deposit-side and redemption-side accounts."""
    dep = {a for a, r in state["accounts"].items() if r["side"] in ("deposit", "both")}
    red = {a for a, r in state["accounts"].items() if r["side"] in ("redeem", "both")}
    hits = []
    for f in sorted(CACHE_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        for ev in data.get("events", []):
            frm, to = ev["from"].lower(), ev["to"].lower()
            if (frm in dep and to in red) or (frm in red and to in dep):
                if frm != to and BCT_POOL not in (frm, to):
                    hits.append({"tco2": data.get("tco2"), "from": frm, "to": to,
                                 "tonnes": round(int(ev["value_wei"]) / 1e18, 1),
                                 "tx_hash": ev["tx_hash"]})
    state["direct_transfers"] = {"n": len(hits), "transfers": hits}
    print(f"[direct] cross-side TCO2 transfers: {len(hits)}")


# -------------------------------------------------------------- stage: funders

def etherscan_txlist(addr, key, action="txlist"):
    q = urllib.parse.urlencode({
        "chainid": 137, "module": "account", "action": action, "address": addr,
        "startblock": 0, "endblock": 99999999, "page": 1, "offset": 50,
        "sort": "asc", "apikey": key})
    with urllib.request.urlopen(f"{ETHERSCAN_V2}?{q}", timeout=30) as r:
        resp = json.loads(r.read())
    if resp.get("status") == "0" and resp.get("message") not in ("No transactions found",):
        raise RuntimeError(f"etherscan error for {addr}: {resp.get('result')}")
    return resp.get("result") or []


def stage_funders(state):
    key = os.environ.get("ETHERSCAN_API_KEY")
    if not key:
        sys.exit("[funders] ETHERSCAN_API_KEY not set -- aborting (stage requires explorer API)")
    eoas = [a for a, r in state["accounts"].items()
            if not r.get("is_contract") and r.get("first_funder") is None]
    print(f"[funders] first incoming native tx for {len(eoas)} EOAs")
    for addr in eoas:
        txs = etherscan_txlist(addr, key)
        rec = state["accounts"][addr]
        first_in = next((t for t in txs
                         if t.get("to", "").lower() == addr and int(t.get("value", "0")) > 0
                         and t.get("isError", "0") == "0"), None)
        if first_in is None:
            # funded via internal tx (contract-mediated, e.g. exchange withdrawal
            # routers or bridges) -- resolve through txlistinternal instead
            time.sleep(0.25)
            itxs = etherscan_txlist(addr, key, action="txlistinternal")
            first_int = next((t for t in itxs
                              if t.get("to", "").lower() == addr and int(t.get("value", "0")) > 0
                              and t.get("isError", "0") == "0"), None)
            rec.pop("earliest_counterparty", None)
            rec.pop("earliest_ts", None)
            if first_int is not None:
                rec["first_funder"] = first_int["from"].lower()
                rec["first_funder_ts"] = first_int["timeStamp"]
                rec["first_funder_matic"] = round(int(first_int["value"]) / 1e18, 4)
                rec["first_funder_via"] = "internal-tx (contract-mediated)"
            else:
                rec["first_funder"] = None
                rec["first_funder_note"] = "no native incoming tx found in plain or internal lists"
        else:
            rec["first_funder"] = first_in["from"].lower()
            rec["first_funder_ts"] = first_in["timeStamp"]
            rec["first_funder_matic"] = round(int(first_in["value"]) / 1e18, 4)
        print(f"  {addr[:10]}... funder={rec.get('first_funder')}")
        time.sleep(0.25)  # free tier 5 req/s; stay well under


# -------------------------------------------------------------- stage: verdict

def stage_verdict(state):
    accounts = state["accounts"]
    fanout = defaultdict(list)
    for addr, rec in accounts.items():
        f = rec.get("first_funder") or rec.get("earliest_counterparty")
        if f:
            fanout[f].append(addr)

    exchanges = {f for f, kids in fanout.items() if len(kids) >= EXCHANGE_FANOUT_THRESHOLD}
    for f in exchanges:
        for kid in fanout[f]:
            accounts[kid]["funder_tag"] = "likely-exchange/disperser"

    common = []
    for f, kids in fanout.items():
        sides = {accounts[k]["side"] for k in kids}
        if len(kids) > 1 and ({"deposit", "redeem"} <= sides or "both" in sides or len(sides) > 1):
            common.append({"funder": f, "wallets": kids,
                           "sides": sorted(sides),
                           "likely_exchange": f in exchanges})

    n_eoa = sum(1 for r in accounts.values() if not r.get("is_contract"))
    n_resolved = sum(1 for r in accounts.values()
                     if not r.get("is_contract") and (r.get("first_funder") or r.get("earliest_counterparty")))
    non_exchange_common = [c for c in common if not c["likely_exchange"]]
    direct_n = (state.get("direct_transfers") or {}).get("n", 0)

    if non_exchange_common or direct_n:
        outcome = "overlap-found"
    elif n_resolved < n_eoa * 0.6:
        outcome = "inconclusive-low-coverage"
    elif any(c["likely_exchange"] for c in common):
        outcome = "no-direct-links; shared funders are exchange-level only (inconclusive on entity identity)"
    else:
        outcome = "no-common-funders-no-direct-links"

    state["verdict"] = {
        "eoas_analyzed": n_eoa,
        "eoas_with_resolved_funder": n_resolved,
        "cross_side_common_funders": common,
        "non_exchange_common_funders": non_exchange_common,
        "direct_cross_side_transfers": direct_n,
        "likely_exchange_funders": sorted(exchanges),
        "outcome": outcome,
    }
    print(f"[verdict] {outcome}")
    print(json.dumps(state["verdict"], indent=2)[:1200])


STAGES = {"nodes": stage_nodes, "code": stage_code, "direct": stage_direct,
          "funders": stage_funders, "verdict": stage_verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="nodes,code,direct",
                    help=f"comma list from {list(STAGES)}")
    args = ap.parse_args()
    state = load_state()
    for name in args.stage.split(","):
        STAGES[name.strip()](state)
        save_state(state)


if __name__ == "__main__":
    main()
