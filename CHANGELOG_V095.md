# The Living Counter V0.9.5 — Shop Operations & Finite Negotiations

## What changed

- **Bounded social bargaining.** A social proposal like “I'll take 50 gold if you go on a date with me” receives a game-owned willingness and cash decision. A mutually approved proposal remains locked until explicit acceptance, which commits the agreed gold amount exactly once. The model cannot attach unlimited extra conditions.
- **Personal goods are not trade stock.** Headphones, phones, hoodies, consoles and similar belongings cannot be transferred just because the NPC discusses them. Refusals remain consistent even if the player raises the amount.
- **Inventory bundles retained.** Real shelf-backed extras still require an explicit confirm; money and stock update together.
- **Relationships record social roleplay separately.** A mutually accepted *fictional* invitation is distinguished from an inventory item, real-world promise or economic side-payment.
- **Actual shop operations.** Shelves now support purchasing one restock unit at a time. New `/restock` and `/ledger` endpoints are backed by persistent, authoritative gold and stock. Daily market spotlight changes prices conservatively; reputation and cash-flow ledger become relevant to customer encounters.
- **F10 Shop Ledger.** Hidden operations dashboard: reputation, earned and spent gold, restock costs, inventory value, and daily spotlight.
- **Liu Xue visual fix.** Removed overlapping full-size portrait crossfade and per-message portrait zoom. Her thinking state uses a visible thought bubble without swapping to an unregistered portrait pose.
- **Hermes PCM visibility.** F5 reports PCM sample rate, wall-clock drift vs played PCM and stream underruns. The Godot client now prebuffers approximately 280 ms rather than 150 ms to reduce gaps on uneven network chunks. Fixed 1.0x speed and 0 pitch shift remain.
- **Repeatable Hermes test tool.** `tools/hermes_pcm_compare_v095.py` reproduces the game's `/stream` request on a Windows machine without saving audio. Compare its returned PCM duration against Hermes Studio and the F5 panel.

## Compatibility

- Five Exodia providers preserved. `groq`/`gemini-api` use `transport=api`; signed-in `chatgpt`/`gemini`/`deepseek` use `transport=browser`. All use `/api/command/tasks/game-dialogue`. No Exodia API credentials are stored in the game.
- Old `save/world.json` files load with new reputation and ledger values defaulted. **Back up the save before installing.**
- No external API or Hermione server changes required. Live Hermes slow speech is still under investigation, not claimed fixed.

## Verification boundaries

- Automated backend and source contract checks cover bounded social consent, no new personal-goods contracts, atomic supply purchase, persistence, and Exodia provider mappings.
- Native Godot screenshot, Mac Hermes voice playback, and live Groq/API tests must be performed on the owner's machines. Python tests do not prove the in-engine rendering or audio naturalness.
