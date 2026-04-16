# Paper 1 MVP Run Status

*2026-04-15. Status of the 168-project Paper 1 MVP run.*

## Summary

- Infrastructure: **built end-to-end**. `evidence_pack_builder.py` + `run_panel.py` + `validate.py` form a complete pipeline. All three were exercised successfully against 168 real BCT projects × 3 panel models × 4 stress-test credits.
- Evidence packs: **168/168 built**, checked into `data/llm-panel-scale/evidence-packs-cache/`. Every pack draws from the existing on-chain BCT dataset and archetype-coded Verra metadata. `evidence_level: "metadata-only"` for all 168 because Verra's public detail page is a JS SPA that urllib cannot parse; a Playwright scraper is the v0.6 upgrade.
- Panel run: **dry-run only**. `runs/bct168-mvp/panel_scores.jsonl` has 504 rows (168 × 3) but all are `mode: "synthetic-archetype-fallback"` because `ANTHROPIC_API_KEY` is not present in the execution environment. The Anthropic SDK v0.95.0 is installed in `/tmp/llm-panel-venv` and the network reaches the Anthropic API (verified by seeing a 401 on an invalid key), so the only missing item is the API key itself.
- Stress tests: **4 synthetic packs built** (`stress-packs/`) and scored; recall is 0/12 under the synthetic fallback (the fallback does not assign disqualifier flags).
- Validator: **runs clean**. It flags dry-run status in `validation_summary.json` and in the stdout report.
- Paper: **draft with placeholders** at `docs/neurips-paper/draft.md`. Every numerical claim from the MVP is marked `[PLACEHOLDER-*]` until live rows land.
- Budget: **documented** at `docs/neurips-paper/api-key-budget.md`. Claude-only MVP ≈ $43; full panel on 2000 projects ≈ $1,150.

## To run for real (10 minutes of setup + ~1h of runtime)

```bash
cd /Users/adelinewen/carbon-neutrality
bash data/llm-panel-scale/setup.sh           # provisions local venv with anthropic SDK
source data/llm-panel-scale/.venv/bin/activate
export ANTHROPIC_API_KEY=sk-ant-<your key>

python data/llm-panel-scale/run_panel.py --run-id bct168-mvp --providers claude-only --only-real
python data/llm-panel-scale/run_panel.py --run-id bct168-stress \
    --packs-dir data/llm-panel-scale/stress-packs --providers claude-only --only-real
python data/llm-panel-scale/validate.py --run-id bct168-mvp --stress-run-id bct168-stress
```

The runner is idempotent. Re-executing after an interruption picks up exactly where it stopped (keyed on `(registry, project_id, model)`).

## Open items

1. `ANTHROPIC_API_KEY` → run the real Claude panel (Stage 1).
2. Playwright scraper → real evidence packs beyond metadata-only (Stage 2 prereq).
3. `OPENAI_API_KEY` + `GOOGLE_API_KEY` → 5-provider panel (Stage 4).
4. Compute for Llama-4-405B and DeepSeek-R2 → full 7-model panel.
5. Expert Delphi recruitment → ground-truth validity bound (paper §6).
6. Paper 4 satellite correlation → external-observable-quality check (paper §7).

None of these block today's commit. The pipeline is the deliverable.
