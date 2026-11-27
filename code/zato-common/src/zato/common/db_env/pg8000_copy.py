# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import lru_cache
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import event as sa_event
from sqlalchemy.dialects.postgresql.pg8000 import PGDialect_pg8000

# zato_pg_wire
from zato_pg_wire.zato_pg_wire import encode_copy_rows

# Zato
from zato.common.db_env.any_of import type_name_of
from zato.common.db_env.pg8000_common import Max_Inline_Size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Dialect
    from sqlalchemy.sql.schema import Table
    from zato.common.typing_ import any_, anylist, dictlist, strtuple
    any_ = any_
    anylist = anylist
    Connection = Connection
    Dialect = Dialect
    dictlist = dictlist
    strtuple = strtuple
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# How many tables with a given set of columns the COPY statements are kept for.
_max_copy_plans = 256

# The execution option with the chunks of a COPY stream.
_stream_option = 'zato_copy_stream'

# ################################################################################################################################
# ################################################################################################################################

class CopyPlan(NamedTuple):
    """ The COPY statement for a set of columns of a table, with the name, the type in PostgreSQL
    and the bind processor of each of the columns, which zato_pg_wire encodes the values of the rows by.
    """
    statement: 'str'
    columns: 'anylist'

# ################################################################################################################################
# ################################################################################################################################

@lru_cache(maxsize=_max_copy_plans)
def get_copy_plan(dialect:'Dialect', table:'Table', names:'strtuple') -> 'CopyPlan':
    """ Builds the COPY statement for the columns of a table given and finds the type of each column.
    """
    preparer = dialect.identifier_preparer

    columns:'anylist' = []
    quoted_names:'anylist' = []

    for name in names:

        # Each column is encoded according to its type in PostgreSQL ..
        column = table.c[name]
        type_name = type_name_of(column.type, dialect)

        # .. after the processing SQLAlchemy applies to its values before it binds them.
        processor = column.type.bind_processor(dialect)

        columns.append((name, type_name, processor))

        quoted_name = preparer.quote(name)
        quoted_names.append(quoted_name)

    table_name = preparer.format_table(table)
    column_list = ', '.join(quoted_names)

    statement = f'COPY {table_name} ({column_list}) FROM STDIN WITH (FORMAT binary)'

    out = CopyPlan(statement, columns)
    return out

# ################################################################################################################################

def encode_rows(plan:'CopyPlan', rows:'dictlist') -> 'anylist':
    """ Encodes rows as a COPY stream in the binary format, in chunks, each large value being a chunk of its own.
    """
    out = encode_copy_rows(rows, plan.columns, Max_Inline_Size)
    return out

# ################################################################################################################################

def copy_rows(connection:'Connection', table:'Table', rows:'dictlist') -> 'None':
    """ Inserts rows into a table of PostgreSQL with one COPY statement in the binary format.
    All the rows have the same keys, which name the columns they fill.
    """
    first_row = rows[0]
    names = tuple(first_row)

    plan = get_copy_plan(connection.dialect, table, names)
    chunks = encode_rows(plan, rows)

    # The cursor of the transaction reads the stream from the chunks given in the execution options.
    options = {_stream_option: chunks}
    _ = connection.exec_driver_sql(plan.statement, execution_options=options)

# ################################################################################################################################

def _do_execute(cursor:'any_', statement:'str', parameters:'any_', context:'any_') -> 'bool':
    """ Executes a COPY statement with the stream of its execution options and leaves any other statement to the dialect.
    """
    if chunks := context.execution_options.get(_stream_option):
        _ = cursor.execute(statement, stream=chunks)
        out = True
    else:
        out = False

    return out

# ################################################################################################################################

def install() -> 'None':
    """ Makes the pg8000 dialect execute the COPY statements of copy_rows with their streams.
    """
    sa_event.listen(PGDialect_pg8000, 'do_execute', _do_execute)

# ################################################################################################################################
# ################################################################################################################################
