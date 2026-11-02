# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The functions below change how the connections of pg8000 use the extended query protocol of PostgreSQL.
# Each statement is prepared once per connection and executed by its name afterwards, bytea parameters are sent
# in the binary format, the rows of a result are decoded by zato_pg_wire, which receives the columns of its native
# types in the binary format, the messages of each round trip leave in one send and their replies are parsed out
# of the bytes that each read of the socket returns, and the begin of each transaction travels to the server together
# with the first statement of the transaction.

# stdlib
from collections import OrderedDict
from functools import lru_cache
from itertools import count
from struct import Struct
from typing import NamedTuple

# pg8000
from pg8000 import converters, core, legacy
from pg8000.converters import make_params
from pg8000.core import BIND, CLOSE, EXECUTE_MSG, H_pack, i_pack, NULL_BYTE, READY_FOR_QUERY, STATEMENT, SYNC_MSG
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

# How many bytes one read from the socket of a connection may return at most.
_read_size = 65536

# The size of the header of each message from the server, its code and its length.
_header_size = 5

# Reads the code and the length of a message from its header.
ci_unpack_from = Struct('!ci').unpack_from

# The statement with which pg8000 opens each transaction of a connection that does not commit automatically.
_begin_statement = 'begin transaction'

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

class SocketWire:
    """ The socket of a connection after its startup, collecting the messages written to it until they are flushed
    in one send, and returning from each read whatever the socket holds, without the buffered file of pg8000 in between.
    """
    __slots__ = ('_socket', '_buffer', 'read1')

    def __init__(self, socket:'any_') -> 'None':
        self._socket = socket
        self._buffer = bytearray()
        self.read1 = socket.recv

    def write(self, data:'bytes') -> 'None':

        # A large value is sent as it is, after the bytes collected before it ..
        if len(data) >= Max_Inline_Size:
            self.flush()
            self._socket.sendall(data)

        # .. and anything else is collected.
        else:
            self._buffer.extend(data)

    def flush(self) -> 'None':
        if self._buffer:
            self._socket.sendall(self._buffer)
            self._buffer.clear()

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
    self._zato_pending_begin = None
    self._zato_received = b''
    self._zato_received_pos = 0

    # pg8000 reports the socket errors of a new connection as InterfaceError, apart from those raised
    # while it requests TLS, which would otherwise reach the caller as a bare OSError that no retry recognizes.
    try:
        _core_init(self, *args, **kwargs)
    except OSError as e:
        raise InterfaceError(f'Could not open a connection: {e}') from e

    # Once the startup is over, the connection uses its socket directly, and closing the buffered file
    # of the startup leaves the socket open, because the socket closes only once its files are closed too.
    startup_file = self._sock
    self._sock = SocketWire(self._usock)
    startup_file.close()

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

def _receive(self:'any_', needed:'int') -> 'None':
    """ Reads from the socket of a connection until its buffer holds at least the number of unread bytes given.
    Each read returns whatever the socket has, so the replies to several messages arrive in one call.
    """
    # The bytes not read yet are kept ..
    unread = self._zato_received[self._zato_received_pos:]
    chunks = [unread]
    unread_size = len(unread)

    # .. and the socket is read until enough bytes are unread.
    while unread_size < needed:

        try:
            chunk = self._sock.read1(_read_size)
        except OSError as e:
            raise InterfaceError('network error') from e

        # An empty read means that the server has closed the connection.
        if not chunk:
            raise InterfaceError('network error')

        chunks.append(chunk)
        unread_size += len(chunk)

    # A reply that arrived in one read is used as it is.
    if not unread and len(chunks) == 2:
        self._zato_received = chunks[1]
    else:
        self._zato_received = b''.join(chunks)

    self._zato_received_pos = 0

# ################################################################################################################################

def _handle_messages(self:'any_', context:'any_') -> 'None':
    """ Handles the messages of the server up to and including the one that reports it is ready for the next query,
    parsing them out of the bytes that each read of the socket returned.
    """
    message_types = self.message_types
    code = None

    while code != READY_FOR_QUERY:

        # The header of the next message gives its code and length ..
        if len(self._zato_received) - self._zato_received_pos < _header_size:
            _receive(self, _header_size)

        received = self._zato_received
        pos = self._zato_received_pos
        code, data_len = ci_unpack_from(received, pos)

        # .. and its data follows the header.
        message_end = pos + 1 + data_len

        if len(received) < message_end:
            _receive(self, 1 + data_len)
            received = self._zato_received
            pos = 0
            message_end = 1 + data_len

        data = received[pos + _header_size:message_end]
        self._zato_received_pos = message_end

        message_types[code](data, context)

    if context.error is not None:
        raise context.error

# ################################################################################################################################

def _execute_simple(self:'any_', statement:'str') -> 'any_':
    """ Executes one statement in the simple query protocol. The begin of a transaction is written to the socket
    without waiting for its reply, which is read together with the reply of the statement that follows it,
    so that the two travel to the server in one round trip.
    """
    context = core.Context(statement)
    self.send_QUERY(statement)

    if statement == _begin_statement:
        self._zato_pending_begin = context
    else:
        core._flush(self._sock)
        _read_replies(self, context)

    return context

# ################################################################################################################################

def _read_replies(self:'any_', context:'any_') -> 'None':
    """ Reads the reply to a pending begin, if one was written before the statement, and then the reply to the statement.
    """
    begin_context = self._zato_pending_begin

    if begin_context is not None:
        self._zato_pending_begin = None

        # A begin that failed still leaves the reply to the statement on the socket, which is read before the error is raised.
        try:
            self.handle_messages(begin_context)
        except DatabaseError:
            self.handle_messages(context)
            raise

    self.handle_messages(context)

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
    _read_replies(self, context)

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
        _read_replies(self, context)

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
    connection_class.execute_simple = _execute_simple
    connection_class.handle_messages = _handle_messages
    connection_class.execute_unnamed = _execute_unnamed
    connection_class.handle_DATA_ROW = _handle_data_row

    # .. and so do the module-level functions that read the socket and convert placeholders.
    core._read = _read
    legacy.convert_paramstyle = _convert_paramstyle

# ################################################################################################################################
# ################################################################################################################################
