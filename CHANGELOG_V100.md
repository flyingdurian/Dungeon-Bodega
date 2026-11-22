# The Living Counter V1.0.0 — Living Interface & New Visitors

## Implemented in the Godot source
- Four new gameplay characters: Safiya al-Nur, Elara Veyne, Rin Kaede and Master Chen Wei; each has its own biography, speech style, bargain strategy, romance/social temperament and Hermes preset mapping.
- Expanded selectable cast from 21 to 25; mixed, fantasy and modern rosters are now 25/13/12.
- New F11 visitor gallery with dedicated illustrated thumbnail assets, eight featured visitor cards, and direct selection into the authoritative `/encounter` endpoint.
- New compact brand header and left-hand native navigation for Visitors, Shelves, Ledger, Relationships; preserved existing bargaining controls, microphones and diagnostics.
- A new illustrated Jade Atelier environment with a Settings toggle to restore the Dynasty Shop.
- Dramatic phrase-level dialogue echoes on emotional cues, triggered by reveal timing, plus a short dialogue-panel light pulse.
- System-font serif dialogue styling through Godot's SystemFont (uses OS fonts; no font files bundled).
- Maintains existing V0.9.5 finite conditional negotiation, real-inventory bundles and restocking.
- Exodia's five providers and API transports are preserved, without credentials in this project.

## Artwork completion status
- Safiya: individually generated, full high-resolution transparent VN portrait.
- Elara, Rin and Master Chen: separate original illustrated character busts extracted from our concept illustration, softened at the edges for compositing. These are FIRST-PASS art assets, not independently re-illustrated or registered multi-expression rigs. A full high-resolution five-expression replacement set remains an art gate.
- No screenshot UI has been pasted into Godot controls. The decorative shop background is a clean environment painting, separate from native interactive UI.

## Verification
- Automated Python, asset and static Godot-source checks are run for every archive. Native Windows Godot rendering, real microphone and Mac Hermes audio are NOT verified in this environment; v1.0.0 is a release candidate until owner playtest.
