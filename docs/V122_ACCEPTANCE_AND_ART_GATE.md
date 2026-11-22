# V1.2.2 — Clean Counter & Shopkeeper Intuition (engineering preview)

## User rejection is authoritative

Seven existing character designs / expression rigs are **REJECTED**, not approved:
Master Chen Wei, Tarek Ashwood, Felix Rowe, Safiya al-Nur, Rin Kaede, Yuna Seo, Mara Copperwell.
See `art/character_art_rejections_v122.json` and `docs/V110_ART_BIBLE.md`.

No UI concept cutout, contact sheet, or low-resolution sprite can satisfy this gate.
The supplied and generated lineup images are references **only**; none are used as new character assets in V1.2.2.

Per-character art acceptance: eight individually drawn, clean transparent, native 1024×1536 minimum portraits (neutral, thinking, amused, skeptical, delighted, annoyed, surprised, sad), one identity anchor, aligned facial scale and costume hardware, correct exposure, no baked matte, no enlarged thumbnail, no screenshot origin. Genuine happiness, sadness and tension must be distinct. Verify each in Godot at 1280×800 and with a side-by-side atlas. The seventh character should not silently inherit another's art.

## Changes in this engineering preview

- The entire always-on Visitors rail is **removed**. No thumbnail renderer builds behind it.
- The shop menu is hidden by default, opened via small ☰ in top-left; F11 still opens Visitor Gallery, Settings retains its picker.
- The old second-face floating reaction cut-in is **removed**, including normal F2 cycling. The main illustrated portrait remains the outward expression.
- Optional **◇ INTUITION** below conversation returns a non-binding tentative interpretation. It never asserts lie detection or displays confirmed private thoughts.
- Intuition is independent of outward emotion: `OUTWARD` is the public character state, `POSSIBLY` is your shopkeeper's impression. Confidence is limited by shop reputation and observed clues.
- Intuition doesn't consume an offer turn, talk to Exodia/Hermes, change trust, spend gold, transfer items, or disclose NPC reservation prices.
- The main dialogue area uses the freed horizontal space; controls remain native Godot widgets.

## Windows acceptance checklist

1. Run `tools/preflight_v122_windows.ps1` and **require actual native Godot parsing**. The automated Python suite is not sufficient.
2. Start Godot at 1280×800: no Visitor sidebar, huge stray faces or floating cut-in; portrait and dialogue are unobstructed.
3. Open ☰ Shop Menu, F11 Gallery, Shelves, F9, F10, F12 and close everything again; no overlay blocks gameplay when closed.
4. Run Maya and a stern visitor. Use `◇ INTUITION` both before and after discovering origin: displayed `OUTWARD` can disagree with the provisional `POSSIBLY` insight without a visual glitch.
5. Confirm a repeated intuition request on the same turn returns the same description, and makes no money/offer/stock changes.
6. Verify 5 Exodia mappings, Groq API speech, Hermes voice, push-to-talk and auto mic all retain functionality.
7. **Art gate fails intentionally** until the seven named character redesigns and 8-state rigs are accepted in native gameplay. Do not call this release an art production pass.
