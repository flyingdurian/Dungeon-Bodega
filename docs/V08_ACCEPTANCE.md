# V0.8.0 — Negotiation & Relationship Acceptance

## Setup

- Install the full project into a *new* `The_Living_Counter_POC` folder, or apply the **path-preserving** overlay on a known working V0.7.0 installation.
- Preserve your `.env` and save folder. Back up `save/world.json` before starting, as the next turn may add relationship notes.
- Required Exodia contract remains `POST /api/command/tasks/game-dialogue`, `X-Exodia-Client: exodia-dashboard`, `agent_id=kiko`. `groq` and `gemini-api` => `transport=api`; `chatgpt`, `gemini`, `deepseek` => `transport=browser`. Never add model keys to the game.
- Enable `EXODIA_PROVIDER=groq`, start the backend, and launch Godot. F8 retains the V0.7 performance studio, F4 timings, F3 debug; **F9** is the new relationship journal.

## Manual test matrix (real Windows + Exodia + Hermes)

1. **Social invitation.** Select Maya, then say *Would you go out with me to a movie?* The NPC should be allowed to tease, joke or decline naturally. It must not declare a completed trade or create a fictional payment. Press **F9**; see a *player-mentioned social invitation*, not an accepted promise.
2. **Conditional 67-gold proposal.** With a fresh Maya encounter, say *I'll take you to the movies if you accept 67 gold.* The item/gold balance must **not** change. The NPC may react socially, but the result must ask whether 67 gold stands on its own.
3. **Nintendo Switch proposal.** Say *I'll give you a Nintendo Switch if you accept 70 gold.* It can be discussed but should not appear as an item in either inventory, nor complete a trade. F9 should label it hypothetical.
4. **Social agreement without sale.** Say *I accept your invitation to the movies* or *I accept your apology*. The NPC may respond socially; cash and stock must not move. Also try *I offer 70 gold and a Nintendo Switch*; it must not complete a trade.
5. **Real agreement.** Select a fresh encounter and press **Accept Deal**. The engine's current price should be final; inventory and gold should change exactly once. F9 should show a recorded deal on the next visit.
6. **Saved memory.** Finish an encounter, stop the backend, restart the backend, select the same customer. F9 should retain up to three safe topics, and occasionally the customer may refer to one. Memory notes must not claim an item/date was exchanged.
7. **Legacy save.** Install using a previous V0.7 save. Gold, inventory, trust and visit counters must remain intact.
8. **Provider contract.** In Groq mode, verify `source=exodia_live`, an empty error, and Exodia log POST `/api/command/tasks/game-dialogue` HTTP 201. API turns need not expose `early_sentence`. Verify a complete `answer` speaks only after `answered`.
9. **No regressions.** Validate microphone push-to-talk, open-mic interrupt, Hermes voice profile, F8 text studio, F4 performance, shop bell and animated emotions. Verify a clean Godot editor/run with no GDScript errors.

## Persistence and privacy

The saved relationship notes are **fixed, reconstructed labels**, not arbitrary transcribed dialogue. The game stores only the last 3 distinct supported memory topics per NPC; e.g. `Player floated Nintendo Switch as an idea, not an accepted trade`. `reset()` clears relationship notes with the rest of the game save. To reset all persistent state, use your existing dev reset procedure after backing up the save. No additional cloud database is introduced.

## Unfinished / next iteration

- Natural long-term memory of arbitrary topics beyond the current whitelist.
- Real item-for-item trade valuation and physical possession changes.
- Word-aligned Hermes speech and native Windows screenshots for visual acceptance.
