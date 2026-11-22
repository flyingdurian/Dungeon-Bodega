---
name: living-counter-visual-bible
summary: Enforce The Living Counter's illustrated-character, dialogue, native-UI and production art standards.
---

# The Living Counter — Production Visual Bible Skill

## Always read this before visual work

**V1.2.3 owner override (highest priority):** Read `docs/QUALITY_LOCK_V123.md`. Twelve real full-size expressive portraits per character are now mandatory; the older eight-expression rule below is superseded. Rejected designs remain blocked until explicit owner approval. Persistent Shelves/Ledger/Relationships/Leads controls and live mic/Hermes output waveform are also mandatory.

This is a **project-local skill**, bundled with the source for coding/art agents.
Follow `docs/V110_ART_BIBLE.md` and `art/character_art_manifest_v11.json`.
Never call a mockup, contact sheet, enlarged thumbnail, or screenshot crop a finished in-game portrait.

## Nonnegotiable character art contract

- One **consistent identity anchor** per character: face geometry, eye style, color, hairstyle, outfit, jewelry and accessories fixed.
- **Twelve distinct hand-illustrated or image-generated expression poses**, minimum (older list below is illustrative; complete canonical set is in `docs/QUALITY_LOCK_V123.md`): neutral, thinking, amused, skeptical, delighted, annoyed, surprised, sad. Two future additions: flustered and furious.
- Separate true-RGBA PNG files, at **native resolution at least 1024×1536** for production. Transparent background and clean semi-transparent edge pixels. No matte, colored background, checkerboard baked into pixels, cropped gameplay mockup, or pasted UI decoration.
- Keep face scale and camera anchor aligned across states. Different facial expression and hand gesture are welcome; an incorrectly shifted head is not.
- **Do not** generate 8 sprite names from 1 source image by copying it or just tinting/warping. A resized 384×512 cell is an art study, not an approved 1024×1536 master.
- Include source, reviewer images, exact expression manifest, native dimensions and a validator report. If an asset does not meet the gate, mark it **incomplete** visibly. No silent placeholders.

## UI implementation contract

- Inspired by the approved V1.1 reference: warm storybook shop, dark plum surfaces, gold/rose/cyan emotional accents, compact top bar, F11 visitor gallery (hidden until opened), no permanent left-side rail, immersive large character, prominently illustrated rich-text dialogue, readable right-side price/offer card, natural voice input, contextual encounter actions.
- The bottom V1.0 **archetype promotional strip is not part of gameplay**. Do not recreate it.
- Implement every input as an actual Godot Control; do not bake a UI into scene art. Decorations may be standalone alpha PNG accents with noninteractive mouse filtering.
- Anchor to the 1440×900 design canvas; ensure 1280×800 scaled presentation and no overlap with text, CTA, portrait or dynamic dialogue.
- Expressions respond automatically to engine/AI emotions. Never place a developer expression picker on the player's main gameplay surface.
- Emphasis is selective, meaningful and timed to speech; stronger feeling gets larger differentiated type rather than making everything glow.

## Review and packaging gate

1. Compare isolated expression exports against the fixed character anchor.
2. Execute `python tools/validate_visual_art_v11.py --strict` and fix every failure before claiming the art is complete.
3. Execute `python -m pytest -q` and native Godot parser/startup checks before claiming a release.
4. Preserve `backend/exodia.py` five-provider API/browser contract, Hermes fixed voice-profile contract, `.env` and saved progress.
5. Document actual screenshots from the running Godot game separately from concept art and asset reviews.

Do not bypass a failed visual gate to ship a version as production ready.

## Owner feedback — V1.2.2 rejection lock

Never reintroduce an always-visible Visitors rail or a floating duplicate face cut-in. The owner has rejected **Master Chen Wei, Tarek Ashwood, Felix Rowe, Safiya al-Nur, Rin Kaede, Yuna Seo and Mara Copperwell**. Those assets remain nonproduction until fully redrawn with all eight native-size expressive states and individually accepted. Refer to `art/character_art_rejections_v122.json`. The optional shopkeeper intuition panel is a probabilistic **player observation**, NOT the NPC's inner monologue, lie detection or an alternative facial expression. It must have no gold, inventory, or accepted-price authority.

## V1.2.3 permanent upgrade

- Never equate a character sheet with 12 independent production portraits. `python tools/validate_portraits_v123.py --strict` is the current objective gate.
- Main portrait acts emotionally, no small duplicate face cut-ins. Store visible disposition and intuition inference independently.
- Always-on direct shop utility buttons required; not an always-on visitor roster.
- Real input/output waveform from captured mic samples / Godot Hermes output, not ornamental animation.

## V1.2.4 staged artwork review

The review directory `godot/assets/art_review/` is intentionally separate from release portraits. Four independent Master Chen native-resolution original candidate PNGs are available for an **F2** in-engine preview. They are **not** yet production-approved or representative of a completed 12-state rig. Always keep candidate counts separate from approved production counts; never pass a strict art gate by cropping a generated art board.
