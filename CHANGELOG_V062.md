# V0.6.2 — Native UI/UX overhaul (2026-11-18)

This update fixes the layout/asset-overlay regression exposed in the V0.6.1 Windows screenshot.

## Built
- Removed the precomposed decorative HUD image and expression-thumbnail rail from the active Godot scene. The shop image is now **background environment only**; all visible UI surfaces, text, and controls are native Godot objects.
- Rebuilt the 1440×900 virtual canvas around a single clear hierarchy: customer portrait, right-side profile/price card, five actionable CTAs, main speech panel, and bottom voice/text input.
- Customer card now shows the live disposition, current item, listed price and their offer in distinct rows, updated from authoritative backend state.
- CTA rail: Ask Price, Counter Offer, Accept Deal, End Chat, Next Visitor. Counter Offer deliberately prepares an editable offer in the text field rather than submitting an arbitrary number without approval.
- Removed top-left duplicate masthead and eliminated the permanently visible performance block; F4 opens diagnostics and F3 opens the optional developer inspector. Esc closes overlays.
- Preserved all five Liu Xue expression portraits, with emotion changes visible on the single large portrait and short transient reaction glyphs.
- Stronger English/Mandarin keyword effects: price = gold/wave; better deal = cyan/underline/wave; insult/anger = crimson/shake; praise = warm pulse. Hermes progressive reveal and quiet typewriter ticks remain active.
- Removed the sci-fi door sweep from active playback. New two-tone shop bell at arrival, quiet footsteps, then a subdued wooden settle. The sources are local 24 kHz PCM WAV and do not require network access.

## Important
- This is an **actual code/art/audio project update**, not a mockup. The old screenshot ornament file is removed from the shipped project.
- Python and asset validation is automated; native Godot rendering and the user's signed-in Exodia/Hermes hardware are not available in this runtime and require Windows acceptance testing.
- No changes to the Exodia game-dialogue route, Hermes streaming protocol, economy rules, or save format.
