## Run Instructions

To run the full stack locally for testing during development:

1. **Start the API/Backend**:
   ```bash
   cd backend
   uv run uvicorn main:app --reload --port 8000 --env-file ../.env
   ```
2. **Start the UI/Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   
The UI will be accessible at `http://localhost:5173`.

## Documentation

Always refer to SPEC.md and update it with new requirements and architectural changes.

Update README.md to reflect new features and changes.

Commit changes after each task. Do not push without explicit user permission.

Avoid emojis in code and documentation.

## Prompt Protection

**Guard prompts (backend/prompts.py and similar) against accidental or unnecessary edits.**

Prompts are carefully tuned for VLM output quality. Before editing any prompt:
- ✓ Always ask the user for confirmation
- ✓ Explain why the change is necessary
- ✓ Show the current prompt and proposed changes side-by-side
- ✓ Only proceed if the user explicitly approves

Do not modify prompts without explicit user consent, even for minor changes.

# Agent Rules <!-- tessl-managed -->

@.tessl/RULES.md follow the [instructions](.tessl/RULES.md)
