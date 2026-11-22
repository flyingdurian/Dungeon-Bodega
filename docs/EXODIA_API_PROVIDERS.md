# Exodia API provider compatibility (release blocking)

Allowed `EXODIA_PROVIDER`: `chatgpt`, `gemini`, `deepseek`, `groq`, `gemini-api`.

All shop dialogue MUST POST to `/api/command/tasks/game-dialogue` with `agent_id: kiko`, `web_research: false`.

| Model | Transport |
| --- | --- |
| chatgpt | browser |
| gemini | browser |
| deepseek | browser |
| groq | api |
| gemini-api | api |

`gemini` and `gemini-api` are distinct. `early_sentence` is optional for browser streams and normally absent for API providers. Speak the final `answer` only when `state: answered`.

Secrets stay in Exodia's `orchestrator/.env`, never in the game. Exodia supports `GROQ_API_KEY`, optional `GROQ_API_KEY_2`, `GEMINI_API_KEY`, optional `GEMINI_API_KEY_2`.

## Release gate

With a signed-in/running Exodia instance and `EXODIA_PROVIDER=groq`, confirm a real shop line yields `source=exodia_live`, empty `error`, Exodia logs POST /api/command/tasks/game-dialogue HTTP 201. API endpoints must not be called via browser transport.
