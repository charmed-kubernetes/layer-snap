import sys
import charms.unit_test

charms.unit_test.patch_reactive()

import snap

sys.modules["charms.layer.snap"] = snap
