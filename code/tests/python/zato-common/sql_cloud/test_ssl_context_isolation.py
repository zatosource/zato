# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# pytest
import pytest

# Zato
from zato.common.db_env import build_ssl_context_from_values
from zato.common.odb.api import SQLConnectionPool
from zato.common.test.expected_records import expected_records

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The outgoing SQL connection whose SSL context cannot be built
    Connection_Name = 'test.sql.ssl.missing-ca'
    Engine          = 'mysql+pymysql'

    # The name of a CA file that is never created in the temporary directory of a test
    Missing_CA_File_Name = 'missing-ca.pem'

    # The logger of the SQL connection pools
    Pool_Logger_Name = 'SQLConnectionPool'

# ################################################################################################################################
# ################################################################################################################################

def _get_config(ca_file:'str') -> 'stranydict':
    """ Returns the configuration of an outgoing MySQL connection with SSL that verifies against the given CA file.
    """
    out:'stranydict' = {
        'engine': ModuleCtx.Engine,
        'host': '127.0.0.1',
        'port': 3306,
        'db_name': 'test_db',
        'username': 'test_user',
        'password': 'test_password',
        'pool_size': 1,
        'ssl': True,
        'ssl_ca_file': ca_file,
        'ssl_cert_file': '',
        'ssl_key_file': '',
        'ssl_verify': True,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSSLContextIsolation:

    def test_missing_ca_file_is_named(self, tmp_path:'Path') -> 'None':
        """ An SSL context that cannot be built names the CA file that could not be loaded.
        """
        ca_file = str(tmp_path / ModuleCtx.Missing_CA_File_Name)
        values = _get_config(ca_file)

        with pytest.raises(Exception) as exc_info:
            _ = build_ssl_context_from_values(values)

        assert ca_file in str(exc_info.value)

# ################################################################################################################################

    def test_missing_ca_file_leaves_pool_without_engine(self, tmp_path:'Path', caplog:'pytest.LogCaptureFixture') -> 'None':
        """ A connection whose CA file is missing is left without an engine instead of raising,
        so that it does not prevent the other connections from starting.
        """
        ca_file = str(tmp_path / ModuleCtx.Missing_CA_File_Name)
        config = _get_config(ca_file)

        with caplog.at_level(logging.WARNING, logger=ModuleCtx.Pool_Logger_Name):
            with expected_records(ModuleCtx.Pool_Logger_Name):
                pool = SQLConnectionPool(ModuleCtx.Connection_Name, config, config)

        assert pool.engine is None

        messages = [record.getMessage() for record in caplog.records]
        assert any(ModuleCtx.Connection_Name in message and ca_file in message for message in messages), messages

# ################################################################################################################################
# ################################################################################################################################
