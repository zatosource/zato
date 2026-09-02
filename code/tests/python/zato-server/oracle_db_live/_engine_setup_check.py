# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys

# oracledb
import oracledb

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_service_url = 'oracle://user1:password1@host1:1521/?service_name=service1'
_sid_url     = 'oracle://user1:password1@host1:1521/testsid'

# ################################################################################################################################
# ################################################################################################################################

def _refuse_thick_mode(*args:'any_', **kwargs:'any_') -> 'None':
    raise Exception('init_oracle_client must not be called')

# ################################################################################################################################
# ################################################################################################################################

# The driver has to stay in thin mode, so any call that would enable thick mode fails the check.
oracledb.init_oracle_client = _refuse_thick_mode

# What is under test is that importing one engine-building module alone
# is enough for oracle:// URLs to load in this interpreter.
mode = sys.argv[1]

if mode == 'odb':
    from zato.common.odb import api as engine_building_module

elif mode == 'db_env':
    from zato.common.db_env import engine as engine_building_module

# .. anything else is not a recognized mode.
else:
    raise Exception(f'Unknown mode: {mode}')

engine_building_module = engine_building_module

# The import made python-oracledb available under the name SQLAlchemy 1.4 knows
assert sys.modules['cx_Oracle'] is oracledb
assert oracledb.is_thin_mode() is True

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from zato.common.typing_ import cast_

# A URL with a service name loads and resolves to the mapped driver ..
engine = create_engine(_service_url)
dialect = cast_('any_', engine.dialect)
assert dialect.dbapi is oracledb

# .. and its DSN carries the service name.
_, connect_kwargs = engine.dialect.create_connect_args(engine.url)
service_dsn = connect_kwargs['dsn']
assert 'SERVICE_NAME=service1' in service_dsn, service_dsn

# A URL whose path is the database name yields a SID DSN instead.
sid_engine = create_engine(_sid_url)
_, sid_connect_kwargs = sid_engine.dialect.create_connect_args(sid_engine.url)
sid_dsn = sid_connect_kwargs['dsn']
assert 'SID=testsid' in sid_dsn, sid_dsn

print('OK', flush=True)

# ################################################################################################################################
# ################################################################################################################################
