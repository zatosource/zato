# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class _ErrorCapture(logging.Handler):
    """ Collects error log records for the duration of a failing import.
    """

    def __init__(self) -> 'None':
        super().__init__(logging.ERROR)
        self.records:'list' = []

# ################################################################################################################################

    def emit(self, record:'logging.LogRecord') -> 'None':
        self.records.append(record)

# ################################################################################################################################
# ################################################################################################################################

def test_failed_enmasse_import_returns_nonzero(in_process_server:'any_') -> 'None':
    """ An enmasse file whose import fails returns a non-zero exit code.
    """
    server, _push_endpoint = in_process_server

    bad_yaml = f"""
pubsub_topic:
  - name: bad.topic.{CryptoManager.generate_hex_string(8)}
    is_active: not-a-boolean
"""

    capture = _ErrorCapture()
    commands_logger = logging.getLogger('zato.server.commands')
    commands_logger.addHandler(capture)

    try:
        exit_code = server.apply_enmasse('failure', bad_yaml)
    finally:
        commands_logger.removeHandler(capture)

    assert exit_code != 0

# ################################################################################################################################
# ################################################################################################################################
