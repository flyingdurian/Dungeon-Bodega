# The Living Counter v0.4 — First Real Playtest Hotfix

**Target:** Windows Godot 4.4+ client + Windows-local Exodia (typically `127.0.0.1:8766`) + Mac Hermes (`10.0.0.129:8000` or `:8880`).

## Corrected from actual player feedback

- **Live answer being discarded:** Exodia previously generated complete answers that were falsely rejected by a very broad price-word filter (`offer`, `gold`, `cost`, `price`, `buy`) and metadata keyword filter (including brand names). V0.4 recognizes ordinary speech such as "that price is steep", "I can't afford it", "ChatGPT", or "GTA 6"; explicit invented contract commitments remain blocked. The dialogue job reports a precise `error` and `source` on fallback. All Exodia tasks still use kiosk/browser contract and existing serialized dispatcher.
- **Walking out means walking out:** directed severe abuse has authoritative patience/trust penalties and can close the encounter immediately. Live Exodia declaration of an explicit departure now becomes a server-side walkout **before** the text/audio response is returned; this path does not change gold or inventory. A terminal walkout or accepted deal never appends a further counteroffer. Stale, interrupted jobs do not close newer turns.
- **No more price nagging every sentence:** ordinary chat brings up the current valid offer only after every third consecutive banter turn (and still on true counters). Fantasy visitors still recognize technology as unfamiliar; modern visitors know iPhones and GTA 6 and aren't penalized for chatting about them.
- **Twenty NPC profiles:** original fantasy ten kept intact plus ten contemporary visitors (Gen Z, millennial, older, collector, technician, data-minded, etc.). Settings supports `Mixed / Fantasy / Modern` and a customer picker; the game `/encounter` API accepts optional `era` with the same values. Existing inventory/currency remains the intentionally experimental magical-crossroads setting.
- **UI first pass:** new richly illustrated shop backdrop, warmer purple-and-gold action buttons, visible quick actions for Accept / Counter +/-10g / List Price / End Negotiation, and updated in-game version marker. The generated UI concept illustration is included as **directional reference only**; actual Godot UI is not an exact reproduction.
- **Diagnostics:** opt-in `GET /diagnostics/dialogue` returns only recent job IDs/status/source/error (no prompt, model answer or secrets). It requires `LIVING_COUNTER_DEBUG=1` and loopback access.

## Known visual limitation

The user disliked the original vector-looking characters. The new shop scene is a real runtime asset, but the 10 contemporary profiles currently use **adapted temporary expression sprites from the existing rig**, NOT ten new dedicated high-fidelity character illustrations. Original fantasy portraits also remain unchanged. Premium character art, 2.5D animation, responsive UI layout and portrait fidelity need a subsequent dedicated art milestone. Do not present the included concept UI as a screenshot of the running Godot build.

## Installation — preserving your working configuration

1. Stop the Living Counter Python process and close Godot. Exodia and Hermes can remain running.
2. **Back up** your current `The_Living_Counter_POC` folder.
3. Unzip `The_Living_Counter_v0.4_Hotfix_Overlay.zip` into your existing `The_Living_Counter_POC` folder. Allow overwrites. Do not delete `.venv`, `.env`, or `save/`.
4. Your `.env` must retain `EXODIA_URL=http://127.0.0.1:8766` (or the Exodia port **you** confirmed) and `HERMES_URL=http://10.0.0.129:8000` (or active :8880).
5. Start with `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1` so `.env` loads; don't use raw Uvicorn unless you explicitly set env vars.
6. Open Godot (`godot/project.godot`), F5, choose **Settings > Visitor roster > Modern**; choose Maya or Kai and press Next Visitor. Existing saved world gold/stock/relationships remain intact.
7. To investigate fallback, set `LIVING_COUNTER_DEBUG=1` in `.env`, restart the director, then visit `http://127.0.0.1:8010/diagnostics/dialogue`. This reports *why* an Exodia response was discarded without publishing player speech or prompts. If you share diagnostics, review sensitive information first.
8. Run `./.venv/Scripts/python.exe -m pytest tests/ -q` (PowerShell spelling `\.venv\Scripts\python.exe -m pytest tests\ -q`) if `pytest` is installed.

## What needs testing on Windows (not validated here)

- Visual alignment at actual Godot window size, modern roster images, mouse/keyboard flow, and terminal customer exits.
- Signed-in Exodia browser/model output, rejection rate, and whether spontaneous departure language results in actual walkout.
- Hermes real time speech, typewriter pacing, and manual interruptions. Audio code is unchanged from v0.3.
- Save compatibility and Windows permission/antivirus behavior.

## Verification

`python -m pytest tests/ -q` => **50 passed** in the available Linux/Python environment. Compiled all Python modules. **No actual Windows Godot, MLX or signed-in Exodia test was possible.** These are acceptance gates, not claims of live verification.

## Follow-up work (not in this hotfix)

Replace all 20 portrait rigs with individually approved, high-fidelity assets; redesign responsive Godot UI (concept reference attached); voice-aligned word timings instead of approximate typewriter pacing; microphone STT without external API reliance; richer memory/intent evaluator and relationship arc; measurable player-heard latency telemetry.
