# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import sys
import traceback
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

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
