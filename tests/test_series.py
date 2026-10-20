"""The experimental series must apply to the pinned tree and stay in sync."""
from __future__ import annotations

import unittest

from harness import TestPatchSeries


class TestExperimentalSeries(TestPatchSeries):
    pass


if __name__ == "__main__":
    unittest.main()
