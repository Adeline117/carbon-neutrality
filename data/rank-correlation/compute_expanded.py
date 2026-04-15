#!/usr/bin/env python3
"""Compute Spearman rank correlation on the full expanded dataset (n=27 with BeZero)."""

import json
import math

# Our grade scale: B=0, BB=1, BBB=2, A=3, AA=4, AAA=5
# BeZero scale: D=0, C=1, B=2, BB=3, BBB=4, A=5, AA=6, AAA=7

OUR_SCALE = {"B": 0, "BB": 1, "BBB": 2, "A": 3, "AA": 4, "AAA": 5}
BZ_SCALE = {"D": 0, "C": 1, "B": 2, "BB": 3, "BBB": 4, "A": 5, "AA": 6, "AAA": 7}

# Full dataset: all 30 projects with our grade and BeZero grade
# From expanded_dataset.md (existing 20) + new_scores.md (10 new)
data = [
    # Original 18 paired (from existing analysis)
    ("EXP01", "Ecomapua", "BB", "C"),
    ("EXP02", "Keo Seima", "BBB", "A"),
    ("EXP03", "Mai Ndombe", "BB", "BB"),
    ("EXP04", "Envira", "BB", "BBB"),
    ("EXP05", "Luangwa", "BB", "B"),
    ("EXP06", "Guanare", "BB", "B"),
    ("EXP07", "Climeworks Orca", "AAA", "AAA"),
    ("EXP08", "Novocarbo Rhine", "AA", "A"),
    ("EXP09", "Exomad Green", "AA", "AA"),
    ("EXP10", "EcoSafi Cookstove", "BBB", "A"),
    # EXP11, EXP12: no BeZero
    ("EXP13", "Rebellion H1", "A", "A"),
    ("EXP14", "Family Forest", "BBB", "BBB"),
    ("EXP15", "Southern Cardamom", "B", "B"),
    ("EXP16", "Qnergy LFG", "BBB", "A"),
    ("EXP17", "Chinese Wind", "B", "C"),
    ("EXP18", "Kariba", "B", "D"),
    ("EXP29", "Rimba Raya", "B", "BB"),
    ("EXP30", "Cordillera Azul", "B", "C"),
    # New 9 with BeZero (EXP28 has no BeZero)
    ("EXP19", "STRATOS DACCS", "AAA", "AAA"),
    ("EXP20", "Octavia DAC", "AAA", "AAA"),
    ("EXP21", "Mati Carbon ERW", "AA", "AA"),
    ("EXP22", "Tradewater ODS", "A", "A"),
    ("EXP23", "Rebellion H2", "BBB", "BB"),
    ("EXP24", "Rebellion H3", "BBB", "BB"),
    ("EXP25", "Guyana J-REDD+", "BBB", "BB"),
    ("EXP26", "BRCarbon APD", "BBB", "A"),
    ("EXP27", "Brazil Nut", "BB", "C"),
]

n = len(data)
print(f"Total paired projects (ours + BeZero): n={n}")

# Convert to numeric
ours = [OUR_SCALE[d[2]] for d in data]
bezero = [BZ_SCALE[d[3]] for d in data]


def rank(values):
    """Compute ranks with average tie-breaking."""
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based average rank
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def spearman(x, y):
    """Compute Spearman rank correlation."""
    rx = rank(x)
    ry = rank(y)
    n = len(x)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def kendall_tau(x, y):
    """Compute Kendall's tau-b."""
    n = len(x)
    concordant = 0
    discordant = 0
    tied_x = 0
    tied_y = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            if dx == 0 and dy == 0:
                tied_x += 1
                tied_y += 1
            elif dx == 0:
                tied_x += 1
            elif dy == 0:
                tied_y += 1
            elif (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
                concordant += 1
            else:
                discordant += 1
    total = n * (n - 1) / 2
    den = math.sqrt((total - tied_x) * (total - tied_y))
    if den == 0:
        return 0.0
    return (concordant - discordant) / den


rho = spearman(ours, bezero)
tau = kendall_tau(ours, bezero)

print(f"Spearman rho: {rho:+.3f}")
print(f"Kendall tau-b: {tau:+.3f}")

# Grade agreement stats
exact = sum(1 for d in data if OUR_SCALE[d[2]] == BZ_SCALE.get(d[3], -99))
# Can't compare directly since scales differ. Let's do ordinal distance.
# Map both to a common scale: our B..AAA = 0..5, BeZero D..AAA = 0..7
# For agreement, check grade equivalence where possible
grade_map_bz_to_ours = {"D": "B", "C": "B", "B": "BB", "BB": "BB", "BBB": "BBB", "A": "A", "AA": "AA", "AAA": "AAA"}
exact_mapped = sum(1 for d in data if d[2] == grade_map_bz_to_ours[d[3]])
within_1 = sum(1 for d in data if abs(OUR_SCALE[d[2]] - OUR_SCALE.get(grade_map_bz_to_ours[d[3]], -99)) <= 1)

print(f"\nGrade agreement (mapping BeZero to our scale):")
print(f"  Exact match: {exact_mapped}/{n} ({100*exact_mapped/n:.0f}%)")
print(f"  Within ±1 grade: {within_1}/{n} ({100*within_1/n:.0f}%)")

# Per-project details
print(f"\n{'ID':<8} {'Name':<25} {'Ours':<6} {'BeZero':<8} {'BZ→Ours':<8} {'Match?'}")
print("-" * 70)
for d in data:
    mapped = grade_map_bz_to_ours[d[3]]
    match = "✓" if d[2] == mapped else f"Δ{abs(OUR_SCALE[d[2]] - OUR_SCALE[mapped])}"
    print(f"{d[0]:<8} {d[1]:<25} {d[2]:<6} {d[3]:<8} {mapped:<8} {match}")

# Save results
results = {
    "n": n,
    "spearman_rho": round(rho, 3),
    "kendall_tau": round(tau, 3),
    "exact_match_rate": round(exact_mapped / n, 3),
    "within_1_rate": round(within_1 / n, 3),
    "projects": [{"id": d[0], "name": d[1], "our_grade": d[2], "bezero_grade": d[3]} for d in data]
}
with open("/Users/adelinewen/carbon-neutrality/data/rank-correlation/expanded_correlation.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to expanded_correlation.json")
