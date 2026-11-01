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

def limit_captured_logs(request:'FixtureRequest', caplog:'LogCaptureFixture') -> 'nonegen':
    """ Keeps the warnings and errors only in the logs that pytest captures for the report of a test,
    while the live log continues to show every record.
    """
    logging_plugin = cast_('any_', request.config.pluginmanager.get_plugin('logging-plugin'))

    handlers:'handlerlist' = [caplog.handler, logging_plugin.report_handler]
    original_levels:'intlist' = []

    for handler in handlers:
        original_levels.append(handler.level)
        handler.setLevel(_captured_log_level)

    try:
        yield
    finally:
        for handler, level in zip(handlers, original_levels):
            handler.setLevel(level)

# ################################################################################################################################
# ################################################################################################################################
