# Snap layer

The Snap layer for Juju enables layered charms to more easily deal with
snap packages in a simple and efficient manner. It provides consistent
configuration for users, allowing them the choice of pulling snaps
from the main snap store, or uploading them as Juju resources for deploys
in environments with limited network access.


## Configuration

To have the Snap layer install snaps automatically, declare the snaps in
`layer.yaml`:

```yaml
includes:
  - layer:basic
  - layer:snap
options:
  snap:
    telegraf:
      channel: stable
      devmode: false
      jailmode: false
      dangerous: false
      classic: false
      revision: null
      connect:
        - ["telegraf:system-observe", ":system-observe"]
        - ["telegraf:log-observe", ":log-observe"]
```

In addition, for Juju 2.0 you should declare Juju resource slots for
the snaps. This allows operators to have snaps distributed from their
Juju controller node rather than the Snap Store, and is necessary for
when your charm is deployed in network restricted environments.

```yaml
resources:
  telegraf:
    type: file
    filename: telegraf.snap
    description: Telegraf snap
```

:no_entry: Charms that need to support Juju 1.25 or earlier cannot
declare the resource entry in metadata.yaml and can only support snap
installs and updates from the Snap Store.

With the Juju resource defined, the operator may deploy your charm
using locally provided snaps instead of the Snap Store:

```sh
juju deploy --resource telegraf=telegraf_0_19.snap cs:telegraf
```

If your charm needs to control installation, update and removal of
snaps itself then do not declare the snaps in `layer.yaml`. Instead,
use the API provided by the `charms.layer.snap` Python package.


### Details

In the example layer.yaml above, each snap to install is declared as an
entry in the snap layer options mapping. Each of these entries is
itself a mapping, with a number of optional keys. Most of the keys
correspond to `snap install` command line options.

* channel (str) - The channel to use instead of `stable`. Defaults to `stable`.
                  Ignored if the snap is being installed from a Juju resource.
* classic (bool) - Acknowledge that the snap uses classic confinement and
                   will have full system access.
* devmode (bool) - Install with non-enforcing security.
* jailmode (bool) - Override a snap's request for non-enforcing security
* dangerous (bool) - Install the snap even if it is unverified and could
                     be dangerous. Implicitly set if the snap is being
                     installed from a Juju resource.
* revision (str) - Install an explicit revision of the snap. Ignored if the
                   snap is being installed from a Juju resource.

One non-install related key is `remove`, which if present and set to True
will force the next charm hook to remove the snap if the reactive flag for that
snap is active.

Another key is `connect`, which declares the `snap connect` commands
to run to connect the snap's plugs to suitable slots. Each entry is a
two element list, with the first item being the plug name and the second
the target snap and slot name. The connections are made after all snaps
have been installed, so you do not need to worry about installation
order.


### Snap Refresh

By default, the `snapd` daemon will query the Snap Store four (4)
times per day to process updates for installed snaps. This layer provides
a charm configuration option for authors and operators to control this
refresh frequency.

>NOTE: this is a global configuration option and will affect the refresh
time for all snaps installed on a system.

>NOTE: requires snapd 2.31 or higher.

Examples:

```sh
## refresh snaps every tuesday
juju config telegraf snapd_refresh="tue"

## refresh snaps at 11pm on the last (5th) friday of the month
juju config telegraf snapd_refresh="fri5,23:00"

## use the system default refresh timer
juju config telegraf snapd_refresh=""
```

Currently, the `snapd` refresh timer may be delayed up to one (1) month. This
can be configured using the `max` option:

```sh
## delay snap refreshes as long as possible
juju config telegraf snapd_refresh="max"
```

For more information on the possible values for `snapd_refresh`, see the
*refresh.timer* section in the [system options][] documentation.

[system options]: https://forum.snapcraft.io/t/system-options/87


## Usage

If you have defined your snaps in layer.yaml for automatic installation
and updates, there is nothing further to do.

### API

If your charm need to control installation, update and removal of snaps
itself, the following methods are available via the `charms.layer.snap`
package::

* `install(snapname, **args)`. Install the snap from the corresponding Juju
  resource (using --dangerous implicitly). If the resource is not
  available, download and install from the Snap Store using the provided
  keyword arguments.

* `refresh(snapname, **args)`. Update the snap. If the snap was installed
  from a local resource then the resource is checked for updates and the
  snap updated if the snap or arguments have changed. If the snap was
  installed from the Snap Store, `snap refresh` is run to update the snap.

* `create_cohort_snapshot(snapname)`. Creates a new cohort snapshot and
  returns the associated key. A cohort snapshot allows snaps on different
  machines to coordinate their refreshes by sharing the cohort snapshot key.

* `join_cohort_snapshot(snapname, cohort_key)`. Joins a cohort snapshot.
  When in a cohort snapshot, new snap revisions will not be automatically
  applied; instead, the leader should periodically check for an available
  refresh, then create a new cohort snapshot and distribute the key in
  a controlled fashion to roll out updates.

* `is_refresh_available(snapname)`. Check whether the given snap can be
  updated. Also available as an automatically managed flag, of the form
  `snap.refresh-available.{snapname}`.

* `remove(snapname)`. The snap is removed.

Keyword arguments correspond to the layer.yaml options and snap command line
options. See the snap command line documentation for authorative details on
what these options do:

* `channel` (str)
* `classic` (boolean)
* `devmode` (boolean)
* `jailmode` (boolean)
* `dangerous` (boolean)
* `revision` (str)


## Charmstore Publication/Release

The [Charm Store](https://jujucharms.com) does not yet understand that
most resources should be optional and requires them to be uploaded
before publication. The Snap layer supports the common workaround for
this, requiring you to upload an empty (0 bytes in size) as a stand in
for the resource.

```sh
charm push $JUJU_REPOSITORY/builds/mycharm cs:~me/mycharm
charm attach cs:~me/mycharm-0 mysnap=empty.snap
charm release cs:~me/mycharm-1 --channel=beta --resource mysnap-0
juju deploy cs:~me/mycharm --channel=beta
```

:watch: This should no longer be required once
[:bug: Issue 103](https://github.com/juju/charmstore-client/issues/103)
is dealt with.


## Support

This layer is maintained on Launchpad by
Stuart Bishop (stuart.bishop@canonical.com).

Code is available using git at git+ssh://git.launchpad.net/layer-snap.

Bug reports can be made at https://bugs.launchpad.net/layer-snap.

Queries and comments can be made on the Juju mailing list, Juju IRC
channels, or at https://answers.launchpad.net/layer-snap.
