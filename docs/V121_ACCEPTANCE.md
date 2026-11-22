# V1.2.1 Windows Installation and Character Art Acceptance

## Recommended: clean project
1. Extract `The_Living_Counter_v1.2.1_Illustrated_Visitors_Full_Project.zip` into its own folder.
2. Copy only your working `.env` from the old project's root into the new `The_Living_Counter_POC` folder. Back up `save/world.json` if you choose to transfer progress.
3. In PowerShell inside `The_Living_Counter_POC`, run `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1`.
4. Open `godot/project.godot` in Godot 4.4+ and press Play.

## Faster option: overlay on V1.2.0
1. Stop the Python backend; close Godot.
2. Extract `The_Living_Counter_v1.2.1_Illustrated_Visitors_Overlay.zip` **into the existing `The_Living_Counter_POC` directory**. Ensure `godot/scripts/Main.gd` and `godot/assets/vn_*.png` land in their normal locations, with folder structure preserved.
3. Restart backend and Godot. The overlay does **not** contain `.env`, saved world data or `backend/exodia.py`.

## Acceptance checks
- Game title reports V1.2.1, no GDScript parser errors.
- Press **F11**: Mara, Tarek, Yuna and Felix appear as distinct illustrated visitors.
- Select each visitor; the large portrait and the gallery thumbnail both match that character (not a placeholder or artwork from a different visitor).
- In an active encounter, press **F2** nine times: the small cut-in cycles neutral, thinking, amused, skeptical, delighted, annoyed, surprised, sad/subdued and elated. The large illustrated master remains steady: no double-face zooms or sudden size changes.
- During natural conversation, the cut-in follows the live NPC mood, while the visitor's voice, bargaining terms and inventory remain unchanged.
- Repeat a Groq or Gemini-API shop line; F4 should report `exodia_live` and the selected provider, not scripted fallback.
- F5 should show the same locked Hermes voice profile as before. The patch makes no TTS speed changes.

## Known remaining visual work
The first eight emotional reaction studies per character are distinct but originate from smaller source-sheet tiles; they are not eight independently painted native-1024×1536 full-body expressions. The strict art-bible audit continues to report an incomplete production rig, especially for sadness, and V1.1's four earlier newcomers are still pending. This patch is an **in-game integration deliverable**, not final art certification.
