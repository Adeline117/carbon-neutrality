#!/usr/bin/env python3
"""Regenerate script/seed/tokenized_pilot.json from the canonical
data/tokenized-pilot/credits.json so the Solidity seed script stays in sync.

Run whenever credits.json changes:
    python3 tools/regen_seed.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "tokenized-pilot" / "credits.json"
OUT = ROOT / "script" / "seed" / "tokenized_pilot.json"

# Must match ICarbonCreditRating.Disqualifiers field order.
DQ_KEYS = [
    "double_counting",
    "failed_verification",
    "sanctioned_registry",
    "no_third_party",
    "human_rights",
    "community_harm",
]


def main() -> None:
    credits = json.loads(SRC.read_text())["credits"]
    rows = []
    for c in credits:
        dq_set = set(c.get("disqualifiers", []))
        unknown = dq_set - set(DQ_KEYS)
        # Silently drop pre_paris_override etc. — these are not on-chain disqualifiers,
        # they're informational flags already baked into the vintage_year dimension score.
        rows.append(
            {
                "id": c["id"],
                "name": c["name"][:60],
                "symbol": "MCC-" + c["id"],
                "scores": c["scores"],
                "flags": [k in dq_set for k in DQ_KEYS],
                "vintage_year": c["vintage_year"],
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    print(f"Wrote {len(rows)} seed rows -> {OUT}")


if __name__ == "__main__":
    main()
