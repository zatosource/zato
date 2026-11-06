# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

# Zato
from zato.common.common_db.config import get_common_engine
from zato.common.common_db.schema import shared_object_table
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite
from zato.common.db_env.engine import call_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.pubsub.sql.generation import GenerationGuard
    from zato.common.typing_ import anydict, intnone

    # Dummy assignments to satisfy type checkers
    anydict = anydict
    Engine = Engine
    GenerationGuard = GenerationGuard
    intnone = intnone

sharedobjectlist = list['SharedObject']

# ################################################################################################################################
# ################################################################################################################################

# The statement that inserts a row unless its key exists, by the dialect of the database.
_insert_by_dialect = {
    Type_PostgreSQL: postgresql_insert,
    Type_SQLite:     sqlite_insert,
}

# ################################################################################################################################
# ################################################################################################################################

class SharedObject(NamedTuple):
    """ One shared object - its name, its document and the version of the document.
    """
    name: 'str'
    data: 'anydict'
    version: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _get(engine:'Engine', object_type:'str', name:'str') -> 'SharedObject | None':

    table = shared_object_table

    query = select(table.c.name, table.c.data, table.c.version)
    query = query.where(table.c.object_type == object_type)
    query = query.where(table.c.name == name)

    with engine.begin() as connection:
        row = connection.execute(query).first()

    if row is None:
        out = None
    else:
        out = SharedObject(row.name, row.data, row.version)

    return out

# ################################################################################################################################

def _list(engine:'Engine', object_type:'str') -> 'sharedobjectlist':

    table = shared_object_table

    query = select(table.c.name, table.c.data, table.c.version)
    query = query.where(table.c.object_type == object_type)
    query = query.order_by(table.c.name)

    out:'sharedobjectlist' = []

    with engine.begin() as connection:
        for row in connection.execute(query):
            item = SharedObject(row.name, row.data, row.version)
            out.append(item)

    return out

# ################################################################################################################################

def _delete(engine:'Engine', object_type:'str', name:'str') -> 'bool':

    table = shared_object_table

    query = table.delete()
    query = query.where(table.c.object_type == object_type)
    query = query.where(table.c.name == name)

    with engine.begin() as connection:
        result = connection.execute(query)

    out = result.rowcount == 1
    return out

# ################################################################################################################################

def _create(engine:'Engine', object_type:'str', name:'str', data:'anydict') -> 'bool':

    dialect_name = engine.dialect.name
    insert = _insert_by_dialect[dialect_name]

    query = insert(shared_object_table)
    now = datetime.now(timezone.utc)

    query = query.values(object_type=object_type, name=name, data=data, version=1, last_updated=now)
    query = query.on_conflict_do_nothing()

    with engine.begin() as connection:
        result = connection.execute(query)

    out = result.rowcount == 1
    return out

# ################################################################################################################################

def _update(engine:'Engine', object_type:'str', name:'str', data:'anydict', version:'int') -> 'bool':

    table = shared_object_table
    now = datetime.now(timezone.utc)

    query = table.update()
    query = query.where(table.c.object_type == object_type)
    query = query.where(table.c.name == name)
    query = query.where(table.c.version == version)
    query = query.values(data=data, version=table.c.version + 1, last_updated=now)

    with engine.begin() as connection:
        result = connection.execute(query)

    out = result.rowcount == 1
    return out

# ################################################################################################################################
# ################################################################################################################################

class SharedObjectStore:
    """ JSON documents in the common database, each under a type and a name. Every write is a compare-and-set
    against the version that the writer read, so of two concurrent writers of one object, only one succeeds.
    """

    def __init__(self) -> 'None':

        # The engine of the common database, resolved on first access.
        self._engine:'Engine | None' = None

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine of the common database that the Zato_Common_DB_* variables select, resolved on first access.
        """
        out = self._engine

        if out is None:
            out = get_common_engine()
            self._engine = out

        return out

# ################################################################################################################################

    def install_generation_guard(self, generation_guard:'GenerationGuard', pubsub_engine:'Engine') -> 'None':
        """ Confirms the generation of the active server in every transaction of the common database, unless the common
        database shares the engine of pub/sub, which confirms it already.
        """
        engine = self.engine

        if engine is not pubsub_engine:
            generation_guard.install(engine)

# ################################################################################################################################

    def get(self, object_type:'str', name:'str') -> 'SharedObject | None':
        """ Returns an object with its document and version, or None if it does not exist.
        """
        engine = self.engine

        out = call_database(engine, _get, engine, object_type, name)
        return out

# ################################################################################################################################

    def list(self, object_type:'str') -> 'sharedobjectlist':
        """ Returns all the objects of a type, by their names.
        """
        engine = self.engine

        out = call_database(engine, _list, engine, object_type)
        return out

# ################################################################################################################################

    def delete(self, object_type:'str', name:'str') -> 'bool':
        """ Deletes an object and returns whether it existed.
        """
        engine = self.engine

        out = call_database(engine, _delete, engine, object_type, name)
        return out

# ################################################################################################################################

    def compare_and_set(self, object_type:'str', name:'str', data:'anydict', version:'intnone') -> 'bool':
        """ Creates an object if version is None and the object does not exist, or replaces the document of an object
        whose version is still the given one, raising the version by one. Returns whether the write took place.
        """
        engine = self.engine

        if version is None:
            out = call_database(engine, _create, engine, object_type, name, data)
        else:
            out = call_database(engine, _update, engine, object_type, name, data, version)

        return out

# ################################################################################################################################
# ################################################################################################################################
