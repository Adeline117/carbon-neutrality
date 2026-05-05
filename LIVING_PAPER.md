# Living Paper Orchestration System

## Project Context (Filled)

| Field | Value |
|-------|-------|
| Paper path | `docs/natcomms-draft/` (5 markdown files) |
| Experiment/data path | `data/` (18 analysis subdirectories) |
| Experiment state | Redemption analysis active; price-quality feedback loop confirmed; statistical robustness complete |
| Target journal | Nature Communications |
| Submission deadline | Aug–Sep 2026 |
| Camera-ready | TBD (post-review) |
| Format | Markdown (not LaTeX) |

## Architecture

```
results/
  manifest.json          ← Single source of truth (all numbers)
  manifest.schema.json   ← Schema + naming conventions

tools/living-paper/
  fill_manifest.py       ← Substitute {{placeholders}} → values
  update_manifest.py     ← Scan source JSONs → update manifest
  audit.py               ← Agent D's integrity checker

review/
  B_impact_report.md     ← Agent B output (auto-generated)
  C_major_changes.md     ← Agent C output (needs human confirm)
  D_audit_*.md           ← Agent D audit reports

docs/natcomms-draft/
  sections-*.md          ← Paper content (Layer 1 stable + Layer 2 placeholders)
```

## Layer Architecture

### Layer 1 — Stable (write-once, direction-agnostic)
- Abstract structure (numbers as `{{placeholders}}`)
- Introduction motivation + problem statement
- Methods description (scoring rubric, pipeline, blockchain queries)
- Notation and definitions
- Experimental setup framework
- Design-level limitations
- Conclusion framing

**Layer 1 rule**: every sentence must remain correct if experiment results flip 2×.

### Layer 2 — Fluid (auto-filled from manifest)
- All specific numbers (PQD, ρ, p-values, %)
- Comparative claims ("X outperforms Y by Z%")
- Table cell values
- Figure references to specific magnitudes
- Data-dependent limitation items

**Placeholder format**: `{{category.metric}}` e.g., `{{composition.renewable_pct_tonnes}}`

## Agent Roles

### Agent A: Structure Stabilizer
**Trigger**: Manual ("稳定化一下" / "run Agent A")
**Task**:
1. Scan paper → classify every paragraph as Layer 1 or Layer 2
2. Write Layer 1 to submission quality (direction-agnostic)
3. Replace Layer 2 numbers with `{{placeholders}}`
4. Mark ambiguous paragraphs with `<!-- FLUID: [description] -->`

**Constraint**: "You are writing a paper with **undetermined** experiment results. Every Layer 1 sentence must remain correct if results flip 2×."

### Agent B: Experiment Tracker
**Trigger**: When `results/` source files change, or "更新数字 [experiment]"
**Task**:
1. Run `python tools/living-paper/update_manifest.py`
2. Compare old vs new values
3. Generate `review/B_impact_report.md`
4. Flag claims whose direction might need adjustment

**Constraint**: "You are a data pipeline, not a narrator. You update numbers, not prose."

### Agent C: Narrative Maintainer
**Trigger**: Agent B flags "claim direction may need adjustment"
**Task**:
1. Read `review/B_impact_report.md`
2. For each flagged claim: adjust strength, flip direction, or delete
3. Major direction flips → `review/C_major_changes.md` (STOP, ask human)
4. Default to weakening, not strengthening

**Constraint**: "You are a defensive narrative maintainer. Your default action is to **weaken claims**, not chase every fluctuation."

### Agent D: Integrity Auditor
**Trigger**: "做一次 freeze audit" / "adversarial review 一下" / deadline proximity
**Modes**: 72h, 24h, adversarial
**Tool**: `python tools/living-paper/audit.py --mode [72h|24h|adversarial]`

## Human Intervention Points (MUST STOP)

- [ ] Agent A: paragraph classification ambiguity
- [ ] Agent B: manifest key collision
- [ ] Agent C: `C_major_changes.md` non-empty
- [ ] Agent D: Blocking list non-empty
- [ ] Result flips paper's main thesis

## Command Interface

| Command | Action |
|---------|--------|
| `稳定化一下` | Agent A: stabilize Layer 1 |
| `更新数字 [experiment]` | Agent B: update manifest from source |
| `锁一下 [section]` | Freeze: replace {{placeholders}} with current values |
| `解锁 [section]` | Re-fluid: extract values back to placeholders |
| `做一次 freeze audit` | Agent D: 72h mode |
| `adversarial review 一下` | Agent D: adversarial mode |
| `show me orphaned` | List all ORPHANED markers |

## Bootstrap Sequence

1. **Day 1**: Run Agent A → stabilize Layer 1 + create all placeholders
2. **Day 1+**: Agent B watches source files, updates manifest on change
3. **On B flags**: Agent C adjusts narrative
4. **Deadline -72h/-24h**: Agent D audits

## Current Status

- [x] Manifest created with all current values (2026-04-20)
- [x] Schema defined
- [x] Fill script ready
- [x] Update script ready
- [x] Audit script ready
- [ ] Paper sections not yet placeholder-ized (Agent A not yet run)
- [ ] Agent B not yet triggered (no source file changes since setup)
