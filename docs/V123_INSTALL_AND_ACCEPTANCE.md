# V1.2.3 — Install & Windows Playtest

**Release status: engineering preview; seven portrait art gates remain OPEN.**

## Install

**Recommended:** extract the complete project ZIP into a new folder and copy your known-working `.env` into `The_Living_Counter_POC/`. If you want your previous progress, back up and copy the original save separately. Never copy `.venv` from an older project unless Python matches your working installation.

**Overlay over V1.2.2:** stop the backend and close Godot. Extract the overlay ZIP *inside* the existing `The_Living_Counter_POC` folder, preserving the included `backend/`, `godot/`, `docs/`, `.agents/`, `tools/` and `tests/` paths. It does **not** overwrite `.env`, world saves or `backend/exodia.py`.

From PowerShell in the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\preflight_v123_windows.ps1
powershell -ExecutionPolicy Bypass -File .\start_windows.ps1
```

Open `godot/project.godot` and press Play. The window title should show **V1.2.3 Living Voices & Art Quality Lock**.

## Exact acceptance tests in 1280×800

1. No persistent Visitors column or duplicate portrait cut-in. The center character remains visible.
2. The four **directly visible** utility buttons (Shelves, Ledger, Relations, Leads) work without opening the hamburger. Each panel closes cleanly; F11 Gallery and Settings continue to work.
3. Hold to talk: the **cyan player waveform** follows the mic; stop speaking and release the button, and bars fall to zero. Open mic follows live audio as well.
4. During Hermes speech, the **rose visitor waveform** follows actual output audio. When Hermes is stopped/finished or the visitor is silent, it is flat. This is an amplitude-time history sampled each game frame, not a frequency visualization or word-level sync.
5. The dialogue box has subtle native ornamental accents and remains readable, including long English and Mandarin phrases. Visual effects do not cover buttons or content.
6. F5 diagnostics shows `PCM receive RMS` separate from `Hermes audible peak`; verify slow-speech cases against direct Hermes Studio PCM if recurring.
7. Check Groq (`EXODIA_PROVIDER=groq`) and optionally `gemini-api`: a real turn yields `source=exodia_live`, API request uses `/api/command/tasks/game-dialogue`, and no old provider-validation error occurs. Don't put any API key into game `.env`.
8. Customer interactions/stock/saves remain stable. No gold, stock or deal changes from `◇ INTUITION`.
9. **Art is NOT approved:** inspect `art/character_art_contract_v123.json`; 12 true independent 1024×1536 RGBA portraits per rejected character must be produced and reviewed before changing their status to approved. Do not accept a contact-sheet crop, artificially upscaled bust, or identical file under new names.

## Art workflow

```powershell
python tools\validate_portraits_v123.py          # readiness report, nonblocking
python tools\validate_portraits_v123.py --strict # MUST fail until native files + owner approval exist
```

When all 12 *original independent master files* exist for one actor, use:

```powershell
python tools\import_portraits_v123.py --character mara_copperwell --source C:\YourFullResPortraits\Mara --install
```

The import script validates before copying and creates an art **review atlas only**; it never auto-approves the art. After reviewing the twelve images at native scale and checking the portrait in Godot, the owner explicitly approves the final rig. No cropped contact-sheet exports are valid input.

## Signoff

The automated source tests do not verify native Godot rendering, correct audio mix on Windows, or emotion-art fidelity. Treat those as separate acceptance gates.
