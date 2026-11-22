# V0.7 — Expressive Dialogue & Character Acting: Acceptance Gate

## Scope and design contract

This milestone retains the existing 1440×900 shop UI, fast Exodia API route,
Hermes preset locking, microphone behavior, game-owned economy and storage.
**No extra AI request** is made for text styling. `DialogueDirector.gd`
calculates deterministic phrase cues from the accepted displayed NPC line.
`DialogueTestStudio.gd` previews the same styling logic offline.

## Windows playtest: exact steps

1. Back up your working V0.6.4 project or extract the V0.7 full build into a new folder.
2. Start your local game backend with `start_windows.ps1` and open `godot/project.godot`.
3. Optional preflight: run `powershell -ExecutionPolicy Bypass -File .\tools\windows_godot_preflight.ps1 -GodotExe "C:\path\to\Godot.exe"` from the project root (use the actual Godot executable path). This checks scripts in Godot headless mode and saves `godot-preflight.log`.
4. Press **F8** to open **Dialogue Performance Studio**. No Exodia or Hermes is called by the studio.
5. Select **Value**: `67 GOLD` should have larger warm-gold typography; `better deal` should glow cyan with an underline. Text should enter progressively, with quiet typing ticks.
6. Select **Anger**: red outlined text should vibrate; the in-game counterpart should give an offended portrait / impactful `!!` reaction when the emphasized phrase is spoken.
7. Select **Persuasion**: a cyan highlighted phrase should flow/undulate rather than shake.
8. Select **Flirting**: rose-pink text; **Delight**: warm gold; **Mandarin**: red/cyan/violet where the matched Chinese phrases appear.
9. Switch the customer selector between **Maya** and **Liu Xue**, and the expression selector between **neutral/thinking/amused/skeptical/annoyed**. Portraits should be real transparent VN assets, not expression-thumbnail UI during normal gameplay.
10. Adjust the **Impact** slider between 0.5 and 1.5. **The selected intensity is saved and affects later real NPC dialogue.** Toggle F8 off; F4 should show the selected value and matched categories.
11. In normal gameplay, test a price, an insult, an amusing invitation and a skeptical question. The character acting cue must fire only as the emphasized phrase becomes visible. A single angry line should never repeatedly slam the counter.
12. Confirm all trade rulings remain consistent and Groq/Gemini API mode does **not** fall back to scripted output. F4 should show the actual provider and Hermes profile.
13. Press F6/F7 to adjust existing speech-paced text timing. With actual Hermes audio, ensure text does not race far ahead. Since Hermes does not supply per-word timestamps, this remains an **approximation**, not certified phoneme-level synchronization.

## Release qualification

- [x] Backend/API and source-directed expressive rules tests run in packaging environment.
- [x] Existing Groq/Gemini API routes and credential separation remain unmodified.
- [x] Real PNGs for both anchor characters, 5 expressions each, are included.
- [ ] Native Windows Godot startup without new GDScript parser errors — **requires Windows playtest**.
- [ ] Visual check of text glow/animation/layout — **requires native Godot screen capture**.
- [ ] Hermes voice/audio synchronization and mix — **requires live Mac Hermes server**.

Do not treat passing Python tests as a substitute for these final runtime checks.
