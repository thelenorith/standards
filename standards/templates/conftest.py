"""
Filesystem sandboxing conftest.py for ap-* projects.

Enforces test isolation by blocking filesystem reads and writes outside
of pytest's tmp_path. Follows FAIL-CLOSED design: if the sandbox cannot
be activated, the test session aborts rather than running unprotected.

Usage:
    Copy this file to your project's tests/conftest.py.
    The sandbox is activated automatically for all tests via autouse fixtures.

Principle:
    Tests must not read or write outside tmp_path. This conftest enforces
    that programmatically rather than relying on developer discipline alone.
"""

import builtins
import os
import pathlib
import shutil
import sys

import pytest

# ---------------------------------------------------------------------------
# Allowed paths: operations within these prefixes are always permitted.
# Customize _EXTRA_ALLOWED_PREFIXES for project-specific read-only paths
# (e.g., package data that must be importable during tests).
# ---------------------------------------------------------------------------
_EXTRA_ALLOWED_PREFIXES: list[str] = []

# Paths that are always allowed (Python internals, installed packages, etc.)
_ALWAYS_ALLOWED_PREFIXES: tuple[str, ...] = (
    # Python standard library and site-packages
    sys.prefix,
    sys.exec_prefix,
    # Common virtual-env locations
    os.path.join(os.getcwd(), ".venv"),
    os.path.join(os.getcwd(), "venv"),
    # Pytest and coverage internals
    "/tmp/pytest",
    # /dev/null, /dev/urandom, etc.
    "/dev/",
    # /proc and /sys for system introspection
    "/proc/",
    "/sys/",
)


def _is_allowed(filepath: str, tmp_path: pathlib.Path | None) -> bool:
    """Return True if *filepath* is inside an allowed location."""
    resolved = os.path.realpath(filepath)

    # tmp_path is always allowed when set
    if tmp_path is not None and resolved.startswith(str(tmp_path)):
        return True

    # Check always-allowed prefixes
    for prefix in _ALWAYS_ALLOWED_PREFIXES:
        if resolved.startswith(prefix):
            return True

    # Check project-specific allowed prefixes
    for prefix in _EXTRA_ALLOWED_PREFIXES:
        if resolved.startswith(os.path.realpath(prefix)):
            return True

    return False


def _is_write_mode(mode: str) -> bool:
    """Return True if *mode* indicates a write operation."""
    return any(ch in mode for ch in ("w", "a", "x", "+"))


# ---------------------------------------------------------------------------
# Sandbox fixture
# ---------------------------------------------------------------------------

class _FilesystemSandbox:
    """Wraps filesystem builtins to block operations outside tmp_path.

    Replaces builtins.open, pathlib read/write methods, os.remove/unlink,
    os.rename, os.makedirs, shutil.copy/copy2/move/rmtree, and
    pathlib.Path.mkdir with guarded versions.

    Raises PermissionError for any disallowed operation.
    """

    def __init__(self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
        self._tmp_path = tmp_path
        self._mp = monkeypatch
        self._active = False

        # Stash originals
        self._orig_open = builtins.open
        self._orig_path_write_text = pathlib.Path.write_text
        self._orig_path_write_bytes = pathlib.Path.write_bytes
        self._orig_path_read_text = pathlib.Path.read_text
        self._orig_path_read_bytes = pathlib.Path.read_bytes
        self._orig_path_mkdir = pathlib.Path.mkdir
        self._orig_path_unlink = pathlib.Path.unlink
        self._orig_path_rmdir = pathlib.Path.rmdir
        self._orig_os_remove = os.remove
        self._orig_os_unlink = os.unlink
        self._orig_os_rename = os.rename
        self._orig_os_makedirs = os.makedirs
        self._orig_shutil_copy = shutil.copy
        self._orig_shutil_copy2 = shutil.copy2
        self._orig_shutil_move = shutil.move
        self._orig_shutil_rmtree = shutil.rmtree

    def activate(self) -> None:
        """Install all guards. Raises RuntimeError if activation fails."""
        sandbox = self

        # --- builtins.open ---
        orig_open = self._orig_open

        def guarded_open(file, mode="r", *args, **kwargs):
            filepath = str(file)
            if _is_write_mode(mode) and not _is_allowed(filepath, sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: write to {filepath!r} blocked (outside tmp_path)"
                )
            if not _is_write_mode(mode) and not _is_allowed(filepath, sandbox._tmp_path):
                # Allow reading the project source tree (for imports, coverage)
                project_root = os.getcwd()
                if not os.path.realpath(filepath).startswith(project_root):
                    raise PermissionError(
                        f"Sandbox: read from {filepath!r} blocked (outside tmp_path and project)"
                    )
            return orig_open(file, mode, *args, **kwargs)

        self._mp.setattr(builtins, "open", guarded_open)

        # --- pathlib.Path write methods ---
        orig_write_text = self._orig_path_write_text

        def guarded_write_text(self_path, *args, **kwargs):
            if not _is_allowed(str(self_path), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: Path.write_text to {self_path!s} blocked"
                )
            return orig_write_text(self_path, *args, **kwargs)

        self._mp.setattr(pathlib.Path, "write_text", guarded_write_text)

        orig_write_bytes = self._orig_path_write_bytes

        def guarded_write_bytes(self_path, *args, **kwargs):
            if not _is_allowed(str(self_path), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: Path.write_bytes to {self_path!s} blocked"
                )
            return orig_write_bytes(self_path, *args, **kwargs)

        self._mp.setattr(pathlib.Path, "write_bytes", guarded_write_bytes)

        # --- pathlib.Path read methods ---
        orig_read_text = self._orig_path_read_text

        def guarded_read_text(self_path, *args, **kwargs):
            filepath = str(self_path)
            if not _is_allowed(filepath, sandbox._tmp_path):
                project_root = os.getcwd()
                if not os.path.realpath(filepath).startswith(project_root):
                    raise PermissionError(
                        f"Sandbox: Path.read_text from {self_path!s} blocked"
                    )
            return orig_read_text(self_path, *args, **kwargs)

        self._mp.setattr(pathlib.Path, "read_text", guarded_read_text)

        orig_read_bytes = self._orig_path_read_bytes

        def guarded_read_bytes(self_path, *args, **kwargs):
            filepath = str(self_path)
            if not _is_allowed(filepath, sandbox._tmp_path):
                project_root = os.getcwd()
                if not os.path.realpath(filepath).startswith(project_root):
                    raise PermissionError(
                        f"Sandbox: Path.read_bytes from {self_path!s} blocked"
                    )
            return orig_read_bytes(self_path, *args, **kwargs)

        self._mp.setattr(pathlib.Path, "read_bytes", guarded_read_bytes)

        # --- pathlib.Path.mkdir ---
        orig_mkdir = self._orig_path_mkdir

        def guarded_mkdir(self_path, *args, **kwargs):
            if not _is_allowed(str(self_path), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: Path.mkdir at {self_path!s} blocked"
                )
            return orig_mkdir(self_path, *args, **kwargs)

        self._mp.setattr(pathlib.Path, "mkdir", guarded_mkdir)

        # --- pathlib.Path.unlink ---
        orig_unlink = self._orig_path_unlink

        def guarded_path_unlink(self_path, *args, **kwargs):
            if not _is_allowed(str(self_path), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: Path.unlink at {self_path!s} blocked"
                )
            return orig_unlink(self_path, *args, **kwargs)

        self._mp.setattr(pathlib.Path, "unlink", guarded_path_unlink)

        # --- pathlib.Path.rmdir ---
        orig_rmdir = self._orig_path_rmdir

        def guarded_path_rmdir(self_path, *args, **kwargs):
            if not _is_allowed(str(self_path), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: Path.rmdir at {self_path!s} blocked"
                )
            return orig_rmdir(self_path, *args, **kwargs)

        self._mp.setattr(pathlib.Path, "rmdir", guarded_path_rmdir)

        # --- os.remove / os.unlink ---
        orig_os_remove = self._orig_os_remove

        def guarded_os_remove(path, *args, **kwargs):
            if not _is_allowed(str(path), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: os.remove({path!r}) blocked"
                )
            return orig_os_remove(path, *args, **kwargs)

        self._mp.setattr(os, "remove", guarded_os_remove)
        self._mp.setattr(os, "unlink", guarded_os_remove)

        # --- os.rename ---
        orig_os_rename = self._orig_os_rename

        def guarded_os_rename(src, dst, *args, **kwargs):
            if not _is_allowed(str(src), sandbox._tmp_path) or not _is_allowed(
                str(dst), sandbox._tmp_path
            ):
                raise PermissionError(
                    f"Sandbox: os.rename({src!r}, {dst!r}) blocked"
                )
            return orig_os_rename(src, dst, *args, **kwargs)

        self._mp.setattr(os, "rename", guarded_os_rename)

        # --- os.makedirs ---
        orig_os_makedirs = self._orig_os_makedirs

        def guarded_os_makedirs(name, *args, **kwargs):
            if not _is_allowed(str(name), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: os.makedirs({name!r}) blocked"
                )
            return orig_os_makedirs(name, *args, **kwargs)

        self._mp.setattr(os, "makedirs", guarded_os_makedirs)

        # --- shutil.copy / copy2 ---
        orig_shutil_copy = self._orig_shutil_copy

        def guarded_shutil_copy(src, dst, *args, **kwargs):
            if not _is_allowed(str(dst), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: shutil.copy to {dst!r} blocked"
                )
            return orig_shutil_copy(src, dst, *args, **kwargs)

        self._mp.setattr(shutil, "copy", guarded_shutil_copy)

        orig_shutil_copy2 = self._orig_shutil_copy2

        def guarded_shutil_copy2(src, dst, *args, **kwargs):
            if not _is_allowed(str(dst), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: shutil.copy2 to {dst!r} blocked"
                )
            return orig_shutil_copy2(src, dst, *args, **kwargs)

        self._mp.setattr(shutil, "copy2", guarded_shutil_copy2)

        # --- shutil.move ---
        orig_shutil_move = self._orig_shutil_move

        def guarded_shutil_move(src, dst, *args, **kwargs):
            if not _is_allowed(str(src), sandbox._tmp_path) or not _is_allowed(
                str(dst), sandbox._tmp_path
            ):
                raise PermissionError(
                    f"Sandbox: shutil.move({src!r}, {dst!r}) blocked"
                )
            return orig_shutil_move(src, dst, *args, **kwargs)

        self._mp.setattr(shutil, "move", guarded_shutil_move)

        # --- shutil.rmtree ---
        orig_shutil_rmtree = self._orig_shutil_rmtree

        def guarded_shutil_rmtree(path, *args, **kwargs):
            if not _is_allowed(str(path), sandbox._tmp_path):
                raise PermissionError(
                    f"Sandbox: shutil.rmtree({path!r}) blocked"
                )
            return orig_shutil_rmtree(path, *args, **kwargs)

        self._mp.setattr(shutil, "rmtree", guarded_shutil_rmtree)

        self._active = True

    @property
    def is_active(self) -> bool:
        """Return True if the sandbox guards are installed."""
        return self._active


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _filesystem_sandbox(tmp_path, monkeypatch):
    """Activate filesystem sandboxing for every test (autouse).

    Fail-closed: if the sandbox cannot be activated, the test fails
    immediately rather than running without protection.
    """
    sandbox = _FilesystemSandbox(tmp_path, monkeypatch)
    try:
        sandbox.activate()
    except Exception as exc:
        pytest.fail(
            f"FAIL-CLOSED: Filesystem sandbox failed to activate: {exc}. "
            "Tests must not run without sandbox protection."
        )

    # Verify the sandbox is actually working (self-test)
    sentinel = tmp_path / ".sandbox_check"
    try:
        sentinel.write_text("ok")
        assert sentinel.read_text() == "ok"
        sentinel.unlink()
    except Exception as exc:
        pytest.fail(
            f"FAIL-CLOSED: Sandbox self-test failed: {exc}. "
            "Writes to tmp_path must work for tests to run."
        )

    yield sandbox

    # No teardown needed — monkeypatch restores everything automatically.
