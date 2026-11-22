# V0.6.1 — Concept Fidelity / Expressive UI Rebuild

## Integrated implementation
- Replaced the previous green/black side-panel composition with a transparent, purple-and-gold ornamental VN HUD and redesigned native Godot controls.
- Added a custom Chinese curio-shop background with lanterns, blossoms, antique shelving and a finished counter.
- Enlarged center portrait and added five distinct expression thumbnails with direct preview controls.
- Moved original bargain commands to the right-side action rail, rebuilt the dialogue frame and added replay speech.
- Added inventory drawer instead of always-open shelves; retained settings, typed input, microphone, Exodia timing and debug windows.
- Expanded emotion keyword styling for English and Mandarin, including anger shaking, gold/price emphasis, pleased glow and skeptical wave.
- Preserved Hermes playback-driven text reveal, Exodia `game-dialogue` route and early-sentence audio support.
- Replaced the placeholder door entry noise with a two-note shop bell and quiet approach footsteps; typing sounds remixed at -36 dB.
- Kept Liu Xue's five transparent VN expressions from V0.6 and added matching face thumbnails.
- Updated Python regression expectations to reflect 21 customers and the fast-game Exodia endpoint.

## Test status
- Automated Python/API and asset checks: pass.
- Native Godot/Windows/Exodia/Hermes integrated screenshot/audio acceptance: NOT run in this environment. User playtest required.

## Installation
Recommended: extract complete V0.6.1 ZIP as a new project; copy existing `.env` and preserve existing save folder.
Alternative: overlay ZIP files onto **V0.6** game root (`The_Living_Counter_POC`), preserving subdirectories.
Use `start_windows.ps1` to launch backend and `godot/project.godot` for game.
