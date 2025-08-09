from __future__ import annotations

import inspect
import os
from pathlib import Path


def project_root(proj_dir_name: str) -> Path:
    """Find an ancestor directory named ``proj_dir_name`` starting from the caller's file.

    Behavior:
    - Starts from the directory containing the caller's module (via ``__file__``).
    - Walks up the parent directories until a directory whose name matches
      ``proj_dir_name`` is found.
    - Returns the matching directory path.

    Notes:
    - On Windows, the name comparison is case-insensitive.
    - If the caller context lacks ``__file__`` (e.g., interactive session), the
      search starts from the current working directory.

    Raises:
    - ValueError: if ``proj_dir_name`` is empty or not a valid directory name.
    - FileNotFoundError: if no matching ancestor directory is found.
    """

    if not proj_dir_name or proj_dir_name in {"/", "\\", "."}:
        raise ValueError("proj_dir_name must be a non-empty directory name")

    start = _caller_file_dir()
    current = start.resolve()

    while True:
        if _is_filenames_equal(current.name, proj_dir_name):
            return current

        parent = current.parent
        if parent == current:
            break  # Reached filesystem root
        current = parent

    raise FileNotFoundError(
        f"Directory named '{proj_dir_name}' not found above {start}"
    )


def _caller_file_dir() -> Path:
    """Best-effort directory of the caller's module file.

    Walk the call stack until we find a frame that has a __file__ in globals,
    then return its parent directory. Fallback to the current working directory
    if no such frame is found (e.g., interactive/REPL).
    """
    stack = inspect.stack()
    try:
        # Skip our own frame (index 0) and any frames from this module
        # so we return the caller of project_root, not helper.py itself.
        for fi in stack[1:]:
            mod_name = fi.frame.f_globals.get("__name__")
            if mod_name == __name__:
                continue

            file = fi.frame.f_globals.get("__file__")
            if file:
                try:
                    return Path(file).resolve().parent
                except Exception:
                    # If resolution fails for any reason, fallback to parent
                    return Path(file).parent
    finally:
        # Break potential reference cycles
        del stack

    return Path.cwd()


def _is_filenames_equal(a: str, b: str) -> bool:
    """Compare directory names with OS-appropriate semantics.

    On Windows, compare case-insensitively; elsewhere, case-sensitively.
    """
    if os.name == "nt":
        return a.lower() == b.lower()
    return a == b
