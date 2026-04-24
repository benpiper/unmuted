"""Security utilities for path validation and workspace access control."""

import os
import logging
from pathlib import Path
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def get_workspace_base() -> Path:
    """Return the permitted base directory for all workspace paths."""
    raw = os.getenv("WORKSPACE_BASE_DIR", "workspaces")
    return Path(raw).expanduser().resolve()


def validate_workspace_path(path: str) -> Path:
    """
    Validate that a path is within the permitted workspace base directory.
    Prevents path traversal attacks.

    Args:
        path: The user-supplied path to validate

    Returns:
        Resolved Path object if valid

    Raises:
        HTTPException: 400 if path is invalid or outside permitted base
    """
    base = get_workspace_base()
    try:
        resolved = Path(path).expanduser().resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    try:
        resolved.is_relative_to(base)
    except ValueError:
        logger.warning(
            "Path traversal attempt blocked",
            extra={"requested": str(path), "resolved": str(resolved), "base": str(base)},
        )
        raise HTTPException(status_code=400, detail="Path not permitted")

    return resolved
