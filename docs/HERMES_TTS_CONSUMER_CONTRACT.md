# Dungeon Bodega — Hermes-Engine Consumer Contract

Hermes-Engine is an independent reusable TTS/speaking-model service. Dungeon Bodega owns only its Godot consumer (`godot/scripts/HermesStream.gd`), `HERMES_URL` configuration, NPC voice mapping, playback queue, diagnostics and consumer tests. Read `docs/PROJECT_BOUNDARIES.md` first. Never copy Hermes server, Studio, models, model dependencies, recordings or release code into this game.

- Confirm `GET {HERMES_URL}/health` before live integration tests. Historic service addresses include `http://10.0.0.129:8000` and port `8880`; neither is assumed active.
- `POST {HERMES_URL}/stream` sends a game-side voice/engine request and returns raw mono PCM16 signed little-endian, not WAV. Use nominal 24 kHz and honor the service's `X-Sample-Rate` when present.
- `GET /reaction/{archetype}/{tag}` is optional; absence must not block text dialogue.
- Do not stop the Godot PCM generator at network EOF; let the last queued sample play. Typewriter pace follows speech only approximately; there are no word/phoneme timestamps.
- Local barge-in must stop speaking and reveal promptly and must suppress stale replies, without rolling back a previously committed trade.
- Preserve NPC voice identity, playback queue, normal 1.0 speed and truthful F4/F5 diagnostics. If Hermes is offline, typed dialogue and deterministic trading must remain playable.

Before adapting the consumer, verify the active external Hermes API. Update only game-side adapter, configuration and tests; service changes must remain in Hermes-Engine's own repository and release process.
