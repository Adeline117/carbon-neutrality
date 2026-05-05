#!/usr/bin/env python3
"""
Agent A Pass 2: Replace remaining hardcoded numbers that are distinctive
enough to replace globally (not context-dependent).

Pass 1 (stabilize.py) used context-matching at 100% confidence → 97 replacements.
Pass 2 uses a curated list of distinctive value→placeholder mappings that are
safe to replace everywhere in the paper.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT / "docs" / "natcomms-draft"
SECTION_FILES = sorted(PAPER_DIR.glob("sections-*.md"))

# Distinctive replacements: (regex_pattern, placeholder, description)
# Only numbers distinctive enough that they ALWAYS mean this manifest entry
# in the context of this paper. Ordered from most-specific to least-specific.
REPLACEMENTS = [
    # Composition
    (r'(?<!\{)69\.1(?![\d}])', '{{composition.renewable_pct_tonnes}}', 'renewable %'),
    (r'(?<!\{)78\.5(?![\d}])', '{{composition.renewable_pct_count}}', 'renewable % by count'),

    # Selection
    (r'1\.87\$?\\times\$?', '{{selection.selection_coefficient}}$\\times$', 'selection coeff'),
    (r'(?<!\d)1\.43\$?\\times\$?', '{{selection.conservative_selection_coeff}}$\\times$', 'conservative selection'),

    # Price-quality
    (r'(?<!\d)16\.08(?!\d)', '{{price_quality.granger_price_to_quality_f}}', 'Granger F price→quality'),
    (r'(?<!\d)6\.32(?!\d)', '{{price_quality.granger_quality_to_price_f}}', 'Granger F quality→price'),

    # Bridge — be careful: 93.5 should stay as token-count figure where stated
    # Only replace "93.5%" near "pass-through" or "bridge" or "token"
    # Actually these were already mostly done in pass 1. Skip.

    # Redemption rates — these are very distinctive
    (r'(?<!\d)91\.3(?![\d}])', '{{redemption.arr_redeemed_pct}}', 'ARR redeemed %'),

    # Quality
    (r'(?<!\d)0\.901(?![\d}])', '{{quality.bezero_rho}}', 'BeZero rho'),

    # CCP
    (r'(?<!\d|\.)1\.87(?!\d|\\)', '{{quality.ccp_cohens_d}}', 'CCP Cohen d'),
    # Note: 1.87 is used for both selection_coefficient and ccp_cohens_d
    # They happen to have the same value. The selection_coefficient pattern above
    # catches "1.87×" while this catches standalone "1.87" near CCP context.
    # We'll handle this with a targeted approach below.
]

# Targeted replacements: (exact_old_string, new_string)
# These are full-context replacements that are unambiguous
TARGETED = [
    # Section 1-2: remaining 69.1 in intro
    ('BCT was 69.1% renewable', 'BCT was {{composition.renewable_pct_tonnes}}% renewable'),
    ('69.1% for renewables alone', '{{composition.renewable_pct_tonnes}}% for renewables alone'),
    ("69.1% by tonnage; 78.5%", "{{composition.renewable_pct_tonnes}}% by tonnage; {{composition.renewable_pct_count}}%"),
    ('BCT 4.2% vs. VCS', 'BCT {{composition.redd_pct_tonnes}}% vs. VCS'),
    # Section 3 Discussion
    ('pool was 69.1% renewable energy', 'pool was {{composition.renewable_pct_tonnes}}% renewable energy'),
    ('(69.1% of pool content)', '({{composition.renewable_pct_tonnes}}% of pool content)'),
    ('(4.2%) as widely', '({{composition.redd_pct_tonnes}}%) as widely'),
    ('BCT REDD+ share = 4.2%', 'BCT REDD+ share = {{composition.redd_pct_tonnes}}%'),
    # Selection coefficient standalone (not ×)
    ('$d$ = 1.87)', '$d$ = {{quality.ccp_cohens_d}})'),
    ("$d$ = 1.87,", "$d$ = {{quality.ccp_cohens_d}},"),
    ("d = 1.87)", "d = {{quality.ccp_cohens_d}})"),
    # Granger
    ("$F$ = 6.32, $p$ = 0.004", "$F$ = {{price_quality.granger_quality_to_price_f}}, $p$ = {{price_quality.granger_quality_to_price_p}}"),
    ("$F$ = 16.08, $p$ <10", "$F$ = {{price_quality.granger_price_to_quality_f}}, $p$ <10"),
    ("F = 6.32", "F = {{price_quality.granger_quality_to_price_f}}"),
    ("F = 16.08", "F = {{price_quality.granger_price_to_quality_f}}"),
    # BeZero
    ("$\\rho$ = +0.901", "$\\rho$ = +{{quality.bezero_rho}}"),
    ("$\\rho$ = +{{quality.bezero_rho}},", "$\\rho$ = +{{quality.bezero_rho}},"),  # avoid double
    ("ρ = +0.901", "ρ = +{{quality.bezero_rho}}"),
    # Bridge tonnage in discussion
    ('BCT renewable energy share = 69.1%', 'BCT renewable energy share = {{composition.renewable_pct_tonnes}}%'),
    # NCT PQD
    ("NCT PQD ({{quality.nct_pqd}})", "NCT PQD ({{quality.nct_pqd}})"),  # already done
    # Figure legends - 69.1%
    ('constitute 69.1% of', 'constitute {{composition.renewable_pct_tonnes}}% of'),
    ('69.1% (deposits only)', '{{composition.renewable_pct_tonnes}}% (deposits only)'),
    ("69.1% renewable energy, 4.2% REDD+", "{{composition.renewable_pct_tonnes}}% renewable energy, {{composition.redd_pct_tonnes}}% REDD+"),
    ("REDD+ (4.2%)", "REDD+ ({{composition.redd_pct_tonnes}}%)"),
    ('69.1%) versus the', '{{composition.renewable_pct_tonnes}}%) versus the'),
    # ARR redeemed
    ("ARR was {{redemption.arr_redeemed_pct}}%", "ARR was {{redemption.arr_redeemed_pct}}%"),  # already done
    ("ARR was 91.3%", "ARR was {{redemption.arr_redeemed_pct}}%"),
    # selection coefficient in tables/figures
    ("coefficient = {{selection.selection_coefficient}}", "coefficient = {{selection.selection_coefficient}}"),  # already
    ("coefficient = 1.87", "coefficient = {{selection.selection_coefficient}}"),
    ("selection coefficient (1.87", "selection coefficient ({{selection.selection_coefficient}}"),
    # 1187 deposits
    ("all 1,187 deposit", "all {{composition.n_deposits}} deposit"),
    ("1187 deposit", "{{composition.n_deposits}} deposit"),
    ("1187 BCT deposit", "{{composition.n_deposits}} BCT deposit"),
    ("1,187 deposits", "{{composition.n_deposits}} deposits"),
    ("$n$ = 1187", "$n$ = {{composition.n_deposits}}"),
    # 35432 redemptions
    ("35,432 redemptions", "{{redemption.n_transfer_events}} redemptions"),
    ("35432 redemption", "{{redemption.n_transfer_events}} redemption"),
    ("35432 Transfer", "{{redemption.n_transfer_events}} Transfer"),
    ("35,432 Transfer", "{{redemption.n_transfer_events}} Transfer"),
]


def apply_targeted(text, dry_run=False):
    """Apply targeted string replacements."""
    count = 0
    for old, new in TARGETED:
        if old == new:
            continue
        if old in text:
            n = text.count(old)
            if not dry_run:
                text = text.replace(old, new)
            count += n
            if dry_run:
                print(f"  [{n}x] {old[:60]} → {new[:60]}")
    return text, count


def main():
    dry_run = "--dry-run" in sys.argv
    total = 0

    for fpath in SECTION_FILES:
        text = fpath.read_text()
        new_text, count = apply_targeted(text, dry_run=dry_run)
        total += count

        if count > 0:
            print(f"{fpath.name}: {count} replacements")
            if not dry_run:
                fpath.write_text(new_text)

    print(f"\nTotal: {total} replacements {'(dry run)' if dry_run else '(applied)'}")


if __name__ == "__main__":
    main()
