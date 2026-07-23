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

# Local
from .schema import metadata

# ################################################################################################################################
# ################################################################################################################################

any_:TypeAlias = Any
SessionFactory:TypeAlias = Callable[[], Session]

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

def create_session_factory(engine:'Engine') -> 'SessionFactory':
    """ Creates sessions whose loaded values remain readable after a transaction commits.
    """
    out = sessionmaker(bind=engine, expire_on_commit=False)
    return out

# ################################################################################################################################

def create_schema(engine:'Engine') -> 'None':
    """ Creates the four rule-engine tables.
    """
    metadata.create_all(engine)

# ################################################################################################################################

def drop_schema(engine:'Engine') -> 'None':
    """ Drops the four rule-engine tables.
    """
    metadata.drop_all(engine)

# ################################################################################################################################
# ################################################################################################################################
