# V0.9.5 Windows Acceptance Checklist

Use a new extracted V0.9.5 folder and copy your existing `.env` after backing it up. Back up `save/world.json` separately. Launch the backend through `start_windows.ps1`, then open `godot/project.godot`. Verify the Godot debugger has **zero parse errors**.

1. **Date + 50 gold.** With Maya buying an item, offer the visible 50 gold conditionally on a date. If she says she's interested and the price is within her fixed limits, answer “Yes, I accept the agreed terms.” The deal must close **exactly once**, for the displayed amount. No new hoodie or meme-sparkle counterconditions should appear. If she rejects the proposal, she must not accept it merely because you say “yes.”
2. **Persistent refusal.** Ask for Maya's headphones with 50 gold, then with 200 gold. She must refuse both; no headphones should appear in inventory, and no cash should transfer.
3. **Changed terms.** On an approved social proposal, answer by adding a phone/hoodie condition. The deal must NOT close. After repeated attempts, the proposal should expire instead of looping.
4. **Real trade bundle.** Stage an owned item from Shelves, offer it with gold, then say “confirm trade.” Only an engine-approved bundle may transfer money and goods, and both must change together.
5. **Restock.** Open Shelves, select an item (including an empty shelf), and use the **RESTOCK 1** button. Gold decreases by the displayed supply cost, stock increases by one. Try buying too many units or spending more gold than you have; it must fail cleanly.
6. **Shop Ledger (F10).** Verify earned gold, purchases, restocking expenses, shop reputation and the featured daily market item. Restart the backend: amounts and stock persist.
7. **Liu Xue image.** Send multiple rapid messages while her portrait is visible. No ghost copy, double face or sudden full-frame zoom should appear during the thinking transition. Her expression may change when a finalized line arrives.
8. **Hermes (F5).** Run five identical Maya voice lines and compare their F5 PCM duration, underruns, sample rate and drift. If slow speech recurs, run `tools/hermes_pcm_compare_v095.py` and compare with Hermes Studio, as explained in `docs/HERMES_PCM_PARITY_V095.md`.
9. **Exodia Groq (live).** With `EXODIA_PROVIDER=groq`, a shop turn must resolve through `/api/command/tasks/game-dialogue`, `transport=api`, source `exodia_live`, empty error. `early_sentence` may legitimately be empty.
10. **Preservation.** F4 diagnostics, F5 voice, F8 dialogue studio, F9 relationship journal, F10 ledger, mic hold and open-mic modes must all remain available.

**Release status:** source build candidate until these native/live checks pass. The test script and Python regressions do not substitute for actual Godot/Hermes playback.
