# Dungeon Bodega — Project Boundaries

**Effective 2026-11-21. Current game baseline: v1.2.4.4.**

These three projects are independent. Do not conflate source, branches, repositories, saves, character assets, roadmaps, versions, tests or release gates.

1. **Dungeon Bodega** (historically The Living Counter) is the standalone Godot game with its own Python FastAPI Game Director, game logic, economy, art, user data and game-side adapters.
2. **Hermes-Engine** is an independently developed reusable TTS/speaking-model API service. Dungeon Bodega only consumes its HTTP API. The game owns its voice mapping and Godot playback consumer, not the Hermes server, Studio, models or dependencies.
3. **The Last Emporium** is the owner's earlier, separate shopkeeper/haggling game. Shared themes do not authorize any game-source or art migration.

Exodia is an additional independent external dialogue/task service. Godot calls the Dungeon Bodega Game Director, which alone calls Exodia. The Game Director is authoritative for prices, gold, inventory, stock, offers, acceptance, trust, patience, walkouts and saves. Exodia narrates; Hermes speaks. Neither external service controls economic state.

Never copy or publish game code into `flyingdurian/Hermes-Engine`, nor vendor Hermes server/model/Studio code into Dungeon Bodega. The historical Hermes `feat/living-counter-poc` branch is misplaced milestone history, not an active game branch. Do not resurrect `publish_to_hermes.sh` or equivalent. Do not modify Hermes-Engine or The Last Emporium as a Dungeon Bodega task.

Before destructive changes, inspect the owner's live Windows tree and protect `.env`, `.venv/`, saves, `.godot/`, local changes, credentials, private recordings and model caches. Native Godot, Windows, Exodia and Hermes acceptance remain independent of source-test results.

The 2026-11-21 v1.2.5.1 migration handoff remains requirements history; it must not be treated as code currently installed in the owner-confirmed v1.2.4.4 tree.
