# The Living Counter V0.8.0 — Negotiation & Relationship Memory

## Implemented (actual source changes)

- **Persistent relationship notes:** Each customer keeps at most 3 deduplicated, classified player-stated topics across encounters and server restarts. The previous visit/deal/trust metadata is preserved.
- **Evidence-aware memories:** Records distinguish hypothetical extra payments, social invitations, explicit *player-stated* intentions, and interests. These notes are never proof that an NPC accepted an item, a date or a promise.
- **Conditional and composite bargaining fix:** "movies"/"cinema" and offers like "70 gold **and** a Nintendo Switch" cannot bypass the side-payment guard and settle a cash trade. Social acceptance such as "I accept your dinner invitation" or "I accept your apology" no longer purchases an item.
- **Human-sounding side-deal replies:** Contextual, varied reactions from the character before asking for a cash-only amount; no one-size-fits-all policy lecture.
- **Revisit continuity:** Returning characters occasionally mention a specific prior topic without implying a commitment. The probability is deliberately low; no repeated mandatory greeting.
- **Compact Exodia context:** At most three small normalized memory records, plus the game's last outcome and current authoritative offer. The latest player line and official game ruling are protected from prompt truncation. No extra model request.
- **Hidden F9 Relationship Journal:** Inspect what the game *actually remembers*, with provenance labels, completed deals and prior visits. The normal main HUD is unchanged; F8 studio and F4 diagnostics remain.
- **Version markers:** V0.8.0 shown by the game title and `/health`.

## Guardrails / deliberate limits

- Cash and stock are still changed **only** by the authoritative engine, not AI dialogue or memories.
- Offers of Nintendo Switches, iPhones, tickets, dates, etc. can be discussed but are **not implemented as bartering items**. They never create a real inventory transfer.
- Memory capture currently uses a *conservative fixed topic vocabulary*. It does not know every possible fact from every conversation; it intentionally avoids another slow, error-prone LLM call.
- The model can reference player *claims* and explicitly marked prior context, but must not treat a hypothetical offer as an accepted NPC promise.
- No new API keys, model endpoints, Hermes speed controls or browser/provider behavior are introduced by this patch.
- Existing `save/world.json` is upgraded in place, without resetting cash, stock, or relationships. Back it up before testing a new build.

## Validation

Run `python -m pytest -q` from the project root. Native Godot and live Exodia/Hermes still need your Windows/Mac playtest; Python source checks are not a substitute.

See `docs/V08_ACCEPTANCE.md` for test scenarios and release gates.
