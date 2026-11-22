# The Living Counter v0.3 — Speech-tail and Exodia response regression fixes

## Root causes in v0.2

1. `godot/scripts/HermesStream.gd` started `AudioStreamGenerator` immediately upon receiving HTTP response headers, even if Hermes had not yet emitted a single audio sample. `get_playback_position()` advanced through this initial silence. The v0.2 end condition compared that clock against total enqueued PCM duration, prematurely stopping the player before the queued tail played.
2. `backend/exodia.py` rejected any generated in-character response with **any digit**, so an AI line referring to `GTA 6`, calendar dates or similar harmless numbers triggered `offline_flavor` instead. `backend/brain.py` then mapped *every* modern-topic fallback to the same "eye-phone" sentence. This made working Exodia calls appear scripted/repetitive.

## Fixes

- Hermes starts the audio generator only when at least ~150 ms PCM is available (or short completed clips). Completion now requires all received PCM samples to enter the ring buffer and waits for actual buffer consumption before finishing; no playback-clock duration guess. Full WAV response endpoint is unchanged.
- Exodia validator allows neutral numbers in dialogue (e.g. `GTA 6`) while continuing to reject AI-generated monetary quotes, transactions or price promises. Game-authored anchor sentence remains authoritative for all gold and item decisions.
- Offline fallback now responds to the specific current modern topic, not always "eye-phone". The UI explicitly labels **EXODIA LIVE** versus **SCRIPTED FALLBACK** during and after speech. In fallback responses, the originating Exodia error remains available on `GET /dialogue/{job_id}` as `error` and is shown briefly before TTS starts.
- New regression tests check the false numeric rejection, distinct off-topic fallback, economic refusal, and Godot playback source contract.
- Added `start_windows.ps1` with a Python 3.11 venv check and `.env` loading. Existing Mac launcher is unchanged.

## Windows quick update

1. **Stop the old game backend** (Ctrl+C), and **close Godot**. Keep Exodia and Hermes running; neither service requires patching.
2. Extract v0.3 into a **new directory** and copy your old `.env` to the v0.3 project root. Do not copy the old `.venv`; create a fresh Python 3.11 venv, or use a preexisting Python 3.11 venv.
3. In PowerShell from the new project folder: `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1`.
4. Open the **v0.3** `godot/project.godot`, press F5; verify in the game Settings the correct Hermes address/port.
5. Ask Silas separately about an iPhone, then GTA 6, then a dragon. While listening, watch the text label: **EXODIA LIVE** must be displayed on actual accepted Exodia answers; if **SCRIPTED FALLBACK** appears, use `/dialogue/{job_id}.error` for the actual cause. Hearing a live model's words is not sufficient evidence if that label says fallback.
6. For speech-tail acceptance, repeat the same 2- to 3-sentence line ~5 times with no interruptions, especially on slower Hermes runs. Ensure it finishes naturally each time. Compare against a Hermes **WAV** response if it still cuts off: if complete WAV audio is also truncated, the issue originates in the TTS generation rather than Godot's PCM playback.

## Verification limits

Backend and mocked Exodia contract tests passed on the development host. GDScript source was audited; a Godot executable and the owner's real Mac Hermes stream were unavailable here. **Audible end-of-sentence completion on your Windows+Mac LAN remains a manual acceptance gate.** The 150ms prebuffer does not prevent a later long network underrun; separate buffering telemetry may still be needed.
