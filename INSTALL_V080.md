# Install V0.8.0

**Recommended:** extract the complete ZIP into a new folder. Copy your *working* `.env` into `The_Living_Counter_POC/`. Back up then copy `save/world.json` if you want to preserve your existing characters, gold and inventory. Open `godot/project.godot`. From the root run:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_windows.ps1
```

**Overlay:** stop Godot and the backend, then extract the overlay ZIP into the root `The_Living_Counter_POC` folder with **preserved subdirectories** (`backend/`, `godot/`, `tests/`, etc.). Do not extract its contents into a flat folder or put the whole project ZIP inside the current project. Reopen Godot after overwriting scripts.

**Test:** visit Maya or Liu Xue, press **F9** for remembered social topics. Press **F8** for the prior dialogue test studio. Keep F4 for timings and selected Hermes profile. The F9 journal is deliberately hidden by default.

**Exodia:** preserve `EXODIA_PROVIDER=groq` or `gemini-api` in `.env` and restart the backend after changing it. API keys stay in Exodia, not this project.

**Limits:** Native Godot, real Groq and Hermes synthesis must be checked on your machine. Python regression tests verify the code and API contract but cannot certify playback or appearance.
