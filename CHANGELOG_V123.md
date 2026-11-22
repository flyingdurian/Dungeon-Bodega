# V1.2.3 — Living Voices & Art Quality Lock (engineering preview)

## Implementation

- Restored **Shelves, Ledger, Relationships, World Leads** as four directly accessible native Godot buttons in a compact upper-left utility dock. **No permanent Visitors rail** or thumbnail faces have returned. F11 remains the visitor gallery.
- Replaced the decorative/static waveform image with two independent signal-driven amplitude-history displays: microphone RMS from `MicrophoneCapture.gd`, and **actual Hermes output-bus peak levels** from `HermesStream.gd`. Silence displays as a flat line. This is an output-level history, **not word/phoneme alignment or an audio spectrum**.
- Added noninteractive plum/gold/blossom corner detailing, hairline accents, and improved visual layering to the native dialogue panel. Kept RichTextLabel, cinematic phrase emphasis and Hermes-led reveal.
- F5 now distinguishes PCM receive RMS from actual audible output peak, to help investigate slow/paused speech.
- Updated the canonical portrait contract to **12 independent, native-size expressive PNGs per character**. Seven owner-rejected characters remain explicitly unapproved. No contact-sheet crops, stretched busts, or artwork from promotional mockups are labeled production complete.
- Added strict `tools/validate_portraits_v123.py` and `tools/import_portraits_v123.py`; import validates all 12 images before changing the game and **never automatically marks them owner-approved**.
- Stored the owner's requirements in `docs/QUALITY_LOCK_V123.md`, `AGENTS.md`, `.agents/skills/living-counter-visual-bible/SKILL.md`, `art/character_art_contract_v123.json`, and `HANDOFF.md`.
- Preserved `backend/exodia.py` byte-for-byte, including all five supported provider mappings; saved games, API credentials, and Hermes preset mapping remain unchanged.

## Verification and release restrictions

- 212 Python/backend/UI tests passed in source; offline GDScript static check passed across 10 scripts.
- Native Godot parser, runtime 1280×800 render and live Windows microphone/Mac Hermes playback are **not verified in this environment**.
- The **strict 12-expression artwork gate intentionally fails** for Master Chen Wei, Tarek Ashwood, Felix Rowe, Safiya al-Nur, Rin Kaede, Yuna Seo, and Mara Copperwell. This package is **not art-complete** and must not be called a final production release.
- Existing neutral artwork for these visitors is retained for engineering playtests until full replacement is independently created and approved. The project will not enlarge their old thumbnail studies into hero portraits.
