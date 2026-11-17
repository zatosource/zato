# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Any, Callable

# SQLAlchemy
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.db_env.engine import call_database

# Local
from .schema import metadata

# ################################################################################################################################
# ################################################################################################################################

any_:TypeAlias = Any
anytuple:TypeAlias = tuple[Any, ...]
callable_:TypeAlias = Callable[..., Any]

# ################################################################################################################################
# ################################################################################################################################

def _enable_foreign_keys(connection:'any_', connection_record:'any_') -> 'None':
    """ Enables referential integrity for one SQLite connection.
    """
    _ = connection_record

    # Apply the connection-local setting ..
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')

    # .. and release the temporary cursor.
    cursor.close()

# ################################################################################################################################

def create_database_engine(database_url:'str', **options:'any_') -> 'Engine':
    """ Creates an SQLAlchemy engine and enables referential integrity for SQLite connections.
    """
    # Build the caller-configured engine ..
    out = create_engine(database_url, **options)

    # .. and ensure SQLite enforces the same foreign keys as server databases.
    if out.dialect.name == 'sqlite':
        event.listen(out, 'connect', _enable_foreign_keys)

    return out

# ################################################################################################################################

class SessionFactory:
    """ Opens the sessions of the rule engine, whose loaded values remain readable after a transaction commits,
    and runs each write transaction in turn with the other writes of the server to the same SQLite file.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine
        self._sessionmaker = sessionmaker(bind=engine, expire_on_commit=False)

# ################################################################################################################################

    def __call__(self) -> 'Session':
        out = self._sessionmaker()
        return out

# ################################################################################################################################

    def write(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs func with a session and the given arguments in one write transaction and returns what func returns.
        """
        out = call_database(self.engine, self._run_write, func, args)
        return out

# ################################################################################################################################

    def _run_write(self, func:'callable_', args:'anytuple') -> 'any_':
        session = self._sessionmaker()

        try:
            with session.begin():
                out = func(session, *args)

        # The session is released whether the transaction committed or not
        finally:
            session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################

def create_session_factory(engine:'Engine') -> 'SessionFactory':
    """ Creates the session factory of the rule engine over an engine.
    """
    out = SessionFactory(engine)
    return out

# ################################################################################################################################

def create_schema(engine:'Engine') -> 'None':
    """ Creates the rule-engine tables.
    """
    metadata.create_all(engine)

# ################################################################################################################################

def drop_schema(engine:'Engine') -> 'None':
    """ Drops the rule-engine tables.
    """
    metadata.drop_all(engine)

# ################################################################################################################################
# ################################################################################################################################
