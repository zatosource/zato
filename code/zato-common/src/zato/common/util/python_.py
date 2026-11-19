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
    from importlib.abc import Loader
    from zato.common.typing_ import intnone, strlist

    Loader = Loader

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# Separates the parts of a dotted module name
_name_separator = '.'

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

def _copy_submodule_attributes(mod_name:'str', module:'module_') -> 'None':
    """ Makes the submodules already imported from a package attributes of the package's new module object.
    """
    prefix = mod_name + _name_separator
    prefix_length = len(prefix)

    for name, submodule in list(sys.modules.items()):
        if name.startswith(prefix):
            child_name = name[prefix_length:]
            if _name_separator not in child_name:
                setattr(module, child_name, submodule)

# ################################################################################################################################

def _import_parent_packages(mod_name:'str') -> 'None':
    """ Imports the packages that a module is in, from the top one down, as Python does before it imports a submodule,
    so that each package exists before the module becomes its attribute.
    """
    parts = mod_name.split(_name_separator)
    parent_parts = parts[:-1]

    for idx in range(1, len(parent_parts) + 1):
        current_parts = parent_parts[:idx]
        parent_name = _name_separator.join(current_parts)

        if parent_name not in sys.modules:

            # A module from a directory that is not in sys.path has no packages that can be imported
            try:
                _ = importlib.import_module(parent_name)
            except ModuleNotFoundError:
                return

# ################################################################################################################################

def _set_parent_attribute(mod_name:'str', module:'module_') -> 'None':
    """ Makes a module an attribute of its parent package, which is what `from package import module` reads.
    """
    parent_name, _, child_name = mod_name.rpartition(_name_separator)

    if parent_name:
        if parent := sys.modules.get(parent_name):
            setattr(parent, child_name, module)

# ################################################################################################################################

def import_module_by_path(path:'str', names:'strlist') -> 'ModuleInfo | None':
    """ Executes the module at the given path anew under the first of the names, which is its primary one,
    and puts it in effect under each of the other names that it was already imported by.
    """

    # Our response to produce
    out = None

    # Local aliases
    mod_path = Path(path)
    mod_name = names[0]

    # The packages of the module exist before it does ..
    _import_parent_packages(mod_name)

    # .. we have both the name of a module and its path so we can import it now ..
    if spec := spec_from_file_location(mod_name, path):
        module = module_from_spec(spec)
        loader = cast_('Loader', spec.loader)

        # .. these are the names that the module will be known by ..
        effective_names:'strlist' = [mod_name]

        for name in names[1:]:
            if name in sys.modules:
                effective_names.append(name)

        # .. a package that is executed anew keeps the submodules that were imported from it ..
        if spec.submodule_search_locations is not None:
            _copy_submodule_attributes(mod_name, module)

        # .. the module is registered before it executes, so that what it imports while it executes finds it ..
        for name in effective_names:
            sys.modules[name] = module

        loader.exec_module(module)

        # .. the packages that the module is in refer to the new object ..
        for name in effective_names:
            _set_parent_attribute(name, module)

        # .. and we build an object encapsulating what we know about the module.
        out = ModuleInfo()
        out.name = mod_name
        out.path = mod_path
        out.module = module

    return out

# ################################################################################################################################
# ################################################################################################################################
