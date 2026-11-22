# The Living Counter — V0.9.2 Conditional Trade & Legibility Patch

## Engine: no silent acceptance of conditional proposals
- `100 gold IF you date me` is a **proposal**, never an unconditional cash offer.
- Untracked phones, consoles, movie tickets and dates can be discussed as fictional/social ideas; they never move currency or inventory.
- Pending trade proposals are explicit and cannot be accidentally accepted by a bare `I accept`.
- Added catalog-backed bundle proposals (up to two shop-stock bonus items, plus gold) with **two-step confirmation**.
- Staged bonuses are only removed from stock when a trade is confirmed. Gold, stock and deal counts change atomically under the game lock.
- Reject unavailable bonus items and item IDs not in the authoritative catalog (HTTP 422), without consuming turn numbers.
- Spoken shorthand for shop items is conservatively recognized; untracked goods remain nonbinding conversation.
- A proposal to buy a different named item cannot silently purchase the currently negotiated item.

## Dialogue
- The Exodia profile now explicitly references the particular condition and whether a staged in-stock bundle can be confirmed.
- `event=proposal` suppresses premature deal claims and preserves safe, character-specific banter rather than generic rule speeches.
- Still no automatic acceptance on the strength of an AI statement; `confirm trade` is required for catalog-backed bundles.

## UI and voice
- Shelves now include a `+ ADD ITEM TO TRADE`/`REMOVE` button and up to two staged bonus items.
- Moved unreadable free-floating action/deal text to an opaque ornate status chip under the right-side buttons.
- Microphone caption now explicitly distinguishes recording, open mic (silence-triggered send), and NPC playback. Open mic does **not** detect emotions.
- Added sadness as a distinct type treatment; strengthened fiery anger, color/motion, and slanted doubt/flirt/sad lettering.
- F5 Hermes Studio now reports measured PCM glyphs/second and detects PCM underruns; does **not** manipulate pitch or claim to solve model generation speed.
- Retains voice profile locks and 1.0x/pitch-zero TTS requests.

## Compatibility
- Exodia providers `chatgpt`, `gemini`, `deepseek` use `browser`; `groq` and `gemini-api` use `api`.
- All use `/api/command/tasks/game-dialogue`, no Groq/Gemini keys are stored by the game.
- API turns do not require `early_sentence`.

## Limitations
- Conditional social deals (movie dates and imaginary devices) are narrative/hypothetical; they cannot become completed economic transactions.
- Actual bundles require an item that exists in shop stock and a manual confirmation. Only bonus shop items are supported; new incoming counterparty items and item-for-item offers beyond this are not yet implemented.
- Real Hermes word timestamps are still unavailable, so text/audio alignment remains approximate.
- Native Windows Godot, signed-in Exodia, and Mac Hermes integration require user acceptance testing; source tests cannot certify them.
