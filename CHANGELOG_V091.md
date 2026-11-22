# V0.9.1 — Hermes Godot Parser Fix

## What failed
Godot rejects `res://scripts/HermesStream.gd` because `total_audio_seconds()` and `stream_is_complete()` use four leading spaces for their bodies, while all other members of the same script use tabs. This produces a parser error and, downstream, `Main.gd` fails to resolve the `HermesStream` class.

## Fix
- Converted the two inconsistent leading indents in `godot/scripts/HermesStream.gd` to tabs. No audio flow or TTS behavior changed.
- Added regression test `tests/test_v091_godot_indentation.py` checking consistent leading indentation for every project GDScript.
- Updated Godot's project title to V0.9.1 for an easy installation check.

## Unchanged
- Exodia's five-provider API/browser transport contract and fast game-dialogue route.
- Hermes voice IDs, PCM streaming logic and other V0.9 features.
- User `.env`, game saves, art assets and Python backend.

## Windows acceptance
1. Close Godot.
2. Unzip the V0.9.1 **overlay inside** the existing `The_Living_Counter_POC` folder, preserving folder structure.
3. Reopen `godot/project.godot` and confirm the new title includes V0.9.1.
4. Press Play. The `HermesStream` global-class parser error should no longer appear.
5. Optionally run `powershell -ExecutionPolicy Bypass -File .\tools\windows_godot_preflight.ps1 -GodotExe '<path-to-your-Godot-exe>'` in the project root before gameplay.

The headless Godot verification cannot be executed in this environment because Godot is not installed. Python tests and source structure checks are not substitutes for native Windows runtime testing.
