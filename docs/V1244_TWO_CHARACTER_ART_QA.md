# V1.2.4.4 — Two-character expression integration (owner review)

**Not a production-art-complete release.** Only Master Chen Wei and Tarek
Ashwood are affected. Each has five independent 1024×1536 RGBA PNG portraits
(Neutral, Thinking, Amused, Skeptical, Annoyed) anchored to their existing
character identity. No character sheets or cut-up reaction thumbnails are used.

## Native gameplay validation (Windows)
1. Install the overlay on V1.2.4.3 and restart Godot (re-import textures).
2. Select Master Chen through F11. Speak neutral, amusing, doubtful and annoyed
   lines; watch the **large main portrait** change, without second-face cut-ins.
3. Press F4. Requested and displayed state must agree for the five available
   expressions; the gate reads `FIVE_STATE_TRIAL_NOT_APPROVED`.
4. For `suspicious`, `angry`, `curious`, `delighted`, `surprised`, `flustered`,
   and `sad`, the F4 gate instead reads `TRIAL_NEAREST_STATE_NOT_APPROVED`
   with an honest available fallback. Do not mistake these for unique art.
5. Repeat for Tarek and press F2 to inspect only the five new candidates (even if old F2 images are left on disk by an overlay).
6. Test Felix/Rin/Safiya/Yuna/Mara: their original blocked art stays blocked.
7. Check Shelves/Ledger/Relationships/Leads, waveform, Groq, Hermes, trade.

## Remaining art
The mandatory 12-state art gate is still blocked: seven more original
transparent 1024×1536 portraits are required **per** Master Chen and Tarek,
as well as the outstanding sets for the remaining five rejected characters.
Owner must inspect and approve the art before release as finished character rigs.

## Technical checks
- `python -m pytest -q`
- `python tools/validate_portraits_v123.py --strict` **must currently fail**.
- `python tools/audit_runtime_portraits.py --json`
- Native Godot parser/import and running encounter screenshot: not available
  in the builder's environment; cannot claim they passed.
