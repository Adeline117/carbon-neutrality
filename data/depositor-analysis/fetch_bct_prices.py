#!/usr/bin/env python3
"""fetch_bct_prices.py -- daily BCT/USD price series (DeFi Llama, keyless).

Restores the committed provenance of the price series used by
scripts/price_quality_analysis.py: the original analysis read a temporary
file (/tmp/bct_prices_merged.json) that was never committed, leaving a 4-row
stub in bct_prices_daily.json. This script re-fetches the full daily series
from the DeFi Llama coins API (source: Polygon DEX pricing for the BCT token)
and overwrites bct_prices_daily.json with the complete record.

API: https://coins.llama.fi/chart/polygon:<token>?start=<ts>&span<=500&period=1d
"""
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TOKEN = "polygon:0x2f800db0fdb5223b3c3f354886d907a671414a7f"
OUT = Path(__file__).resolve().parent / "bct_prices_daily.json"
START = 1633046400  # 2021-10-01
SPAN = 450
DAY = 86400


def fetch(start):
    url = f"https://coins.llama.fi/chart/{TOKEN}?start={start}&span={SPAN}&period=1d"
    with urllib.request.urlopen(url, timeout=45) as r:
        d = json.loads(r.read())
    return d.get("coins", {}).get(TOKEN, {}).get("prices", [])


def main():
    rows, start = {}, START
    for _ in range(8):
        chunk = fetch(start)
        if not chunk:
            break
        for p in chunk:
            rows[int(p["timestamp"]) // DAY] = {"timestamp": int(p["timestamp"]),
                                                "price": p["price"]}
        last = max(int(p["timestamp"]) for p in chunk)
        if last <= start + DAY:
            break
        start = last + DAY
        time.sleep(1)
    series = [rows[k] for k in sorted(rows)]
    OUT.write_text(json.dumps(series, indent=1))
    f, l = series[0], series[-1]
    fd = datetime.fromtimestamp(f["timestamp"], tz=timezone.utc).date()
    ld = datetime.fromtimestamp(l["timestamp"], tz=timezone.utc).date()
    print(f"{len(series)} daily points: {fd} (${f['price']:.2f}) -> {ld} (${l['price']:.4f})")


if __name__ == "__main__":
    main()
