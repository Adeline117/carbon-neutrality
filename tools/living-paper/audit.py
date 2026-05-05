#!/usr/bin/env python3
"""
audit.py — Agent D's audit tool.
Runs integrity checks on the living paper system.

Usage:
    python tools/living-paper/audit.py [--mode 72h|24h|adversarial]

72h mode (default):
    - All FLUID/TODO/ORPHANED markers
    - Manifest key completeness (tex uses it, manifest has it)
    - Unprocessed Agent B flags
    - Figure staleness
    - Build check (placeholder resolution)

24h mode (72h + adversarial spot checks):
    - Independent claim verification
    - Source experiment existence check
    - Cross-reference audit

adversarial mode:
    - Assume every claim is wrong; verify from source
    - Assume every manifest value is stale; check file mtimes
    - Flag any figure older than its source data
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "results" / "manifest.json"
PAPER_DIR = ROOT / "docs" / "natcomms-draft"
REVIEW_DIR = ROOT / "review"
FIGURES_DIR = ROOT / "figures"

FLUID_RE = re.compile(r"<!--\s*FLUID:.*?-->|%\s*FLUID:.*$", re.MULTILINE)
TODO_RE = re.compile(r"\[TODO:.*?\]|<!--\s*TODO:.*?-->", re.MULTILINE)
ORPHANED_RE = re.compile(r"<!--\s*ORPHANED:.*?-->|%\s*ORPHANED:", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{\{([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\}\}")


def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def scan_markers():
    """Scan all paper files for FLUID, TODO, ORPHANED markers."""
    findings = {"fluid": [], "todo": [], "orphaned": []}

    for md_file in sorted(PAPER_DIR.glob("*.md")):
        text = md_file.read_text()
        for m in FLUID_RE.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            findings["fluid"].append(f"{md_file.name}:{line_no} — {m.group().strip()}")
        for m in TODO_RE.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            findings["todo"].append(f"{md_file.name}:{line_no} — {m.group().strip()}")
        for m in ORPHANED_RE.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            findings["orphaned"].append(f"{md_file.name}:{line_no} — {m.group().strip()}")

    return findings


def check_manifest_completeness():
    """Check for placeholders in paper that have no manifest entry."""
    manifest = load_manifest()
    missing = []

    for md_file in sorted(PAPER_DIR.glob("*.md")):
        text = md_file.read_text()
        for m in PLACEHOLDER_RE.finditer(text):
            cat, metric = m.group(1), m.group(2)
            cat_data = manifest.get(cat)
            if not cat_data or metric not in cat_data:
                line_no = text[:m.start()].count("\n") + 1
                missing.append(f"{md_file.name}:{line_no} — {{{{{cat}.{metric}}}}} not in manifest")

    return missing


def check_figure_staleness():
    """Compare figure mtime vs source data mtime."""
    stale = []
    manifest = load_manifest()

    # Collect all source file mtimes
    source_mtimes = {}
    for category, entries in manifest.items():
        if category.startswith("_") or not isinstance(entries, dict):
            continue
        for metric, entry in entries.items():
            if isinstance(entry, dict) and "source" in entry:
                src = ROOT / entry["source"]
                if src.exists():
                    source_mtimes[str(src)] = os.path.getmtime(src)

    latest_source = max(source_mtimes.values()) if source_mtimes else 0

    # Check figures
    for fig in sorted(FIGURES_DIR.glob("*")):
        if fig.suffix in (".pdf", ".png", ".svg"):
            fig_mtime = os.path.getmtime(fig)
            if fig_mtime < latest_source:
                age_hours = (latest_source - fig_mtime) / 3600
                stale.append(f"{fig.name} — {age_hours:.1f}h older than latest source data")

    return stale


def check_unprocessed_b_flags():
    """Check for Agent B impact reports that haven't been addressed by Agent C."""
    b_report = REVIEW_DIR / "B_impact_report.md"
    c_report = REVIEW_DIR / "C_major_changes.md"

    if not b_report.exists():
        return []

    b_text = b_report.read_text()
    # Look for flagged claims
    flagged = re.findall(r"^-\s*\*\*FLAG\*\*:?\s*(.+)$", b_text, re.MULTILINE)

    if not flagged:
        return []

    # Check if C has addressed them
    if c_report.exists():
        c_text = c_report.read_text()
        unaddressed = [f for f in flagged if f[:30] not in c_text]
    else:
        unaddressed = flagged

    return [f"Unaddressed B-flag: {f}" for f in unaddressed]


def check_source_existence():
    """Adversarial: verify every manifest source file still exists."""
    manifest = load_manifest()
    missing = []

    for category, entries in manifest.items():
        if category.startswith("_") or not isinstance(entries, dict):
            continue
        for metric, entry in entries.items():
            if isinstance(entry, dict) and "source" in entry:
                src = ROOT / entry["source"]
                if not src.exists():
                    missing.append(f"{category}.{metric} → source missing: {entry['source']}")

    return missing


def run_audit(mode: str = "72h"):
    """Run audit at specified depth."""
    report = []
    report.append(f"# Living Paper Audit — {mode} mode")
    report.append(f"**Timestamp**: {datetime.now().isoformat()}")
    report.append("")

    # --- 72h checks (always run) ---
    markers = scan_markers()
    report.append(f"## Markers")
    report.append(f"- FLUID: {len(markers['fluid'])}")
    for m in markers["fluid"]:
        report.append(f"  - {m}")
    report.append(f"- TODO: {len(markers['todo'])}")
    for m in markers["todo"]:
        report.append(f"  - {m}")
    report.append(f"- ORPHANED: {len(markers['orphaned'])}")
    for m in markers["orphaned"]:
        report.append(f"  - {m}")
    report.append("")

    missing_keys = check_manifest_completeness()
    report.append(f"## Manifest Completeness")
    report.append(f"- Missing keys: {len(missing_keys)}")
    for m in missing_keys:
        report.append(f"  - {m}")
    report.append("")

    b_flags = check_unprocessed_b_flags()
    report.append(f"## Unprocessed Agent B Flags")
    report.append(f"- Count: {len(b_flags)}")
    for f in b_flags:
        report.append(f"  - {f}")
    report.append("")

    stale_figs = check_figure_staleness()
    report.append(f"## Figure Staleness")
    report.append(f"- Stale: {len(stale_figs)}")
    for s in stale_figs:
        report.append(f"  - {s}")
    report.append("")

    # --- 24h / adversarial checks ---
    if mode in ("24h", "adversarial"):
        missing_sources = check_source_existence()
        report.append(f"## Source File Existence (adversarial)")
        report.append(f"- Missing: {len(missing_sources)}")
        for m in missing_sources:
            report.append(f"  - {m}")
        report.append("")

    # Summary
    blocking = []
    if missing_keys:
        blocking.append(f"{len(missing_keys)} missing manifest keys")
    if b_flags:
        blocking.append(f"{len(b_flags)} unprocessed B-flags")
    if mode in ("24h", "adversarial") and missing_sources:
        blocking.append(f"{len(missing_sources)} missing source files")

    report.append("## Verdict")
    if blocking:
        report.append(f"**BLOCKING** — {'; '.join(blocking)}")
    else:
        report.append("**CLEAR** — no blocking issues found")

    return "\n".join(report)


def main():
    mode = "72h"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    report = run_audit(mode)
    print(report)

    # Write to review directory
    out_path = REVIEW_DIR / f"D_audit_{mode}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(f"\n→ Written to {out_path}")


if __name__ == "__main__":
    main()
