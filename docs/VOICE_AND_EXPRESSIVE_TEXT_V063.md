# Voice + expressive text integration specification (V0.6.3)

## Voice identity
The source of truth is `godot/assets/hermes_profile_manifest.json` and each NPC's `voice` mapping in `backend/content.py`.
At the beginning of an encounter, Godot resolves `engine`, `voice_id`, `profile_id`, `instruct`, `speed`, `archetype`, `mood=neutral` exactly once. A new turn cannot swap the voice. Engine can change only with an explicit settings action. Old IDs map as follows:
- `m04_silas_rogue` -> `m06_finn_rogue`
- `m05_roderic_hunter` -> `m09_thane_guard`
- `m06_fenwick_merchant` -> `m04_marcus_merchant`

Hermes payload keeps `pitch_shift=0.0`; do not reintroduce varying mood-based pitch. F4 shows actual engine, voice ID, resolved preset, speed, and locked mood. These are the **request values**, not proof the TTS server honored them: confirm against Hermes logs/audio.

## Expressive typewriter
`RichTextLabel` is native Godot control, not a screenshot. `DialoguePop.gd` installs `revealpop` BBCode and animates first-visible characters with a short vertical spring plus alpha fade. `_emotion_bbcode()` adds capped 5 strong emphasized phrases with native BBCode background, font size and time effects.
- Gold/price: amber highlight / gentle wave.
- Anger/rejection: coral/red highlight / shake.
- Skepticism/hesitation: violet wave.
- Delight/flirting: warm gold pulse.
- Persuasion: cyan wave.
- Original quiet typewriter ticks are mixed at -25 dB during advancement.

Hermes provides PCM but not word alignment. `_build_speech_times()` estimates relative glyph timing using the actually consumed PCM timeline (`heard_seconds()`), with natural pauses for punctuation and CJK. The effect is **approximate**, not phoneme alignment. Calibrate interactively with F6 (slower) and F7 (faster), saved 0.70–1.50 in Godot user settings. For exact highlights at word timing, Hermes should expose word/phoneme timestamps.

## Spoken text and money
The game can discuss hypothetical gifts/dates, but never records them as payment. Conditional non-cash trade propositions are declined until a cash-only proposal is confirmed. If an NPC counters or a deal completes, that line is confirmed by the engine, and contradictory model text is never prefixed. `game_authoritative` in F4 means the engine controlled spoken text (not that Exodia was unavailable). `offline_fallback` means Exodia failed. 

## Acceptance tests
1. With live Groq, confirm one freeform chat returns `exodia_live`, HTTP 201 from Exodia, `error: null`.
2. With an offer of 61 gold, propose a date+67 gold: NPC must NOT agree to both; the offer stays unchanged until a cash-only quote.
3. Quote 67 gold alone: if accepted, transaction AND right-hand offer display 67. If countered, text must clearly state the new offer.
4. Challenge “you just accepted 67”: game recognizes a clarification, not a bid.
5. Test Maya's happy, skeptical, angry lines and Liu Xue's Mandarin; confirm keyword colors, pop/shake, subtle typing clicks, and F6/F7 adjustment.
6. Listen to three separate lines from one visitor; confirm identical voice identity/pacing and fixed profile readout.
