## 2025-04-27 - [CRITICAL] Path Traversal via Incorrect exception expectation in pathlib
**Vulnerability:** The workspace path validation in `backend/security.py` failed to prevent path traversal because it expected `pathlib.Path.is_relative_to` to raise a `ValueError` if the path wasn't relative, rather than returning `False`.
**Learning:** `pathlib.Path.is_relative_to(other)` returns a boolean and does *not* throw an exception if the path is outside `other`. Thus, a `try-except ValueError` construct around it is an insecure and ineffective validation measure in this project's security controls.
**Prevention:** Always verify boolean-returning path checks directly with `if not resolved.is_relative_to(base):` instead of relying on caught exceptions for access control validations.

## 2026-04-29 - [HIGH] Insecure Direct Object Reference (IDOR) in Job Creation Endpoint
**Vulnerability:** The `/api/project/render` endpoint allowed any authenticated user to create a rendering job and potentially interact with any workspace directory path, because it was missing the `await verify_project_ownership(req.directory_path, db, current_user)` check that other endpoints have.
**Learning:** Due to the RPC-heavy nature of the FastAPI backend using standard background jobs, POST endpoints handling project mutations must explicitly call the ownership verification dependency instead of relying on generic route-level middleware, which is easy to accidentally omit when adding new endpoints.
**Prevention:** Whenever creating a new POST route that mutates or interacts with project state via `directory_path`, ensure the `verify_project_ownership` dependency is explicitly awaited at the top of the route handler.
## 2024-04-30 - [IDOR in Job Status and Cancellation]
**Vulnerability:** Insecure Direct Object Reference (IDOR) where `/api/jobs/{job_id}/status` and `/api/jobs/{job_id}` (DELETE) endpoints relied solely on the in-memory `job_manager` to lookup jobs without querying the database to verify if the job belonged to a project owned by the `current_user`.
**Learning:** Any endpoint exposing state or allowing mutation must verify the caller's authorization against the persisted data model (database), even if the primary state tracking is delegated to an in-memory cache or job queue. Caches and managers typically lack the relational context required for authorization.
**Prevention:** Always join the related entity (e.g., `JobRecord` -> `Project`) and check the `owner_id` against the current user's ID before allowing access to an object.

## 2024-05-01 - [MEDIUM] Information Leakage in Extract Project Endpoint
**Vulnerability:** The `/api/project/extract` endpoint was catching generic exceptions and returning the raw string representation of the exception (`str(e)`) directly to the client in an HTTPException with status code 400.
**Learning:** Returning raw exception details can leak sensitive information about the internal workings, file paths, or state of the application to potentially malicious users.
**Prevention:** Catch generic exceptions, log them securely with full traceback using `logger.error`, and return a generic "Internal server error" message with status code 500 to the client. Always ensure `except HTTPException: raise` is placed before the generic catch-all so intentional API errors are not swallowed.
