# V1.2.0 — Interactive Trade Desk (engineering candidate; art gate open)

## Interactive Trade Desk
- Added an item-inspection panel implemented as actual Godot Controls, not a pasted UI screenshot.
- Inspect a catalogued item's physical condition, maker/provenance mark, and a nonbinding price range.
- 2D rotation and zoom of existing independent item illustrations; **not** a simulated 3D model.
- Added authoritative `POST /trade-desk/action` with strict turn ordering, capped observations and idempotent actions.
- Spoken commands `examine the condition`, `check the maker mark`, and `appraise` use the same authoritative logic.
- The inspection cannot modify inventory, gold, accepted terms, stock, or item identity.

## Four new character archetypes (29 total)
- Mara Copperwell — fantasy clockwork restorer.
- Tarek Ashwood — fantasy frontier mapmaker.
- Yuna Seo — modern forensic gemologist.
- Felix Rowe — modern auction showman.
- Each has a distinct personality, bargain strategy, 3 Living Encounter cases, and a mapped existing Hermes preset.

## Art readiness — NOT YET COMPLETE
- One new Mara solo 1024×1536 illustration is imported as a single transparent neutral-state candidate; it has not passed identity/edge manual review.
- The other three visitors currently have **no approved standalone portraits**, and none of the four has an approved eight-state rig. They must not be represented as production art-complete.
- Keep the V1.1 art bible and use `tools/validate_visual_art_v12.py --strict` before signoff; it currently fails intentionally.
- No contact-sheet crops, screenshots, vector placeholders, or reused customer portraits are claimed as finished assets.

## Contract preservation
- Five Exodia providers and API-vs-browser mapping remain unchanged; no Exodia credentials are placed in the game.
- Hermes speaker/profile mapping and PCM playback are unchanged; no artificial pitch-speed correction is added.
- Existing `save/world.json` is not included in the overlay.
