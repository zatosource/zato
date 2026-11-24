# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from subprocess import run

# pytest
import pytest

# Zato
from zato.common.db_env.common import get_env_values
from zato.common.db_env.database import database_config
from zato.common.db_env.fence import get_generation_file_path
from zato.common.pubsub.sql.config import get_batch_size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import CompletedProcess

    # Dummy assignments to satisfy type checkers
    CompletedProcess = CompletedProcess

# ################################################################################################################################
# ################################################################################################################################

_database_prefixes = (database_config.env_prefix,) + database_config.alias_env_prefixes

_renamed_names = ('Zato_PubSub_Batch_Size', 'Zato_PubSub_DB_Batch_Size',
    'Zato_Database_Generation_File', 'Zato_PubSub_Generation_File')

# The read of the variables of the Zato database in a process of its own, which logs to its standard error
# and prints the host that it read.
_read_in_new_process = """
import logging
import sys

from zato.common.db_env.common import get_env_values
from zato.common.db_env.database import database_config

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(message)s', force=True)

values = get_env_values(database_config)
print(values['host'])
"""

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_environment(monkeypatch:'pytest.MonkeyPatch') -> 'None':
    """ Removes every variable of the Zato database and of its aliases for the duration of one test.
    """
    for name in list(os.environ):
        for prefix in _database_prefixes:
            if name.startswith(prefix):
                monkeypatch.delenv(name)
                break

    for name in _renamed_names:
        monkeypatch.delenv(name, raising=False)

# ################################################################################################################################

def _read_once() -> 'CompletedProcess[str]':
    """ Reads the variables of the Zato database in a new process, which has reported no alias yet,
    with the environment of the test.
    """
    command = [sys.executable, '-c', _read_in_new_process]

    out = run(command, capture_output=True, text=True, check=True)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_database_variables_are_read_under_an_alias(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_PubSub_DB_Host', 'postgresql.example.com')
    monkeypatch.setenv('Zato_PubSub_DB_Port', '5432')
    monkeypatch.setenv('Zato_PubSub_DB_Name', 'zato')

    values = get_env_values(database_config)

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

def test_alias_with_a_different_value_is_reported(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_PubSub_DB_Host', 'postgresql-pubsub.example.com')
    monkeypatch.setenv('Zato_Audit_Log_DB_Host', 'postgresql-audit-log.example.com')

    result = _read_once()

    assert result.stdout.strip() == 'postgresql-pubsub.example.com'
    assert 'Environment variable Zato_Database_Host not set, using Zato_PubSub_DB_Host' in result.stderr
    assert 'Environment variable Zato_Audit_Log_DB_Host ignored' in result.stderr

# ################################################################################################################################

def test_alias_with_the_same_value_is_not_reported(monkeypatch:'pytest.MonkeyPatch') -> 'None':

    monkeypatch.setenv('Zato_PubSub_DB_Host', 'postgresql.example.com')
    monkeypatch.setenv('Zato_Audit_Log_DB_Host', 'postgresql.example.com')

    result = _read_once()

    assert result.stdout.strip() == 'postgresql.example.com'
    assert 'Environment variable Zato_Database_Host not set, using Zato_PubSub_DB_Host' in result.stderr
    assert 'Zato_Audit_Log_DB_Host' not in result.stderr

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
