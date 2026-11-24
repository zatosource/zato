# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# pytest
import pytest

# Zato
from zato.common.db_env import common as db_env_common
from zato.common.db_env.common import get_env_values, Type_PostgreSQL
from zato.common.db_env.database import database_config
from zato.common.db_env.fence import get_generation_file_path
from zato.common.pubsub.sql.config import get_batch_size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strset

    # Dummy assignments to satisfy type checkers
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

_database_prefixes = (database_config.env_prefix,) + database_config.alias_env_prefixes

_renamed_names = ('Zato_PubSub_Batch_Size', 'Zato_PubSub_DB_Batch_Size',
    'Zato_Database_Generation_File', 'Zato_PubSub_Generation_File')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_environment(monkeypatch:'pytest.MonkeyPatch') -> 'None':
    """ Removes every variable of the Zato database and of its aliases, and the record of reported aliases,
    for the duration of one test.
    """
    for name in list(os.environ):
        for prefix in _database_prefixes:
            if name.startswith(prefix):
                monkeypatch.delenv(name)
                break

    for name in _renamed_names:
        monkeypatch.delenv(name, raising=False)

    reported_alias_names:'strset' = set()
    monkeypatch.setattr(db_env_common, '_reported_alias_names', reported_alias_names)

# ################################################################################################################################
# ################################################################################################################################

def test_database_variables_are_read_under_an_alias(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_PubSub_DB_Type', Type_PostgreSQL)
    monkeypatch.setenv('Zato_PubSub_DB_Host', 'postgresql.example.com')
    monkeypatch.setenv('Zato_PubSub_DB_Port', '5432')
    monkeypatch.setenv('Zato_PubSub_DB_Name', 'zato')

    values = get_env_values(database_config)

    assert values['type'] == Type_PostgreSQL
    assert values['host'] == 'postgresql.example.com'
    assert values['port'] == '5432'
    assert values['name'] == 'zato'

# ################################################################################################################################

def test_database_variable_takes_precedence_over_its_aliases(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_Database_Host', 'postgresql.example.com')
    monkeypatch.setenv('Zato_PubSub_DB_Host', 'postgresql-pubsub.example.com')

    values = get_env_values(database_config)

    assert values['host'] == 'postgresql.example.com'

# ################################################################################################################################

def test_aliases_are_read_in_their_order(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_Common_DB_Host', 'postgresql-common.example.com')
    monkeypatch.setenv('Zato_Audit_Log_DB_Host', 'postgresql-audit-log.example.com')

    values = get_env_values(database_config)

    assert values['host'] == 'postgresql-audit-log.example.com'

# ################################################################################################################################

def test_sqlite_path_is_read_under_an_alias(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_Common_DB_Path', '/opt/zato/env/common.db')

    values = get_env_values(database_config)

    assert values['name'] == '/opt/zato/env/common.db'

# ################################################################################################################################

def test_alias_with_a_different_value_is_reported(
    monkeypatch:'pytest.MonkeyPatch',
    caplog:'pytest.LogCaptureFixture',
    ) -> 'None':

    monkeypatch.setenv('Zato_PubSub_DB_Host', 'postgresql-pubsub.example.com')
    monkeypatch.setenv('Zato_Audit_Log_DB_Host', 'postgresql-audit-log.example.com')

    with caplog.at_level(logging.INFO, logger=db_env_common.logger.name):
        values = get_env_values(database_config)

    assert values['host'] == 'postgresql-pubsub.example.com'
    assert 'Environment variable Zato_Database_Host not set, using Zato_PubSub_DB_Host' in caplog.text
    assert 'Environment variable Zato_Audit_Log_DB_Host ignored' in caplog.text

# ################################################################################################################################

def test_alias_with_the_same_value_is_not_reported(
    monkeypatch:'pytest.MonkeyPatch',
    caplog:'pytest.LogCaptureFixture',
    ) -> 'None':

    monkeypatch.setenv('Zato_PubSub_DB_Host', 'postgresql.example.com')
    monkeypatch.setenv('Zato_Audit_Log_DB_Host', 'postgresql.example.com')

    with caplog.at_level(logging.INFO, logger=db_env_common.logger.name):
        _ = get_env_values(database_config)

    assert 'Zato_Audit_Log_DB_Host' not in caplog.text

# ################################################################################################################################

def test_batch_size_is_read_under_an_alias(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_PubSub_DB_Batch_Size', '1234')

    batch_size = get_batch_size()

    assert batch_size == 1234

# ################################################################################################################################

def test_generation_file_is_read_under_an_alias(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_PubSub_Generation_File', '/opt/zato/env/pubsub-generation')

    path = get_generation_file_path()

    assert path == '/opt/zato/env/pubsub-generation'

# ################################################################################################################################
# ################################################################################################################################
