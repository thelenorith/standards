"""
Tests for conftest.py filesystem sandbox.

Verifies that the sandbox:
1. Blocks writes outside tmp_path (builtins.open, pathlib, os, shutil)
2. Blocks reads outside tmp_path and project root
3. Allows operations inside tmp_path
4. Fails CLOSED — tests abort if sandbox cannot activate
5. Catches bypass attempts (symlinks, relative paths, ..)

Copy this file to your project's tests/test_conftest.py.
Run with: pytest tests/test_conftest.py -v
"""

import builtins
import os
import pathlib
import shutil
import tempfile

import pytest


# ===================================================================
# 1. WRITE BLOCKING — operations outside tmp_path must raise
# ===================================================================


class TestWriteBlocking:
    """Verify writes outside tmp_path are blocked."""

    def test_builtins_open_write_blocked(self, tmp_path):
        """builtins.open() in write mode outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_write_blocked.txt"
        with pytest.raises(PermissionError, match="Sandbox.*write.*blocked"):
            open(outside, "w")

    def test_builtins_open_append_blocked(self, tmp_path):
        """builtins.open() in append mode outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_append_blocked.txt"
        with pytest.raises(PermissionError, match="Sandbox.*write.*blocked"):
            open(outside, "a")

    def test_builtins_open_exclusive_create_blocked(self, tmp_path):
        """builtins.open() in exclusive-create mode outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_exclusive_blocked.txt"
        with pytest.raises(PermissionError, match="Sandbox.*write.*blocked"):
            open(outside, "x")

    def test_builtins_open_readwrite_blocked(self, tmp_path):
        """builtins.open() in r+ mode outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_rw_blocked.txt"
        with pytest.raises(PermissionError, match="Sandbox.*write.*blocked"):
            open(outside, "r+")

    def test_path_write_text_blocked(self, tmp_path):
        """pathlib.Path.write_text() outside tmp_path raises PermissionError."""
        outside = pathlib.Path("/tmp/conftest_test_write_text.txt")
        with pytest.raises(PermissionError, match="Sandbox.*write_text.*blocked"):
            outside.write_text("should not work")

    def test_path_write_bytes_blocked(self, tmp_path):
        """pathlib.Path.write_bytes() outside tmp_path raises PermissionError."""
        outside = pathlib.Path("/tmp/conftest_test_write_bytes.bin")
        with pytest.raises(PermissionError, match="Sandbox.*write_bytes.*blocked"):
            outside.write_bytes(b"should not work")

    def test_path_mkdir_blocked(self, tmp_path):
        """pathlib.Path.mkdir() outside tmp_path raises PermissionError."""
        outside = pathlib.Path("/tmp/conftest_test_mkdir_blocked")
        with pytest.raises(PermissionError, match="Sandbox.*mkdir.*blocked"):
            outside.mkdir()

    def test_path_unlink_blocked(self, tmp_path):
        """pathlib.Path.unlink() outside tmp_path raises PermissionError."""
        outside = pathlib.Path("/tmp/conftest_test_unlink_blocked.txt")
        with pytest.raises(PermissionError, match="Sandbox.*unlink.*blocked"):
            outside.unlink()

    def test_path_rmdir_blocked(self, tmp_path):
        """pathlib.Path.rmdir() outside tmp_path raises PermissionError."""
        outside = pathlib.Path("/tmp/conftest_test_rmdir_blocked")
        with pytest.raises(PermissionError, match="Sandbox.*rmdir.*blocked"):
            outside.rmdir()

    def test_os_remove_blocked(self, tmp_path):
        """os.remove() outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_os_remove.txt"
        with pytest.raises(PermissionError, match="Sandbox.*os.remove.*blocked"):
            os.remove(outside)

    def test_os_unlink_blocked(self, tmp_path):
        """os.unlink() outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_os_unlink.txt"
        with pytest.raises(PermissionError, match="Sandbox.*os.remove.*blocked"):
            os.unlink(outside)

    def test_os_rename_blocked(self, tmp_path):
        """os.rename() outside tmp_path raises PermissionError."""
        src = "/tmp/conftest_test_rename_src.txt"
        dst = "/tmp/conftest_test_rename_dst.txt"
        with pytest.raises(PermissionError, match="Sandbox.*os.rename.*blocked"):
            os.rename(src, dst)

    def test_os_rename_dest_blocked(self, tmp_path):
        """os.rename() with dest outside tmp_path raises PermissionError."""
        src = tmp_path / "inside.txt"
        src.write_text("data")
        dst = "/tmp/conftest_test_rename_escape.txt"
        with pytest.raises(PermissionError, match="Sandbox.*os.rename.*blocked"):
            os.rename(str(src), dst)

    def test_os_makedirs_blocked(self, tmp_path):
        """os.makedirs() outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_makedirs_blocked/deep/path"
        with pytest.raises(PermissionError, match="Sandbox.*os.makedirs.*blocked"):
            os.makedirs(outside)

    def test_shutil_copy_blocked(self, tmp_path):
        """shutil.copy() to outside tmp_path raises PermissionError."""
        src = tmp_path / "source.txt"
        src.write_text("data")
        dst = "/tmp/conftest_test_shutil_copy.txt"
        with pytest.raises(PermissionError, match="Sandbox.*shutil.copy.*blocked"):
            shutil.copy(str(src), dst)

    def test_shutil_copy2_blocked(self, tmp_path):
        """shutil.copy2() to outside tmp_path raises PermissionError."""
        src = tmp_path / "source.txt"
        src.write_text("data")
        dst = "/tmp/conftest_test_shutil_copy2.txt"
        with pytest.raises(PermissionError, match="Sandbox.*shutil.copy2.*blocked"):
            shutil.copy2(str(src), dst)

    def test_shutil_move_blocked(self, tmp_path):
        """shutil.move() to outside tmp_path raises PermissionError."""
        src = tmp_path / "source.txt"
        src.write_text("data")
        dst = "/tmp/conftest_test_shutil_move.txt"
        with pytest.raises(PermissionError, match="Sandbox.*shutil.move.*blocked"):
            shutil.move(str(src), dst)

    def test_shutil_rmtree_blocked(self, tmp_path):
        """shutil.rmtree() outside tmp_path raises PermissionError."""
        outside = "/tmp/conftest_test_shutil_rmtree"
        with pytest.raises(PermissionError, match="Sandbox.*shutil.rmtree.*blocked"):
            shutil.rmtree(outside)


# ===================================================================
# 2. READ BLOCKING — reads outside tmp_path and project root
# ===================================================================


class TestReadBlocking:
    """Verify reads from outside tmp_path and project root are blocked."""

    def test_builtins_open_read_outside_project_blocked(self, tmp_path):
        """builtins.open() read of file outside project root raises PermissionError."""
        # /etc/hostname is outside both tmp_path and project root
        with pytest.raises(PermissionError, match="Sandbox.*read.*blocked"):
            open("/etc/hostname", "r")

    def test_path_read_text_outside_project_blocked(self, tmp_path):
        """pathlib.Path.read_text() outside project root raises PermissionError."""
        outside = pathlib.Path("/etc/hostname")
        with pytest.raises(PermissionError, match="Sandbox.*read_text.*blocked"):
            outside.read_text()

    def test_path_read_bytes_outside_project_blocked(self, tmp_path):
        """pathlib.Path.read_bytes() outside project root raises PermissionError."""
        outside = pathlib.Path("/etc/hostname")
        with pytest.raises(PermissionError, match="Sandbox.*read_bytes.*blocked"):
            outside.read_bytes()


# ===================================================================
# 3. ALLOWED OPERATIONS — inside tmp_path must work
# ===================================================================


class TestAllowedOperations:
    """Verify that operations inside tmp_path succeed normally."""

    def test_write_and_read_file_in_tmp_path(self, tmp_path):
        """Writing and reading a file inside tmp_path works."""
        f = tmp_path / "test.txt"
        f.write_text("hello")
        assert f.read_text() == "hello"

    def test_write_bytes_in_tmp_path(self, tmp_path):
        """Writing and reading bytes inside tmp_path works."""
        f = tmp_path / "test.bin"
        f.write_bytes(b"\x00\x01\x02")
        assert f.read_bytes() == b"\x00\x01\x02"

    def test_builtins_open_write_in_tmp_path(self, tmp_path):
        """builtins.open() write inside tmp_path works."""
        f = tmp_path / "test.txt"
        with open(f, "w") as fh:
            fh.write("hello")
        with open(f, "r") as fh:
            assert fh.read() == "hello"

    def test_mkdir_in_tmp_path(self, tmp_path):
        """pathlib.Path.mkdir() inside tmp_path works."""
        d = tmp_path / "subdir"
        d.mkdir()
        assert d.is_dir()

    def test_unlink_in_tmp_path(self, tmp_path):
        """pathlib.Path.unlink() inside tmp_path works."""
        f = tmp_path / "to_delete.txt"
        f.write_text("bye")
        f.unlink()
        assert not f.exists()

    def test_os_remove_in_tmp_path(self, tmp_path):
        """os.remove() inside tmp_path works."""
        f = tmp_path / "to_delete.txt"
        f.write_text("bye")
        os.remove(str(f))
        assert not f.exists()

    def test_os_rename_in_tmp_path(self, tmp_path):
        """os.rename() inside tmp_path works."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("data")
        os.rename(str(src), str(dst))
        assert dst.exists()
        assert not src.exists()

    def test_os_makedirs_in_tmp_path(self, tmp_path):
        """os.makedirs() inside tmp_path works."""
        deep = tmp_path / "a" / "b" / "c"
        os.makedirs(str(deep))
        assert deep.is_dir()

    def test_shutil_copy_in_tmp_path(self, tmp_path):
        """shutil.copy() inside tmp_path works."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("data")
        shutil.copy(str(src), str(dst))
        assert dst.read_text() == "data"

    def test_shutil_move_in_tmp_path(self, tmp_path):
        """shutil.move() inside tmp_path works."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("data")
        shutil.move(str(src), str(dst))
        assert dst.exists()
        assert not src.exists()

    def test_shutil_rmtree_in_tmp_path(self, tmp_path):
        """shutil.rmtree() inside tmp_path works."""
        d = tmp_path / "tree"
        d.mkdir()
        (d / "file.txt").write_text("data")
        shutil.rmtree(str(d))
        assert not d.exists()


# ===================================================================
# 4. FAIL-CLOSED — sandbox must be active, tests fail if it isn't
# ===================================================================


class TestFailClosed:
    """Verify the sandbox fails closed: tests cannot run without protection."""

    def test_sandbox_is_active(self, _filesystem_sandbox):
        """The sandbox fixture must report itself as active."""
        assert _filesystem_sandbox.is_active, (
            "FAIL-CLOSED VIOLATION: Sandbox is not active. "
            "Tests are running without filesystem protection."
        )

    def test_sandbox_fixture_is_not_none(self, _filesystem_sandbox):
        """The sandbox fixture must exist and be a real object."""
        assert _filesystem_sandbox is not None, (
            "FAIL-CLOSED VIOLATION: Sandbox fixture is None."
        )

    def test_open_is_guarded(self, _filesystem_sandbox):
        """builtins.open must be the guarded version, not the original."""
        # The guarded version raises PermissionError for disallowed paths.
        # If open were the original, this would raise FileNotFoundError instead.
        with pytest.raises(PermissionError):
            open("/nonexistent/path/outside/sandbox.txt", "w")

    def test_write_text_is_guarded(self, _filesystem_sandbox):
        """pathlib.Path.write_text must be the guarded version."""
        with pytest.raises(PermissionError):
            pathlib.Path("/nonexistent/path/outside/sandbox.txt").write_text("x")

    def test_write_bytes_is_guarded(self, _filesystem_sandbox):
        """pathlib.Path.write_bytes must be the guarded version."""
        with pytest.raises(PermissionError):
            pathlib.Path("/nonexistent/path/outside/sandbox.bin").write_bytes(b"x")

    def test_os_remove_is_guarded(self, _filesystem_sandbox):
        """os.remove must be the guarded version."""
        with pytest.raises(PermissionError):
            os.remove("/nonexistent/path/outside/sandbox.txt")

    def test_shutil_rmtree_is_guarded(self, _filesystem_sandbox):
        """shutil.rmtree must be the guarded version."""
        with pytest.raises(PermissionError):
            shutil.rmtree("/nonexistent/path/outside/sandbox")


# ===================================================================
# 5. BYPASS RESISTANCE — symlinks, .., relative paths
# ===================================================================


class TestBypassResistance:
    """Verify the sandbox cannot be bypassed by path tricks."""

    def test_symlink_escape_write_blocked(self, tmp_path):
        """Writing via symlink that points outside tmp_path is blocked.

        Creates a symlink inside tmp_path that points to /tmp (outside sandbox),
        then verifies that writing through the symlink is blocked.
        """
        target_dir = "/tmp"
        link = tmp_path / "escape_link"
        # Create symlink: tmp_path/escape_link -> /tmp
        os.symlink(target_dir, str(link))
        escaped_file = link / "conftest_symlink_escape_test.txt"

        with pytest.raises(PermissionError, match="Sandbox.*blocked"):
            escaped_file.write_text("escaped!")

    def test_dotdot_escape_write_blocked(self, tmp_path):
        """Writing via ../../../tmp is blocked."""
        # Build a path that traverses out of tmp_path
        escaped = tmp_path / ".." / ".." / ".." / "tmp" / "conftest_dotdot_test.txt"
        with pytest.raises(PermissionError, match="Sandbox.*blocked"):
            escaped.write_text("escaped!")

    def test_dotdot_escape_os_rename_blocked(self, tmp_path):
        """os.rename() with ../ destination is blocked."""
        src = tmp_path / "legitimate.txt"
        src.write_text("data")
        dst = str(tmp_path / ".." / ".." / ".." / "tmp" / "conftest_rename_escape.txt")
        with pytest.raises(PermissionError, match="Sandbox.*blocked"):
            os.rename(str(src), dst)

    def test_symlink_escape_shutil_copy_blocked(self, tmp_path):
        """shutil.copy() via symlink pointing outside tmp_path is blocked."""
        src = tmp_path / "source.txt"
        src.write_text("data")
        target_dir = "/tmp"
        link = tmp_path / "escape_copy_link"
        os.symlink(target_dir, str(link))
        dst = str(link / "conftest_shutil_copy_escape.txt")

        with pytest.raises(PermissionError, match="Sandbox.*blocked"):
            shutil.copy(str(src), dst)


# ===================================================================
# 6. ERROR MESSAGE QUALITY — messages must aid debugging
# ===================================================================


class TestErrorMessages:
    """Verify error messages contain useful debugging information."""

    def test_write_error_includes_path(self, tmp_path):
        """PermissionError message includes the blocked path."""
        target = "/tmp/conftest_error_msg_test.txt"
        with pytest.raises(PermissionError) as exc_info:
            open(target, "w")
        assert target in str(exc_info.value)

    def test_write_error_mentions_sandbox(self, tmp_path):
        """PermissionError message identifies the sandbox as the source."""
        with pytest.raises(PermissionError) as exc_info:
            open("/tmp/conftest_sandbox_msg_test.txt", "w")
        assert "Sandbox" in str(exc_info.value)

    def test_write_error_mentions_tmp_path(self, tmp_path):
        """PermissionError message mentions tmp_path for guidance."""
        with pytest.raises(PermissionError) as exc_info:
            open("/tmp/conftest_tmppath_msg_test.txt", "w")
        assert "tmp_path" in str(exc_info.value)
