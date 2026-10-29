# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The functions below change how the connections of pg8000 use the extended query protocol of PostgreSQL.
# Each statement is prepared once per connection and executed by its name afterwards, bytea parameters are sent
# in the binary format, the rows of a result are decoded by zato_pg_wire, which receives the columns of its native
# types in the binary format, and messages are written to and read from the socket without intermediate copies.

# stdlib
from collections import OrderedDict
from functools import lru_cache
from itertools import count
from typing import NamedTuple

# pg8000
from pg8000 import converters, core, legacy
from pg8000.converters import make_params
from pg8000.core import BIND, CLOSE, EXECUTE_MSG, H_pack, i_pack, NULL_BYTE, STATEMENT, SYNC_MSG
from pg8000.dbapi import convert_paramstyle
from pg8000.exceptions import DatabaseError, InterfaceError

# zato_pg_wire
from zato_pg_wire.zato_pg_wire import RowDecoder

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anylistnone, anytuple, intlist
    any_ = any_
    anydict = anydict
    anylist = anylist
    anylistnone = anylistnone
    anytuple = anytuple
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# A value at least this large is written to the socket as it is, rather than copied into the buffer of its message.
Max_Inline_Size = 65536

# How many prepared statements each connection keeps.
Max_Statements = 512

# How many statement texts the conversion of their placeholders is kept for.
_max_statement_texts = 2048

# The format codes of the extended query protocol.
_text_format   = 0
_binary_format = 1

# The length of a value that is NULL.
_null_length = i_pack(-1)

# The size of the length in the header of each message.
_length_size = 4

# The placeholder style SQLAlchemy uses with pg8000.
_format_style = 'format'

# The prefix of the names of the statements a connection prepares.
_statement_prefix = 'zato_'

# The Python types that are sent as bytea.
_binary_types = (bytes, bytearray, memoryview)

# The format codes of a parameter as they are sent in a Bind message.
_text_format_bin   = H_pack(_text_format)
_binary_format_bin = H_pack(_binary_format)

# The SQLSTATE codes of a prepared statement the server no longer has, or whose result changed with the schema.
_stale_statement_codes = {'26000', '0A000'}

# A statement whose result has no columns has no result format codes.
_no_result_formats:'intlist' = []

# The handlers of pg8000 that the connections use for the statements they do not prepare themselves.
_core_init = core.CoreConnection.__init__
_core_handle_data_row = core.CoreConnection.handle_DATA_ROW

# ################################################################################################################################
# ################################################################################################################################

class PreparedStatement(NamedTuple):
    """ A statement prepared by a connection, together with the description of its result.
    """
    name_bin: 'bytes'
    columns: 'anylistnone'
    input_funcs: 'anylist'
    decoder: 'RowDecoder | None'
    result_formats: 'intlist'

# ################################################################################################################################
# ################################################################################################################################

class DecodedContext(core.Context):
    """ The context of one execution of a prepared statement, whose rows are read by the decoder of the statement.
    """
    def __init__(self, statement:'str', stream:'any_', prepared:'PreparedStatement') -> 'None':
        super().__init__(statement, stream, prepared.columns, prepared.input_funcs)
        self.decoder = prepared.decoder

# ################################################################################################################################
# ################################################################################################################################

def _keep_bytes(value:'any_') -> 'bytes':
    """ Keeps a bytea parameter as bytes, so that it is sent as it is.
    """
    out = bytes(value)
    return out

# ################################################################################################################################

def _init(self:'any_', *args:'any_', **kwargs:'any_') -> 'None':
    """ Gives a new connection its cache of prepared statements and the counter that names them.
    """
    self._zato_statements = OrderedDict()
    self._zato_statement_ids = count()

    _core_init(self, *args, **kwargs)

# ################################################################################################################################

def _write_message(self:'any_', code:'bytes', parts:'anylist', length:'int') -> 'None':
    """ Writes one message to the socket of a connection, its header first and then each of its parts as they are.
    """
    message_length = length + _length_size
    header = code + i_pack(message_length)

    try:
        core._write(self._sock, header)

        for part in parts:
            core._write(self._sock, part)

    # A socket that was closed is reported the way pg8000 reports it ..
    except ValueError as e:
        if str(e) == 'write to closed file':
            raise InterfaceError('connection is closed')
        else:
            raise

    # .. as is a connection without a socket.
    except AttributeError:
        raise InterfaceError('connection is closed')

# ################################################################################################################################

def _send_message(self:'any_', code:'bytes', data:'bytes') -> 'None':
    """ Writes one message without copying its data into a buffer of its own.
    """
    data_length = len(data)
    _write_message(self, code, [data], data_length)

# ################################################################################################################################

def _read(sock:'any_', size:'int') -> 'bytes':
    """ Reads one block of a message from the socket of a connection, which a buffered socket returns in full.
    """
    try:
        out = sock.read(size)
    except OSError as e:
        raise InterfaceError('network error') from e

    # A buffered socket returns fewer bytes only when the server has closed the connection.
    received = len(out)

    if received < size:
        raise InterfaceError('network error')

    return out

# ################################################################################################################################

def _send_bind(
    self:'any_',
    statement_name_bin:'bytes',
    params:'anytuple',
    result_formats:'intlist' = _no_result_formats,
    ) -> 'None':
    """ Sends a Bind message in which bytea parameters are binary and the columns of the result have the formats given.
    Large parameters are written to the socket as they are.
    """
    # The portal is unnamed and each parameter has a format code of its own ..
    head = bytearray(NULL_BYTE + statement_name_bin)
    param_count = H_pack(len(params))
    head.extend(param_count)

    for value in params:
        if isinstance(value, bytes):
            head.extend(_binary_format_bin)
        else:
            head.extend(_text_format_bin)

    head.extend(param_count)

    # .. each value follows its length ..
    parts:'anylist' = [head]
    current = head

    for value in params:

        if value is None:
            current.extend(_null_length)

        elif isinstance(value, bytes):
            value_length = len(value)
            length_bin = i_pack(value_length)
            current.extend(length_bin)

            # .. a large bytea value becomes a part of the message of its own ..
            if value_length < Max_Inline_Size:
                current.extend(value)
            else:
                parts.append(value)
                current = bytearray()
                parts.append(current)

        # .. any other value is text ..
        else:
            data = value.encode(self._client_encoding)
            length_bin = i_pack(len(data))
            current.extend(length_bin)
            current.extend(data)

    # .. and each column of the result has a format code too.
    format_count = H_pack(len(result_formats))
    current.extend(format_count)

    for result_format in result_formats:
        format_bin = H_pack(result_format)
        current.extend(format_bin)

    length = 0

    for part in parts:
        length += len(part)

    _write_message(self, BIND, parts, length)

# ################################################################################################################################

def _prepare(self:'any_', statement:'str', oids:'anytuple') -> 'PreparedStatement':
    """ Prepares a statement under a name of its own and builds the decoder of its result.
    """
    statements = self._zato_statements
    statement_count = len(statements)

    # Once the cache is full, the statement used least recently is closed in the round trip that parses the new one ..
    if statement_count >= Max_Statements:
        _, evicted = statements.popitem(last=False)
        close_message = STATEMENT + evicted.name_bin
        self._send_message(CLOSE, close_message)

    statement_id = next(self._zato_statement_ids)
    statement_name = f'{_statement_prefix}{statement_id}'
    name_bin = statement_name.encode('ascii') + NULL_BYTE

    # .. the statement is parsed and described ..
    context = core.Context(statement)

    self.send_PARSE(name_bin, statement, oids)
    self.send_DESCRIBE_STATEMENT(name_bin)
    core._write(self._sock, SYNC_MSG)
    core._flush(self._sock)
    self.handle_messages(context)

    # .. and a statement that returns rows receives the decoder of its columns.
    if context.columns is None:
        decoder = None
        result_formats = _no_result_formats

    else:
        column_types:'anylist' = []

        for column, input_func in zip(context.columns, context.input_funcs):
            type_oid = column['type_oid']
            column_types.append((type_oid, input_func))

        decoder = RowDecoder(column_types)
        result_formats = decoder.result_formats

    out = PreparedStatement(name_bin, context.columns, context.input_funcs, decoder, result_formats)
    return out

# ################################################################################################################################

def _execute_unnamed(self:'any_', statement:'str', vals:'anytuple'=(), oids:'anytuple'=(), stream:'any_'=None) -> 'any_':
    """ Executes one statement, preparing it first if this connection has not prepared it yet.
    """
    statements = self._zato_statements
    key = (statement, tuple(oids))

    # A statement prepared already is executed by its name ..
    if prepared := statements.get(key):
        statements.move_to_end(key)

    # .. any other one is prepared first ..
    else:
        prepared = _prepare(self, statement, oids)
        statements[key] = prepared

    # .. and it is bound and executed in one round trip.
    context = DecodedContext(statement, stream, prepared)
    params = make_params(self.py_types, vals)

    self.send_BIND(prepared.name_bin, params, prepared.result_formats)
    core._write(self._sock, EXECUTE_MSG)
    core._write(self._sock, SYNC_MSG)
    core._flush(self._sock)

    try:
        self.handle_messages(context)

    # A statement the server no longer has, or whose result changed with the schema, is prepared anew next time.
    except DatabaseError as e:
        error = e.args[0]
        if error['C'] in _stale_statement_codes:
            del statements[key]
        raise

    return context

# ################################################################################################################################

def _handle_data_row(self:'any_', data:'bytes', context:'any_') -> 'None':
    """ Reads one row of a result, with the decoder of its prepared statement if it has one.
    """
    # Only a statement that returns rows receives them, so it has a decoder and a list of rows.
    if isinstance(context, DecodedContext):
        decoder = cast_('RowDecoder', context.decoder)
        rows = cast_('anylist', context.rows)

        row = decoder.decode(data)
        rows.append(row)

    else:
        _core_handle_data_row(self, data, context)

# ################################################################################################################################

@lru_cache(maxsize=_max_statement_texts)
def _number_placeholders(query:'str') -> 'str':
    """ Turns the %s placeholders of a statement into the numbered ones of PostgreSQL.
    """
    out, _ = convert_paramstyle(_format_style, query, ())
    return out

# ################################################################################################################################

def _convert_paramstyle(style:'str', query:'str', args:'any_') -> 'anytuple':
    """ Converts the placeholders of a statement, reusing the conversion of a statement seen before.
    """
    if style == _format_style:
        statement = _number_placeholders(query)
        out = (statement, args)
    else:
        out = convert_paramstyle(style, query, args)

    return out

# ################################################################################################################################

def install() -> 'None':
    """ Makes the connections of pg8000 prepare their statements once, exchange bytea values and the columns
    of native types in the binary format, decode rows in Rust and write messages without copying them.
    """
    # The converters of pg8000 map Python types to functions of each kind ..
    py_types:'anydict' = converters.PY_TYPES

    for python_type in _binary_types:
        py_types[python_type] = _keep_bytes

    # .. the connections use the functions of this module ..
    connection_class:'any_' = core.CoreConnection

    connection_class.__init__ = _init
    connection_class._send_message = _send_message
    connection_class.send_BIND = _send_bind
    connection_class.execute_unnamed = _execute_unnamed
    connection_class.handle_DATA_ROW = _handle_data_row

    # .. and so do the module-level functions that read the socket and convert placeholders.
    core._read = _read
    legacy.convert_paramstyle = _convert_paramstyle

# ################################################################################################################################
# ################################################################################################################################
