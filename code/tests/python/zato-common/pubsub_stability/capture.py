# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from pytest import FixtureRequest, LogCaptureFixture
    from zato.common.typing_ import any_, intlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    intlist = intlist

    handlerlist = list[logging.Handler]
    nonegen     = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

# The lowest level of the records that pytest keeps for the report of a test. A long run logs each publication
# and delivery, and keeping all of these records for hours grows the heap that each full garbage collection traverses,
# which stalls the event loop for longer as the run goes on.
_captured_log_level = logging.WARNING

# ################################################################################################################################
# ################################################################################################################################

class _DetachedRecordFilter(logging.Filter):
    """ Renders the message and the traceback of each captured record into text, so that the record no longer refers
    to the arguments of its message, to its exception or to the frames of its traceback. A record of a lost database
    connection otherwise keeps that connection, its socket and its prepared statements alive for as long as pytest
    keeps the record.
    """
    def __init__(self) -> 'None':
        super().__init__()
        self._formatter = logging.Formatter()

    def filter(self, record:'logging.LogRecord') -> 'bool':

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self._formatter.formatException(record.exc_info)
            record.exc_info = None

        record.msg = record.getMessage()
        record.args = None

        return True

# ################################################################################################################################
# ################################################################################################################################

def limit_captured_logs(request:'FixtureRequest', caplog:'LogCaptureFixture') -> 'nonegen':
    """ Keeps the warnings and errors only in the logs that pytest captures for the report of a test, each as text alone,
    while the live log continues to show every record.
    """
    logging_plugin = cast_('any_', request.config.pluginmanager.get_plugin('logging-plugin'))

    handlers:'handlerlist' = [caplog.handler, logging_plugin.report_handler]
    original_levels:'intlist' = []
    record_filter = _DetachedRecordFilter()

    for handler in handlers:
        original_levels.append(handler.level)
        handler.setLevel(_captured_log_level)
        handler.addFilter(record_filter)

    try:
        yield
    finally:
        for handler, level in zip(handlers, original_levels):
            handler.setLevel(level)
            handler.removeFilter(record_filter)

# ################################################################################################################################
# ################################################################################################################################
