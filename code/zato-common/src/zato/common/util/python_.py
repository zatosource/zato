# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
import traceback
from importlib.util import module_from_spec, spec_from_file_location
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

        # .. first, get all the path parts, reversed, because we are traversing them backwards ..
        parts = mod_path.parts
        parts = list(reversed(parts))

        # .. the first element is the file name so we need to remove its extension ..
        mod_file = parts[0]
        mod_file = Path(mod_file)
        mod_file_name = mod_file.stem

        # .. now, look up our root ..
        root_idx = parts.index(root)

        # .. get the rest of the module's path, from right above its name (hence we start from 1) until the root ..
        mod_name_parts = parts[1:root_idx]

        # .. we have the names and we can reverse them back so they run from top to bottom again ..
        mod_name_parts = list(reversed(mod_name_parts))

        # .. we can append the final file name now ..
        mod_name_parts.append(mod_file_name)

        # .. and this gives us the full module name ..
        mod_name = '.'.join(mod_name_parts)

    # .. we have both the name of a module and its path so we can import it now ..
    if spec := spec_from_file_location(mod_name, path):
        module = module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module) # type: ignore

        print(111, module)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    import sys
    sys.path.insert(0, '#################################')

    path = '#################################'

    import_module_by_path(path, 'src')

# ################################################################################################################################
# ################################################################################################################################
