# The Living Counter — permanent quality lock (owner directive, V1.2.3)

This file is authoritative for future production milestones. It supersedes old "8 expressions" art-completion language in V1.1/V1.2.

## Character portrait completion contract

**Every visitor needs 12 individually illustrated, visually distinct acting portraits before the character is described as production complete**: neutral, thinking, curious, skeptical, suspicious, amused, delighted, annoyed, angry, surprised, sad, flustered. Each state has its own native 1024×1536-or-larger full-illustrated transparent RGBA PNG (not a cropped sprite, not a resized small reaction panel, and not the same image with a different filter). Preserve identity, head size and shoulder/costume registration in every pose. Align against the approved Liu Xue / Elara Veyne art direction; a lineup/contact sheet is reference, not a deliverable.

**Explicitly rejected artwork — not approved for release:** Master Chen Wei, Tarek Ashwood, Felix Rowe, Safiya al-Nur, Rin Kaede, Yuna Seo, Mara Copperwell. Never mark them complete or force tiny expression studies onto the full portrait. Their older artwork may remain for engineering-only testing, with release state clearly marked INCOMPLETE. For each visitor: independent files -> quantitative art validator -> side-by-side identity review -> native Godot runtime screenshot -> owner acceptance -> `approved=true` in `character_art_status_v123.json`.

## Interface and accessibility invariants

- NO always-visible Visitors column or oversized portrait thumbnails obscuring the environment; use the optional F11 gallery.
- Shelves, Ledger, Relationships, and World Leads **must be directly accessible as on-screen controls** during normal play, not only through a hidden hamburger or keyboard shortcut. Keep the central illustrated character unobstructed.
- Player and visitor require two separate **real signal-driven** waveform indicators: microphone capture RMS and actual Godot Hermes audio output. Never use fake waveform texture motion, noise, or a thinking animation as a substitute.
- Chatbox must have a decorated yet readable nameplate, clear text hierarchy, transparent ornamental accents, and emotion-specific phrase emphasis synchronized as well as possible to audible playback. No baked mockup UI; live controls only.
- NPC's visible mood is separate from optional **shopkeeper intuition** (a fallible inference, never mind-reading or guaranteed lie detection). No floating second-face reaction portraits.
- Keep Exodia's five providers and API vs browser transport mappings byte-for-byte compatible. Keep Hermes preset voice, 1.0x/pitch-safe playback, microphone, savings and authoritative economy unchanged unless the milestone specifically requires a change.

## Mandatory release gates

1. `python -m pytest -q` for backend/UI regression suite.
2. `python tools/validate_portraits_v123.py --strict` and visual review for *all seven rejected characters*; currently intentionally fails.
3. Headless Godot parser/import and a real 1280×800 gameplay screenshot; waveform bars must move with live mic and visitor speech **and remain flat during silence**.
4. Verify shop buttons, F11, F4/F5, Exodia Groq/Gemini API route and Hermes voice profiles work simultaneously.
5. New files never overwrite `.env`, save data, or external Exodia fixes; ship path-preserving overlays.

An engineering preview may be shipped with an explicit red art blocker, but never as an art-complete or native-runtime-certified release.
