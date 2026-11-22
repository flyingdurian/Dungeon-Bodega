# V0.6.3 — Bargain Continuity + Expressive Speech (2026-11-18)

## Fixes implemented
- **Authoritative negotiations.** The engine alone decides the price, deal state and outcome. After accepting a 67-gold quote, the visible offer is 67—not the old customer offer.
- **Model/engine speech conflict.** New `backend/trade_dialogue.py` locks terminal results and official counteroffers. AI cannot prepend an unsupported “yes” to a contrary 61-gold counteroffer. Safe, noncommercial personality flavor may still accompany a ruling. F4 distinguishes `game_authoritative` narration from direct `exodia_live` lines; this is NOT an offline script failure.
- **Off-ledger gifts/romance.** Conditional offers involving movie dates, Nintendo Switches, gifts, etc. are NOT accepted as payment. The engine requests a cash-only confirmation. Ordinary banter/flirting remains allowed.
- **Quote continuity.** “You just accepted 67 gold” is a clarification about the previous quote, not a fresh bid. Recent official price and last proposal are included in the compact Exodia prompt. Price/side-deal turns cannot start speculative early audio.
- **API provider contract preserved.** `chatgpt`, `gemini`, `deepseek` use `transport=browser`; `groq`, `gemini-api` use `transport=api`; all use `/api/command/tasks/game-dialogue`. No API keys in the game. A successful API answer needs no `early_sentence`.
- **Hermes voice stability.** Every encounter resolves a named Hermes Studio profile once and fixes engine/voice/speed/speaking instructions plus neutral TTS mood across turns. Legacy profile names are explicitly mapped to manifest-supported IDs. Pitch shift remains 0.0. F4 shows all resolved values.
- **Typewriter effect.** Native `RichTextEffect` animates each newly visible glyph using a brief fade/vertical spring. Dialogue reveal follows estimated characters relative to PCM **played**, weighted for CJK glyphs and punctuation. Typing ticks remain quieter than speech.
- **Emotional text.** Expanded Mandarin/English emotional lexicon: price/gold highlight, angry shake, skeptical wave, positive pulse, cyan persuasion; bold backgrounds and larger font are capped at five strong effects per line.
- **Player tunable pacing.** Press F6 for *slower* text, F7 for *faster* text; scale 0.7–1.5 is saved to `user://living_counter.cfg` and shown with voice diagnostics in F4.

## Verification
- 76 Python/API/source and contract tests passed, including 5-provider routing, missing `early_sentence`, mock Groq live shop line, romance/gift conditional offers, accepted price visibility and contradictory model text.
- Full-project and hotfix overlay ZIP integrity verified after packaging.
- **Native Godot, live signed-in Exodia and Mac Hermes were not executed in this environment**. The speech pacing is an approximation; word-level timestamps require Hermes alignment data.

## Installation
1. Recommended: extract the complete ZIP into a fresh directory, copy your working `.env` and saved backend world as applicable; DO NOT copy an old `backend/exodia.py` over this version.
2. Or extract the overlay inside the existing `The_Living_Counter_POC` folder, preserving paths. Keep `.env` and `.venv`.
3. Restart backend using `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1`, then reopen `godot/project.godot`.
4. Keep `EXODIA_PROVIDER=groq` for the API fast path, or choose `gemini-api` for Gemini API; `gemini` is the browser provider.
5. Test F4 provider/voice diagnostics and F6/F7 speech pacing. Check deal 67 gold vs old offer 61, and conditional movie-date proposal.
