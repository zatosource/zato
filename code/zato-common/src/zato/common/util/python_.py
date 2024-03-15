# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib
import sys
import traceback
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from logging import getLogger
from pathlib import Path
from threading import current_thread

# Zato
from zato.common.typing_ import cast_, module_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ModuleInfo:
    name: 'str'
    path: 'Path'
    module: 'module_'

# ################################################################################################################################
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

def get_module_name_by_path(path:'str | Path') -> 'str':

    # Local aliases
    root = ''
    root_idx:'intnone' = None
    mod_path = Path(path)

    # If we are in a directory of that name, it means that this directory should be treated as our root,
    # note that currently there is only one directory configured here.
    immediate_root_list = ['services']

    # All the roots that we may potentially find
    root_list = ['src', 'source']

    # Get and reverse the parts of the path for the ease of their manipulation
    parts = mod_path.parts
    parts = list(reversed(parts))

    # This is our parent directory ..
    parent = parts[1]

    # .. first, check if our immediate root is a name that we recognize ..
    if parent in immediate_root_list:

        # .. if yes, the name of the file becomes the module's name.
        mod_name = mod_path.stem
        return mod_name

    # We are here if our parent directory is not an immediate root and we need to find one ..
    for root in root_list:
        try:
            root_idx = parts.index(root)
        except ValueError:
            pass
        else:
            # .. we have a match, i.e. we matched a specific root ..
            break

    # .. if there is no root, it means that we have no choice but to assume ..
    # .. that the name of the module is the same as its file ..
    if not root_idx:
        mod_name = mod_path.stem

    # .. otherwise, we can make use of the root found above ..
    else:

        # .. the first element is the file name so we need to remove its extension ..
        mod_file = parts[0]
        mod_file = Path(mod_file)
        mod_file_name = mod_file.stem

        # .. get the rest of the module's path, from right above its name (hence we start from 1) until the root ..
        mod_name_parts = parts[1:root_idx]

        # .. we have the names and we can reverse them back so they run from top to bottom again ..
        mod_name_parts = list(reversed(mod_name_parts))

        # .. we can append the final file name now unless it is __init__.py ..
        # .. which we can ignore because Python recognizes it implicitly ..
        if mod_file_name != '__init__':
            mod_name_parts.append(mod_file_name)

        # .. and this gives us the full module name ..
        mod_name = '.'.join(mod_name_parts)

    # .. we are ready to return the name to our caller ..
    return mod_name

# ################################################################################################################################

def import_module_by_path(path:'str') -> 'ModuleInfo | None':

    # Local aliases
    mod_path = Path(path)

    # .. turn the path into its corresponding module name ..
    mod_name = get_module_name_by_path(mod_path)

    # .. we have both the name of a module and its path so we can import it now ..
    if spec := spec_from_file_location(mod_name, path):
        module = module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module) # type: ignore

        # .. build an object encapsulating what we know about the module
        out = ModuleInfo()
        out.name = mod_name
        out.path = mod_path
        out.module = module

        # .. finally, we can return it to our caller.
        return out

# ################################################################################################################################
# ################################################################################################################################
