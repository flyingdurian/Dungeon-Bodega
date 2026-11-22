"""Read-only Exodia diagnostics; makes NO browser-model tasks and edits NO settings."""
import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.exodia import ExodiaClient, ExodiaError

try:
    client = ExodiaClient()
    try:
        print(f"Exodia: {client.url}; browser model: {client.provider}; agent: kiko")
        providers = client._json('GET', '/api/command/providers')
        print('Providers check: PASS (HTTP 200; local dashboard header accepted)')
        instructions = client._json('GET', '/api/command/model-instructions')
        text = next((str(v.get('text', '')) for v in instructions.get('models', [])
                     if v.get('provider') == client.provider), '')
        print(f'Active model saved instruction length: {len(text)} / 4000 chars')
        if text and 'mines' in text.lower():
            print('CAUTION: saved model instructions mention Mines; other game rules may conflict.')
        print('No model task was created. Log into the browser UI before starting gameplay.')
    finally:
        client.close()
except ExodiaError as e:
    print(f'Exodia: FAIL: {e}', file=sys.stderr)
    sys.exit(1)
