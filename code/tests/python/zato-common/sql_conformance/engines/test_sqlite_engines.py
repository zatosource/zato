# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
import sys
from argparse import Namespace

# SQLAlchemy
from sqlalchemy import event, MetaData, text

# Zato
from zato.cli import ZatoCommand
from zato.common.api import ZATO_ODB_POOL_NAME
from zato.common.db_env.connection import set_sqlite_pragmas
from zato.common.db_env.database import new_unshared_database_engine
from zato.common.db_env.engine import connect_sqlite_file, get_sqlite_file_engine, new_zato_engine
from zato.common.odb.api import SQLConnectionPool
from zato.common.settings_db import SettingsDB
from zato.common.test.sql_conformance.barrier import replicated_environment
from zato.common.test.sql_conformance.disk import get_disk_dir
from zato.common.test.sql_conformance.sources import ModuleCtx as SourcesModuleCtx
from zato.common.test.zato_database import file_database_engine
from zato.common.typing_ import cast_
from zato.common.util.api import get_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from sqlalchemy.engine import Engine

    Engine = Engine
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How SQLite reports the synchronous level `full`
    Synchronous_Full = 2

    # The journal mode of every SQLite database of Zato
    Journal_Mode_WAL = 'wal'

    # The production sources that connect the Django databases of the Dashboard
    Django_Signal_Sources = (
        'code/zato-web-admin/src/zato/admin/settings.py',
    )

    # The connection of a signal handler that gives a Django connection its settings
    Django_Signal_Connection = 'connection_created.connect(set_django_connection)'

    # A Django process with one SQLite database, which reports the settings of its connection
    Django_Script = """
import sys
from django.conf import settings
settings.configure(DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': sys.argv[1]}})
import django
django.setup()
from django.db import connection
from django.db.backends.signals import connection_created
from zato.common.db_env.connection import set_django_connection
connection_created.connect(set_django_connection)
with connection.cursor() as cursor:
    cursor.execute('pragma journal_mode')
    journal_mode = cursor.fetchone()[0]
    cursor.execute('pragma synchronous')
    synchronous = cursor.fetchone()[0]
print(journal_mode, synchronous)
""".strip()

# ################################################################################################################################
# ################################################################################################################################

def _check_engine(engine:'Engine') -> 'None':
    """ Asserts that the connections of an engine receive the settings of durability from their hook,
    never from the compiled defaults of SQLite.
    """
    assert event.contains(engine, 'connect', set_sqlite_pragmas)

    with engine.connect() as connection:
        journal_mode = connection.execute(text('pragma journal_mode')).scalar()
        synchronous = connection.execute(text('pragma synchronous')).scalar()

    assert journal_mode == ModuleCtx.Journal_Mode_WAL
    assert synchronous == ModuleCtx.Synchronous_Full

# ################################################################################################################################

# ################################################################################################################################

def test_zato_database_engine(tmp_path:'Path') -> 'None':
    with file_database_engine(tmp_path) as engine:
        _check_engine(engine)

# ################################################################################################################################

def test_unshared_zato_database_engine(tmp_path:'Path') -> 'None':
    with file_database_engine(tmp_path):
        engine = new_unshared_database_engine()
        try:
            _check_engine(engine)
        finally:
            engine.dispose()

# ################################################################################################################################

def test_sqlite_file_engine(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'analytics.db')
    engine = get_sqlite_file_engine(db_path, MetaData(), needs_pool=True, needs_background_checkpoint=False)
    _check_engine(engine)

# ################################################################################################################################

def test_replicated_zato_database_engine() -> 'None':

    # The directory has a short path, which the socket of the barrier needs
    directory = get_disk_dir('replicated-engine')
    shutil.rmtree(directory)
    os.makedirs(directory)

    with replicated_environment(directory) as barrier:
        with file_database_engine(directory) as engine:
            _check_engine(engine)

    assert barrier.request_count > 0

# ################################################################################################################################

def test_configuration_database_pool(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'config.db')

    config = {
        'name': ZATO_ODB_POOL_NAME,
        'engine': 'sqlite',
        'sqlite_path': db_path,
        'db_name': db_path,
        'is_active': True,
        'fs_sql_config': {},
    }

    pool = SQLConnectionPool(ZATO_ODB_POOL_NAME, config, config)
    engine = cast_('Engine', pool.engine)

    try:
        _check_engine(engine)
    finally:
        engine.dispose()

# ################################################################################################################################

def test_configuration_database_utility_engine(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'config.db')
    engine = get_engine({'engine': 'sqlite', 'sqlite_path': db_path})

    try:
        _check_engine(engine)
    finally:
        engine.dispose()

# ################################################################################################################################

def test_command_line_engine(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'config.db')
    args = Namespace(verbose=False, store_log=False, store_config=False, odb_type='sqlite', odb_path=db_path)

    command = ZatoCommand(args)
    engine = command._get_engine(args)

    try:
        _check_engine(engine)
    finally:
        engine.dispose()

# ################################################################################################################################

def test_settings_database_engine(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'settings.db')

    settings_db = SettingsDB(db_path, None)
    engine = settings_db.get_engine()

    try:
        _check_engine(engine)
    finally:
        engine.dispose()

# ################################################################################################################################

def test_dashboard_engine(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'web-admin.sqlite3')
    engine = new_zato_engine(f'sqlite:///{db_path}')

    try:
        _check_engine(engine)
    finally:
        engine.dispose()

# ################################################################################################################################

def test_sqlite3_connection(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'warehouse.db')
    connection = connect_sqlite_file(db_path)

    try:
        journal_mode = connection.execute('pragma journal_mode').fetchone()[0]
        synchronous = connection.execute('pragma synchronous').fetchone()[0]
    finally:
        connection.close()

    assert journal_mode == ModuleCtx.Journal_Mode_WAL
    assert synchronous == ModuleCtx.Synchronous_Full

# ################################################################################################################################

def test_django_connection(tmp_path:'Path') -> 'None':
    db_path = os.path.join(tmp_path, 'django.db')

    result = subprocess.run([sys.executable, '-c', ModuleCtx.Django_Script, db_path],
        capture_output=True, text=True, check=True)

    journal_mode, synchronous = result.stdout.split()

    assert journal_mode == ModuleCtx.Journal_Mode_WAL
    assert int(synchronous) == ModuleCtx.Synchronous_Full

# ################################################################################################################################

def test_django_signal_connected() -> 'None':
    """ The Dashboard connects the handler that gives each Django connection its settings.
    """
    for relative_path in ModuleCtx.Django_Signal_Sources:
        path = os.path.join(SourcesModuleCtx.Installation_Dir, relative_path)

        with open(path) as source_file:
            source = source_file.read()

        assert ModuleCtx.Django_Signal_Connection in source, path

# ################################################################################################################################
# ################################################################################################################################
