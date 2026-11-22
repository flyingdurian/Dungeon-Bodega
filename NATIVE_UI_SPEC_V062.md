# The Living Counter — V0.6.2 Native Visual Contract

Canvas: logical **1440×900**, scaled by Godot to the requested desktop window. Controls are native and interactive; do not use screenshot overlays or rasterized buttons.

## Composition acceptance

| UI area | Design-space bounds | Behavior |
| --- | --- | --- |
| Shop environment | 0,0–1440,900 | Artwork only, no baked controls or dialogue |
| Character portrait | x147 y29 / 842×740 | Transparent VN PNG; changing texture reflects emotional state; no visible thumbnails |
| Thin status ribbon | x247 y13 / 1159×55 | Wait, prompt count, day, gold, compact settings |
| Customer/price card | x1036 y81 / 378×284 | Name, title, disposition, current item, listed price, their offer |
| Actions | x1056 / width341, y392..712 | Ask Price, Counter Offer, Accept Deal, End Chat, Next Visitor |
| Primary dialogue | x171 y590 / 852×194 | Nameplate, subtle status, Hermes-paced rich text, Replay voice |
| Player composer | x218 y811 / 806×69 | One editable text field and Send |
| Microphone | bottom left | Hold-to-talk and separate open-mic toggle |
| Diagnostics | F4 only | Hidden by default; no overlay clutter |

## Art direction
- Deep plum and crimson surfaces, illuminated warm ivory dialogue, brushed gold linework, restrained floral ornamentation and real portrait alpha.
- Do not use an expression-state selector as the default UI: states are represented by the character portrait, and can add one short reaction cue.
- Do not duplicate the top-left logo or draw from an image that already contains UI.
- Do not cover CTAs with the character, dialogue, or diagnostics.

## Expression / speech behavior
- NPC dialogue is revealed by progress from Hermes audio playback, not instantly dumped; in text-only mode the local typewriter advances normally.
- Render expressions using the five portrait assets. Thinking bubble is transient and disappears on response.
- Emotion BBCode is generated from unstyled original plain text, with one pass to avoid tag overlap. CJK and English keywords must both be recognized.
- Typewriter ticks are subtle and bounded by an approximately 120 ms maximum rate; incoming speech is always louder than ticks.

## Audio scene beats
1. Arrival: a recognizable, fixed-pitch two-note brass counter bell.
2. A short time later: quiet approach footsteps.
3. At counter: a restrained wood/fabric settle, not a synthesized rising whoosh.
4. Aggressive customer: optional small wooden impact. No full-screen shake for every ordinary line.

## Required manual QA
- Launch game in Godot at 1280×800 and maximized; inspect all controls and ensure no clipping/collisions.
- Select Liu Xue, then force neutral, thinking, amused, skeptical, annoyed naturally through encounters; verify full-size portraits change without thumbnails.
- Check listed price and offer update after counters and deal outcomes; all five CTA actions must hit the real backend.
- Speak with Hermes and ensure typewriter emphasis follows playback and typing clicks are quieter than the voice.
- Inspect Chinese examples: “这个价格” (gold), “太贵” (red), “便宜一点” (cyan), “谢谢” (warm).
- Verify F4 panel starts hidden and Esc closes active overlays.
- Check the new arrival bell with headphones and desktop speakers. Tune mix if needed.
