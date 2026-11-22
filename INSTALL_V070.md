# V0.7.0 preview install & rollback

## Recommended: clean install

Extract `The_Living_Counter_v0.7.0_Expressive_Performance_Full_Project.zip` to a new folder. Open `The_Living_Counter_POC`, copy your **existing working `.env`** into this folder, and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_windows.ps1
```

Open `godot/project.godot` in Godot 4.4+ and play. Existing game saves remain in Godot's `user://` location.

## Overlay on V0.6.4

Stop the backend and Godot. Unzip `The_Living_Counter_v0.7.0_Expressive_Performance_Hotfix_Overlay.zip` **inside** your existing `The_Living_Counter_POC` folder, preserving `godot/`, `backend/`, `tests/`, `docs/`, `tools/`. Overwrite the included files. The overlay intentionally has **no `.env`** and **does not overwrite `backend/exodia.py`**, so local API-provider settings and connection secrets remain untouched.

## Verify

Press **F8** in the running game for the new test studio. Use six benchmark buttons and the intensity slider to preview accent colors, motion and portraits. Press **F4** for diagnostics and F6/F7 for existing approximate speech-timing calibration.

Optional Windows parser preflight from inside `The_Living_Counter_POC`:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\windows_godot_preflight.ps1 -GodotExe 'C:\path\to\Godot_v4.x-stable_win64.exe'
```

Follow `docs/V07_ACCEPTANCE.md`. If any native Godot script parser errors occur, **revert to your prior V0.6.4 directory** and provide the exact first error; no backend-data migration is needed for this milestone.

## Scope

This preview adds the deterministic visual dialogue director, emotional cue acting, F8 local calibration, and seven style categories. It does not yet implement V0.8 long-term relationships, V0.95 inventory progression, or word-aligned Hermes timestamps. The Exodia Groq/Gemini API contract remains unchanged.
