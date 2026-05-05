#!/usr/bin/env python3
"""
fill_manifest.py — Substitute {{category.metric}} placeholders in markdown
with values from results/manifest.json.

Usage:
    python tools/living-paper/fill_manifest.py [--check] [--in-place] [file...]

Modes:
    (default)   Print filled content to stdout
    --check     Exit 1 if any unfilled placeholders remain (CI mode)
    --in-place  Overwrite files with filled content

Placeholder format in markdown:
    {{composition.renewable_pct_tonnes}}  → "69.1"
    {{selection.selection_coefficient}}    → "1.87"
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "results" / "manifest.json"
PLACEHOLDER_RE = re.compile(r"\{\{([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\}\}")


def load_manifest() -> dict:
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def resolve(manifest: dict, category: str, metric: str) -> str | None:
    cat = manifest.get(category)
    if not cat:
        return None
    entry = cat.get(metric)
    if not entry:
        return None
    val = entry.get("value") if isinstance(entry, dict) else entry
    if val is None:
        return None
    # Format: numbers get str(), strings pass through
    if isinstance(val, float):
        # Avoid trailing zeros: 69.1 not 69.10000
        return f"{val:g}"
    return str(val)


def fill(text: str, manifest: dict) -> tuple[str, list[str]]:
    """Return (filled_text, list_of_unresolved_placeholders)."""
    unresolved = []

    def replacer(m):
        cat, metric = m.group(1), m.group(2)
        val = resolve(manifest, cat, metric)
        if val is None:
            unresolved.append(f"{cat}.{metric}")
            return m.group(0)  # Leave placeholder as-is
        return val

    filled = PLACEHOLDER_RE.sub(replacer, text)
    return filled, unresolved


def main():
    check_mode = "--check" in sys.argv
    in_place = "--in-place" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not files:
        # Default: all paper markdown files
        paper_dir = ROOT / "docs" / "natcomms-draft"
        files = sorted(str(p) for p in paper_dir.glob("*.md"))

    manifest = load_manifest()
    all_unresolved = []

    for fpath in files:
        text = Path(fpath).read_text()
        filled, unresolved = fill(text, manifest)
        all_unresolved.extend(f"{fpath}:{u}" for u in unresolved)

        if in_place:
            Path(fpath).write_text(filled)
            print(f"  filled: {fpath} ({len(unresolved)} unresolved)")
        elif not check_mode:
            print(filled)

    if check_mode:
        if all_unresolved:
            print("UNRESOLVED PLACEHOLDERS:")
            for u in all_unresolved:
                print(f"  {u}")
            sys.exit(1)
        else:
            print("All placeholders resolved.")
            sys.exit(0)


if __name__ == "__main__":
    main()
