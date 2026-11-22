# V1.1.0 Living Encounters — Windows Acceptance Checklist

## Setup and regression

Use a new extracted full project folder; copy `.env` and optionally your backed-up `save/world.json`. Preserve Exodia provider configuration: `groq` and `gemini-api` use API transport, `deepseek/gemini/chatgpt` use browser. No keys in the game.

1. In PowerShell from `The_Living_Counter_POC`, run `powershell -ExecutionPolicy Bypass -File .\tools\preflight_v11_windows.ps1`. Verify Python tests pass, check the *reported* production-art gaps, then run native Godot parser if installed. The art validator's non-strict report does **not** mean all character rigs pass the gate.
2. Run backend launcher; inspect `/health` for version `1.1.0`; open `godot/project.godot`, run the scene and inspect the Godot debugger for parser/runtime errors.
3. At the scaled 1280×800 window verify no overlap between the visitor rail, large portrait, dialogue text, 3 encounter buttons, right-side trade controls and microphone input.

## Living Encounters test paths

- Open **Maya** using the new left visitor rail. A case title appears at the speech frame; hover to read its motive.
- Select **Inspect object**. A detail is spoken; no gold or merchandise changes. The button becomes unavailable for repeated rewards.
- Select **Ask origin**. A new concern is revealed; the case title still reflects the current situation.
- Select **Offer assistance**. The case resolves and a future opportunity appears. Press **F12** to verify the lead is saved. Restart the backend and reopen F12: the same lead persists.
- Repeat the actions by speaking *"Let me inspect that item"*, *"Tell me where you got it"* and *"Let me help you"* using Hold-to-Talk. These should map to the same server actions.
- Speak four ordinary casual lines to Maya or Garrick; customer reveals one new concern without an arbitrary cash change. Each case has only one scripted initiative to avoid incessant interruptions.
- Repeat with **Liu Xue** and check that authoritatively revealed facts are voiced primarily in Mandarin.
- Select **Garrick** and inspect his artifact. Walk away and return: existing economy, memory and stock save must still work.
- Attempt a monetary offer while an encounter remains open; the existing price/conditional bundle logic must still be authoritative.
- During an Exodia response, contextual buttons must not create conflicting turns.
- Check negative cases: nonexistent session, invalid action, duplicate turn, action after encounter closed.

## Art sign-off (currently outstanding)

Review `docs/V110_ART_BIBLE.md`, `art/character_art_manifest_v11.json`, and `art/Elara_Veyne_8_Expressions_Original_Sheet.png`. The contact sheet is **not** a replacement for high-resolution production character portraits. Don't sign off an art-complete release until the strict validator passes for all four new visitors and the actual Godot portraits visually match their approved identity anchors.

## Audio & performance

Keep your known-good fast API provider. Exodia dialogue still uses `/api/command/tasks/game-dialogue`; encounter actions resolve locally and are labeled `LIVING ENCOUNTER · GAME`, not mistaken for Exodia fallback. Do not change Hermes request speed/pitch to mask a slow audio problem. Use F5 to compare generated PCM duration and playback time under a fixed character preset.
