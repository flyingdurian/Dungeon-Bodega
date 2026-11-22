# Hermes / Living Counter: isolate the intermittent slow playback

The shop sends `POST /stream` directly to the existing Mac Hermes server (no API key), using a **locked** customer profile. Default Qwen voice is selected from the shipped `hermes_profile_manifest.json`; playback requests use `speed=1.0`, `pitch_shift=0.0`, `mood=neutral`, `temperature=0.45`, `repetition_penalty=1.3`, `streaming_interval=0.5`, `stream_chunk_min=85`. V0.9.5 adds a 280 ms initial PCM buffer. It does not pitch-shift the voice.

Run this from PowerShell in the extracted project root with the game **not currently speaking**, while Mac Hermes is running:

```powershell
.\.venv\Scripts\python.exe .\tools\hermes_pcm_compare_v095.py --url http://10.0.0.129:8000 --engine qwen --profile f01_sakura_genki --repetitions 3
```

For Liu Xue's actual Qwen request, use the `Vivian` speaker with her locked Mandarin instructions; the default profile probe above is for Maya and is enough to compare Mac TTS against Godot's mixer initially.

Compare **the same exact sentence** in three places: the CLI's reported `PCM=...s` and `X-Sample-Rate`, Hermes Studio's audio duration with matching profile/controls, and the game's **F5** after the line finishes (PCM played, received, sample rate, underruns, playback drift). Do not compare differently worded sentences: duration can vary naturally with punctuation and language.

- Direct PCM already unusually long, but studio is normal: request/settings, Qwen instruction or model streaming behavior differs. Compare the full request fields before changing playback speed.
- Direct PCM duration normal, but Godot takes much longer and **F5 underruns/drift** are high: the in-game streaming/buffer path needs fixing, not the language model.
- Direct PCM and Godot playback approximately match, but both sound slow: the synthesized prosody is slow. Prefer testing an appropriate preset or model settings **in Hermes Studio first**, not arbitrary client pitch shifts.
- `X-Sample-Rate` differs from Godot's F5 value: fix the PCM sample-rate contract. Mismatching the declared rate can change perceived speed/pitch.

The probe reports timings and run ID only; it does not store audio. It requires `httpx` (included in `requirements-game.txt`). Avoid running it while the game is synthesizing, because Hermes only allows one inference at a time.
