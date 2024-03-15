# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from traceback import TracebackException

# Zato
from zato.common.version import get_version

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callnone

# ################################################################################################################################
# ################################################################################################################################

def pretty_format_exception(e:'Exception', cid:'str', utcnow_func:'callnone'=None) -> 'str':

    # Response to produce
    out = []

    focus_character = '·'
    focus_marker = focus_character * 3

    header1 = f'{focus_marker} Error {focus_marker}'
    header2 = f'{focus_marker} Details {focus_marker}'
    header3 = f'{focus_marker} Context {focus_marker}'

    # Extract the traceback from the exception
    tb = TracebackException.from_exception(e)

    exc_arg  = e.args[0] if e.args else e.args
    exc_type = e.__class__.__name__

    # For the error summary, we need to last frame in the stack,
    # i.e. the one that actually triggered the exception.
    frame = tb.stack[-1]

    file_path   = frame.filename
    line_number = frame.lineno
    func_name   = frame.name

    error_line = f'>>> {exc_type}: \'{exc_arg}\''
    file_line  = f'>>> File "{file_path}", line {line_number}, in {func_name}'
    code_line  = f'>>>   {frame.line}'

    details = ''.join(list(tb.format()))

    now = utcnow_func() if utcnow_func else datetime.utcnow().isoformat() + ' (UTC)'

    out.append(header1)
    out.append('\n')
    out.append('\n')

    out.append(error_line)
    out.append('\n')

    out.append(file_line)
    out.append('\n')

    out.append(code_line)
    out.append('\n')
    out.append('\n')

    out.append(header2)
    out.append('\n')
    out.append('\n')

    out.append(details)
    out.append('\n')

    out.append(header3)
    out.append('\n')
    out.append('\n')

    out.append(cid)
    out.append('\n')

    out.append(now)
    out.append('\n')

    out.append(get_version())
    out.append('\n')

    result = ''.join(out)
    result = result.strip()

    return result

# ################################################################################################################################
# ################################################################################################################################
