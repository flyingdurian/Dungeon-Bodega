# V0.9 Hermes / Living Shop — acceptance checklist

## Windows launch gate
1. Run `powershell -ExecutionPolicy Bypass -File .\tools\windows_godot_preflight.ps1 -GodotExe 'C:\path\to\Godot_v4_win64.exe'` from the project root (or execute script with its documented path). Confirm no GDScript parser errors.
2. Restart the backend with `start_windows.ps1`; leave `.env` from the running installation unchanged. Check `/health` shows v0.9.0.
3. Start Godot and check no errors in Debugger after entering, speaking, interrupting and advancing visitor.

## Hermes & captions
- Press **F5**; confirm correct preselected `profile`, voice and engine for Maya and Liu Xue. The voice must stay locked within each encounter.
- Use **Check Hermes**. `READY` means a successful GET `/health`, not proof that TTS will succeed for every utterance.
- Speak two longer English turns and one Mandarin turn with Liu Xue. Inspect PCM received, PCM heard, underrun count and caption calibration. There must be no abrupt pitch changes caused by playback-speed settings.
- Verify text appears as audio plays; the typewriter effect is approximate (no word timestamps). Follow another turn to see that calibration is reused. Press F6/F7 for manual pacing if desired.
- Start an utterance, interrupt with hold-to-talk, verify the speech stops and the next turn uses the same voice preset.
- In F4, verify the actual model and voice request are reported (if Hermes supplies the response headers).

## Art and interface
- The shop background and both VN character image sets remain high-res raster illustrations. No expression strip or screenshot-HUD overlay appears.
- Lantern illumination should breathe subtly, and shift hue gently with emotional dialogue. Character portrait should breathe, crossfade expressions, and subtly respond to speech. No stretching or severe shake.
- A decorative voice waveform should become visible while speaking or listening. F5 should be hidden during normal gameplay. All five offer CTAs remain clickable and correctly aligned at 1280x800 and 1440x900.

## Exodia compatibility — release blocker
- `chatgpt`, `gemini`, `deepseek` use browser; `groq`, `gemini-api` use API transport, always POST `/api/command/tasks/game-dialogue`.
- API providers may return only final `answer`; missing `early_sentence` is **not** an error.
- With real `EXODIA_PROVIDER=groq`, confirm `source=exodia_live` and empty job `error`; Exodia logs POST 201.
- Exodia model credentials never enter game `.env` or the Godot project.

## Limitations
- This package passed source-level Python checks; a native Godot build, actual Hermes server and signed-in Exodia were unavailable in the build environment. It is a V0.9 preview candidate, not a certified desktop release.
- Hermes still provides PCM rather than word timestamps. Caption alignment is estimate and should not be described as exact lip-sync.
- V0.9 adds illustrated atmosphere and acting polish, not new independently painted full-body illustrations for all 21 visitors.
