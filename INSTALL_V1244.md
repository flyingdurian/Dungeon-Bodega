# V1.2.4.4 — Two-character native portrait acting review

## What this overlay does
Adds **five different 1024×1536 transparent original illustrations each** for Master Chen Wei and Tarek Ashwood (neutral, thinking, amused, skeptical, annoyed); replaces their previous main portraits; enables these five distinct states during *ordinary gameplay* without requiring F2. F4 reports real displayed state. Other five rejected visitors are unchanged.

These ten independent PNGs are installed in `godot/assets/vn_<actor>_<state>.png`. This is an **unapproved in-game trial**; the strict 12-state art-bible gate is still open.

## Hotfix installation (over V1.2.4.3)
1. Stop the backend and close Godot.
2. Extract `The_Living_Counter_v1.2.4.4_Two_Visitor_Portrait_Overlay.zip` into the existing `The_Living_Counter_POC` folder. Allow overwrites and preserve the `godot/assets/`, `godot/scripts/` and other paths.
3. Do **not** delete your `.env` or `save/world.json`. Neither is included in the overlay. The Exodia provider integration is not changed.
4. Restart the backend using `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1`, then reopen `godot/project.godot`; allow Godot to import the ten new textures.
5. Open F11, choose Master Chen or Tarek and start speaking. Use F2 to cycle the five current portraits immediately without waiting for Exodia. F4 reports `FIVE_STATE_TRIAL_NOT_APPROVED` when one of those five renders.
6. If F4 says `TRIAL_NEAREST_STATE_NOT_APPROVED`, the requested emotion is one of the seven **not yet illustrated** states. It is shown as the nearest existing expression and **is not** a distinct new portrait.

## Full project installation
Extract the complete ZIP into a fresh folder. Copy only your working `.env` and backed-up save if desired. Start the backend and Godot as above.

## Required visual checks
- Ensure the main portrait changes during actual speech, with **no additional cut-in portrait** or double-face overlay.
- Watch neutral → amused → skeptical → thinking → annoyed transitions for both characters. Use F2 if an actual model conversation does not naturally trigger all five.
- Check no rectangular background, UI screenshot or sprite sheet is visible in the portrait.
- Check Shelves, Ledger, Relationships, Leads and the player/visitor audio meters remain usable.
- F4 should truthfully show requested vs displayed state and exact filename.
- No source tests substitute for a native Godot playtest or owner art approval.
