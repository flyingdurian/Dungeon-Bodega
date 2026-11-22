# Dungeon Bodega — Current Development Handoff

**Canonical source:** `flyingdurian/Dungeon-Bodega` (`main`) and the owner's Windows working folder `C:\Users\TFBOSS\Documents\GitHub\Dungeon-Bodega`. Owner-confirmed QA build: **v1.2.4.4**; former working title **The Living Counter**. The dated v1.2.5.1 migration handoff is not a newer source baseline.

**Scope:** 29-person roster, Godot client and authoritative FastAPI Game Director. Exodia dialogue and Hermes-Engine TTS are external services, and The Last Emporium is a separate game. Read `docs/PROJECT_BOUNDARIES.md` and `docs/HERMES_TTS_CONSUMER_CONTRACT.md`. No game-to-Hermes publishing, no cross-project assets or source, no modifications to external projects.

**Art QA:** Master Chen and Tarek remain five-state QA trials, not owner-approved 12-state rigs; strict production gate blocked. Do not infer V1.2.5.1 Denise/Maya intake or allowlist files exist in this baseline. Preserve all roster IDs/voices, Exodia provider contract and saves.

**Next checkpoint:** verify a clean Git checkout includes or can reproducibly restore required binary game assets, then run Windows Python 3.11 tests, native Godot import and gameplay, and separate live Exodia/Hermes tests. No historical test count proves current native acceptance. Sanitized code-only ZIP tests cannot prove binary asset availability.

---

## Historical milestone records (retained)

## V1.2.3 engineering work (owner quality lock)
- See `docs/QUALITY_LOCK_V123.md`: 12 expression images required per visitor, all seven rejected remain NOT approved; strict art gate is required before full production release.
- Keep four direct shop buttons without restoring intrusive Visitors rail.
- Two signal-driven waveform meters; mic from capture RMS and Hermes from dedicated output bus peak; never use fake image.
- Preserve five Exodia providers; do not touch `backend/exodia.py` / `.env` / saves.
- Native Godot runtime must still be verified before release signoff.

## V1.2.2 Clean Counter & Intuition (engineering preview)

- Removed user-rejected Visitors rail and floating second-face reaction cards; F11 Gallery and hidden ☰ menu retain selection.
- Added optional `GET /intuition/{session_id}` player-skill inference; no authoritative private thoughts or trade mutation.
- Seven user-rejected visual rigs remain `REJECTED_ART_PENDING_COMPLETE_REDRAW`. Do not mark them production ready.
- Exodia source deliberately byte-identical to V1.2.1; all five transports preserved. Native Godot playtest still pending.
- Source QA and artifacts documented in `docs/V122_ACCEPTANCE_AND_ART_GATE.md`.

## V1.2.1 — Four illustrated visitors (2026-11-19)
Four master portraits, thumbnails, and nine distinct cut-in expressions per new V1.2 NPC integrated in Godot. F2 local acting preview; F11 gallery. Main portrait remains stable; source sheets and build script in repo. 202 regression tests pass, native Godot untested. Full-resolution art bible gate remains open. Exodia provider adapter preserved byte-for-byte.

## V1.2.0 Engineering Candidate (art gate OPEN)
- Added native Godot TradeDeskPanel and authoritative `POST /trade-desk/action` (condition/origin/appraise) and 2D item art rotate/zoom.
- New four cast entries: mara_copperwell, tarek_ashwood, yuna_seo, felix_rowe (29 total); three Living Encounter cases each; existing Hermes presets.
- Appraisal advisory only: cannot alter gold, stock or accepted price. EXODIA PROVIDER BRIDGE unchanged from V1.1.
- Strict visual art gate intentionally incomplete: one Mara neutral portrait candidate, three new portrait sets missing; older V1.1 gaps remain. Native Godot launch not checked here.
- Full verification instructions `docs/V120_ACCEPTANCE.md` and `CHANGELOG_V120.md`.

## V1.1.0 Living Encounters — Latest handoff

- Engine: `backend/living_encounters.py` implements three case variants for Maya, Liu Xue and Garrick, contextual actions, one NPC initiative and persistent world leads. `backend/engine.py` and `backend/app.py` add action and leads endpoints without touching economic settlement rules. Exodia provider bridge is unchanged from V1.0.
- Godot: `godot/scripts/Main.gd` adds a native left visitor rail and three context actions, moves the speech box and adds F12 Leads. F3–F11 retained. No baked UI mockup.
- Art: `art/Elara_Veyne_8_Expressions_Original_Sheet.png` and 8 exported transparent state PNGs. These are authored expression studies and below production native-resolution art gate. Safiya/Rin/Master Chen not art-complete.
- Skill: `.agents/skills/living-counter-visual-bible/SKILL.md`, `docs/V110_ART_BIBLE.md`, `tools/validate_visual_art_v11.py`. The strict gate is expected to FAIL until remaining portrait art is finished. Don't claim all four character rigs complete.
- QA: `python -m pytest -q`, `python tools/check_gdscript_static_v11.py`, Windows native Godot preflight. See `docs/V110_ACCEPTANCE.md`.
- Must preserve `.env`, save files, Hermes 1.0x voice profile, and Exodia five-provider API/browser mappings in all subsequent builds.

## V1.0.0 development handoff
Completed: expanded roster 21→25; new visitor gallery, two new stage backdrop choices, word-cue animation, four individual illustrated character previews and UI navigation changes. Confirm integration paths before packaging and preserve `backend/exodia.py` five-provider API transport contract; do not overwrite .env or saves. The three cropped bust preview assets are provisional, NOT final five-expression transparent rigs. Godot native parser/runtime verification is still an external release gate. See `docs/V100_ACCEPTANCE.md`.

## V0.9.5 handoff — finite social offers, shop ledger, Hermes PCM diagnostics
See CHANGELOG_V095.md, docs/V095_ACCEPTANCE.md and docs/HERMES_PCM_PARITY_V095.md. Five-provider Exodia contract preserved. Native Godot/Windows/Hermes verification outstanding.

## V0.9.2 (2026-11-18) — Conditional Trade / UI Readability
- Ground truth: `backend/proposals.py` + `backend/engine.py` pending proposal gate; catalog bonus items need explicit confirmation. 
- Godot: shelf-to-trade staging, opaque status area, mic-state clarity, sad/anger effects, voice pace telemetry.
- Exodia's five-provider Groq/Gemini API contract is mandatory and preserved; no credentials stored in game.
- Regression suite: 155 passing; full native Godot and live integration tests still outstanding.
- Read `CHANGELOG_V092.md` and `docs/V092_ACCEPTANCE.md`.

## V0.9.1 — HermesStream parser hotfix
- Fixed two inconsistent leading indents in `godot/scripts/HermesStream.gd`; this prevents Godot from parsing global class `HermesStream` and triggers an error in `Main.gd` line 31.
- Added GDScript indentation regression test, unchanged fast Groq/Gemini-API contract, and a new project title so installers can verify the update.
- Native Godot runtime acceptance pending on Windows. See `CHANGELOG_V091.md`.

# Current handoff: V0.9.0 Hermes & Living Interface Preview

This release builds on V0.8.0. Features: F5 voice inspector + health, adaptive PCM caption pacing, subtle illustrated atmospheric lighting and portrait acting, optional multilingual STT. No backend bargain/exodia logic changes apart from version metadata and optional STT language. Keep EXODIA_PROVIDERS/Groq API transport and the official game-dialogue endpoint at every merge. See `docs/V09_ACCEPTANCE.md`, `docs/HERMES_WORD_TIMING_REQUEST.md`, `CHANGELOG_V09.md`.

**Known QA limit:** Godot executable and Mac Hermes are not present here. Native preflight and speaker audition remain required.

---

## V0.8.0 — Negotiation & relationship memory (2026-11-18)

Implements source-level persistent, bounded, evidence-labeled per-customer memories. Memory is never a contract: hypothetical dates/gadgets and player-stated intentions cannot change game cash or inventory. `backend/relationship_memory.py`, `backend/engine.py` and `backend/exodia.py` supply fixed-topic context to the same fast `/api/command/tasks/game-dialogue` route without another LLM request. New hidden F9 Relationship Journal in `godot/scripts/Main.gd`; F8/F4/voice/UI preserved. `backend/content.py`, Hermes profile manifest and Exodia provider allowlist are unchanged. See `CHANGELOG_V080.md`, `docs/V08_ACCEPTANCE.md`, `INSTALL_V080.md`. Live Godot + Exodia + Hermes acceptance pending.

## V0.7 — Expressive Dialogue preview (2026-11-18)

The current development preview adds a shared local `DialogueDirector.gd` for seven animated emotional styles and a **F8 performance test studio** (Maya/Liu Xue, six dialogue samples, live adjustable impact intensity and typewriter speed). All actual gameplay text and the studio use the same renderer; no extra model inference. **F4** shows matched categories and intensity, and F6/F7 remain text-pacing controls. Native Windows Godot + Hermes acceptance remains necessary. See `CHANGELOG_V070.md` and `docs/V07_ACCEPTANCE.md`.


## V0.6.4 expressive dialogue and natural conversation
- Fixed exact source of repeated policy statement in `backend/trade_dialogue.py`; no more forced every-third-turn counteroffer. Explicit settlement guardrails are preserved at the game boundary, and banter supports playful/hypothetical remarks.
- `backend/exodia.py` short profile/prompt revised without changing five-provider Groq/Gemini API contract. User-supplied Exodia developer patch is release-blocking, never overwrite it with browser-only allowlist.
- `godot/scripts/EmotionGlyph.gd` is a new `RichTextEffect`; `DialoguePop.gd` now tracks actual visible glyphs for entrance tweens. `Main.gd` selects up to four high-impact emotion phrases in English or Mandarin with stronger text emphasis. F4 displays the chosen emphasis types.
- Voice selection uses Hermes preset manifest (30 IDs) and is locked for encounter; request speed pinned at 1.0 due Hermes V3 pitch-changing resample, pitch 0.0. `HermesStream.gd` records server run/model/instruction headers when present. Native Godot/Mac speech quality not verified; owner must test.
- Tests and shipping info in `CHANGELOG_V064.md`, `INSTALL_V064.md`. No mockup output was substituted for code.

## Active milestone V0.6.3 — bargain continuity / expressive speech / API and voice safety
- Implemented strict authoritative deal assembly (`backend/trade_dialogue.py`) with cash-only side deal guard and quote recap. A completed deal's visible offer now equals the accepted price.
- Groq + gemini-api preserved with `transport=api`; browser providers remain separate. Exodia developer production contract is **release-blocking**; see `docs/EXODIA_API_PROVIDERS.md`. No provider secrets in game.
- Godot `DialoguePop.gd` adds actual per-glyph entrance tween; Hermes **played PCM** drives estimated language-weighted text reveal. F6 slower / F7 faster saved locally. English/Mandarin emotional BBCode highlights expanded.
- Voice profile locked per session from `hermes_profile_manifest.json`; legacy preset aliases resolved explicitly. F4 displays provider, TTS engine, actual voice ID, preset, speed, mood, narration provenance and pacing.
- 76 Python/API/source contract tests pass; real Windows+Mac live test pending. See `CHANGELOG_V063.md`.

## Active milestone: V0.6.2 UI overhaul (2026-11-18)
- Replaced V0.6.1's precomposed ornament screenshot and expression thumbnail column with real, native Godot controls. Source: `godot/scripts/Main.gd`.
- New authoritative info panel with distinct item/price/offer/mood labels; five live CTA buttons and one text/microphone composer.
- New bell + counter-settle PCM WAV, preserved Hermes speech-synced rich-text and enhanced bilingual emphasis.
- Diagnostics hidden by default (F4). See `NATIVE_UI_SPEC_V062.md` for visual/layout acceptance gates and `CHANGELOG_V062.md` for delta.
- Native Godot, signed-in Exodia and Mac Hermes acceptance pending; no claim of live visual/audio confirmation.

## V0.6.1 visual fidelity integration
This milestone replaced the old layout in `godot/scripts/Main.gd` with the transparent ornate game HUD. Assets: `godot/assets/vn_ui_ornaments_v061.png`, `shop_bg_v061_dynasty.png`, five Liu Xue thumbs and original bell/footstep/typewriter WAV files. Use `VISUAL_FIDELITY_RULES_v061.md` as style/acceptance contract. Existing 21 NPC roster and Exodia game dialogue/early-sentence integration retained; backend port 8010, Exodia port 8766, Hermes remote port 8000. Python tests passed; native Godot not run. Do not claim one-to-one fidelity without Windows screenshot comparison.

## V0.6 expressive-dialogue hotfix
- Real implementation pass completed beyond concept art: Liu Xue is integrated into the actual roster/content layer.
- Godot client now includes typewriter ticks, event SFX hooks, keyword styling, and expanded portrait support.
- Repetition issue for returning-customer greetings reduced with varied greeting pools.
- Art direction anchor included at `LIU_XUE_ART_BIBLE_v06.png`.

# Living Counter v0.5 Handoff — 2026-11-17

Lead development milestone: **Presence & Responsiveness**. Owner approval: portrait upgrade, thinking state, local mic STT, open mic, prompt diet and diagnostics. Project is a Windows-first standalone Godot + Python app; **Exodia** at `127.0.0.1:8766` (user verified) supplies AI dialogue through local signed-in browser; **Hermes** at `10.0.0.129:8000` or `8880` supplies TTS from the Mac. Game director 127.0.0.1:8010 owns all negotiation decisions.

V0.5 is implemented and 58 Python/API tests pass; real Windows/Mac acceptance still pending. See `CHANGELOG_V05.md` for feature deltas, install steps, measurements, limitations. Preserve `save/`, `.env`, `.venv`, and Godot `user://` config when updating.

Key implementation files: `backend/exodia.py` compact prompt/profile, 45s saved-instruction count cache, performance metrics; `backend/dialogue_jobs.py` job metrics; `backend/stt_local.py` faster-whisper CPU/GPU worker; `backend/app.py` `/transcribe`, `/stt/health`, `/diagnostics/dialogue`; `godot/scripts/MicrophoneCapture.gd` VAD and hold-to-talk; `godot/scripts/Main.gd` thinking, open mic, F4 diagnostics, Maya VN art; `godot/assets/thinking_taps.wav`; `art/maya_vn_expression_master.png` + five cropped `vn_maya_*` states; `start_windows.ps1` corrected Python check and optional STT install.

Target: <=4 seconds **user send to audible NPC response**, not yet met/verified. Prompt size measured down ~54% before adding short lore. Exodia browser delay and Hermes first PCM measured independently; see in-game F4 and local `/diagnostics/dialogue` (debug mode). Don't claim model inference accelerated without owner data. Real microphone test must cover echo, threshold and accidental interruptions. Godot is not installed in this execution environment, so its GDScript needs the owner's first launch gate.

Art: only Maya was upgraded to cohesive high-resolution five-state original illustration in this release. Do not present image concept art or preview composites as running Godot screenshots. Remaining 19 customers still use legacy artwork.

## V1.2.4 Portrait Recovery preview (2026-11-19)
- F2 review mode, rejected-art constant fix, 4/12 original Master Chen art candidates staged only, no production portrait replacement.
- Seven-character 12-state art lock remains in force; V1.2.4 not owner-approved. Run `python tools/validate_portraits_v123.py --strict` to see open blocker.
- Exodia provider code unchanged; no live Godot/Hermes validation claim.


## V1.2.4.3 — Audio and layout correction
Restored readable 4-row shop dock; both voice meters now live inside opaque panels below contextual controls. Glyph emphasis is mildly audio-level-reactive. F4/F8 shortcut collision fixed. Seven rejected portrait sets remain a hard release blocker; no neutral-only artwork has been approved.

## V1.2.4.4 (Nov 19, 2026) — Two-character art integration
Master Chen and Tarek have five individual native RGBA portraits (neutral,
thinking, amused, skeptical, annoyed) installed in `godot/assets/` and F2 review.
Godot `Main.gd` uses them in ordinary conversations through explicitly flagged
unapproved QA exception. F4 displays actual state and `FIVE_STATE_TRIAL_NOT_APPROVED`
or honest nearest-state fallback. All other rejected artwork locked. STRICT gate
remains failed until all 12 states and owner approval. Exodia unchanged.
Native Godot Windows playtest is still required.
