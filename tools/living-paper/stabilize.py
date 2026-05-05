#!/usr/bin/env python3
"""
Agent A: Stabilize paper by replacing hardcoded numbers with {{manifest}} placeholders.

Strategy:
  - Build (value, context_keywords) → manifest_key mapping
  - For each manifest entry, search paper text for the value near expected context
  - Replace ONLY high-confidence matches (value + context within 80 chars)
  - Report all replacements and ambiguous/unmatched numbers

Usage:
    python tools/living-paper/stabilize.py --dry-run     # Report only
    python tools/living-paper/stabilize.py --apply        # Write placeholders
    python tools/living-paper/stabilize.py --audit        # Check existing placeholders
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "results" / "manifest.json"
PAPER_DIR = ROOT / "docs" / "natcomms-draft"
# Target the root section files (the actively edited ones)
SECTION_FILES = sorted(PAPER_DIR.glob("sections-*.md"))

# Context windows: how many chars around a number to check for context keywords
CONTEXT_WINDOW = 120


def load_manifest():
    m = json.load(open(MANIFEST_PATH))
    entries = []
    for cat, metrics in m.items():
        if cat.startswith("_") or not isinstance(metrics, dict):
            continue
        for metric, entry in metrics.items():
            if not isinstance(entry, dict) or "value" not in entry:
                continue
            entries.append({
                "key": f"{cat}.{metric}",
                "placeholder": f"{{{{{cat}.{metric}}}}}",
                "value": entry["value"],
                "unit": entry.get("unit", ""),
            })
    return entries


def value_to_patterns(value, unit=""):
    """Generate regex patterns that match how a value appears in text."""
    patterns = []
    if isinstance(value, (int, float)):
        s = f"{value:g}"
        # Escape dots for regex
        escaped = re.escape(s)
        # Match with optional comma formatting: 21984482 → 21,984,482
        if isinstance(value, int) and value >= 1000:
            formatted = f"{value:,}"
            patterns.append(re.escape(formatted))
        elif isinstance(value, float):
            # 69.1 should match 69.1
            patterns.append(escaped)
            # Also match formatted integers if value is like 21984482.0
            if value == int(value) and value >= 1000:
                patterns.append(re.escape(f"{int(value):,}"))
        else:
            patterns.append(escaped)
        # Always add the plain number
        if escaped not in patterns:
            patterns.append(escaped)
    elif isinstance(value, str):
        # String values like "<0.0001" or "<10^-64"
        patterns.append(re.escape(value))
        # Also match LaTeX-style: <10^{-64} or <10^-64
        if "^" in value:
            patterns.append(re.escape(value).replace(r"\^", r"\^[\{]?").rstrip("}") + r"[\}]?")
    return patterns


# Context keywords for disambiguation — map manifest key prefixes to expected nearby words
CONTEXT_HINTS = {
    "composition.renewable_pct_tonnes": ["renewable", "wind", "solar", "composition", "tonnage", "dominated"],
    "composition.redd_pct_tonnes": ["REDD", "redd", "nature"],
    "composition.fossil_switch_pct": ["fossil", "switch"],
    "composition.waste_methane_pct": ["waste", "methane"],
    "composition.arr_pct": ["ARR", "afforestation"],
    "composition.industrial_gas_pct": ["industrial gas"],
    "composition.ifm_pct": ["IFM", "forestry"],
    "composition.n_deposits": ["deposit", "1,187", "1187"],
    "composition.n_projects": ["project", "168"],
    "composition.total_tonnes": ["tonnes", "million", "total"],
    "selection.selection_coefficient": ["selection coefficient", "1.87", "over-select", "base rate"],
    "selection.vcs_base_rate_renewable": ["VCS", "base rate", "37%", "issuance"],
    "selection.n_wallets": ["wallet", "depositor"],
    "selection.gini": ["Gini", "concentrated"],
    "selection.effective_n_hhi": ["effective", "HHI"],
    "selection.wallet_majority_renewable_pct": ["majority-renewable", "wallets"],
    "selection.bootstrap_point": ["bootstrap", "excess"],
    "selection.bootstrap_ci_lo": ["bootstrap", "CI", "0.496"],
    "selection.bootstrap_ci_hi": ["bootstrap", "CI", "0.547"],
    "selection.conservative_selection_coeff": ["conservative", "1.43"],
    "selection.redd_underrepresentation": ["under-represent", "REDD"],
    "quality.bct_pqd": ["BCT", "PQD", "0.679"],
    "quality.nct_pqd": ["NCT", "PQD"],
    "quality.char_pqd": ["CHAR", "PQD", "biochar"],
    "quality.ccp_cohens_d": ["CCP", "Cohen", "calibration"],
    "quality.bezero_rho": ["BeZero", "Spearman", "0.901"],
    "quality.llm_panel_kappa": ["Fleiss", "kappa", "LLM", "panel"],
    "quality.quality_atlas_pqd_min": ["DACCS", "0.076", "atlas"],
    "quality.quality_atlas_pqd_max": ["0.759", "renewable", "atlas"],
    "quality.bbb_gate_pqd": ["BBB", "gate", "0.405"],
    "quality.bbb_gate_improvement_pct": ["gate", "improvement", "40.5"],
    "price_quality.pearson_r": ["Pearson", "0.774", "correlated"],
    "price_quality.granger_price_to_quality_f": ["price-to-quality", "16.08", "Granger"],
    "price_quality.granger_quality_to_price_f": ["quality-to-price", "6.32", "Granger"],
    "price_quality.granger_quality_to_price_p": ["0.004", "Granger"],
    "price_quality.n_weekly_obs": ["weekly", "55"],
    "price_quality.ols_beta_renewable": ["1.8", "beta", "percentage-point", "renewable share"],
    "redemption.redd_redeemed_pct": ["REDD", "99.8", "redeemed"],
    "redemption.renewable_redeemed_pct": ["renewable", "3.6", "redeemed"],
    "redemption.ifm_redeemed_pct": ["IFM", "93", "redeemed"],
    "redemption.arr_redeemed_pct": ["ARR", "91.3", "redeemed"],
    "redemption.industrial_gas_redeemed_pct": ["industrial gas", "100", "redeemed"],
    "redemption.depositor_redeemer_overlap_pct": ["overlap", "1.4%", "depositor", "redeemer"],
    "redemption.redeemer_top10_share": ["top 10", "85%", "tonnage"],
    "redemption.quality_gap_weighted": ["tonnage-weighted", "7 points", "gap"],
    "redemption.mean_quality_redeemed_weighted": ["38.7", "redeemed", "weighted"],
    "redemption.mean_quality_deposited_weighted": ["31.7", "deposited", "weighted"],
    "redemption.n_unique_redeemers": ["28,897", "redeemer"],
    "redemption.n_transfer_events": ["35,432", "Transfer", "redemption"],
    "bridge_decomposition.total_bridged_tokens": ["369", "bridged"],
    "bridge_decomposition.bct_deposited_tokens": ["345", "deposited", "BCT"],
    "bridge_decomposition.bct_coverage_pct": ["93.5", "pass-through"],
    "bridge_decomposition.not_bct_tokens": ["24", "never entered"],
    "temporal.spearman_rho_full": ["-0.24", "Spearman", "temporal"],
    "temporal.spearman_rho_preterra": ["-0.13", "pre-Terra"],
    "temporal.vintage_free_rho": ["+0.24", "vintage", "excluded"],
    "within_pool.permutation_z": ["-0.64", "permutation", "within-pool"],
    "within_pool.mean_quality": ["32.3", "universe", "uniformly"],
    "welfare.welfare_gap_median_usd_millions": ["146", "welfare", "million"],
    "predictive_stranding.b_grade_redemption_rate_pct": ["B", "2.4%", "grade"],
    "predictive_stranding.bb_grade_redemption_rate_pct": ["BB", "31.0%", "grade"],
    "predictive_stranding.bbb_grade_redemption_rate_pct": ["BBB", "78.0%", "grade"],
}


def find_replacements(text, entries):
    """Find all manifest values in text with context-aware matching."""
    replacements = []
    for entry in entries:
        key = entry["key"]
        value = entry["value"]
        patterns = value_to_patterns(value, entry["unit"])
        hints = CONTEXT_HINTS.get(key, [])

        for pat in patterns:
            for m in re.finditer(pat, text):
                start, end = m.start(), m.end()
                # Get surrounding context
                ctx_start = max(0, start - CONTEXT_WINDOW)
                ctx_end = min(len(text), end + CONTEXT_WINDOW)
                context = text[ctx_start:ctx_end]

                # Score context match
                hint_matches = sum(1 for h in hints if h.lower() in context.lower())
                confidence = hint_matches / max(len(hints), 1)

                # Skip very common numbers without context (e.g., "2" could match many things)
                val_str = str(value)
                if len(val_str) <= 2 and isinstance(value, int) and confidence < 0.3:
                    continue
                # Skip if value is too generic (like "0.2" without strong context)
                if isinstance(value, float) and value < 1 and len(val_str) <= 3 and confidence < 0.3:
                    continue

                # Already a placeholder?
                before = text[max(0, start-2):start]
                if "{{" in before:
                    continue

                replacements.append({
                    "key": key,
                    "placeholder": entry["placeholder"],
                    "matched_text": m.group(),
                    "position": start,
                    "line": text[:start].count("\n") + 1,
                    "context": context.replace("\n", " ")[:200],
                    "confidence": confidence,
                    "hint_matches": hint_matches,
                    "total_hints": len(hints),
                })

    # Deduplicate: for same position, keep highest confidence match
    by_pos = {}
    for r in replacements:
        pos = r["position"]
        if pos not in by_pos or r["confidence"] > by_pos[pos]["confidence"]:
            by_pos[pos] = r

    return sorted(by_pos.values(), key=lambda x: x["position"])


def apply_replacements(text, replacements, min_confidence=0.3):
    """Apply replacements from end to start (to preserve positions)."""
    filtered = [r for r in replacements if r["confidence"] >= min_confidence]
    # Sort by position descending so we don't shift indices
    for r in sorted(filtered, key=lambda x: x["position"], reverse=True):
        pos = r["position"]
        end = pos + len(r["matched_text"])
        text = text[:pos] + r["placeholder"] + text[end:]
    return text


def main():
    dry_run = "--dry-run" in sys.argv or len(sys.argv) == 1
    do_apply = "--apply" in sys.argv
    audit = "--audit" in sys.argv

    entries = load_manifest()
    print(f"Loaded {len(entries)} manifest entries")
    print(f"Paper files: {[f.name for f in SECTION_FILES]}")
    print()

    total_replacements = 0
    total_high_conf = 0

    for fpath in SECTION_FILES:
        text = fpath.read_text()
        replacements = find_replacements(text, entries)

        high_conf = [r for r in replacements if r["confidence"] >= 0.3]
        low_conf = [r for r in replacements if r["confidence"] < 0.3]

        print(f"{'='*70}")
        print(f"  {fpath.name}: {len(high_conf)} high-confidence + {len(low_conf)} low-confidence matches")
        print(f"{'='*70}")

        for r in high_conf:
            conf_pct = int(r["confidence"] * 100)
            print(f"  L{r['line']:3d} | {r['matched_text']:>12s} → {r['placeholder']:50s} [{conf_pct}%]")

        if low_conf and dry_run:
            print(f"\n  Low-confidence (skipped):")
            for r in low_conf[:10]:
                conf_pct = int(r["confidence"] * 100)
                print(f"  L{r['line']:3d} | {r['matched_text']:>12s} → {r['key']:50s} [{conf_pct}%] SKIP")

        total_replacements += len(replacements)
        total_high_conf += len(high_conf)

        if do_apply:
            # Only apply 100% confidence matches to avoid false positives
            safe = [r for r in replacements if r["confidence"] >= 1.0]
            if safe:
                new_text = apply_replacements(text, replacements, min_confidence=1.0)
                fpath.write_text(new_text)
                print(f"\n  → Applied {len(safe)} replacements (100% confidence) to {fpath.name}")

        print()

    print(f"TOTAL: {total_high_conf} high-confidence replacements across {len(SECTION_FILES)} files")
    if dry_run:
        print("(Dry run — use --apply to write changes)")


if __name__ == "__main__":
    main()
