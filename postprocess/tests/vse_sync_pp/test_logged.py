### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.source.logged"""

from decimal import Decimal
from io import StringIO
from unittest import TestCase

from vse_sync_pp.parsers.gnss import TimeErrorParser
from vse_sync_pp.source import logged


class TestLogged(TestCase):
    """Test cases for vse_sync_pp.source.logged"""

    def test_reject(self):
        """Check that a line rejected by the parser is skipped, and does not
        prevent subsequent lines from being yielded
        """
        file = StringIO("\n".join((
            "847914.839,3,4",
            "2026-10-03T03:34:46Z,5,13107631",
            "847915.839,5,-1",
        )))

        self.assertEqual(
            list(logged(file, TimeErrorParser())),
            [
                ("gnss/time-error", (Decimal("847914.839"), 3, 4)),
                ("gnss/time-error", (Decimal("847915.839"), 5, -1)),
            ],
        )
