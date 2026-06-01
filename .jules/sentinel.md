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

## 2025-02-27 - CORS Wildcard and Credentials Collision
**Vulnerability:** The application was susceptible to overly permissive CORS configuration. Although rendering deployments were auto-detected, custom CORS rules from `CORS_ORIGINS` could introduce wildcard origins or improperly formatted URLs that crash Starlette when used alongside `allow_credentials=True`.
**Learning:** Starlette/FastAPI CORS middleware throws an error if `allow_credentials=True` is combined with `allow_origins=["*"]`. Furthermore, accepting unvalidated inputs for CORS origins opens the application to broader attack surfaces.
**Prevention:** Validate origin URLs using `urllib.parse.urlparse` to ensure valid schemes (http/https) and explicitly ignore/strip wildcard domains from dynamic environments variables when `allow_credentials` is enabled.

## 2025-02-27 - Information Leakage via Raw Exceptions
**Vulnerability:** In `backend/main.py`, the `extract_project` endpoint caught generic exceptions and exposed `str(e)` directly back to the client in an HTTPException.
**Learning:** Returning `str(e)` on unhandled exceptions can leak internal paths, logic, or unhandled states, providing attackers with more context.
**Prevention:** Catch explicit/expected exceptions, or safely log generic ones and return a sanitized, generic error message (like "Internal server error") to the API client.
