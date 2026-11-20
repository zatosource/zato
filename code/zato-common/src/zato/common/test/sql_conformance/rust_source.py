# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The reading of Rust sources for the static scans of SQL conformance.

# stdlib
import os
import re
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.sql_conformance.sources import source_file_list
    from zato.common.typing_ import strlist, strnone, strstrdict

    source_file_list = source_file_list

# ################################################################################################################################
# ################################################################################################################################

concat_constant_list = list['ConcatConstant']
strmatch             = re.Match[str]

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

    # A macro without arguments whose expansion is one string literal
    String_Macro = re.compile(r'macro_rules!\s*(\w+)\s*\{\s*\(\s*\)\s*=>\s*\{\s*"((?:[^"\\]|\\[\s\S])*)"\s*\}\s*;?\s*\}')

    # A string constant whose value concat! assembles, up to the opening parenthesis of its arguments
    Concat_Constant = re.compile(r'\bconst\s+\w+\s*:\s*&(?:\'static\s+)?str\s*=\s*concat!\s*\(')

    # One argument of concat!, a string literal or a macro without arguments, followed by what separates it from the next
    Concat_Argument = re.compile(r'\s*(?:"((?:[^"\\]|\\[\s\S])*)"|(\w+)!\s*\(\s*\))\s*([,)])')

    # The end of the arguments of concat! after a trailing comma
    Concat_End = re.compile(r'\s*\)')

    # A line continuation of a string literal, which ends the line and removes the leading whitespace of the next one
    String_Continuation = re.compile(r'\\\n\s*')

    # The escapes of a string literal and the characters they stand for
    String_Escapes = {
        r'\"': '"',
        r'\\': '\\',
        r'\n': '\n',
        r'\t': '\t',
    }

    String_Escape = re.compile(r'\\["\\nt]')

# ################################################################################################################################
# ################################################################################################################################

class ConcatConstant(NamedTuple):
    """ A string constant that concat! assembles. Its value is None if an argument of concat! is neither
    a string literal nor a macro of the same source whose expansion is a string literal.
    """
    index: int
    value: 'strnone'

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

def _replace_escape(match:'strmatch') -> 'str':
    escape = match.group(0)

    out = ModuleCtx.String_Escapes[escape]
    return out

# ################################################################################################################################

def decode_string_literal(literal:'str') -> 'str':
    """ Returns the value of the content of a Rust string literal, with its line continuations and escapes resolved.
    """
    out = ModuleCtx.String_Continuation.sub('', literal)
    out = ModuleCtx.String_Escape.sub(_replace_escape, out)

    return out

# ################################################################################################################################

def get_string_macros(text:'str') -> 'strstrdict':
    """ Returns the value of each macro of a Rust source whose expansion is one string literal, by the name of the macro.
    """
    out:'strstrdict' = {}

    for match in ModuleCtx.String_Macro.finditer(text):
        name = match.group(1)
        literal = match.group(2)
        out[name] = decode_string_literal(literal)

    return out

# ################################################################################################################################

def _assemble_concat(text:'str', index:'int', string_macros:'strstrdict') -> 'strnone':
    """ Returns the value that concat! assembles from the arguments that begin at the given index,
    or None if an argument cannot be read.
    """
    parts:'strlist' = []

    while True:

        # Each argument is a string literal or a macro whose expansion is known ..
        match = ModuleCtx.Concat_Argument.match(text, index)

        if not match:
            return None

        literal, macro_name, separator = match.groups()

        if macro_name:
            if macro_name not in string_macros:
                return None
            parts.append(string_macros[macro_name])
        else:
            value = decode_string_literal(literal)
            parts.append(value)

        index = match.end()

        # .. the arguments end with the closing parenthesis ..
        if separator == ')':
            break

        # .. which may follow a trailing comma.
        if end_match := ModuleCtx.Concat_End.match(text, index):
            index = end_match.end()
            break

    out = ''.join(parts)
    return out

# ################################################################################################################################

def get_concat_constants(text:'str') -> 'concat_constant_list':
    """ Returns each string constant of a Rust source whose value concat! assembles, with the value assembled
    from string literals and from the macros of the same source whose expansion is a string literal.
    """
    string_macros = get_string_macros(text)
    out:'concat_constant_list' = []

    for match in ModuleCtx.Concat_Constant.finditer(text):
        value = _assemble_concat(text, match.end(), string_macros)

        constant = ConcatConstant(match.start(), value)
        out.append(constant)

    return out

# ################################################################################################################################
# ################################################################################################################################
