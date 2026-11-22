> **V1.2.2 OWNER OVERRIDE:** The persistent left-side Visitors column is explicitly rejected and MUST NOT be rebuilt. Visitor selection is a hidden F11 gallery or a compact menu. Floating small expression portraits are also rejected: acting belongs to the full illustrated portrait. See `docs/V122_ACCEPTANCE_AND_ART_GATE.md` and `art/character_art_rejections_v122.json`. This overrides the old V1.1 left-navigation requirement below.

# The Living Counter — V1.1 Visual & Acting Art Bible

**Approval source**: User-supplied V1.1 interface benchmark, translated to native Godot controls. **Creative direction**: 80% design-language inspiration, not screenshot tracing or asset reuse.

## Composition

The shop scene fills the screen behind a life-sized illustrated character, who remains the emotional focal point. Keep a restrained top bar for day/gold/AI indicator. On the **left**, put real selectable visitors and navigation. On the **right**, show the character's identity, disposition, item, listed price, their offer, and real trade actions. Place an ornate, high-contrast voice-synchronized dialogue frame near the counter's bottom with contextual story interactions. Keep voice input clear. Do **not** include the reference image's promotional row of four archetypes at the bottom.

Top-down hierarchy: illustration → expressive speech → actual terms → contextual choices → secondary shop records. Native Godot buttons, panel borders and tooltips; ornaments are noninteractive separate assets only. Avoid putting text over highlights, windows, or portrait faces.

## Color & typographic language

- Background: painterly warm mahogany, porcelain blue and amber lanterns, with natural shadow depths.
- Foreground: deep plum/ink `#210b2a`; borders gold `#ffca75`; primary dialogue warm ivory `#fef0df`.
- Emotions: gold value/delight, red anger, cyan persuasion, violet doubt, rose flirtation, subdued slate-blue sadness, green agreement.
- Typography: elegant readable serif for speech, stronger bold/italic variants for selective emphasized phrases. No neon effect on every word.
- Subtle verbal cues may add animated symbol/particle accents by the speaker, not giant floating widgets covering the face.

## Production character spec

**Required eight states** for each of Safiya, Elara, Rin and Master Chen:

1. Neutral/listening — a calm, distinct anchor.
2. Thinking — purposeful eye/hand movement.
3. Amused — light smiling or playful expression.
4. Skeptical — guarded or doubtful reaction.
5. Delighted — genuinely warm reaction.
6. Annoyed — displeasure that is easily distinguishable.
7. Surprised — authentic surprise, not just widened pupils.
8. Sad — meaningful subdued emotional read.

Recommended future states: **flustered/teasing** and **furious/walkout**.

Export full portrait PNGs with transparency at **1024×1536 native pixels minimum**. Preserve overall pose alignment and signature costume hardware. Character expressions must be separately illustrated, not vectors recolored over one photo or stretched contact-sheet cells. Portrait edges should blend into the shop naturally without imported matte/backdrop. Art assets are independent from UI layout and have consistent anchor/scale in Godot.

## Character-specific visual anchors

- **Safiya al-Nur**: adult desert astronomer, indigo celestial veil, crescent and astrolabe jewelry, braided dark hair, amber eyes. Poised, meticulous, otherworldly but grounded.
- **Elara Veyne**: adult manuscript scholar, violet-black side braid, silver floral head ornament and dangling gems, ivory lace blouse, ornate navy-purple velvet cloak. Reserved, sharp, unexpectedly amused.
- **Rin Kaede**: adult modern performer, expressive stage personality, carefully kept signature hairstyle and accessories, fashionable stage-ready outfit distinct from a historical character. Energetic and theatrical without changing her identity between expressions.
- **Master Chen Wei**: older Chinese master appraiser, meticulous eyeglasses, silver-white hair and beard, traditional layered appraisal attire, dignified gestures. Expressions must preserve his age and distinctive facial proportions.

## Actual V1.1 artwork progress

See `art/character_art_manifest_v11.json`. Elara now has **8 different illustrative poses**, exported separately as transparent 768×1024 previews from an authored composite. These are **expression studies below the 1024×1536 native production resolution gate**. Safiya, Rin and Master Chen still have only their V1.0 single portrait assets. **The four full production rigs are not art-complete.** Any claim otherwise is inaccurate.

## Why the previous technique failed

Cropping people out of a full UI concept gives mismatched light, weak transparency edges, inconsistent poses and no independent expression rig. Baking the UI into an image makes buttons fake and text unreadable. This project now uses a code/native-UI gate plus a separate art sign-off; neither is satisfied by a screenshot mockup.
