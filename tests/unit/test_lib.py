import unittest.mock as mock
import pytest

from charms.layer import snap
from charms import reactive


@pytest.fixture(autouse=True)
def mock_subprocess():
    """Prevent any subprocess from actually occurring from the snap module."""
    with mock.patch.object(snap, "subprocess") as patched:
        yield patched


def test_get_star_flag():
    assert snap.get_installed_flag("test") == "snap.installed.test"
    assert snap.get_refresh_available_flag("test") == "snap.refresh-available.test"
    assert snap.get_local_flag("test") == "snap.local.test"
    assert snap.get_disabled_flag("test") == "snap.disabled.test"


@mock.patch.object(snap, "refresh")
def test_refresh(mock_refresh):
    reactive.set_flag("snap.installed.test")
    snap.install("test")
    mock_refresh.assert_called_once_with("test")
    assert snap.is_installed("core")
    assert snap.is_installed("test")
    assert snap.get_installed_snaps() == ["core", "test"]


@mock.patch.object(snap, "_install_store")
def test_install_store(mock_install_store):
    reactive.clear_flag("snap.installed.test")
    snap.install("test")
    mock_install_store.assert_called_once_with("test")
    assert snap.is_installed("core")
    assert snap.is_installed("test")
    assert snap.get_installed_snaps() == ["core", "test"]


def test_remove(mock_subprocess):
    reactive.set_flag("snap.installed.test")
    snap.remove("test")
    mock_subprocess.check_call.assert_called_once_with(["snap", "remove", "test"])
    assert not snap.is_installed("test")
