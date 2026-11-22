# V1.2.4.2 — Runtime truth & diagnostic layout hotfix

## Verified root causes
- Godot project window title was V1.2.4 while an older V1.2.3 in-game banner remained hard-coded in `Main.gd`.
- Requested emotion could be `annoyed` while the actually displayed portrait stayed `neutral`: the existing unapproved-art gate intentionally locks seven rejected visitors to their only available production-size neutral portrait.
- F4 was a fixed-size Label with more text than its allocated bounds and drew across buttons/dialogue.

## Changes
- In-game build label reads V1.2.4 PORTRAIT RECOVERY, consistent with project.godot; a regression test compares them.
- F4 diagnostics use a clipped, scrollable container and include a close control. Portrait requested/displayed/gate/filename appear first.
- Exodia integration, gameplay economy, Hermes and production portrait approval remain unchanged.

## Explicit incomplete work
**This is not an art fix.** None of the seven rejected visitors has a complete 12-expression, native-resolution, owner-approved portrait set. A release must not masquerade tiny cropped art or transparent-border screenshots as full portrait rigs. Current art remains blocked, and natural gameplay still displays neutral for those visitors.

## Install
Overlay these files over V1.2.4 (including the separate portrait diagnostic overlay, which is incorporated here), keeping the folder layout. Restart Godot. F4 should scroll instead of covering game buttons. No `.env`, saves, or Exodia files are changed.
