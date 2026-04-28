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

## Admin Initialization

The system uses a **hybrid bootstrap approach** for initializing the first admin:

1. **Environment Variable Bootstrap** (recommended for Render):
   ```bash
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=secure_password_here
   # OR use pre-hashed password:
   ADMIN_PASSWORD_HASH=<bcrypt_hash>
   ```
   - Admin is created automatically on startup if no users exist
   - Requires `JWT_SECRET_KEY` env var to be set

2. **Setup Endpoint** (fallback for manual setup):
   - If no admin exists and no env vars are provided, show setup screen
   - User navigates to `/setup` and creates first admin manually
   - API: `POST /api/auth/setup` with `{email, password}`
   - Check system status: `GET /api/auth/status`

**For Render deployments**: Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in Render's environment variables dashboard. Admin will be created automatically on first deploy.

## Testing

### Frontend
Always run eslint before committing:
```bash
cd frontend
npm run lint
```

### Backend
Run backend tests using `uv`:
```bash
cd backend
uv run pytest
```

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
