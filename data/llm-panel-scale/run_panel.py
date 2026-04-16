#!/usr/bin/env python3
"""Run the LLM panel over a set of evidence packs and a rubric.

For each project × each model in the panel, send a structured scoring prompt
derived from `data/llm-panel-irr/prompt.md`, parse the returned JSON, and
append to `runs/<run_id>/panel_scores.jsonl` (one line per project × model).

Providers:
    --providers claude-only      # Opus 4.6, Sonnet 4.5, Haiku 4.5 (MVP)
    --providers full             # + GPT-5, Gemini, Llama, DeepSeek stubs

If ANTHROPIC_API_KEY is set, the Anthropic client is used for real calls. If
it is not set, the runner writes a "synthetic" row derived from a deterministic
archetype-scoring fallback so downstream pipelines (validate.py, etc.) can
still be exercised. The synthetic fallback is intentionally pessimistic about
itself: every row includes `"mode": "synthetic-archetype-fallback"` so a human
reviewer can always distinguish real model scores from the stub.

Usage:
    python3 run_panel.py --packs-dir ../evidence-packs-cache --run-id bct168-mvp \
        --providers claude-only --limit 10
    python3 run_panel.py --run-id bct168-mvp --providers claude-only  # full 168
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
REPO = Path("/Users/adelinewen/carbon-neutrality")
RUBRICS = REPO / "data" / "scoring-rubrics"
RUNS_DIR = HERE / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

DIMS = [
    "removal_type",
    "additionality",
    "permanence",
    "mrv_grade",
    "vintage_year",
    "co_benefits",
    "registry_methodology",
]

# Closed-set disqualifier IDs and adjustment IDs per the rubric (v0.6.0)
DISQUALIFIERS = [
    "double_counting",
    "failed_verification",
    "sanctioned_registry",
    "no_third_party",
    "human_rights",
    "community_harm",
    "biodiversity_harm",
]
ADJUSTMENTS = ["commercial_plantation_arr"]


# ---------- provider registry ----------

@dataclass
class ModelSpec:
    model_id: str
    provider: str  # "anthropic" | "openai" | "google" | "stub"
    display_name: str


CLAUDE_PANEL: list[ModelSpec] = [
    ModelSpec("claude-opus-4-6", "anthropic", "claude-opus-4-6"),
    ModelSpec("claude-sonnet-4-5", "anthropic", "claude-sonnet-4-5"),
    ModelSpec("claude-haiku-4-5-20251001", "anthropic", "claude-haiku-4-5-20251001"),
]

FULL_PANEL_EXTRA: list[ModelSpec] = [
    ModelSpec("gpt-5", "openai", "gpt-5"),
    ModelSpec("gemini-2.5-pro", "google", "gemini-2.5-pro"),
    ModelSpec("llama-4-405b", "stub", "llama-4-405b"),  # run via local vLLM when keyed up
    ModelSpec("deepseek-r2", "stub", "deepseek-r2"),
]


def resolve_panel(providers: str) -> list[ModelSpec]:
    if providers == "claude-only":
        return CLAUDE_PANEL
    if providers == "full":
        return CLAUDE_PANEL + FULL_PANEL_EXTRA
    raise SystemExit(f"unknown --providers value: {providers!r}")


# ---------- prompt builder ----------

SYSTEM_PROMPT = """You are an independent carbon credit quality reviewer applying version \
0.6.0 of the on-chain carbon credit quality rating framework. You are scoring a single \
carbon credit project in isolation, using ONLY the rubric files provided (as a structured \
rubric object inside the user message) and the evidence pack inside the user message. \
Do NOT look up current market prices, commercial ratings, or anything framework-specific \
beyond the cited rubric bands. Output strict JSON per the schema at the end of the user \
message. Integer scores 0-100 inclusive. Use exactly the closed-set disqualifier and \
adjustment IDs. Do not add any other fields."""


def build_user_prompt(evidence_pack: dict, rubric_bundle: dict) -> str:
    return (
        "## Task\n\n"
        "Score the following carbon credit on the 7 dimensions in the rubric. Return "
        "strict JSON only; no prose outside the JSON.\n\n"
        "## Rubric (v0.6.0)\n\n"
        f"```json\n{json.dumps(rubric_bundle, indent=2)}\n```\n\n"
        "## Evidence pack\n\n"
        f"```json\n{json.dumps(evidence_pack, indent=2)}\n```\n\n"
        "## Output schema\n\n"
        "```json\n"
        "{\n"
        '  "project_ref": {"registry": "<string>", "project_id": "<string>"},\n'
        '  "rater_model": "<string>",\n'
        '  "scored_at": "<ISO timestamp>",\n'
        '  "scores": {\n'
        '    "removal_type": 0, "additionality": 0, "permanence": 0,\n'
        '    "mrv_grade": 0, "vintage_year": 0, "co_benefits": 0,\n'
        '    "registry_methodology": 0\n'
        "  },\n"
        '  "disqualifiers": [],\n'
        '  "adjustments": [],\n'
        '  "reasoning": {\n'
        '    "removal_type": "<1-2 sentences citing which rubric band>",\n'
        '    "additionality": "...",\n'
        '    "permanence": "...",\n'
        '    "mrv_grade": "...",\n'
        '    "vintage_year": "...",\n'
        '    "co_benefits": "...",\n'
        '    "registry_methodology": "..."\n'
        "  }\n"
        "}\n"
        "```\n"
    )


def load_rubric_bundle() -> dict:
    """Load all 8 rubric files into a single bundle that fits inside a single prompt."""
    bundle: dict[str, Any] = {}
    bundle["index"] = json.loads((RUBRICS / "index.json").read_text())
    for f in sorted(RUBRICS.glob("0*.json")):
        bundle[f.stem] = json.loads(f.read_text())
    return bundle


# ---------- JSON extraction ----------

JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)


def extract_json(text: str) -> dict | None:
    """Pull the first JSON object from a model response. Returns None on failure."""
    if not text:
        return None
    # Try fenced code block first
    m = JSON_FENCE_RE.search(text)
    candidate = m.group(1) if m else text.strip()
    # Try the whole string
    for payload in (candidate, text.strip()):
        try:
            return json.loads(payload)
        except Exception:
            continue
    # Fallback: find first {...} balanced block
    stack = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if stack == 0:
                start = i
            stack += 1
        elif ch == "}":
            stack -= 1
            if stack == 0 and start is not None:
                try:
                    return json.loads(text[start : i + 1])
                except Exception:
                    start = None
    return None


# ---------- providers ----------

def call_anthropic(model_id: str, system: str, user: str, max_tokens: int = 2000) -> dict:
    """Call the Anthropic Messages API. Returns a dict with status/text.

    Requires the `anthropic` Python SDK and ANTHROPIC_API_KEY env var.
    """
    try:
        import anthropic  # type: ignore
    except ImportError:
        return {
            "status": "sdk-missing",
            "text": None,
            "error": "pip install anthropic (not installed in this env)",
        }
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "status": "no-api-key",
            "text": None,
            "error": "set ANTHROPIC_API_KEY to enable live calls",
        }
    client = anthropic.Anthropic(api_key=api_key)
    for attempt in range(3):
        try:
            msg = client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            # Claude returns content as a list of blocks
            blocks = msg.content or []
            text = "".join(getattr(b, "text", "") for b in blocks)
            return {
                "status": "ok",
                "text": text,
                "usage": {
                    "input_tokens": getattr(msg.usage, "input_tokens", None),
                    "output_tokens": getattr(msg.usage, "output_tokens", None),
                },
            }
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            time.sleep(2 ** attempt)
    return {"status": "error", "text": None, "error": last_err}


def call_openai_stub(model_id: str, system: str, user: str, **_: Any) -> dict:
    return {
        "status": "stub",
        "text": None,
        "error": "OPENAI_API_KEY not set; add to run GPT-5 leg",
    }


def call_google_stub(model_id: str, system: str, user: str, **_: Any) -> dict:
    return {
        "status": "stub",
        "text": None,
        "error": "GOOGLE_API_KEY not set; add to run Gemini leg",
    }


def call_stub(model_id: str, system: str, user: str, **_: Any) -> dict:
    return {"status": "stub", "text": None, "error": f"no provider wired for {model_id}"}


PROVIDER_DISPATCH: dict[str, Callable[..., dict]] = {
    "anthropic": call_anthropic,
    "openai": call_openai_stub,
    "google": call_google_stub,
    "stub": call_stub,
}


# ---------- synthetic archetype fallback ----------

# When no provider is available, we still need to exercise downstream code. The
# fallback encodes the author's own v0.4.1 archetype scores for the 11 project
# types in project_classification_final.json. This is NOT a model score — every
# row flagged "mode": "synthetic-archetype-fallback" is excluded from IRR
# computations that claim to measure LLM agreement.

ARCHETYPE_BASELINE: dict[str, dict[str, int]] = {
    "Renewable": {
        "removal_type": 25,  # avoidance, low
        "additionality": 20, "permanence": 65, "mrv_grade": 55,
        "vintage_year": 30, "co_benefits": 25, "registry_methodology": 40,
    },
    "Fossil switch": {
        "removal_type": 20, "additionality": 25, "permanence": 55, "mrv_grade": 55,
        "vintage_year": 30, "co_benefits": 20, "registry_methodology": 40,
    },
    "Waste/Methane": {
        "removal_type": 35, "additionality": 55, "permanence": 60, "mrv_grade": 65,
        "vintage_year": 40, "co_benefits": 30, "registry_methodology": 50,
    },
    "REDD+": {
        "removal_type": 30, "additionality": 25, "permanence": 35, "mrv_grade": 40,
        "vintage_year": 30, "co_benefits": 65, "registry_methodology": 30,
    },
    "IFM": {
        "removal_type": 40, "additionality": 30, "permanence": 45, "mrv_grade": 50,
        "vintage_year": 40, "co_benefits": 40, "registry_methodology": 40,
    },
    "ARR": {
        "removal_type": 60, "additionality": 55, "permanence": 50, "mrv_grade": 55,
        "vintage_year": 55, "co_benefits": 60, "registry_methodology": 55,
    },
    "Agriculture": {
        "removal_type": 55, "additionality": 45, "permanence": 35, "mrv_grade": 45,
        "vintage_year": 50, "co_benefits": 55, "registry_methodology": 45,
    },
    "Industrial gas": {
        "removal_type": 40, "additionality": 35, "permanence": 70, "mrv_grade": 70,
        "vintage_year": 35, "co_benefits": 15, "registry_methodology": 35,
    },
    "Industrial": {
        "removal_type": 30, "additionality": 40, "permanence": 55, "mrv_grade": 55,
        "vintage_year": 40, "co_benefits": 30, "registry_methodology": 45,
    },
    "Cookstove": {
        "removal_type": 25, "additionality": 35, "permanence": 25, "mrv_grade": 40,
        "vintage_year": 40, "co_benefits": 55, "registry_methodology": 40,
    },
    "Energy efficiency": {
        "removal_type": 25, "additionality": 35, "permanence": 45, "mrv_grade": 50,
        "vintage_year": 40, "co_benefits": 30, "registry_methodology": 45,
    },
}


def synthetic_score(evidence_pack: dict, model_id: str) -> dict:
    """Deterministic archetype-based scoring that varies slightly per model via
    a hash salt. Used only when no provider is available."""
    arch = evidence_pack["fields"]["type_archetype"]
    base = ARCHETYPE_BASELINE.get(arch, {d: 45 for d in DIMS})
    # Per-model jitter via hash — keeps the synthetic leg reproducible
    salt = int(
        hashlib.md5(
            (model_id + evidence_pack["project_ref"]["project_id"]).encode()
        ).hexdigest(),
        16,
    )
    jitter = [(salt >> (4 * i)) & 0xF for i in range(7)]  # 0..15 per dim
    sign = [1 if (salt >> (3 + 4 * i)) & 1 else -1 for i in range(7)]
    scores = {}
    for i, d in enumerate(DIMS):
        v = base[d] + sign[i] * (jitter[i] - 7)  # -7..+8
        scores[d] = max(0, min(100, v))
    # Vintage year discount from pack vintages
    try:
        vintages = [int(v) for v in (evidence_pack["fields"].get("vintage") or "").split(",") if v]
        if vintages:
            # Apply v0.6 deterministic vintage decay, mildly
            age = 2026 - max(vintages)
            scores["vintage_year"] = max(0, min(100, 80 - 5 * age))
    except Exception:
        pass
    # Cookstove: apply biodiversity_harm? REDD+: apply community_harm only if flagged
    disq: list[str] = []
    return {
        "project_ref": evidence_pack["project_ref"],
        "rater_model": model_id,
        "scored_at": dt.datetime.utcnow().isoformat() + "Z",
        "scores": scores,
        "disqualifiers": disq,
        "adjustments": [],
        "reasoning": {d: f"archetype-baseline[{arch}]" for d in DIMS},
        "mode": "synthetic-archetype-fallback",
    }


# ---------- runner ----------

def score_one(
    evidence_pack: dict,
    rubric_bundle: dict,
    spec: ModelSpec,
) -> dict:
    user = build_user_prompt(evidence_pack, rubric_bundle)
    fn = PROVIDER_DISPATCH.get(spec.provider, call_stub)
    resp = fn(spec.model_id, SYSTEM_PROMPT, user)
    record: dict[str, Any] = {
        "project_ref": evidence_pack["project_ref"],
        "rater_model": spec.model_id,
        "provider": spec.provider,
        "scored_at": dt.datetime.utcnow().isoformat() + "Z",
    }

    if resp.get("status") == "ok":
        parsed = extract_json(resp["text"] or "")
        if parsed is None:
            record["mode"] = "parse-error"
            record["raw_response"] = (resp["text"] or "")[:2000]
            record["scores"] = {d: None for d in DIMS}
            record["disqualifiers"] = []
            record["adjustments"] = []
        else:
            record["mode"] = "live"
            record["scores"] = {d: int(parsed.get("scores", {}).get(d, 0)) for d in DIMS}
            dqs = [d for d in parsed.get("disqualifiers", []) if d in DISQUALIFIERS]
            adjs = [a for a in parsed.get("adjustments", []) if a in ADJUSTMENTS]
            record["disqualifiers"] = dqs
            record["adjustments"] = adjs
            record["reasoning"] = parsed.get("reasoning", {})
            record["usage"] = resp.get("usage", {})
    else:
        # Fall back to synthetic archetype scoring so the pipeline still
        # produces a full run. This row is clearly flagged.
        synth = synthetic_score(evidence_pack, spec.model_id)
        synth["fallback_reason"] = resp.get("status")
        synth["fallback_error"] = resp.get("error")
        record.update(synth)
    return record


def run(
    run_id: str,
    packs_dir: Path,
    panel: list[ModelSpec],
    limit: int | None = None,
    only_real: bool = False,
) -> Path:
    rubric_bundle = load_rubric_bundle()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_dir / "panel_scores.jsonl"

    packs = sorted(packs_dir.glob("*.json"))
    if limit is not None:
        packs = packs[:limit]

    print(f"Scoring {len(packs)} projects × {len(panel)} models -> {out_path}")
    # Track existing rows so re-running is idempotent
    seen: set[tuple[str, str, str]] = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            try:
                r = json.loads(line)
                seen.add((
                    r["project_ref"]["registry"],
                    r["project_ref"]["project_id"],
                    r["rater_model"],
                ))
            except Exception:
                continue

    n_live = 0
    n_synthetic = 0
    with out_path.open("a") as f:
        for pack_path in packs:
            pack = json.loads(pack_path.read_text())
            for spec in panel:
                key = (
                    pack["project_ref"]["registry"],
                    pack["project_ref"]["project_id"],
                    spec.model_id,
                )
                if key in seen:
                    continue
                rec = score_one(pack, rubric_bundle, spec)
                if only_real and rec.get("mode") != "live":
                    continue
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if rec.get("mode") == "live":
                    n_live += 1
                else:
                    n_synthetic += 1
    print(f"  wrote rows: live={n_live} synthetic={n_synthetic}")
    # Summary
    summary = {
        "run_id": run_id,
        "panel": [m.model_id for m in panel],
        "n_projects": len(packs),
        "rows_live": n_live,
        "rows_synthetic": n_synthetic,
        "created_at": dt.datetime.utcnow().isoformat() + "Z",
    }
    (run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))
    return out_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument(
        "--packs-dir",
        type=Path,
        default=HERE / "evidence-packs-cache",
    )
    p.add_argument(
        "--providers",
        default="claude-only",
        choices=["claude-only", "full"],
    )
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--only-real", action="store_true", help="skip synthetic fallback rows")
    args = p.parse_args()
    panel = resolve_panel(args.providers)
    run(args.run_id, args.packs_dir, panel, limit=args.limit, only_real=args.only_real)


if __name__ == "__main__":
    main()
