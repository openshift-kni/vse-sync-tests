### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.source.muxed"""

import json
from collections import namedtuple
from decimal import Decimal
from io import StringIO
from itertools import zip_longest
from unittest import TestCase

from vse_sync_pp.parsers import PARSERS
from vse_sync_pp.source import muxed

CaseValue = namedtuple("CaseValue", "input,expected")
NO_PARSER = CaseValue(
    {
        "id": "im-not-a-parser",
        "data": ["I", "should", "not", "be"],
    },
    None,
)
DPLL_LIST = CaseValue(
    {
        "id": "dpll/time-error",
        "data": ["1876878.28", "3", "3", "-0.79"],
    },
    ("dpll/time-error", (Decimal("1876878.28"), 3, 3, Decimal("-0.79"))),
)
DPLL_DICT = CaseValue(
    {
        "id": "dpll/time-error",
        "data": {
            "timestamp": "1876878.28",
            "eecstate": "3",
            "state": "3",
            "terror": "-0.79",
        },
    },
    ("dpll/time-error", (Decimal("1876878.28"), 3, 3, Decimal("-0.79"))),
)
GNSS_LIST = CaseValue(
    {
        "id": "gnss/time-error",
        "data": ["681011.839", "5", "2", "-3"],
    },
    ("gnss/time-error", (Decimal("681011.839"), 5, 2)),
)

GNSS_DICT = CaseValue(
    {
        "id": "gnss/time-error",
        "data": {
            "timestamp": "681011.839",
            "state": "5",
            "terror": "2",
            "ferror": "-3",
        },
    },
    ("gnss/time-error", (Decimal("681011.839"), 5, 2)),
)

# Whole-second ISO 8601 timestamps are rejected by the GNSS parser (see
# tests/vse_sync_pp/parsers/test_gnss.py). A rejected line must be skipped
# rather than aborting the source: this is the shape reported in the field.
GNSS_REJECTED = {
    "id": "gnss/time-error",
    "data": ["2026-10-03T03:34:46Z", "5", "13107631"],
}


class TestMuxed(TestCase):
    def _test(self, *cases):
        file = StringIO("\n".join(json.dumps(c.input) for c in cases))

        parsers = {}
        for case in cases:
            key = case.input["id"]
            if key in PARSERS:
                parsers[key] = PARSERS[key]()

        actual_values = muxed(file, parsers)
        expected = [c.expected for c in cases if c.expected is not None]

        for actual, expected in zip_longest(actual_values, expected):
            self.assertEqual(actual, expected)

    def test_filter(self):
        """Check that lines with no parser are ignored"""
        self._test(NO_PARSER, DPLL_LIST, GNSS_LIST)

    def test_tuple(self):
        """Check that lines with json arrays are ingested properly"""
        self._test(DPLL_LIST, GNSS_LIST)

    def test_dict(self):
        """Check that lines with json objects are ingested properly"""
        self._test(DPLL_DICT, GNSS_DICT)

    def test_mixed(self):
        """Check that muxed can process a mixture of lines with json
        arrays and json objects
        """
        self._test(DPLL_DICT, GNSS_LIST)

    def test_reject(self):
        """Check that a line rejected by its parser is skipped, and does not
        prevent subsequent lines from being yielded
        """
        file = StringIO("\n".join(json.dumps(c) for c in (
            DPLL_LIST.input,
            GNSS_REJECTED,
            GNSS_LIST.input,
            DPLL_DICT.input,
        )))
        parsers = {
            case.input["id"]: PARSERS[case.input["id"]]()
            for case in (DPLL_LIST, GNSS_LIST, DPLL_DICT)
        }

        self.assertEqual(
            list(muxed(file, parsers)),
            [DPLL_LIST.expected, GNSS_LIST.expected, DPLL_DICT.expected],
        )
