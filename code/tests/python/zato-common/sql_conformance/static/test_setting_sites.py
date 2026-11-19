# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import io
import re
import tokenize

# Zato
from zato.common.test.sql_conformance.rust_source import get_enclosing_function, get_line, remove_test_modules
from zato.common.test.sql_conformance.sources import get_setting_files, ModuleCtx as SourcesModuleCtx

# Local
from registry import ModuleCtx as RegistryModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.sql_conformance.sources import SourceFile
    from zato.common.typing_ import strlist

    SourceFile = SourceFile

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # A statement that sets one of the settings of durability, whatever its value
    Setting_Patterns = (
        re.compile(r'\bpragma\s+(?:\w+\.)?(?:synchronous|journal_mode)\s*=', re.IGNORECASE),
        re.compile(r'\bpragma_update\s*\([^;]*?[\'"](?:synchronous|journal_mode)[\'"]', re.IGNORECASE),
        re.compile(r'\bsynchronous_commit\s*(?:=|\bto\b)', re.IGNORECASE),
    )

    # A statement whose value is a literal word
    Literal_Value_Pattern = re.compile(r'.*?(?:=|\bto\b|[\'"]\s*,)\s*[\'"]?[A-Za-z0-9_]+\b', re.IGNORECASE)

    # The signs of a value that is formatted into a statement
    Formatted_Value_Markers = ('{', '%s', '%(', '.format(', '" +', '\' +')

# ################################################################################################################################
# ################################################################################################################################

def _get_statement(text:'str', index:'int') -> 'str':
    """ Returns the text from the given index to the end of its line.
    """
    end = text.find('\n', index)

    if end == -1:
        end = len(text)

    out = text[index:end]
    return out

# ################################################################################################################################

def _is_allowed_site(source:'SourceFile', text:'str', index:'int') -> 'bool':
    """ Returns whether a setting at the given index is in the module of the settings or in a Rust function
    that opens the SQLite file of the active-standby node.
    """
    if source.is_linked:
        return False

    if source.relative_path == RegistryModuleCtx.Setting_Module_Path:
        return True

    function_name = get_enclosing_function(text, index)

    for rust_path, rust_function in RegistryModuleCtx.Rust_Setting_Functions:
        if source.relative_path == rust_path:
            if function_name == rust_function:
                return True

    return False

# ################################################################################################################################

def _get_text(source:'SourceFile') -> 'str':
    """ Returns the text of a source, without the Rust modules that only the tests compile.
    """
    out = source.read()

    if source.path.endswith(SourcesModuleCtx.Rust_Suffix):
        out = remove_test_modules(out)

    return out

# ################################################################################################################################

def _get_string_ranges(text:'str') -> 'list[tuple[int, int]]':
    """ Returns the start and the end offset of each string literal of Python code.
    """
    out:'list[tuple[int, int]]' = []

    line_offsets = [0]
    for line in text.splitlines(keepends=True):
        line_offsets.append(line_offsets[-1] + len(line))

    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type == tokenize.STRING:
            start_line, start_column = token.start
            end_line, end_column = token.end
            start = line_offsets[start_line - 1] + start_column
            end = line_offsets[end_line - 1] + end_column
            out.append((start, end))

    return out

# ################################################################################################################################

def _get_setting_matches(source:'SourceFile', text:'str') -> 'list[re.Match[str]]':
    """ Returns each statement of a source that sets a setting of durability. In Python code, a statement
    is a string literal, so a variable whose name is that of a setting is not one.
    """
    out:'list[re.Match[str]]' = []
    is_python = source.path.endswith(SourcesModuleCtx.Python_Suffix)

    if is_python:
        string_ranges = _get_string_ranges(text)
    else:
        string_ranges = []

    for pattern in ModuleCtx.Setting_Patterns:
        for match in pattern.finditer(text):

            if is_python:
                index = match.start()
                if not any(start <= index < end for start, end in string_ranges):
                    continue

            out.append(match)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_settings_only_in_their_module() -> 'None':
    """ The settings of durability are set only in the module of the settings and in the Rust functions that open
    the SQLite file of the active-standby node, so that each database of Zato receives them from one place.
    """
    findings:'strlist' = []

    for source in get_setting_files():
        text = _get_text(source)

        for match in _get_setting_matches(source, text):
            if not _is_allowed_site(source, text, match.start()):
                line = get_line(text, match.start())
                findings.append(f'{source.path}:{line} -> {match.group(0)}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_settings_are_literal() -> 'None':
    """ Each setting of durability is given as a literal value, never as a value formatted into the statement,
    so that no configuration and no caller can change it.
    """
    findings:'strlist' = []

    for source in get_setting_files():
        text = _get_text(source)

        for match in _get_setting_matches(source, text):
            statement = _get_statement(text, match.start())

            is_formatted = False
            for marker in ModuleCtx.Formatted_Value_Markers:
                if marker in statement:
                    is_formatted = True

            is_literal = ModuleCtx.Literal_Value_Pattern.match(statement)

            if is_formatted or not is_literal:
                line = get_line(text, match.start())
                findings.append(f'{source.path}:{line} -> {statement}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
