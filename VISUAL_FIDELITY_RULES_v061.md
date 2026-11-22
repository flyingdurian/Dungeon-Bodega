# The Living Counter — Visual Fidelity Rules (v0.6.1)

## Source of truth
Reference: user-provided `image(20261118-112850).png` (concept) compared against `image(20261118-112903).png` (previous live game).
The older UI was a functional prototype, NOT an approved visual direction. Use the concept for hierarchy, materials, contrast, layout and emotional text. Do not convert a flattened mockup into a noninteractive screenshot.

## Native Godot composition (1440 × 900)
- Main scene: Chinese curio shop, warm glowing lanterns, wood, blossoms; separate backdrop PNG.
- Primary transparent character: large central portrait, 920×800 viewport, begins around x166, y-24. Never put a flat photo background behind a character.
- Five expressions: stacked thumbnail selectors at left x14, y126+106n. Active expression is emphasized; click to preview.
- Action rail: four ornate purple/gold controls at right x1146, y319/397/475/553. All remain mapped to original authoritative game actions.
- Dialogue: primary focus. Ornate transparent HUD overlay has a dialogue frame at x219, y599, w910, h192; live Godot RichTextLabel x251,y658,w856,h117.
- Speaker ribbon x245, y572, w301, h54. Replay voice beside nameplate.
- Primary voice input: purple/rose voice element lower-left, hold/release to send; open mic still optional.
- Text input: native LineEdit lower center x248 y815, not a screenshot field.
- Developer timings: small right-side panel x1145 y630 (F4 toggles) + top HUD readout.
- Inventory: collapsible drawer; do not cover the main portrait by default.

## Color system
- Ornamental gold: #F7CE7C / bright strokes #FFCF4F
- Ink/plum dialogue: #170923 / #351536
- Ivory dialogue body: #FEF0DF
- Anger/impact: #FF535D with shake and strong outline
- Positive/pleased: #FFE37A with pulse or bright wave
- Bargaining/value: luminous gold for price; aqua or violet for doubt/context
- Speech controls: purple/magenta, never an industrial black-gray bar

## Text animation requirements
- Drive reveal from Hermes audio progress when speaking, fall back to time-based text when speech is off/unavailable.
- Use the original LLM plaintext as authoritative content. Add BBCode only in rendering, not in model output or TTS.
- One-pass keyword matching to avoid corrupted nesting. Support Mandarin and English; price, hostile, pleased, skeptical and emphatic punctuation spans.
- Minimize noise: short felt typing clicks ~120ms apart at -36 dB relative to game mix, never overpower voice.
- Do not use overlong text cascades, fullscreen flashing or blanket paragraph shake.
- Character can be interrupted; text must not continue past an interrupted Hermes segment.

## Audio cues
- Enter: two-note shop bell, no sweeping sci-fi synthesizer (new `sfx_shop_bell_v061.wav`).
- Approach: quiet footsteps, delayed 0.55s after bell (new `sfx_customer_footsteps_v061.wav`).
- Violent exit/counter impact: brief wood thud + short dialogue impact movement.
- Sounds are independent from Hermes; the spoken line remains clearly audible.

## QA and acceptance
- Verify portrait transparency and consistency with all five modes.
- Compare at 1440×900, then at 1280×800 window scaling.
- Verify highlighted `这个价格`, `太贵`, `better deal`, `gold`, `谢谢` and `leave` have obvious distinct styles in the actual Godot scene.
- Test scripted fallback + live Exodia early_sentence, and barge-in while the first sentence speaks.
- Test clear bell, quiet approach, natural Hermes volume, typing clicks no louder than speech.
- Close/open inventory drawer and F4 timings; settings and actions must still work.

## Limitations
- This is an integrated high-fidelity layout *pass*, not a pixel-identical reconstruction of a raster concept. Exact font and brush/particle details are still subject to native Godot playtest.
- Hermes does not return word timestamps: text sync is approximate playback-time sync.
- Other customers retain prior non-illustrated art until their VN portrait sets are upgraded.
