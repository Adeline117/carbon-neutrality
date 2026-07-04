#!/usr/bin/env python3
"""fetch_nft_sales.py -- per-tokenId sale-price panel for NFTX-vaulted collections.

Value proxy for the cross-asset replication: marketplace sales (all venues
indexed by the Alchemy NFT API getNFTSales endpoint) for each vault's
underlying collection. Each sale: tokenId, price (native ETH sellerFee),
block, marketplace. Cached to nftx_raw/sales_<symbol>.json. Resumable.

Env: ALCHEMY_API_KEY.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "nftx_raw"
RAW.mkdir(exist_ok=True)
KEY = os.environ.get("ALCHEMY_API_KEY") or sys.exit("set ALCHEMY_API_KEY")
BASE = f"https://eth-mainnet.g.alchemy.com/nft/v3/{KEY}/getNFTSales"

# vault symbol -> underlying NFT contract (resolved via vault.assetAddress())
COLLECTIONS = {
    "MILADY": "0x5af0d9827e0c53e4799bb226655a1de152a425a5",
    "PHUNK": "0xf07468ead8cf26c752c676e43c814fee9c8cf402",
    "WIZARD": None,  # resolved at runtime below
    "MEEB": None,
    "MANA": None,
    "BGAN": None,
}
VAULTS = {
    "MILADY": "0x227c7df69d3ed1ae7574a1a7685fded90292eb48",
    "PHUNK": "0xb39185e33e8c28e0bb3dbbce24da5dea6379ae91",
    "WIZARD": "0x87931e7ad81914e7898d07c68f145fc0a553d8fb",
    "MEEB": "0x641927e970222b10b2e8cdbc96b1b4f427316f16",
    "MANA": "0x2d77f5b3efa51821ad6483adaf38ea4cb1824cc5",
    "BGAN": "0xc3b5284b2c0cfa1871a6ac63b6d6ee43c08bdc79",
}
RPC = f"https://eth-mainnet.g.alchemy.com/v2/{KEY}"


def asset_address(vault):
    req = urllib.request.Request(RPC, data=json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": vault, "data": "0x1ba46cfd"}, "latest"]}).encode(),  # assetAddress()
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.loads(r.read())["result"]
    return "0x" + res[26:]


def fetch_sales(sym, contract):
    out_path = RAW / f"sales_{sym}.json"
    if out_path.exists():
        print(f"  {sym}: cached ({len(json.loads(out_path.read_text())['sales'])} sales)")
        return
    sales, page_key = [], None
    while True:
        params = {"contractAddress": contract, "order": "asc", "limit": 1000}
        if page_key:
            params["pageKey"] = page_key
        q = urllib.parse.urlencode(params)
        with urllib.request.urlopen(f"{BASE}?{q}", timeout=45) as r:
            resp = json.loads(r.read())
        for x in resp.get("nftSales", []):
            fee = x.get("sellerFee") or {}
            if fee.get("symbol") not in ("ETH", "WETH"):
                continue  # keep the native-denominated panel homogeneous
            sales.append({"tokenId": x["tokenId"],
                          "price_eth": int(fee.get("amount", "0")) / 10 ** int(fee.get("decimals", 18)),
                          "block": x.get("blockNumber"),
                          "marketplace": x.get("marketplace")})
        page_key = resp.get("pageKey")
        print(f"    {sym}: {len(sales)} sales so far", flush=True)
        time.sleep(0.3)
        if not page_key:
            break
    out_path.write_text(json.dumps({"symbol": sym, "contract": contract, "sales": sales}))
    print(f"  {sym}: done, {len(sales)} sales")


def main():
    for sym, vault in VAULTS.items():
        contract = COLLECTIONS.get(sym) or asset_address(vault)
        print(f"{sym} underlying: {contract}")
        fetch_sales(sym, contract)


if __name__ == "__main__":
    main()
