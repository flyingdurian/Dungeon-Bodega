# V1.2.4 portrait diagnostics — installation

This is an **audit/diagnostic patch**, **NOT new production character artwork**.

1. Install V1.2.4 full project first, or apply its overlay to V1.2.3. The screenshot titled V1.2.3 is not V1.2.4.
2. Close Godot and extract this ZIP into `The_Living_Counter_POC` preserving its `godot/`, `tools/`, `docs/`, `tests/` folders. Overwrite only `godot/scripts/Main.gd`.
3. Reopen Godot and press Play. Open F4 during Tarek or Rin dialogue. The diagnostic now explicitly shows **requested** vs **displayed** emotion and the production-art restriction.
4. In V1.2.4, press F11 to select Master Chen, then F2 for four isolated art review candidates; they are not production-approved.
5. Run `python tools/audit_runtime_portraits.py` to regenerate the inventory; `python tools/validate_portraits_v123.py --strict` will intentionally fail until all seven complete 12 approved original masters.

This patch DOES NOT modify `backend/exodia.py`, Hermes integration, player saves, `.env`, shop economy or UI layout. It does not fabricate, upscale or promote rejected portraits.
