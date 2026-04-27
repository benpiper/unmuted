## 2025-04-27 - [CRITICAL] Path Traversal via Incorrect exception expectation in pathlib
**Vulnerability:** The workspace path validation in `backend/security.py` failed to prevent path traversal because it expected `pathlib.Path.is_relative_to` to raise a `ValueError` if the path wasn't relative, rather than returning `False`.
**Learning:** `pathlib.Path.is_relative_to(other)` returns a boolean and does *not* throw an exception if the path is outside `other`. Thus, a `try-except ValueError` construct around it is an insecure and ineffective validation measure in this project's security controls.
**Prevention:** Always verify boolean-returning path checks directly with `if not resolved.is_relative_to(base):` instead of relying on caught exceptions for access control validations.
