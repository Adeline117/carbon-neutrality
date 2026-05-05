#!/usr/bin/env python3
"""
update_manifest.py — Agent B's core tool.
Reads experiment result JSONs and updates results/manifest.json.

Usage:
    python tools/living-paper/update_manifest.py [--diff] [--source path/to/results.json]

Without --source: scans all known source files referenced in the manifest and
updates values that have changed.

With --source: updates only manifest entries whose source matches the given path.

--diff: print what changed without writing (dry run).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "results" / "manifest.json"


def load_json(path: Path) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def extract_value_from_source(source_data: dict, category: str, metric: str) -> any:
    """
    Attempt to extract a value from source data.
    This is a heuristic mapper — extend as needed for new experiment formats.
    """
    # Direct key lookup strategies
    key_attempts = [
        metric,
        metric.replace("_pct", ""),
        metric.replace("_tonnes", ""),
    ]

    for key in key_attempts:
        if key in source_data:
            val = source_data[key]
            if isinstance(val, dict) and "value" in val:
                return val["value"]
            return val

    # Nested lookup
    for top_key, top_val in source_data.items():
        if isinstance(top_val, dict):
            for key in key_attempts:
                if key in top_val:
                    return top_val[key]

    return None


def update_manifest(source_filter: str | None = None, dry_run: bool = False) -> list[dict]:
    """Update manifest from source files. Returns list of changes."""
    manifest = load_json(MANIFEST_PATH)
    if not manifest:
        print("ERROR: Cannot load manifest.json")
        sys.exit(1)

    changes = []

    for category, entries in manifest.items():
        if category.startswith("_"):
            continue
        if not isinstance(entries, dict):
            continue

        for metric, entry in entries.items():
            if not isinstance(entry, dict) or "source" not in entry:
                continue

            source_path = ROOT / entry["source"]

            if source_filter and entry["source"] != source_filter:
                continue

            source_data = load_json(source_path)
            if source_data is None:
                continue

            new_val = extract_value_from_source(source_data, category, metric)
            if new_val is not None and new_val != entry.get("value"):
                changes.append({
                    "category": category,
                    "metric": metric,
                    "old": entry.get("value"),
                    "new": new_val,
                    "source": entry["source"]
                })
                if not dry_run:
                    entry["value"] = new_val

    if not dry_run and changes:
        manifest["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        manifest["_meta"]["last_updated_by"] = "update_manifest.py"
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)

    return changes


def main():
    dry_run = "--diff" in sys.argv
    source_filter = None

    if "--source" in sys.argv:
        idx = sys.argv.index("--source")
        if idx + 1 < len(sys.argv):
            source_filter = sys.argv[idx + 1]

    changes = update_manifest(source_filter=source_filter, dry_run=dry_run)

    if changes:
        print(f"{'[DRY RUN] ' if dry_run else ''}Changes detected ({len(changes)}):")
        for c in changes:
            print(f"  {c['category']}.{c['metric']}: {c['old']} → {c['new']}  (from {c['source']})")
    else:
        print("No changes detected.")


if __name__ == "__main__":
    main()
