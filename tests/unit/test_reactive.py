import unittest.mock as mock

from reactive import snap
from charms import layer
from charms.reactive import set_flag, clear_flag


@mock.patch.object(snap, "snap")
def test_install(mock_snap_lib):
    mock_snap_lib.get_installed_flag.side_effect = lambda s: f"snap.installed.{s}"

    layer.options.return_value = {
        "core": {},
        "install-me": {"classic": True},
        "remove-me": {"remove": True},
    }
    set_flag("snap.installed.remove-me")
    set_flag("snap.installed.core")
    clear_flag("snap.installed.install-me")
    snap.install()
    # guarantees the call order is remove-me first
    mock_snap_lib.assert_has_calls(
        [
            mock.call.get_installed_flag("remove-me"),
            mock.call.remove("remove-me"),
            mock.call.get_installed_flag("core"),
            mock.call.get_installed_flag("install-me"),
            mock.call.install("install-me", classic=True),
            mock.call.connect_all(),
        ]
    )


@mock.patch.object(snap, "snap")
@mock.patch.object(snap, "check_refresh_available")
def test_refresh(mock_check_refresh_available, mock_snap_lib):
    mock_snap_lib.get_installed_snaps.return_value = ["core", "install-me"]

    layer.options.return_value = {
        "core": {},
        "install-me": {"classic": True},
        "remove-me": {"remove": True},
    }
    set_flag("snap.installed.install-me")
    set_flag("snap.installed.core")
    clear_flag("snap.installed.remove-me")
    snap.refresh()
    mock_check_refresh_available.assert_called_once_with()

    # ignores any snap with a "remove=True" attribute
    mock_snap_lib.assert_has_calls(
        [
            mock.call.refresh("core"),
            mock.call.refresh("install-me", classic=True),
            mock.call.connect_all(),
        ]
    )
