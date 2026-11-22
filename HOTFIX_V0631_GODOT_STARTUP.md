# The Living Counter V0.6.3.1 — Godot 4 Startup Hotfix

## Why this is needed

Two runtime errors reported after loading the V0.6.3 **complete project**:

1. `DialoguePop.gd:12` accessed `CharFXTransform.absolute_index`, which is a Godot 3 property and does not exist in Godot 4. Replaced with `relative_index`. The per-character reveal effect still resets at every new spoken line.
2. `Main.gd:_refresh_catalog()` called `HTTPRequest.request()` while its previous request was still processing. Catalog refreshes are now serialized; refreshes received while one is underway are coalesced and performed after completion.

Non-fatal editor warnings also cleaned up: an unused speech-card handle, an unused compose-panel handle, the unused mood parameter in `_speak_segment`, and the microphone bus variable shadowing Node.name. Mic bus routing uses the renamed variable everywhere.

No protocol changes: all five Exodia providers including Groq / Gemini API remain supported. No Hermes, STT, or economy changes in this patch.

## Apply the small overlay

1. Close the game and Godot editor. Stop the game backend if it is running.
2. Extract the **V0.6.3.1 Startup Crash Hotfix** ZIP directly into the V0.6.3 `The_Living_Counter_POC` folder, maintaining folder paths. Overwrite the existing files.
3. Reopen `godot/project.godot` and press Play.
4. Verify a customer arrives and the typewriter effect renders with no `absolute_index` error. Trigger several quick turns and a new encounter; verify no overlapping catalog request error.

The overlay does not contain `.env`, `.venv`, saves, or credentials.

## Verification performed here

- Automated Python/API regression tests, including API provider transport mapping and source-level Godot crash regression tests.
- Verified ZIP integrity and preservation of overlay directory paths.

**Limitation:** Godot was not installed in the build environment, so the Windows/Godot runtime must be validated on the owner's PC. Do not mistake static/source checks for a real Godot editor or audio-device test.
