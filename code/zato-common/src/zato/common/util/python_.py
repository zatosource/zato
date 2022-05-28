# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from threading import current_thread
import traceback
from logging import getLogger

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

def get_python_id(item):

    # Python-level ID contains all the core details about the object that requests this information and its current thread
    _current_thread = current_thread()
    _current_thread_ident = cast_('int', _current_thread.ident)
    python_id = '{}.{}.{}'.format(hex(id(item)), _current_thread.name, hex(_current_thread_ident))

    return python_id

# ################################################################################################################################
# ################################################################################################################################

def get_current_stack():
    sep = '*' * 80
    out = ['\n', sep]

    for line in traceback.format_stack():
        out.append(line.strip())

    out.append(sep)

    return '\n'.join(out)

# ################################################################################################################################
# ################################################################################################################################

def log_current_stack():
    logger.info(get_current_stack())

# ################################################################################################################################
# ################################################################################################################################

# Taken from https://stackoverflow.com/a/16589622
def get_full_stack():
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. if an exception is present
        del stack[-1]    # remove call of full_stack, the printed exception will contain the caught exception caller instead
    trace = 'Traceback (most recent call last):\n'
    stack_string = trace + ''.join(traceback.format_list(stack))

    if exc is not None:
        stack_string += '  '
        stack_string += traceback.format_exc()
        stack_string = stack_string.lstrip(trace)

    return stack_string

# ################################################################################################################################
# ################################################################################################################################
