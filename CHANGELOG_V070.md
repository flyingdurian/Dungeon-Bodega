# The Living Counter — V0.7.0 (Expressive Dialogue Preview)

## Shipped code

- Added deterministic, reusable `godot/scripts/DialogueDirector.gd`: phrase-level emphasis for **gold/value, anger, persuasion, doubt, delight, flirting, and agreement**, with English and Mandarin rules, ranked matches, overlap prevention and a maximum of three accents per line.
- Added native **F8 Dialogue Performance Studio** (`DialogueTestStudio.gd`) with six sample lines, Maya/Liu Xue portrait choices, emotion selector, adjustable effect intensity, reveal-speed control, and the actual character appearance and text SFX. The studio never contacts Exodia or Hermes.
- Main Godot client now uses the same performance director as F8. Cues activate during text reveal; NPC portraits react with appropriate expression changes; small animated reaction symbols appear and serious anger may trigger one counter impact.
- Added **saved effect intensity** (0.5–1.5×) for live dialogue and F4 emphasis diagnostics. Preserved the prior speech-timed typewriter, F6/F7 timing calibration, microphone and replay functions.
- Extended `EmotionGlyph.gd` with rose/flirting, green/agreement and intensity-aware movement. Kept `DialoguePop.gd` intact for first-appearance tweening.

## Important protections

- Backend bargain rules were not changed. No new LLM request is made by the new rendering system.
- All five Exodia providers stay configured (`chatgpt`, `gemini`, `deepseek`, `groq`, `gemini-api`) with API/browser transport mapping preserved. `early_sentence` is optional on API turns. No game-side Groq/Gemini credentials.
- Hermes voice profile locking remains unchanged at 1.0x pitch-safe speed.
- V0.8 persistent relationships and V0.95 inventory progression are **future milestones**, not part of this build.

## Verification

Python regression suite and source-directed performance-pattern tests pass. Native Godot/GDScript runtime and the Windows + signed-in Exodia + remote Hermes configuration **cannot be run in this environment**. Follow `docs/V07_ACCEPTANCE.md` before promoting to production.
