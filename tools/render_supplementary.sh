#!/bin/bash
# Render the submission Supplementary Information PDF from the authoritative
# markdown: resolve {{placeholders}} via the living-paper manifest, swap math
# Greek for text glyphs (font compatibility), then pandoc -> xelatex.
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
python3 tools/living-paper/fill_manifest.py docs/natcomms-draft/supplementary-information.md > "$TMP/si.md"
python3 - "$TMP/si.md" <<'EOF'
import sys
p = sys.argv[1]
s = open(p).read()
for a, b in [(r'$\rho$', 'ρ'), (r'$\tau$-b', 'τ-b'), (r'$\tau$', 'τ'), (r'$\kappa$', 'κ'),
             (r'$\Gamma$', 'Γ'), (r'$\beta$', 'β'), (r'$\geq$', '≥'), (r'$\leq$', '≤')]:
    s = s.replace(a, b)
open(p, 'w').write(s)
EOF
pandoc "$TMP/si.md" -o docs/natcomms-draft/latex/supplementary.pdf \
  --pdf-engine=/Library/TeX/texbin/xelatex \
  -V geometry:margin=2.5cm -V fontsize=11pt \
  -V mainfont="Times New Roman" -V mathfont="STIX Two Math" \
  --metadata title="Supplementary Information: Transparency without pricing"
echo "rendered docs/natcomms-draft/latex/supplementary.pdf"
