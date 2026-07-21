# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Schema evolution for environment-configured databases - tables created by older
# releases learn here about newly declared columns, indexes and widened column types.

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy import text as sa_text

# Zato
from zato.common.db_env.common import Type_MySQL, Type_Oracle, Type_PostgreSQL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Table
    from sqlalchemy.engine import Engine

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def ensure_columns(engine:'Engine', table:'Table') -> 'None':
    """ Adds to an existing table any columns its declaration has gained since the table
    was first created - new columns arrive with new releases and the databases created
    by older ones need to learn about them.
    """
    inspector = inspect(engine)
    existing = inspector.get_columns(table.name)

    # The names the database already knows about
    existing_names = set()

    for column_info in existing:
        existing_names.add(column_info['name'])

    # Oracle DB is the one dialect that does not accept the COLUMN keyword here
    if engine.dialect.name == Type_Oracle:
        add_clause = 'ADD'
    else:
        add_clause = 'ADD COLUMN'

    for column in table.columns:

        if column.name in existing_names:
            continue

        # Let the dialect render the correct type name for this column
        type_sql = column.type.compile(engine.dialect)
        ddl = f'ALTER TABLE {table.name} {add_clause} {column.name} {type_sql}'

        with engine.begin() as connection:
            _ = connection.execute(sa_text(ddl))

        logger.info('Added column `%s` to table `%s`', column.name, table.name)

# ################################################################################################################################

def ensure_indexes(engine:'Engine', table:'Table') -> 'None':
    """ Creates on an existing table any indexes its declaration has gained since the table
    was first created - create_all only builds indexes together with new tables,
    so databases created by older releases need to learn about new ones here.
    """
    inspector = inspect(engine)
    existing = inspector.get_indexes(table.name)

    # The names the database already knows about
    existing_names = set()

    for index_info in existing:
        existing_names.add(index_info['name'])

    for index in table.indexes:

        if index.name in existing_names:
            continue

        index.create(engine)

        logger.info('Added index `%s` to table `%s`', index.name, table.name)

# ################################################################################################################################

def ensure_column_types(engine:'Engine', table:'Table') -> 'None':
    """ Widens to 64 bits any integer columns whose declaration has become BigInteger since
    the table was first created - ids started out as 32-bit INT and databases created
    by older releases need the wider type before their autoincrement overflows.
    """

    # Only these two dialects render Integer as a 32-bit INT - SQLite integers
    # are always 64-bit and Oracle's INTEGER is already a 38-digit NUMBER.
    if engine.dialect.name not in (Type_MySQL, Type_PostgreSQL):
        return

    inspector = inspect(engine)
    existing = inspector.get_columns(table.name)

    # The type the database currently holds each column as
    existing_types = {}

    for column_info in existing:
        existing_types[column_info['name']] = column_info['type']

    for column in table.columns:

        # Only columns declared as 64-bit can need widening ..
        declared_sql = column.type.compile(engine.dialect)

        if declared_sql != 'BIGINT':
            continue

        # .. and only when the database still holds them as something narrower -
        # .. MySQL reflection may add a display width, hence the prefix check.
        existing_type = existing_types[column.name]
        existing_sql = existing_type.compile(engine.dialect)

        if existing_sql.startswith('BIGINT'):
            continue

        # MySQL's MODIFY restates the full definition, so the autoincrement primary key keeps its property ..
        if engine.dialect.name == Type_MySQL:
            if column.primary_key:
                ddl = f'ALTER TABLE {table.name} MODIFY {column.name} BIGINT NOT NULL AUTO_INCREMENT'
            else:
                ddl = f'ALTER TABLE {table.name} MODIFY {column.name} BIGINT'

        # .. while PostgreSQL changes the type alone and any attached sequence stays in place.
        else:
            ddl = f'ALTER TABLE {table.name} ALTER COLUMN {column.name} TYPE BIGINT'

        with engine.begin() as connection:
            _ = connection.execute(sa_text(ddl))

        logger.info('Widened column `%s` of table `%s` to BIGINT', column.name, table.name)

# ################################################################################################################################
# ################################################################################################################################
