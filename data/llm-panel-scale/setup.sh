#!/usr/bin/env bash
# Provision the Python environment for the LLM panel pipeline.
#
# Creates a local venv at .venv (gitignored) with the anthropic SDK and
# writes a wrapper that routes `python3 data/llm-panel-scale/*.py` through it.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${HERE}/.venv"

if [ ! -d "${VENV}" ]; then
  echo "Creating venv at ${VENV}"
  python3 -m venv "${VENV}"
fi

"${VENV}/bin/pip" install --quiet --upgrade pip
"${VENV}/bin/pip" install --quiet anthropic

echo "Environment ready. Activate with:"
echo "  source ${VENV}/bin/activate"
echo "Then set:"
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
echo "And run:"
echo "  python data/llm-panel-scale/run_panel.py --run-id bct168-mvp --providers claude-only --only-real"
