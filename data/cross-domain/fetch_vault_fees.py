#!/usr/bin/env python3
"""fetch_vault_fees.py -- read NFTX vault fee schedules via on-chain view calls.

Reads mintFee/randomRedeemFee/targetRedeemFee for the six analysed vaults and
writes nftx_vault_fees.json. Values are current at call time; historical fee
schedules may have differed (fees are owner-settable). Env: ALCHEMY_API_KEY.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

KEY = os.environ.get("ALCHEMY_API_KEY") or sys.exit("set ALCHEMY_API_KEY")
RPC = f"https://eth-mainnet.g.alchemy.com/v2/{KEY}"
SELECTORS = {"mintFee": "0x13966db5", "randomRedeemFee": "0xf7fce334",
             "targetRedeemFee": "0xfeb8eba5"}
VAULTS = {
    "MILADY": "0x227c7df69d3ed1ae7574a1a7685fded90292eb48",
    "PHUNK": "0xb39185e33e8c28e0bb3dbbce24da5dea6379ae91",
    "WIZARD": "0x87931e7ad81914e7898d07c68f145fc0a553d8fb",
    "MEEB": "0x641927e970222b10b2e8cdbc96b1b4f427316f16",
    "MANA": "0x2d77f5b3efa51821ad6483adaf38ea4cb1824cc5",
    "BGAN": "0xc3b5284b2c0cfa1871a6ac63b6d6ee43c08bdc79",
}


def call(to, data):
    req = urllib.request.Request(RPC, data=json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"]}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return int(json.loads(r.read())["result"], 16)


def main():
    out = {"note": "fees in percent of one vault token; current values (owner-settable), "
                   "read at run time via eth_call", "vaults": {}}
    for sym, addr in VAULTS.items():
        fees = {name: call(addr, sel) / 1e16 for name, sel in SELECTORS.items()}
        fees["exit_selection_priced"] = fees["targetRedeemFee"] > fees["randomRedeemFee"]
        out["vaults"][sym] = fees
        print(sym, fees)
    (Path(__file__).resolve().parent / "nftx_vault_fees.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
