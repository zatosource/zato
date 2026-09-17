# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from linecache import getline
from sysconfig import get_paths

# Zato
from zato.common.exception import ZatoException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from types import TracebackType
    from zato.common.typing_ import anydict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

_zato_module_prefix = 'zato.'
_source_indent      = '    '
_block_separator    = '\n\n'
_keys_separator     = ', '

_paths = get_paths()
_library_paths = (_paths['stdlib'], _paths['platstdlib'], _paths['purelib'], _paths['platlib'])

# ################################################################################################################################
# ################################################################################################################################

def _get_message(e:'BaseException') -> 'str':
    """ Returns the text that goes after the exception's type name.
    """

    # A Zato exception keeps its text in .msg because its __str__ is __repr__ ..
    if isinstance(e, ZatoException):
        out = e.msg
        if out is None:
            out = ''

    # .. str(KeyError) wraps the key in quotes, so the key itself is used ..
    elif isinstance(e, KeyError):
        out = e.args[0]

    # .. an AttributeError from a dict is a missing key, so the existing ones are listed ..
    elif isinstance(e, AttributeError):
        if isinstance(e.obj, dict):
            out = _get_missing_key_message(e.name, e.obj)
        else:
            out = str(e)

    # .. everything else speaks for itself.
    else:
        out = str(e)

    return out

# ################################################################################################################################

def _get_missing_key_message(name:'strnone', data:'anydict') -> 'str':

    keys:'strlist' = []

    for key in sorted(data):
        keys.append(f'`{key}`')

    if keys:
        existing = _keys_separator.join(keys)
        out = f'no such key `{name}`, existing keys: {existing}'
    else:
        out = f'no such key `{name}`, it has no keys'

    return out

# ################################################################################################################################

def _get_error_line(e:'BaseException') -> 'str':

    type_name = type(e).__name__
    message = _get_message(e)

    if message:
        out = f'{type_name}: {message}'
    else:
        out = type_name

    return out

# ################################################################################################################################

def _is_user_frame(module_name:'str', filename:'str') -> 'bool':

    if module_name.startswith(_zato_module_prefix):
        out = False
    elif filename.startswith(_library_paths):
        out = False
    else:
        out = True

    return out

# ################################################################################################################################

def _find_user_traceback(e:'BaseException') -> 'TracebackType | None':
    """ Returns the deepest traceback entry that belongs to the user's own code.
    """
    out = None
    traceback = e.__traceback__

    while traceback:
        frame = traceback.tb_frame
        module_name = frame.f_globals['__name__']
        filename = frame.f_code.co_filename

        if _is_user_frame(module_name, filename):
            out = traceback

        traceback = traceback.tb_next

    return out

# ################################################################################################################################

def _get_location_block(traceback:'TracebackType') -> 'str':

    frame = traceback.tb_frame
    filename = frame.f_code.co_filename
    function_name = frame.f_code.co_name
    line_number = traceback.tb_lineno

    source_line = getline(filename, line_number)
    source_line = source_line.strip()

    location = f'{filename}, line {line_number}, in {function_name}'
    out = f'{location}\n{_source_indent}{source_line}'

    return out

# ################################################################################################################################

def explain_exception(e:'Exception', cid:'str') -> 'str':
    """ Returns the error, the line in the user's service where it happened and the CID, with no traceback.
    """
    blocks:'strlist' = []

    # The error itself ..
    error_block = _get_error_line(e)

    # .. along with what it was raised from ..
    if e.__cause__:
        cause_line = _get_error_line(e.__cause__)
        error_block = f'{error_block}\nCaused by {cause_line}'

    blocks.append(error_block)

    # .. the line in the user's code, if the error went through any ..
    if traceback := _find_user_traceback(e):
        location_block = _get_location_block(traceback)
        blocks.append(location_block)

    # .. and the CID to find the full details in the server log.
    blocks.append(f'CID: {cid}')

    out = _block_separator.join(blocks)
    return out

# ################################################################################################################################
# ################################################################################################################################
