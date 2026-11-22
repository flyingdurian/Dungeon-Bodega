# The Living Counter v0.5 — Presence & Responsiveness

**Windows-first release candidate, built over V0.4.** The 3–4-second conversational objective is a target, not a verified network measurement. The full end-to-end loop requires the owner's Exodia signed-in browser, Hermes Mac server, Windows microphone and Godot runtime.

## Implemented

- **Exodia prompt diet.** The current utterance is sent once; per-turn NPC instructions retain name, era, style, tactics, world knowledge and guardrails but omit long biographies and repeated scaffolding. Dialogue prompt contains at most two recent exchanges; older history is omitted rather than silently fabricated. The authoritative game still stores the actual history. Saved-instruction length is fetched at most once per 45 seconds per Exodia URL/provider. All existing 4,000-/12,000-character checks and task IDs/cancellation/agent_id=kiko rules remain.
- **Live observability.** Each completed dialogue job exposes safe performance fields: player input, prompt and instruction character counts, task creation latency, Exodia wait and total elapsed time, output length and response source. In Godot the header shows wait and prompt size; **F4** toggles a breakdown. **F3** still opens the separate economy inspector (requires LIVING_COUNTER_DEBUG=1). Debug HTTP endpoint also reports rolling median and p90 for completed live dialogue jobs.
- **Local microphone STT.** `/transcribe` now consumes Godot WAV and uses local faster-whisper; no Anthropic, OpenAI or Exodia STT API key is required. On Windows the launcher checks/installs optional STT requirements and starts a nonblocking model prewarm when enabled. First-time model download requires internet; default tiny.en runs CPU/int8. `/stt/health` reports model loading/ready/errors. `STT_MODEL_SIZE=base.en` can improve accuracy at a speed cost; NVIDIA CUDA is optional and requires matching runtime libraries.
- **Open mic (experimental).** Hold-to-talk releases to send; open-mic mode listens for speech onset, interrupts the old response, then submits audio after **1.2 seconds of silence**. Sensitivity: `speech_threshold=0.018` RMS (editable in `MicrophoneCapture.gd`). Headphones strongly recommended to avoid Hermes audio feeding back into the microphone. Open mic is OFF at every application launch and is never silently restored from preferences.
- **Thinking state.** Customer portrait changes at send time, status displays an animated ellipsis/elapsed time, and a restrained pair of counter taps loops intermittently. Stop the sound when the response arrives or is interrupted. No fake prewritten voiced words.
- **Visual-novel expression pilot.** Maya "Byte" Torres now has **five matching 434–435×724 transparent illustrated portraits** (`vn_maya_{neutral,thinking,amused,skeptical,annoyed}.png`) with consistent identity and clothing, taken from one generated master sheet (`art/maya_vn_expression_master.png`). All 19 other customers retain their previous V0.4 art rigs pending the remaining high-resolution portrait rollout. Godot expression mapping falls back to legacy sprites for these characters; the prototype therefore remains an **art-incomplete V0.5**.
- **Windows launcher compatibility.** Corrected the PowerShell quoted `python -c` version parser bug, preserved the venv and existing `.env` workflow, and added optional local STT dependency setup.

## Windows hotfix (overlay)

1. **Back up** your current `The_Living_Counter_POC` folder, especially `.env`, `save/`, and `user://` Godot settings if you need rollback.
2. Stop Uvicorn (`Ctrl+C`) and close Godot. Extract the **v0.5 hotfix overlay** into the existing project root; overwrite matching source and asset files. The ZIP does **not** contain `.env`, `.venv`, or `save/`.
3. Existing `.env` can retain `EXODIA_URL=http://127.0.0.1:8766` and `HERMES_URL=http://10.0.0.129:8000`. Set `STT_PREWARM=1` if desired; the launcher enables it by default when unspecified.
4. Run: `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1`. Local STT model download can delay first use, but the backend can run while it loads.
5. Open `godot/project.godot` in Godot 4.4+ and press F5. Choose **Maya** from the settings to inspect the new high-res expression states. Test HOLD TO TALK, then explicitly turn OPEN MIC on. Press F4 for timing data.
6. Check `http://127.0.0.1:8010/stt/health` for readiness, `http://127.0.0.1:8010/health` for backend, and `http://10.0.0.129:8000/health` (or Mac port 8880) for Hermes. `/docs` contains the API.

## Measured in development, not on the owner's Windows computer

- On a representative opening turn, the old instructions+prompt were 1,934 characters; the new version was initially measured at 882 characters (before the extra small lore field, which adds a little). Benchmark real wait against Gemini, ChatGPT and DeepSeek separately; shorter prompts cannot guarantee a 3–4-second answer over Exodia's browser-driven pipeline.
- **58 automated Python/API tests passed**, including prompt compaction, local STT mocked binary contract, Exodia task behavior, fallback, economy, walkouts and portrait asset integrity.
- Did **not** complete real Godot runtime compilation, actual Whisper inference, Exodia browser session latency, Windows VAD/echo handling or Hermes+Windows PCM listening tests in this Linux environment. These remain owner acceptance gates.

## Acceptance test suggestions

- With Maya, ask one sentence about GTA 6, then one about iPhones; verify each answer is fresh and F4 shows LIVE EXODIA vs fallback reason.
- First-response metric: start measuring from **release to send** (for mic) or SEND (for text), to first audible Hermes PCM. Inspect Exodia wait and Hermes first-audio separately. Targets: median under four seconds **if achievable**; track 90th percentile and any 10-second outliers without hiding them.
- Pause for 1.2 seconds after a spoken statement in OPEN MIC; check transcript and submission, then speak while NPC is responding to verify rapid local barge-in. Wear headphones, and avoid leaving mic on when not needed.
- Confirm that five Maya expressions display at the intended game scale and that other characters still load legacy art.
- Verify cancellation never replays an old Exodia or Hermes response and the game economy remains authoritative.

## Remaining work

- Actual high-res expression art for the other 19 customers (95 portrait files), likely a dedicated art production stage.
- True word/phoneme alignment of Hermes speech to typewriter text; current alignment remains approximate.
- Headset-independent acoustic echo cancellation for always-open mic. Current VAD is energy-based, not a full duplex conversational audio stack.
- Real STT microphone calibration across different Windows headsets, Whisper sizes and GPU/CPU capabilities.
- Faster-than-4-second service response is not guaranteed: browser automation, provider-side inference and Hermes generation remain outside prompt-size control.
