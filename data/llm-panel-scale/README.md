# LLM Panel at Scale — Paper 1 infrastructure

This is the MVP + scale-up pipeline for Paper 1 (NeurIPS 2027 Datasets & Benchmarks / KDD 2027). It extends the 29-credit `data/llm-panel-irr/` study to the full VCM (targeting 2000 projects), with a multi-provider panel.

See `docs/neurips-paper/draft.md` and `docs/neurips-paper/api-key-budget.md` for the paper and the budget/staging plan.

## Components

1. **`evidence_pack_builder.py`** — builds one standardized JSON pack per project.
2. **`run_panel.py`** — for each (project × model) pair, sends a scoring prompt and writes a JSONL row. Supports `--providers claude-only` (MVP) or `--providers full`. Falls back to a clearly-flagged synthetic archetype stub when no provider key is available.
3. **`validate.py`** — IRR (Fleiss' κ, ICC, Cohen's κ), external correlation, stress-test recall.

## Directory layout

```
data/llm-panel-scale/
  evidence_pack_builder.py
  run_panel.py
  validate.py
  evidence-packs-cache/       # 168 pre-built packs for the BCT universe
  stress-packs/               # 4 adversarial stress-test packs
  runs/
    bct168-mvp/
      panel_scores.jsonl          # one row per (project × model)
      validation_summary.json     # IRR output
      per_project_composites.csv  # per-project composite and grade
      run_summary.json
    bct168-stress/
      panel_scores.jsonl          # the 4 stress credits scored by the panel
      run_summary.json
```

## Quickstart

```bash
# 1. Build evidence packs for the 168 BCT projects (already done; re-run with --force to rebuild)
python3 data/llm-panel-scale/evidence_pack_builder.py

# 2. Set your API key and run the panel
export ANTHROPIC_API_KEY=sk-ant-...
python3 data/llm-panel-scale/run_panel.py --run-id bct168-mvp --providers claude-only --only-real
python3 data/llm-panel-scale/run_panel.py --run-id bct168-stress \
    --packs-dir data/llm-panel-scale/stress-packs --providers claude-only --only-real

# 3. Validate
python3 data/llm-panel-scale/validate.py --run-id bct168-mvp --stress-run-id bct168-stress
```

## Notes

- Without an `ANTHROPIC_API_KEY`, the runner falls back to a deterministic archetype-based stub. Those rows are clearly flagged with `mode: "synthetic-archetype-fallback"` and should NOT be reported as model scores.
- The `--only-real` flag drops the synthetic fallback rows entirely, so any `runs/<id>/panel_scores.jsonl` contains live scores only.
- The runner is idempotent: re-running with the same `--run-id` skips `(registry, project_id, model)` triples already present.
- Evidence-pack scraping is resilient to network failure; packs fall back to `evidence_level: "metadata-only"` and record the status per source in `provenance`.

## v0.6 workstream

1. Playwright-based Verra/GS scraper for real page-scraped evidence packs on the 500/2000 scale-ups.
2. PDF-body extraction for PDDs and monitoring reports (via `pypdf`/`pdfplumber`).
3. OpenAI, Google, and open-weight provider integrations (`call_openai_stub`, `call_google_stub` currently return `{status: "stub"}`).
4. Per-dimension band-walk: validator emits one plot per dimension showing Claude opus / sonnet / haiku score distributions.
5. Expert Delphi comparison harness (takes a `delphi_consensus.jsonl` and reports `expert vs panel` κ).
