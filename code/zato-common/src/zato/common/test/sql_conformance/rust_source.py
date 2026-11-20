# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The reading of Rust sources for the static scans of SQL conformance.

# stdlib
import os
import re

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.sql_conformance.sources import source_file_list

    source_file_list = source_file_list

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The attribute of a module that only the tests compile, followed by the module
    Test_Module_Pattern = re.compile(r'#\[cfg\(test\)\]\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+\w+\s*\{')

    # A module in a file of its own that only the tests compile
    Test_Module_File = re.compile(r'#\[cfg\(test\)\]\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+(\w+)\s*;')

    # The modules whose files hold their submodules in a directory of the same name as the crate root
    Root_Modules = ('lib.rs', 'main.rs', 'mod.rs')

    # The start of a function definition
    Function_Pattern = re.compile(r'\bfn\s+(\w+)')

# ################################################################################################################################
# ################################################################################################################################

def _find_closing_brace(text:'str', opening_index:'int') -> 'int':
    """ Returns the index of the brace that closes the one at the given index.
    """
    depth = 0

    for index in range(opening_index, len(text)):
        character = text[index]

        if character == '{':
            depth += 1

        elif character == '}':
            depth -= 1
            if depth == 0:
                return index

    raise Exception(f'No closing brace for the one at {opening_index}')

# ################################################################################################################################

def remove_test_modules(text:'str') -> 'str':
    """ Returns a Rust source with each module that only the tests compile replaced by blank lines,
    so that the line numbers of the rest of the source remain the same.
    """
    out = text

    while match := ModuleCtx.Test_Module_Pattern.search(out):
        opening_index = match.end() - 1
        closing_index = _find_closing_brace(out, opening_index)

        removed = out[match.start():closing_index + 1]
        blank_lines = '\n' * removed.count('\n')

        out = out[:match.start()] + blank_lines + out[closing_index + 1:]

    return out

# ################################################################################################################################

def get_test_module_paths(sources:'source_file_list') -> 'set[str]':
    """ Returns the path of each file that holds a module only the tests compile.
    """
    out:'set[str]' = set()

    for source in sources:
        text = source.read()
        directory, file_name = os.path.split(source.path)

        if file_name in ModuleCtx.Root_Modules:
            module_dir = directory
        else:
            module_dir = os.path.join(directory, file_name.removesuffix('.rs'))

        for match in ModuleCtx.Test_Module_File.finditer(text):
            module_name = match.group(1)
            out.add(os.path.join(module_dir, f'{module_name}.rs'))
            out.add(os.path.join(module_dir, module_name, 'mod.rs'))

    return out

# ################################################################################################################################

def get_enclosing_function(text:'str', index:'int') -> 'str':
    """ Returns the name of the last function whose definition starts before the given index.
    """
    out = ''

    for match in ModuleCtx.Function_Pattern.finditer(text, 0, index):
        out = match.group(1)

    return out

# ################################################################################################################################

def get_line(text:'str', index:'int') -> 'int':
    """ Returns the line number of the given index.
    """
    out = text.count('\n', 0, index) + 1
    return out

# ################################################################################################################################
# ################################################################################################################################
