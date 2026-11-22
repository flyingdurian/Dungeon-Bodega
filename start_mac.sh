#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ ! -d .venv ]]; then
  "$PYTHON_BIN" -m venv .venv
fi
source .venv/bin/activate
if ! python -c 'import fastapi, httpx, PIL' >/dev/null 2>&1; then
  python -m pip install -r requirements-game.txt
fi
if [[ ! -f godot/assets/customer_silas_neutral.png || ! -f godot/assets/shop_bg.png || ! -f godot/assets/item_mana_potion.png ]]; then
  echo 'Generating bundled original shop assets...'
  python tools/make_art.py
  python tools/make_items.py
fi
if [[ "${LIVING_COUNTER_OFFLINE:-0}" == "1" || "${EXODIA_ENABLED:-1}" == "0" ]]; then
  echo 'NPC dialogue: OFFLINE RULES demo (no Exodia task calls).'
else
  echo "NPC dialogue: EXODIA browser tasks (${EXODIA_PROVIDER:-deepseek} at ${EXODIA_URL:-http://127.0.0.1:8765})"
  echo 'Sign in to the selected provider using Exodia browser windows before testing.'
fi
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  echo 'Push-to-talk transcription: separately configured remote STT provider.'
else
  echo 'Push-to-talk transcription: not configured (typed conversation works).'
fi
echo "Hermes speech: ${HERMES_URL:-http://10.0.0.129:8000} (set in Godot Settings if using port 8880)"
echo 'Game director: http://127.0.0.1:8010/docs'
echo 'Launch Godot separately: godot --path godot'
exec python -m uvicorn backend.app:app --host 127.0.0.1 --port 8010 --workers 1 --log-level warning
