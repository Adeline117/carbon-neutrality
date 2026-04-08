#!/usr/bin/env python3
"""Extract the final scored JSON from each LLM rater's transcript JSONL file.

The 3 rater subagents (Opus, Sonnet, Haiku) each emitted a single assistant
message containing a JSON code block at the end. We walk the transcripts,
find the final assistant message per rater, pull the ```json``` block, and
write it to data/llm-panel-irr/raw/<model_id>/scored.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_ROOT = ROOT / "raw"

TRANSCRIPTS = {
    "claude-opus-4-6": Path(
        "/Users/adelinewen/.claude/projects/-Users-adelinewen-carbon-neutrality/"
        "e0ae360e-ec50-48e7-80ce-d2703665bdac/subagents/agent-a06c603fca666fa26.jsonl"
    ),
    "claude-sonnet-4-6": Path(
        "/Users/adelinewen/.claude/projects/-Users-adelinewen-carbon-neutrality/"
        "e0ae360e-ec50-48e7-80ce-d2703665bdac/subagents/agent-a6c848578d9b60d8b.jsonl"
    ),
    "claude-haiku-4-5": Path(
        "/Users/adelinewen/.claude/projects/-Users-adelinewen-carbon-neutrality/"
        "e0ae360e-ec50-48e7-80ce-d2703665bdac/subagents/agent-ad39d42065f452eb1.jsonl"
    ),
}

JSON_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def extract_final_assistant_text(transcript_path: Path) -> str:
    """Return the last assistant text message in the transcript."""
    lines = transcript_path.read_text().splitlines()
    last_text = ""
    for line in lines:
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "assistant":
            continue
        msg = d.get("message", {})
        for c in msg.get("content", []):
            if isinstance(c, dict) and c.get("type") == "text":
                last_text = c.get("text", last_text)
    return last_text


def extract_scored_json(text: str) -> dict:
    """Pull the last ```json``` fenced block and parse it."""
    matches = JSON_BLOCK.findall(text)
    if not matches:
        # Sometimes there's no json fence; try finding a bare {...}
        # Fall through with raise if we can't find one.
        raise ValueError("No json code block found")
    # Prefer the LAST match (the final answer)
    return json.loads(matches[-1])


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    summary = []
    for model_id, transcript in TRANSCRIPTS.items():
        if not transcript.exists():
            print(f"{model_id}: transcript missing at {transcript}")
            continue
        text = extract_final_assistant_text(transcript)
        try:
            scored = extract_scored_json(text)
        except Exception as e:
            print(f"{model_id}: failed to extract — {e}")
            continue

        out_dir = OUT_ROOT / model_id
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "scored.json").write_text(json.dumps(scored, indent=2))

        n_credits = len(scored.get("credits", []))
        print(f"{model_id}: extracted {n_credits} credits -> {out_dir / 'scored.json'}")
        summary.append({"model": model_id, "n": n_credits})

    (OUT_ROOT / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
