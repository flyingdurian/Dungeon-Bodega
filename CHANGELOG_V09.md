# The Living Counter V0.9.0 — Hermes Voice Studio & Living Interface

## Implemented in the real Godot project
- Added F5 **Hermes Voice Studio**: monitor voice profile, fixed speaker/engine, requested speed/pitch, server health, played and received PCM durations, stream underruns and model/run headers when available.
- Added GET `/health` request to Hermes on startup and when owner presses **Check Hermes**. This is non-blocking and does not change game or Exodia readiness.
- Improved caption pacing: weighted English/Mandarin punctuation timelines are adjusted by measured PCM duration when available and learned per stable voice ID across completed turns. Calibration is stored in local settings. No extra model calls.
- Kept Hermes voice ID and preset locked per customer encounter with speed 1.0× and pitch shift 0.0. Liu Xue uses Qwen's existing `Vivian` Mandarin-friendly speaker where Qwen is selected. This choice should be auditioned on the actual server.
- Added a subtle illustrated atmosphere layer rendered over the actual painted shop backdrop; gold lantern light breathes slowly and shifts gently toward red/violet for emotional dialogue.
- Added a responsive voice waveform accent, status label, portrait breath, near-invisible speaking motion and crossfades between genuine transparent illustrated portrait states. No new vector art or screenshot UI overlay.
- Optional multilingual microphone setting: set `STT_MODEL_SIZE=base` and `STT_LANGUAGE=auto`; an English-only Whisper model will now report a clear error if used in auto language mode.
- Preserved all 21 visitors, F8 Dialogue Studio, F9 Relationship Journal, bargaining authority and existing high-fidelity PNG assets.
- Preserved Exodia API contract: five providers and correct browser/API transport.

## Verification
- Python/API and static Godot/asset tests are automated.
- Native Windows Godot, Exodia and Mac Hermes live runtime remain an acceptance gate: see `docs/V09_ACCEPTANCE.md`.

## Deliberately not claimed
- True word-level timings or lip-sync (Hermes does not yet provide timestamps).
- New illustrations for all 21 visitors; existing Maya and Liu Xue illustrations are retained and animated via lightweight native controls.
