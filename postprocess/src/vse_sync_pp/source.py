### SPDX-License-Identifier: GPL-2.0-or-later

"""Log message sources."""

import json
import logging
from decimal import Decimal

log = logging.getLogger(__name__)


def preview(line, limit=80):
    """Return a short preview of `line` suitable for a log message"""
    return line[:limit] + '...' if len(line) > limit else line


def logged(file, parser):
    """Generator yielding (id_, data) for lines in `file` parsed by `parser`.

    `id_` is the value of the corresponding parser attribute;
    `data` is the canonical data produced by `parser` for a line.
    Lines rejected by `parser` are logged and skipped, so that one malformed
    line does not abort the whole source.

    `file` is closed just before returning.
    """
    line_number = 0
    while True:
        line = file.readline()
        line_number += 1
        if line == '':
            file.close()
            return
        stripped = line.rstrip()
        # A rejected line must not abort the source: log and skip
        try:
            data = parser.parse_line(stripped)
        except ValueError as e:
            log.warning(
                "Skipping rejected %s line %d: %s (content: %r)",
                parser.id_, line_number, e, preview(stripped)
            )
            continue
        if data is not None:
            yield (parser.id_, data)


def muxed(file, parsers):
    """Generator yielding (id_, data) for multiplexed content in `file`.

    Each line in `file` must be a JSON-encoded object with pairs at 'id' and
    'data'. If there is no parser for the value at 'id' in `parsers`, then the
    line is discarded: otherwise a pair is generated.

    `id_` is the value at 'id';
    `data`  the values within data must be the equivalent to  canonical data
    produced by the parser at `id_` in `parsers` for the value at 'data'.
    They can be in the form of a JSON array or a JSON object.
    If the data is a JSON array then the ordering must match the parser output.
    If the data is a JSON object then the names must match the parser output.
    Lines rejected by the parser are logged and skipped, so that one malformed
    line does not abort the whole source.


    `file` is closed just before returning.
    """
    line_number = 0
    while True:
        line = file.readline()
        line_number += 1
        if line == '':
            file.close()
            return

        # Skip empty lines and whitespace-only lines
        stripped = line.rstrip()
        if not stripped:
            continue

        # Try to parse JSON, skip invalid lines
        try:
            obj = json.loads(stripped, parse_float=Decimal)
        except json.JSONDecodeError as e:
            # Log malformed JSON with context, then skip
            log.warning(
                "Skipping malformed JSON at line %d: %s (content: %r)",
                line_number, e, preview(stripped)
            )
            continue

        # Skip if 'id' or 'data' keys are missing
        if 'id' not in obj or 'data' not in obj:
            continue

        id_ = obj['id']
        try:
            parser = parsers[id_]
        except KeyError:
            pass
        else:
            if isinstance(obj['data'], dict):
                data = tuple(obj['data'][name] for name in parser.elems)
            else:
                data = obj['data']
            # A rejected line must not abort the source: log and skip
            try:
                parsed = parser.make_parsed(data)
            except ValueError as e:
                log.warning(
                    "Skipping rejected %s data at line %d: %s (content: %r)",
                    id_, line_number, e, preview(stripped)
                )
                continue
            yield (id_, parsed)
