import unittest.mock as mock

from reactive import snap
from charms import layer
from charms.reactive import set_flag


@mock.patch.object(snap, "snap")
def test_install(mock_snap_lib):
    mock_snap_lib.get_installed_flag.side_effect = lambda s: f"snap.installed.{s}"

    layer.options.return_value = {
        "core": {},
        "install-me": {"classic": True},
        "remove-me": {"remove": True},
    }
    set_flag("snap.installed.remove-me")
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
