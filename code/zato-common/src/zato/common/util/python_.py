# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib
import sys
import traceback
from logging import getLogger
from pathlib import Path
from threading import current_thread

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

def get_python_id(item):

    # Python-level ID contains all the core details about the object that requests this information and its current thread
    _current_thread = current_thread()
    _current_thread_ident = cast_('int', _current_thread.ident)
    python_id = '{}.{}.{}'.format(hex(id(item)), _current_thread.name, hex(_current_thread_ident))

    return python_id

# ################################################################################################################################

def get_current_stack():
    sep = '*' * 80
    out = ['\n', sep]

    for line in traceback.format_stack():
        out.append(line.strip())

    out.append(sep)

    return '\n'.join(out)

# ################################################################################################################################

def log_current_stack():
    logger.info(get_current_stack())

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

def reload_module_(mod_name:'str') -> 'None':

    if mod_name in sys.modules:
        _ = importlib.reload(sys.modules[mod_name])
    else:
        _ = importlib.import_module(mod_name)

# ################################################################################################################################

def import_module_by_path(path:'str', root:'str'='') -> 'None':

    # Local aliases
    mod_path = Path(path)

    # If there is not root, it means that the name of the module is the same as its file ..
    if not root:
        mod_name = mod_path.stem

    # .. otherwise, we need to traverse up until we found the root directory ..
    else:
        pass

    # .. and then we can build the name of the module, starting from root down ..

    '''
    if name is None:
        name = Path(path).stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
    '''

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    path =

# ################################################################################################################################
# ################################################################################################################################
