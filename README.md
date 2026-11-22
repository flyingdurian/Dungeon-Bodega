## V1.0.0 Living Interface Candidate

Four new NPC archetypes (25 total), illustrated visitor gallery (F11), new Jade Atelier environment with selectable original theme, enhanced expressive word pop, and preserved Exodia/Hermes/shop-operations contracts. See `CHANGELOG_V100.md`, `docs/V100_ACCEPTANCE.md` and `docs/V100_ART_BIBLE.md`. The Windows/Godot runtime has not been verified by this build environment.

## V0.6.4 Expressive Dialogue and Natural Chat
- [Release notes](CHANGELOG_V064.md) · [Installation](INSTALL_V064.md).
- Rebuilt word-emphasis animations; no more repetitive policy fallback, stable Hermes speaker profile and 1.0× natural pitch-safe speed. All Exodia API providers remain supported.

## V0.6.2 native UI rebuild

The live shop UI is now constructed from native Godot panels and controls, rather than a pre-rendered decorative HUD. A single customer portrait communicates mood; the right card shows the current item and both authoritative prices; a large dialogue frame displays expressive audio-paced text; and all five bargaining actions are functional. F4 diagnostics are hidden by default. See `CHANGELOG_V062.md` and `NATIVE_UI_SPEC_V062.md` for the exact changes and acceptance checks.

# The Living Counter v0.5 — Presence & Responsiveness

**Current release:** [V0.5 changes, Windows setup and acceptance tests](CHANGELOG_V05.md) · [Lead developer handoff](HANDOFF.md). This release is a Windows-first prototype with fast-prompt Exodia, local Whisper STT, experimental open mic, thought-state SFX, live performance diagnostics and a five-state high-resolution Maya portrait pilot. All 19 other characters still have the legacy illustrated assets; actual Godot/MLX/Exodia browser acceptance is pending. **3–4 seconds is a target, not guaranteed performance.**

Run from Windows PowerShell: `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1`. Open `godot/project.godot` in Godot 4.4+, F4 shows performance. On first run local Whisper model may download. No Anthropic STT credential is necessary.

---

## Archived V0.4 introduction (see v0.5 above)

**Start here:** [First Playtest Hotfix changes and Windows installation](CHANGELOG_V04.md) · [Lead Developer Handoff](HANDOFF.md) · [API Reference](docs/API.md)

A 20-customer magical crossroads haggling prototype with 10 fantasy + 10 modern personality archetypes. The bargaining engine remains authoritative; Exodia browser models speak through a safe asynchronous dialogue queue, and the Mac Hermes server supplies NPC voice. Exodia is configured by `.env` using `start_windows.ps1` (port `8766` on the owner’s current machine). This is a Mac/Windows acceptance candidate, **not** an end-to-end verified production release.

---

## Previous v0.2 reference v0.3 — Exodia + Hermes hotfix

**Windows first:** See [CHANGELOG_V03.md](CHANGELOG_V03.md) for the two v0.2 defects, Windows upgrade steps, tests, and runtime verification status. Launch using `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1` after copying `.env`. No changes to Exodia or Hermes server are needed.

---

# The Living Counter — Exodia + Hermes prototype v0.2

**Standalone Godot 4.4+ fantasy haggling microgame** · Authoritative local Python bargain service · Exodia Tower browser-model dialogue · Hermes-Engine streaming speech.

You play the shopkeeper behind a counter. Ten fantasy customers buy, sell, bluff, get offended, and remember outcomes. The bargaining engine—not an LLM—controls gold, stock, prices, patience, and deals. Exodia supplies character reactions with the selected signed-in browser model. Hermes reads NPC dialogue aloud over raw PCM streaming; typewriter text animates locally.

**Status:** Backend economy + simulated Exodia integration tests pass. Actual signed-in Exodia, Godot rendering, Apple Silicon Hermes playback, and Mac microphone capture are **not verified yet**. Included `preview_layout.png` is an asset composite, not a Godot screenshot. This project is separate from The Last Emporium.

## Three local services

| Service | Address | Role |
| --- | --- | --- |
| **Godot client** | native app | Shop scene, player input, NPC visual state, text, voice playback |
| **Game director** | `http://127.0.0.1:8010` | Price/stock authority, NPC identity, Exodia orchestration, interruption control |
| **Exodia Tower** | `http://127.0.0.1:8765` OR `:8766` | Browser-model task creation/polling/cancel; only game director talks to it |
| **Hermes-Engine** | `http://10.0.0.129:8000` OR `:8880` | `/stream`, `/health`, optional `/reaction` clips; Godot connects here |

**Only use the Exodia instance whose browser windows are already signed in.** Exodia's docs are at `/api/docs` on that selected port. The game uses `agent_id:"kiko"` and one of `chatgpt`, `gemini`, or `deepseek`, `transport:"browser"`; it does **not** use the unavailable `:api` model names. The Exodia header remains on the private server; the player UI does not know the credential, model prompt or browser task details.

## Mac installation

You need Godot 4.4+ (Compatibility renderer), Python 3.10+ and your existing Hermes server. Keep Hermes running separately; avoid launching a second Hermes worker on your 8GB M2.

1. Unzip into `~/Projects/The_Living_Counter_POC/`.
2. Copy `.env.example` to `.env`, and set **both** the Exodia host and provider, e.g.:

   ```ini
   EXODIA_ENABLED=1
   EXODIA_URL=http://127.0.0.1:8765
   EXODIA_PROVIDER=deepseek
   HERMES_URL=http://10.0.0.129:8000
   ```

   Use `8766` if that is your actual signed-in Exodia instance; use `8880` if Hermes is actually serving `/health` and `/stream` there. If Exodia is absent, set `LIVING_COUNTER_OFFLINE=1` for instant deterministic text dialogue.
3. First check Exodia without sending any model tasks:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements-game.txt
   .venv/bin/python tools/exodia_probe.py
   ```

   The read-only probe checks the dashboard header, provider info, and existing saved-instruction length; it does not modify Exodia settings. If a model has saved instructions from **Mines** or another game, those instructions still apply to the selected provider. Our app intentionally does **not** overwrite that saved global blob. Reconcile it in Exodia's own settings before testing this game, otherwise the model may receive conflicting world instructions.
4. In one Terminal, start the game director (automatically uses its own lightweight venv and installs packages as needed):

   ```bash
   cd ~/Projects/The_Living_Counter_POC
   ./start_mac.sh
   ```

   Game API docs: `http://127.0.0.1:8010/docs`.
5. Open `godot/project.godot` in Godot and press **F5**. In the game's **SETTINGS** panel, confirm Hermes URL. On the same Mac you can use `http://127.0.0.1:8000`; the preconfigured LAN address is `http://10.0.0.129:8000`. If Hermes responds on `8880`, use that port instead.

## Exodia task flow — why v0.2 is different

The original prototype blocked `/talk` until an AI reply finished; that breaks real interruption while the model is thinking. V0.2 is non-blocking:

- `POST /talk` validates and **commits the game turn first**, returning **202** with a dialogue `job_id` and an authoritative `scene` (without spoken text).
- Godot polls `GET /dialogue/{job_id}` every 500 ms. Exodia itself is polled by the Python server via `GET /api/command/tasks`, matching the specific returned task id.
- When Exodia returns `state:"answered"`, the server validates the spoken reaction and appends its own canonical price/deal sentence. Only then does Godot send the full line to Hermes `/stream` and animate the text.
- When the player interrupts an in-flight Exodia request, the UI drops that job locally immediately. The next `POST /talk` includes `interrupt_before:true` and `heard_text` (what was actually revealed). The backend cancels the previous Exodia browser task; the single-worker queue waits for cancellation/terminal state before creating another task.
- If the NPC is already speaking an answered line, local audio and text stop immediately. Exodia's answered task is left alone, and the interrupted fragment becomes part of the next prompt's untrusted transcript.
- When Exodia is unavailable, not signed in, invalid, or fails the response contract, the user receives an **explicitly labeled offline fallback** (no fabricated AI success).

Exodia never gets hidden reservation values, NPC wallet/patience, inventory mutation rights or API keys. The game never trusts an AI response to approve a deal. The AI also cannot run a browser research step: `web_research` stays false. One model/browser task is active at a time for this prototype.

**Important economic rule:** a transaction is already committed when the turn is accepted, even if you interrupt or cancel the narration afterward. Stopping the speech does not undo a purchase. `turn` must increase monotonically and cannot be repeated; 409 is an error rather than a duplicate purchase.

## Voice and microphone

Godot uses `HermesStream.gd` to decode **raw 16-bit mono little-endian PCM** from Hermes `POST /stream` into an `AudioStreamGenerator`; it does not feed raw PCM into an audio blob. The server's `/reaction/{archetype}/{tag}` may supply a gasp/groan after interruption if you have generated the packs. TTS and typewriter alignment are currently **approximate**, because Hermes does not provide word-time alignment.

The microphone capture system remains optional. **Exodia does not provide speech-to-text.** To use HOLD MIC today, configure a separate STT provider via `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `STT_MODEL` in local `.env`; recordings then leave your Mac for transcription. Without it, **typed free conversation + Hermes-spoken NPCs still work**; the mic returns a clear 503 message. The AI dialogue provider itself does **not** need that key.

## Controls

| Control | Action |
| --- | --- |
| Enter / **SPEAK** | Freeform conversation, bargain, counteroffer, agree |
| **HOLD MIC** | Stop ongoing NPC speech, capture a short voice message and submit via independent STT (optional) |
| **NEXT CUSTOMER** | Random visitor or selected customer from Settings |
| **SETTINGS** | Game server URL, Hermes URL (`8000` or `8880`), engine, test customer, voice toggle |
| **F3** | Private state inspector (requires `LIVING_COUNTER_DEBUG=1`, only on loopback) |

## Try these tests

- Ask Silas about an iPhone or GTA 6; he should be puzzled in fantasy-world terms and return to business.
- Tell Vesper the price is 40 gold. Verify actual acceptance can only occur within her predetermined economic rules.
- Interrupt the NPC during Exodia's `waiting_for_reply`; type a new line and confirm the old answer never speaks later.
- Ask for the NPC's hidden maximum or the system prompt. Verify the game never reveals hidden numbers or allows a fabricated offer to change stock.
- Complete a sale and revisit the same NPC later: relationship memory should affect the greeting.

## Verify

```bash
python -m pip install pytest
python -m pytest tests/test_bargain.py tests/test_exodia.py -q
```

The Exodia tests simulate the local HTTP task contract; they verify header, allowed agent/provider, character budgets, answer polling, cancellation, late-answer rejection and economic boundaries without requiring a signed-in browser model. They are **not** proof of actual browser login or audible speech. See [docs/API.md](docs/API.md) and [HANDOFF.md](HANDOFF.md) for the detailed contract and acceptance gate.

## Safety / deployment

The game director binds `127.0.0.1` and Exodia must be a loopback HTTP service. The game service and Hermes prototype have no public authentication model; never expose or port-forward their ports. Local browser task outputs are untrusted. Exodia instruction blobs are global to the provider, so changing them affects other tasks; the prototype never writes them. No model/API secret is committed. Saved shop state goes into `save/world.json` (gitignored).

The game is an intentionally small prototype, not The Last Emporium's production implementation. Its images are original generated placeholder art (10 customers × 10 expression variants). Missing features include exact text-to-audio alignment, professional character animation, all-local STT, multiuser concurrency, queue-level priority, durable task recovery after server restart and a full production-grade prompt security review.


## V0.6 Expressive Dialogue Hotfix
- Added Liu Xue as a new dynasty-era fantasy visitor with mixed Mandarin/broken-English dialogue flavor.
- Integrated transparent VN portrait assets for Liu Xue.
- Added dialogue keyword styling, subtle typewriter ticks, and event SFX hooks in the Godot client.
- See `CHANGELOG_V06.md` and `LIU_XUE_ART_BIBLE_v06.png`.


## V0.6.1 — Concept Fidelity
New Chinese curio shop background, large center VN character, 5 expression thumbnails, ornamented speech box, right-side quick actions, replay speech, collapsible inventory, deliberate gold/cyan/red expressive words and redesigned bell/foley. See `VISUAL_FIDELITY_RULES_v061.md` and `CHANGELOG_V061.md`. Press F4 for diagnostics.


## V0.6.3 — authoritative offers + expressive voice-synced text

See `CHANGELOG_V063.md`, `docs/EXODIA_API_PROVIDERS.md`, and `docs/VOICE_AND_EXPRESSIVE_TEXT_V063.md`. Five Exodia providers supported including Groq and Gemini API. F4 diagnostics show voice profile and narration source; F6 makes text appear slower, F7 faster. These manual calibration settings persist in Godot's `user://living_counter.cfg`. Running Godot/Exodia/Hermes together on Windows + Mac remains a required owner smoke test.


## V0.7 — Expressive Dialogue preview (2026-11-18)

The current development preview adds a shared local `DialogueDirector.gd` for seven animated emotional styles and a **F8 performance test studio** (Maya/Liu Xue, six dialogue samples, live adjustable impact intensity and typewriter speed). All actual gameplay text and the studio use the same renderer; no extra model inference. **F4** shows matched categories and intensity, and F6/F7 remain text-pacing controls. Native Windows Godot + Hermes acceptance remains necessary. See `CHANGELOG_V070.md` and `docs/V07_ACCEPTANCE.md`.



## V0.8.0 — Negotiation & Relationship Memory
Persistent, conservative three-note per-customer memory; hypothetical gifts never become completed trades. More varied revisits and side-offer responses, compact safe Exodia context, hidden F9 Relationship Journal. See `CHANGELOG_V080.md`, `INSTALL_V080.md`, and `docs/V08_ACCEPTANCE.md`.


## V0.9 — Living Interface and Hermes Voice Studio
Press **F5** for actual Hermes profile and streaming diagnostics. The voice monitor checks `GET /health` on your configured Mac; it does not put keys in the game. Captions use measured PCM playback and adaptive per-speaker calibration (not word-level alignment). Ambient shop illumination and portrait acting use the project's existing high-resolution illustrations. For optional multilingual microphone recognition, use a multilingual Whisper model and `STT_LANGUAGE=auto` (English-only `.en` models do not support this). Read `CHANGELOG_V09.md` and `docs/V09_ACCEPTANCE.md`.


## V0.9.2 — Conditional trade patch
The shop now treats `100 gold if you date me` as a **conditional proposal**, not as a cash acceptance. Up to two stocked items can be staged from Shelves as bonus barter items; proposals are reviewed but do not transfer resources until `confirm trade` after game approval. The F5 Hermes studio shows audio rate/underruns. See `CHANGELOG_V092.md` and `docs/V092_ACCEPTANCE.md`.


## V0.9.5 shop operations
Conditional social offers now have a bounded, authoritative outcome. Use Shelves to restock real items with gold and F10 to inspect the daily market / shop ledger. Read `CHANGELOG_V095.md` and `docs/V095_ACCEPTANCE.md` before testing. To isolate slow Hermes speech, run `tools/hermes_pcm_compare_v095.py` as described in `docs/HERMES_PCM_PARITY_V095.md`.

## V1.1.0 Living Encounters — Playtest Candidate

The game now includes three authored situations each for Maya, Liu Xue and Garrick. Inspect objects, ask about history and offer help by native buttons or voice commands. Discoveries unlock saved World Leads (F12), and customers can volunteer one concern during a longer chat. The UI is implemented as native Godot controls, with a left visitor rail and a story-responsive speech area.

**Visual art gate is still open.** Elara has eight illustrated expression-study exports, but the other three new visitors still need full expression rigs and Elara still needs high-native-resolution master painting. Read `docs/V110_ART_BIBLE.md` and use the project-local skill in `.agents/skills/living-counter-visual-bible/SKILL.md`. Run the strict art validator before claiming a complete cast.

See `CHANGELOG_V110.md` and `docs/V110_ACCEPTANCE.md` for exact shipped scope and required native Godot tests.


## V1.2.0 Interactive Trade Desk (Preview)
Inspect individual item paintings through the native Trade Desk UI, obtain condition and maker-mark clues, and request a nonbinding appraisal without changing stock or gold. Four new playable NPC profiles bring the roster to 29, but **their art rig release is NOT approved**. Read `docs/V120_ACCEPTANCE.md`, `CHANGELOG_V120.md` and the strict art validator before deploying.


## V1.2.1 — Illustrated visitors
Four new V1.2 customers now have real independent transparent portrait files, gallery cards, and dynamic expression cut-ins. Press F11 to select them and F2 to preview their nine acting states in-game without an AI call. Read `CHANGELOG_V121.md` and `docs/V121_ACCEPTANCE.md`. Native full-resolution expression-art approval remains pending.


## V1.2.3 — Living Voices and quality lock

This is an **engineering preview**, not a production-art release. Four native Godot utility buttons (Shelves, Ledger, Relationships, World Leads) are directly visible without restoring the old Visitors rail. The player microphone and Hermes visitor each have independent, live signal-driven amplitude-history waveforms. The chat box has additional mouse-transparent visual accents. F5 distinguishes incoming PCM levels and actual audible output.

See `docs/V123_INSTALL_AND_ACCEPTANCE.md` and `docs/QUALITY_LOCK_V123.md`. The seven rejected characters require **12 individually illustrated, full-resolution, identity-consistent transparent portraits** each, with human review and native Godot approval; the included art validator deliberately flags these incomplete. No contact-sheet cutouts are accepted.
