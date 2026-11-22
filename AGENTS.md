## Owner quality override — V1.2.3 (READ FIRST)

Always read `docs/QUALITY_LOCK_V123.md` and `.agents/skills/living-counter-visual-bible/SKILL.md` **before** touching visual art, character logic, GUI, or voice. This directive supersedes any earlier 8-expression minimum: **12 full-resolution, distinct portraits per character**; no fake waveforms; restore persistent utility buttons; no permanent Visitors rail. Do not ship as production-approved while `tools/validate_portraits_v123.py --strict` fails.

# Development entry point — The Living Counter

For **every new character, UI element, expression, and portrait-art task**, read:

- `.agents/skills/living-counter-visual-bible/SKILL.md`
- `docs/V110_ART_BIBLE.md`
- `art/character_art_manifest_v11.json`

This is a repository-local skill, not a guarantee that an account-level plugin or global skill has been installed. Follow it on every future build. Do not regress the five-provider Exodia contract or Hermes voice profile mapping. Keep handoffs concise and track native Godot playtest proof separately from source tests.

V1.2 character additions: also consult `art/character_art_manifest_v12.json`, `docs/V120_ACCEPTANCE.md`, and run `python tools/validate_visual_art_v12.py --strict`. Never mark missing portraits as art-complete; do not use screenshot or contact-sheet cutouts to fill them.

V1.2.2 owner override: No permanent Visitors rail or floating second-face reaction cards. Seven character designs are rejected; consult `art/character_art_rejections_v122.json` and `docs/V122_ACCEPTANCE_AND_ART_GATE.md` before claiming portrait completion.

## V1.2.4 candidate review and source/art integrity

A newly rendered high-resolution portrait candidate is not an owner-approved production expression.
F2 cycles only independent candidate files under `godot/assets/art_review/` for currently selected rejected characters.
Never make `F2` or a generated contact sheet silently set `approved=true`, alter economy, or replace runtime art.
See `docs/V124_PORTRAIT_RECOVERY.md` and `art/portrait_recovery_status_v124.json` before claiming completion.

## V1.2.4.4 two-character owner-review exception
Master Chen Wei and Tarek Ashwood are **five-state in-game QA trials only**,
not owner-approved or twelve-state-complete. Their independent native 1024×1536
transparent images are now shown in ordinary gameplay for emotional states.
Remaining seven states per actor are still required before art approval.
The other five rejected visitors remain neutral-locked. Read
`art/portrait_trial_v1244.json` and `docs/V1244_TWO_CHARACTER_ART_QA.md`.
Do not use sheets, crop studies, or resized reaction icons to fill gaps.
