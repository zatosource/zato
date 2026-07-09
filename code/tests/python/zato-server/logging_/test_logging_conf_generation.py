# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato - conftest
import conftest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestLoggingConfGeneration:
    """ The environment was created with Zato_Server_Log_Max_Size and Zato_Server_Log_Backup_Count set,
    so the generated logging.conf must carry their values in maxBytes and backupCount.
    """

    def test_generated_conf_carries_max_size(self, zato_server:'anydict') -> 'None':

        logging_conf_path = os.path.join(zato_server['server_dir'], 'config', 'repo', 'logging.conf')

        with open(logging_conf_path, 'r') as logging_conf_file:
            contents = logging_conf_file.read()

        assert f'maxBytes: {conftest.Log_Max_Size}' in contents

# ################################################################################################################################

    def test_generated_conf_carries_backup_count(self, zato_server:'anydict') -> 'None':

        logging_conf_path = os.path.join(zato_server['server_dir'], 'config', 'repo', 'logging.conf')

        with open(logging_conf_path, 'r') as logging_conf_file:
            contents = logging_conf_file.read()

        assert f'backupCount: {conftest.Log_Backup_Count}' in contents

        # The built-in default must not be present anywhere - the env variable replaced it
        assert 'maxBytes: 1000000000' not in contents

# ################################################################################################################################
# ################################################################################################################################
