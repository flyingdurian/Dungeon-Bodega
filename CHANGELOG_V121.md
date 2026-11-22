# The Living Counter V1.2.1 — Four Illustrated Visitors & Reaction Integration

## Playable changes
- Added individual illustrated **master portraits** and visitor-gallery thumbnails for Mara Copperwell, Tarek Ashwood, Yuna Seo and Felix Rowe.
- Extracted **nine unique transparent reaction sprites per character**: neutral, thinking, amused, skeptical, delighted, annoyed, surprised, sad/subdued, and elated.
- Introduced a small illustrated **live reaction cut-in** beside the customer portrait. Its sprite follows the same mood signal used by the main scene; the full-size master stays stable to prevent Liu Xue-style double-face zooms.
- Press **F2** when one of the four visitors is at the counter to cycle the nine illustrated reaction states locally **without invoking Exodia or Hermes**. Press **F11** to open the native visitor gallery.
- Replaced the four newcomers' gallery thumbnails and fixed the cramped left-rail visitor list, which previously had more IDs than names and could collide with the shelves buttons.
- Corrected the text in the roster filter to reflect all 29 characters. Exodia transports, credentials, Hermes profiles, negotiation and saves are unchanged.

## Source assets & reproducibility
- The expression sheets are in `art/source_sheets_v121`.
- `tools/build_v121_character_art.py` reproduces the extracted PNG assets.
- `art/character_art_runtime_v121.json` documents exact source-pixel dimensions, all nine reaction states, and the art-quality gate.

## Art-quality distinction
- **Functional in-game portrait integration: implemented.** Each character now has real independent RGBA assets and reactive on-screen artwork.
- **Full-resolution art bible sign-off: not complete.** The source sheets contain smaller reaction studies, not eight individually painted 1024×1536 full-size portraits. Tarek, Yuna and Felix's independent masters are also below target resolution. The sadness art is intentionally tracked as a subdued study rather than claiming a fully emotional grief portrait.
- Previous V1.1 cast art requirements remain open. No image was enlarged merely to pass the size validator, and no UI mockup screenshot was used as an actual game asset.

## Verification
- 202 Python/API and asset regression tests passed in the build environment.
- Offline GDScript indentation/string sanity: passed.
- Native Godot runtime / Windows Exodia / Mac Hermes: **not tested here**; see `docs/V121_ACCEPTANCE.md`.
