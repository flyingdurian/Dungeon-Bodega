# Install The Living Counter V0.6.4

**Overlay**: Extract the overlay ZIP directly within the EXISTING `The_Living_Counter_POC` directory so it overwrites `backend/`, `godot/`, `docs/`, and other files at their correct relative paths. Do not put the ZIP's contents one folder above or inside `godot/`. Stop Godot and the Python backend first, then restart both.

**Complete project**: Extract to a fresh directory. Copy `.env` from your working install and any saves you want to keep. Run `powershell -ExecutionPolicy Bypass -File .\start_windows.ps1` in `The_Living_Counter_POC` and open `godot/project.godot`.

**Exodia**: Your `.env` chooses `EXODIA_PROVIDER=groq`, `gemini-api`, `deepseek`, `gemini`, or `chatgpt`. The keys remain in Exodia, not the game. Groq/Gemini API use `transport=api` and the other three use `browser`; endpoint is always `/api/command/tasks/game-dialogue`.

**Debug**: F4 shows provider/source, Hermes voice preset ID, model/run ID if reported, speed, dialogue-emphasis categories, and audio latency. F6/F7 change approximate text pacing. No Windows/Godot runtime certification was performed by the build environment.
