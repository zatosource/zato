# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys

# Zato
from conftest import License_Key_Name, License_Key_Value
from zato.common.odb.api import SQLConnectionPool
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The child script that checks one engine-building module in a plain interpreter
_check_script = os.path.join(os.path.dirname(__file__), '_engine_setup_check.py')

# How long the child interpreter may run
_check_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def _run_check(mode:'str') -> 'None':
    """ Runs the engine setup check in a child interpreter so no import made
    by pytest itself can mask what the module under test provides.
    """
    command = [sys.executable, _check_script, mode]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_check_timeout)

    failure_details = f'exit code: {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}'

    assert result.returncode == 0, failure_details
    assert 'OK' in result.stdout, failure_details

# ################################################################################################################################
# ################################################################################################################################

class TestEngineSetup:

    def test_engine_setup_through_odb(self) -> 'None':
        """ Importing the ODB module alone lets oracle:// engines load in thin mode.
        """
        _run_check('odb')

# ################################################################################################################################

    def test_engine_setup_through_db_env(self) -> 'None':
        """ Importing the environment database module alone lets oracle:// engines load in thin mode.
        """
        _run_check('db_env')

# ################################################################################################################################
# ################################################################################################################################

class TestPoolURL:

    def _build_pool(self, extra:'str') -> 'SQLConnectionPool':

        config = {
            'engine':    'oracle',
            'username':  'user1',
            'password':  'password1',
            'host':      'localhost',
            'port':      '1521',
            'db_name':   'service1',
            'name':      'test.oracle.db.url',
            'extra':     extra,
            'pool_size': 1,
        }

        out = SQLConnectionPool('test.oracle.db.url', config, config)
        return out

# ################################################################################################################################

    def test_url_uses_service_name_by_default(self, monkeypatch:'any_') -> 'None':
        """ The database name goes into the URL as a service name unless extra says otherwise.
        """
        monkeypatch.setenv(License_Key_Name, License_Key_Value)

        pool = self._build_pool('')

        assert pool.engine is not None

        engine = cast_('any_', pool.engine)
        assert engine.url.query['service_name'] == 'service1'
        assert not engine.url.database

# ################################################################################################################################

    def test_url_uses_sid_when_extra_says_so(self, monkeypatch:'any_') -> 'None':
        """ A connection whose extra carries use_sid keeps the database name in the URL's path.
        """
        monkeypatch.setenv(License_Key_Name, License_Key_Value)

        pool = self._build_pool('use_sid=True')

        assert pool.engine is not None

        engine = cast_('any_', pool.engine)
        assert engine.url.database == 'service1'
        assert 'service_name' not in engine.url.query

# ################################################################################################################################
# ################################################################################################################################
