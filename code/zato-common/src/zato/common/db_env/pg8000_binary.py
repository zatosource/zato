# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pg8000 sends every parameter and receives every column as text, which turns each bytea value into hex digits
# twice its size. The functions below make it send bytea parameters and receive bytea columns in the binary format
# of the extended query protocol, as they are.

# pg8000
from pg8000 import converters, core
from pg8000.converters import make_params
from pg8000.core import BIND, FLUSH_MSG, H_pack, i_pack, i_unpack, NULL_BYTE, SYNC_MSG

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple
    any_ = any_
    anydict = anydict
    anylist = anylist
    anytuple = anytuple

# ################################################################################################################################
# ################################################################################################################################

# The format codes of the extended query protocol.
_text_format   = 0
_binary_format = 1

# The length of a value that is NULL.
_null_length = -1

# Where the first value of a DataRow message begins, after the count of its values, and how long each length is.
_first_value_offset = 2
_length_size        = 4

# The Python types that are sent as bytea.
_binary_types = (bytes, bytearray, memoryview)

# ################################################################################################################################
# ################################################################################################################################

def _keep_bytes(value:'any_') -> 'bytes':
    """ Keeps a bytea parameter as bytes, so that it is sent as it is.
    """
    out = bytes(value)
    return out

# ################################################################################################################################

def _read_binary(value:'bytes') -> 'bytes':
    """ Stands in for the reader of a bytea column received in the binary format, whose value is taken as it arrives.
    """
    return value

# ################################################################################################################################

def _send_bind(self:'any_', statement_name_bin:'bytes', params:'anytuple', result_formats:'anylist | None'=None) -> 'None':
    """ Sends a Bind message whose bytea parameters, and the columns whose format is given as binary, travel as they are.
    """
    if result_formats is None:
        result_formats = []

    message = bytearray(NULL_BYTE + statement_name_bin)

    # Each parameter has a format code of its own ..
    message.extend(H_pack(len(params)))

    for value in params:
        if isinstance(value, bytes):
            message.extend(H_pack(_binary_format))
        else:
            message.extend(H_pack(_text_format))

    # .. a bytea value is sent as it is and any other one as text ..
    message.extend(H_pack(len(params)))

    for value in params:
        if value is None:
            message.extend(i_pack(_null_length))
        else:
            if isinstance(value, bytes):
                data = value
            else:
                data = value.encode(self._client_encoding)
            message.extend(i_pack(len(data)))
            message.extend(data)

    # .. and each column of the result has a format code too.
    message.extend(H_pack(len(result_formats)))

    for result_format in result_formats:
        message.extend(H_pack(result_format))

    self._send_message(BIND, message)
    core._write(self._sock, FLUSH_MSG)

# ################################################################################################################################

def _execute_unnamed(self:'any_', statement:'str', vals:'anytuple'=(), oids:'anytuple'=(), stream:'any_'=None) -> 'any_':
    """ Executes one statement with the unnamed prepared statement, reading its bytea columns in the binary format.
    """
    context = core.Context(statement, stream=stream)

    # The statement is parsed and described before it is bound, so that the types of its columns are known ..
    self.send_PARSE(NULL_BYTE, statement, oids)
    core._write(self._sock, SYNC_MSG)
    core._flush(self._sock)
    self.handle_messages(context)

    self.send_DESCRIBE_STATEMENT(NULL_BYTE)
    core._write(self._sock, SYNC_MSG)
    core._flush(self._sock)
    self.handle_messages(context)

    # .. its bytea columns are received in the binary format ..
    result_formats:'anylist' = []

    if context.columns is not None:
        for idx, column in enumerate(context.columns):
            if column['type_oid'] == converters.BYTES:
                result_formats.append(_binary_format)
                context.input_funcs[idx] = _read_binary
            else:
                result_formats.append(_text_format)

    # .. and it is executed with its parameters.
    params = make_params(self.py_types, vals)
    self.send_BIND(NULL_BYTE, params, result_formats)
    self.send_EXECUTE()
    core._write(self._sock, SYNC_MSG)
    core._flush(self._sock)
    self.handle_messages(context)

    return context

# ################################################################################################################################

def _handle_data_row(self:'any_', data:'bytes', context:'any_') -> 'None':
    """ Reads one row of a result, taking the bytea columns received in the binary format as they are.
    """
    idx = _first_value_offset
    row:'anylist' = []

    for func in context.input_funcs:
        length = i_unpack(data, idx)[0]
        idx += _length_size

        if length == _null_length:
            value = None
        else:
            end = idx + length

            if func is _read_binary:
                value = data[idx:end]
            else:
                value = func(str(data[idx:end], encoding=self._client_encoding))

            idx = end

        row.append(value)

    context.rows.append(row)

# ################################################################################################################################

def install() -> 'None':
    """ Makes the connections of pg8000 send and receive bytea values in the binary format.
    """
    # The converters of pg8000 map Python types to functions of each kind.
    py_types:'anydict' = converters.PY_TYPES

    for python_type in _binary_types:
        py_types[python_type] = _keep_bytes

    core.CoreConnection.send_BIND = _send_bind
    core.CoreConnection.execute_unnamed = _execute_unnamed
    core.CoreConnection.handle_DATA_ROW = _handle_data_row

# ################################################################################################################################
# ################################################################################################################################
