#!/usr/bin/env python3
"""v0.6 rubric refinement: auto-remap registry_methodology scores from 4-tier
to 2-tier (CCP/Non-CCP) based on each credit's registry and methodology.

Updates credits.json files IN PLACE. Run with --dry-run to preview changes.

Usage:
    python3 tools/remap_registry_v06.py                         # apply
    python3 tools/remap_registry_v06.py --dry-run               # preview
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# CCP-approved methodology keywords (from ICVCM 2025-2026 approved list)
# NOTE: "CAR " and "ACR " have trailing spaces to avoid matching "CAR" in "CarbonCure"
# or "ACR" in "AR-ACM0003". The latter is a CDM methodology, not an ACR one.
CCP_METHODOLOGY_KEYWORDS = {
    "VM0047", "VM0044", "VM0045", "VM0042", "VM0048", "VM0050",
    "AM0023",  # LDAR
    "TPDDTEC",  # Gold Standard cookstoves (CCP with conditions)
    "ART TREES",
}
CCP_REGISTRY_KEYWORDS = {
    "Isometric",  # Isometric methodologies approved
    "Puro",  # Puro is CCP-Eligible program
    "Rainbow",  # CCP-Eligible per 2025
}
# CAR and ACR are CCP-eligible programs; their protocols are broadly approved.
# But we match on registry name, not methodology string, to avoid false positives.
CCP_REGISTRY_PROGRAMS = {"CAR", "ACR"}

# ICVCM-rejected methodology keywords
ICVCM_REJECTED = {"ACM0002", "AM0001", "AMS-I", "ACM0006", "ACM0012"}

# Known overcrediting evidence (published research)
KNOWN_OVERCREDITING_METHODOLOGIES = {"VM0009", "VM0015"}  # REDD+ per West et al.


def classify_credit(credit: dict) -> tuple[int, str]:
    """Return (new_score, rationale) for registry_methodology under v0.6 2-tier rubric."""
    registry = credit.get("registry") or credit.get("underlying_registry", "")
    methodology = credit.get("methodology", "")
    name = credit.get("name", "")
    # Combine all text fields for overcrediting search
    all_text = f"{registry} {methodology} {name}"

    # Check for ICVCM-rejected
    for kw in ICVCM_REJECTED:
        if kw in methodology:
            score = 25
            for oc in KNOWN_OVERCREDITING_METHODOLOGIES:
                if oc in all_text:
                    score = max(0, score - 15)
            return score, f"ICVCM-rejected methodology ({kw})"

    # Check for CCP-eligible via methodology keywords
    is_ccp = False
    for kw in CCP_METHODOLOGY_KEYWORDS:
        if kw in methodology:
            is_ccp = True
            break

    # Check via registry keywords (Puro, Isometric, Rainbow)
    if not is_ccp:
        for kw in CCP_REGISTRY_KEYWORDS:
            if kw in registry or kw in name:
                is_ccp = True
                break

    # Check CAR/ACR as registry programs (match on registry field only, not methodology)
    if not is_ccp:
        for prog in CCP_REGISTRY_PROGRAMS:
            # Match "CAR" or "ACR" as standalone words in registry, not as substrings
            # of methodology strings like "AR-ACM0003"
            if prog in registry and prog not in methodology:
                is_ccp = True
                break
            # Also match if registry starts with the program name
            if registry.startswith(prog) or f"({prog})" in registry:
                is_ccp = True
                break

    if is_ccp:
        base = 80
        if "cookstove" in name.lower() or "TPDDTEC" in methodology or "VM0050" in methodology:
            base = 75
        for oc in KNOWN_OVERCREDITING_METHODOLOGIES:
            if oc in all_text:
                base = max(0, base - 15)
        return base, "CCP-eligible"

    # Non-CCP but recognized registry
    recognized = any(r in registry for r in [
        "Verra", "Gold Standard", "CDM", "Plan Vivo", "Regen", "Nori", "OFP",
        "EcoRegistry", "Cercarbono",
    ])
    if recognized:
        base = 45
        for oc in KNOWN_OVERCREDITING_METHODOLOGIES:
            if oc in all_text:
                base = max(0, base - 15)
        return base, "Non-CCP, recognized registry"

    # Unrecognized / synthetic / no registry
    if "Synthetic" in registry or "Unrecognized" in registry or not registry:
        return 15, "No recognized registry"

    return 40, "Non-CCP, other"


def process_file(path: Path, dry_run: bool) -> None:
    data = json.loads(path.read_text())
    changes = []
    for credit in data["credits"]:
        old = credit["scores"]["registry_methodology"]
        new, reason = classify_credit(credit)
        if old != new:
            changes.append((credit["id"], credit["name"][:40], old, new, reason))
            if not dry_run:
                credit["scores"]["registry_methodology"] = new

    if changes:
        print(f"\n{path.name}: {len(changes)} changes")
        for cid, name, old, new, reason in changes:
            delta = new - old
            print(f"  {cid:6s} {name:40s}  {old:3d} → {new:3d} ({delta:+d})  [{reason}]")
        if not dry_run:
            path.write_text(json.dumps(data, indent=2))
            print(f"  Written to {path}")
    else:
        print(f"\n{path.name}: no changes")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN — no files will be modified\n")

    files = [
        ROOT / "data" / "pilot-scoring" / "credits.json",
        ROOT / "data" / "tokenized-pilot" / "credits.json",
    ]
    for f in files:
        if f.exists():
            process_file(f, dry_run)

    if not dry_run:
        print("\nDone. Run score.py to regenerate scores.csv / scores.md.")


if __name__ == "__main__":
    main()
