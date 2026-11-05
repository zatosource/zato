# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from decimal import Decimal
from functools import lru_cache
from struct import Struct
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import event as sa_event
from sqlalchemy.dialects.postgresql.pg8000 import PGDialect_pg8000

# Zato
from zato.common.db_env.pg8000_wire import Max_Inline_Size
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Dialect
    from sqlalchemy.sql.schema import Table
    from zato.common.typing_ import any_, anylist, callable_, callnone, dictlist, strtuple
    any_ = any_
    anylist = anylist
    callable_ = callable_
    callnone = callnone
    Connection = Connection
    Dialect = Dialect
    dictlist = dictlist
    strtuple = strtuple
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

copy_column_list = list['CopyColumn']

_int2   = Struct('!h')
_int4   = Struct('!i')
_int8   = Struct('!q')
_float8 = Struct('!d')

# The header of a binary NUMERIC - the count of its digits, the weight of the first one, its sign and its display scale.
_numeric_header = Struct('!hhHh')

# The signs of a binary NUMERIC.
_numeric_positive          = 0x0000
_numeric_negative          = 0x4000
_numeric_nan               = 0xC000
_numeric_positive_infinity = 0xD000
_numeric_negative_infinity = 0xF000

# The digits of a binary NUMERIC are in base 10000, each one covering four decimal digits.
_numeric_base        = 10_000
_numeric_base_digits = 4
_decimal_base        = 10

# The header of a COPY stream in the binary format - its signature, its flags and the length of its extension area.
_copy_header = b'PGCOPY\n\xff\r\n\x00' + _int4.pack(0) + _int4.pack(0)

# The field count that ends a COPY stream.
_copy_trailer = _int2.pack(-1)

# The length of a field that is NULL.
_null_length = _int4.pack(-1)

# The encoding of the text sent by the connections.
_text_encoding = 'utf8'

# The epochs of the binary timestamps of PostgreSQL, with a time zone and without one.
_postgresql_epoch_utc   = datetime(2000, 1, 1, tzinfo=timezone.utc)
_postgresql_epoch_naive = datetime(2000, 1, 1)

_microseconds_per_second = 1_000_000
_seconds_per_day         = 86_400

# The binary values of a boolean.
_boolean_values = {
    True: b'\x01',
    False: b'\x00',
}

# How many tables with a given set of columns the COPY statements are kept for.
_max_copy_plans = 256

# The execution option with the chunks of a COPY stream.
_stream_option = 'zato_copy_stream'

# ################################################################################################################################
# ################################################################################################################################

class CopyColumn(NamedTuple):
    """ One column of a COPY stream, with the function that encodes its values.
    """
    name: 'str'
    encoder: 'callable_'
    processor: 'callnone'

# ################################################################################################################################

class CopyPlan(NamedTuple):
    """ The COPY statement for a set of columns of a table and how each of the columns is encoded.
    """
    statement: 'str'
    columns: 'copy_column_list'

# ################################################################################################################################
# ################################################################################################################################

def _encode_text(value:'str') -> 'bytes':
    out = value.encode(_text_encoding)
    return out

# ################################################################################################################################

def _encode_bytes(value:'bytes') -> 'bytes':
    return value

# ################################################################################################################################

def _encode_boolean(value:'bool') -> 'bytes':
    out = _boolean_values[value]
    return out

# ################################################################################################################################

def _encode_int2(value:'int') -> 'bytes':
    out = _int2.pack(value)
    return out

# ################################################################################################################################

def _encode_int4(value:'int') -> 'bytes':
    out = _int4.pack(value)
    return out

# ################################################################################################################################

def _encode_int8(value:'int') -> 'bytes':
    out = _int8.pack(value)
    return out

# ################################################################################################################################

def _encode_float8(value:'float') -> 'bytes':
    out = _float8.pack(value)
    return out

# ################################################################################################################################

def _encode_special_numeric(number:'Decimal') -> 'bytes':
    """ Encodes NaN or an infinity as a binary NUMERIC, which has no digits.
    """
    if number.is_nan():
        sign = _numeric_nan
    elif number > 0:
        sign = _numeric_positive_infinity
    else:
        sign = _numeric_negative_infinity

    out = _numeric_header.pack(0, 0, sign, 0)
    return out

# ################################################################################################################################

def _encode_numeric(value:'int | float | Decimal') -> 'bytes':
    """ Encodes a number as a binary NUMERIC - its digits in base 10000, most significant first,
    the weight of the first digit, the sign and the display scale.
    """

    # A float is encoded through its shortest decimal representation ..
    if isinstance(value, float):
        shortest = repr(value)
        number = Decimal(shortest)
    else:
        number = Decimal(value)

    # .. NaN and the infinities have no digits ..
    if not number.is_finite():
        out = _encode_special_numeric(number)
        return out

    decimal_sign, decimal_digits, exponent = number.as_tuple()
    exponent = cast_('int', exponent)

    if decimal_sign:
        sign = _numeric_negative
    else:
        sign = _numeric_positive

    # .. the decimal digits become one integer ..
    coefficient = 0

    for decimal_digit in decimal_digits:
        coefficient = coefficient * _decimal_base + decimal_digit

    # .. which is scaled so the decimal point falls on a boundary of the base 10000 digits ..
    if exponent >= 0:
        coefficient *= _decimal_base ** exponent
        scale = 0
    else:
        scale = -exponent

    padding = -scale % _numeric_base_digits
    coefficient *= _decimal_base ** padding

    padded_scale = scale + padding
    fraction_digit_count = padded_scale // _numeric_base_digits

    # .. split into the base 10000 digits, least significant first ..
    digits:'anylist' = []

    while coefficient:
        coefficient, digit = divmod(coefficient, _numeric_base)
        digits.append(digit)

    digit_count = len(digits)
    weight = digit_count - 1 - fraction_digit_count

    # .. the trailing zero digits are implied by the weight ..
    first_nonzero = 0

    while first_nonzero < digit_count and digits[first_nonzero] == 0:
        first_nonzero += 1

    digits = digits[first_nonzero:]
    digits.reverse()

    # .. a zero has no digits at all ..
    if not digits:
        weight = 0
        sign = _numeric_positive

    # .. and the digits follow the header.
    digit_count = len(digits)

    out = bytearray(_numeric_header.pack(digit_count, weight, sign, scale))

    for digit in digits:
        packed = _int2.pack(digit)
        out.extend(packed)

    out = bytes(out)
    return out

# ################################################################################################################################

def _encode_since(value:'datetime', epoch:'datetime') -> 'bytes':
    """ Encodes a timestamp as the number of microseconds since the epoch given.
    """
    delta = value - epoch

    days_seconds = delta.days * _seconds_per_day
    seconds = days_seconds + delta.seconds
    seconds_microseconds = seconds * _microseconds_per_second
    microseconds = seconds_microseconds + delta.microseconds

    out = _int8.pack(microseconds)
    return out

# ################################################################################################################################

def _encode_timestamptz(value:'datetime') -> 'bytes':
    out = _encode_since(value, _postgresql_epoch_utc)
    return out

# ################################################################################################################################

def _encode_timestamp(value:'datetime') -> 'bytes':
    out = _encode_since(value, _postgresql_epoch_naive)
    return out

# ################################################################################################################################
# ################################################################################################################################

# The encoder of each type of column, by the name of the type in PostgreSQL without its length.
_encoders = {
    'BIGINT': _encode_int8,
    'BOOLEAN': _encode_boolean,
    'BYTEA': _encode_bytes,
    'DOUBLE PRECISION': _encode_float8,
    'INTEGER': _encode_int4,
    'NUMERIC': _encode_numeric,
    'SMALLINT': _encode_int2,
    'TEXT': _encode_text,
    'TIMESTAMP WITH TIME ZONE': _encode_timestamptz,
    'TIMESTAMP WITHOUT TIME ZONE': _encode_timestamp,
    'VARCHAR': _encode_text,
}

# ################################################################################################################################
# ################################################################################################################################

@lru_cache(maxsize=_max_copy_plans)
def get_copy_plan(dialect:'Dialect', table:'Table', names:'strtuple') -> 'CopyPlan':
    """ Builds the COPY statement for the columns of a table given and finds the encoder of each column.
    """
    preparer = dialect.identifier_preparer

    columns:'copy_column_list' = []
    quoted_names:'anylist' = []

    for name in names:

        # Each column is encoded according to its type in PostgreSQL ..
        column = table.c[name]
        type_name = column.type.compile(dialect=dialect)
        type_name, _, _ = type_name.partition('(')
        encoder = _encoders[type_name]

        # .. after the processing SQLAlchemy applies to its values before it binds them.
        processor = column.type.bind_processor(dialect)

        copy_column = CopyColumn(name, encoder, processor)
        columns.append(copy_column)

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
    current = bytearray(_copy_header)
    out:'anylist' = [current]

    column_count = len(plan.columns)
    field_count = _int2.pack(column_count)

    for row in rows:
        current.extend(field_count)

        for column in plan.columns:
            value = row[column.name]

            # A NULL value has only its length ..
            if value is None:
                current.extend(_null_length)
                continue

            # .. any other one is processed the way SQLAlchemy would process it ..
            if column.processor:
                value = column.processor(value)

            data = column.encoder(value)
            size = len(data)
            size_bin = _int4.pack(size)
            current.extend(size_bin)

            # .. and a large one is sent as it is.
            if size < Max_Inline_Size:
                current.extend(data)
            else:
                out.append(data)
                current = bytearray()
                out.append(current)

    current.extend(_copy_trailer)

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
