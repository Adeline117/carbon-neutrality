#!/usr/bin/env python3
"""fetch_nftx_events.py -- reproducible NFTX vault event pull (Ethereum mainnet).

Replaces the unreproducible aggregates in nftx_validation_results.json with a
saved, auditable pipeline. Two sources per vault, both via the Etherscan v2
API (chainid=1, key in ETHERSCAN_API_KEY):

1. Vault ERC-20 Transfer logs filtered to mint (from=0x0) and burn (to=0x0):
   identifies minter and redeemer WALLETS (the vault token is minted to the
   account that deposits NFTs and burned from the account that redeems).
2. Vault Minted/Redeemed event logs (decoded for uint256[] nftIds): identifies
   WHICH NFT tokenIds entered and left each vault, for the value-selectivity
   test.

Caches per vault to nftx_raw/<symbol>.json. Resumable; rate-limited.
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
API = "https://api.etherscan.io/v2/api"
KEY = os.environ.get("ETHERSCAN_API_KEY") or sys.exit("set ETHERSCAN_API_KEY")

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO32 = "0x" + "0" * 64
# NFTX v2 events: Minted(uint256[] nftIds, uint256[] amounts, address to)
#                 Redeemed(uint256[] nftIds, uint256[] amounts, address to)
MINTED = "0x1f72ad2a14447fa756b6f5aca53504645af79813493aca2d906b69e4aaeb9492"
REDEEMED = "0x63b13f6307f284441e029836b0c22eb91eb62a7ad555670061157930ce884f4e"

VAULTS = {
    "MILADY": "0x227c7df69d3ed1ae7574a1a7685fded90292eb48",
    "PHUNK": "0xb39185e33e8c28e0bb3dbbce24da5dea6379ae91",
    "WIZARD": "0x87931e7ad81914e7898d07c68f145fc0a553d8fb",
    "MEEB": "0x641927e970222b10b2e8cdbc96b1b4f427316f16",
    "MANA": "0x2d77f5b3efa51821ad6483adaf38ea4cb1824cc5",
    "BGAN": "0xc3b5284b2c0cfa1871a6ac63b6d6ee43c08bdc79",
}


def get_logs(address, topic0, topic1=None, topic2=None, from_block=0):
    """Paginate getLogs by advancing fromBlock past the last returned log."""
    out = []
    while True:
        params = {"chainid": 1, "module": "logs", "action": "getLogs",
                  "address": address, "topic0": topic0,
                  "fromBlock": from_block, "toBlock": "latest",
                  "page": 1, "offset": 1000, "apikey": KEY}
        if topic1 is not None:
            params.update({"topic1": topic1, "topic0_1_opr": "and"})
        if topic2 is not None:
            params.update({"topic2": topic2, "topic0_2_opr": "and"})
        q = urllib.parse.urlencode(params)
        with urllib.request.urlopen(f"{API}?{q}", timeout=45) as r:
            resp = json.loads(r.read())
        res = resp.get("result") or []
        if isinstance(res, str):  # error string
            raise RuntimeError(res)
        out.extend(res)
        time.sleep(0.25)
        if len(res) < 1000:
            return out
        from_block = int(res[-1]["blockNumber"], 16) + 1


def decode_uint_array_event(data_hex):
    """Decode (uint256[] nftIds, uint256[] amounts, address to) from event data."""
    d = data_hex[2:]
    words = [d[i:i + 64] for i in range(0, len(d), 64)]
    off_ids = int(words[0], 16) // 32
    to = "0x" + words[2][24:]
    n_ids = int(words[off_ids], 16)
    ids = [int(words[off_ids + 1 + i], 16) for i in range(n_ids)]
    return ids, to


def fetch_vault(sym, addr):
    out_path = RAW / f"{sym}.json"
    if out_path.exists():
        print(f"  {sym}: cached")
        return
    print(f"  {sym}: fetching")
    mints_t = get_logs(addr, TRANSFER, topic1=ZERO32)          # from == 0x0
    burns_t = get_logs(addr, TRANSFER, topic2=ZERO32)          # to == 0x0
    minted_ev = get_logs(addr, MINTED)
    redeemed_ev = get_logs(addr, REDEEMED)

    def tf(logs, party_topic_idx):
        return [{"block": int(l["blockNumber"], 16), "tx": l["transactionHash"],
                 "wallet": "0x" + l["topics"][party_topic_idx][26:],
                 "value_wei": int(l["data"], 16)} for l in logs]

    def ev(logs, kind):
        rows = []
        for l in logs:
            try:
                ids, to = decode_uint_array_event(l["data"])
            except Exception:
                continue
            rows.append({"block": int(l["blockNumber"], 16), "tx": l["transactionHash"],
                         "to": to, "nft_ids": ids, "kind": kind})
        return rows

    out = {"vault": sym, "address": addr,
           "erc20_mints": tf(mints_t, 2), "erc20_burns": tf(burns_t, 1),
           "minted_events": ev(minted_ev, "mint"),
           "redeemed_events": ev(redeemed_ev, "redeem")}
    out_path.write_text(json.dumps(out))
    print(f"    mints {len(out['erc20_mints'])}, burns {len(out['erc20_burns'])}, "
          f"minted_ev {len(out['minted_events'])}, redeemed_ev {len(out['redeemed_events'])}")


def main():
    for sym, addr in VAULTS.items():
        fetch_vault(sym, addr)


if __name__ == "__main__":
    main()
