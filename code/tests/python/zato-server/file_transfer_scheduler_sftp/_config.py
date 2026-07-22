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

    # The file that the hot-deployed test service appends each received file transfer item to
    evidence_file = ''

    # Names of the hot-deployed test services
    service_store_file = 'file-transfer-scheduler-test.store-file'
    service_always_raise = 'file-transfer-scheduler-test.always-raise'

    # The environment variable through which the server finds the SFTP client key on disk
    key_env_name = 'Zato_Test_FT_SFTP_Key_File'

# ################################################################################################################################
# ################################################################################################################################
