# V1.2.0 — Trade Desk / New Cast Acceptance

## Install
Extract into a new folder, preserve `.env` and back up your save before migrating. To apply the small overlay to a V1.1 project, extract with folders intact. Run Windows preflight and then open Godot. **This is a development candidate, not an art-complete or Godot-runtime-certified release.**

## Gameplay
1. Select a visitor. The fourth button in the contextual strip opens **TRADE DESK**.
2. Inspect a real item illustration; rotate left/right or zoom the 2D preview.
3. Try **Appraise** before examining — the game must explain that evidence is insufficient, not invent a value.
4. Examine condition, then check maker mark, then appraise. Notes and a bounded gold range appear. The range is NOT a binding offer.
5. Repeated inspection or appraisal cannot reward additional trust or change money/stock; stale requests return HTTP 409.
6. Close the panel and negotiate the item normally. The existing sale, cash-plus-inventory bundles, and conditional social terms must still work.
7. Use the microphone phrases `Examine the condition`, `Check the maker mark`, `Appraise`. They must use the same local action as clicking.
8. Try the four new visitor IDs in Settings or Gallery and check their dialogue and 3-case encounter variants.

## Explicit visual limitations
- 29 profiles exist; the final 4-character art rollout is **not complete**. Mara has one neutral illustration candidate; Tarek, Yuna, and Felix still need dedicated artwork.
- All four require eight individually illustrated native 1024×1536 transparent expression states. V1.1's remaining character rig gaps also still apply.
- Do not count any character as art-complete until strict validator and in-engine screenshot review pass.
- This build cannot claim a successful native Godot launch without verification in your Windows Godot editor.

## Regression / contracts
- `python -m pytest -q`
- `python tools/validate_visual_art_v12.py` (status report); strict mode is expected to fail until art is complete.
- `GET /health` version must read `1.2.0`.
- `POST /trade-desk/action` valid and invalid request cases; the 5 Exodia providers remain intact.
- F4 timing and F5 Hermes voice diagnostics should be unchanged. Compare with your working previous installation before adopting the update as production.
