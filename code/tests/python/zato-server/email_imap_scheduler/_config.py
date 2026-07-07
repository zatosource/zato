# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    """ Connection details of the test server, populated by the session fixture in conftest.
    """
    host = '127.0.0.1'
    server_port = 0
    invoke_password = ''
    server_directory = ''

    # The file that the hot-deployed test service appends each received IMAP message to
    evidence_file = ''

    # Names of the hot-deployed test services
    service_store_message = 'imap-scheduler-test.store-message'
    service_always_raise = 'imap-scheduler-test.always-raise'

# ################################################################################################################################
# ################################################################################################################################
