# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import re

# pytest
import pytest

# Zato
from zato.common.test.sql_conformance.python_ast import get_calls, get_dotted_name, get_import_aliases, get_package_name, parse
from zato.common.test.sql_conformance.rust_source import get_line, remove_test_modules
from zato.common.test.sql_conformance.sources import get_python_files, get_rust_files

# Local
from registry import Rust_Writer_Guard, Rust_Writers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from registry import RustWriter
    from zato.common.test.sql_conformance.sources import SourceFile
    from zato.common.typing_ import strlist, strset

    RustWriter = RustWriter
    SourceFile = SourceFile
    strset = strset

    line_name_list   = list[tuple[int, str]]
    source_file_list = list[SourceFile]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The package against which the imports of a test module are resolved, as test modules are imported
    # from their own directories, by absolute names
    Test_Package = ''

    # A statement given as a literal to a method of rusqlite that runs or prepares it
    Statement_Literal = re.compile(
        r'\.(?:execute|execute_batch|query|query_row|query_one|prepare|prepare_cached)\s*\(\s*"((?:[^"\\]|\\.)*)"')

    # A statement of the writer that a method of rusqlite runs or prepares, by its key among the statements of the writer
    Statement_Field = re.compile(r'\.(?:execute_batch|prepare|prepare_cached)\s*\(\s*&(?:self\.)?statements\.(\w+)\s*\)')

# The name of each Rust writer, by which its tests are told apart
_writer_ids:'strlist' = []

for _writer in Rust_Writers:
    _writer_ids.append(_writer.name)

# ################################################################################################################################
# ################################################################################################################################

def _get_writer_source(writer:'RustWriter') -> 'SourceFile':
    """ Returns the module that builds a writer.
    """
    for source in get_python_files(is_production=True):
        if source.relative_path == writer.path and not source.is_linked:
            return source

    raise Exception(f'Module of the writer not found -> {writer.path}')

# ################################################################################################################################

def _get_rust_sources(writer:'RustWriter') -> 'source_file_list':
    """ Returns the Rust files whose code runs the statements of a writer.
    """
    out:'source_file_list' = []

    for source in get_rust_files():
        if source.relative_path in writer.sources and not source.is_linked:
            out.append(source)

    if len(out) != len(writer.sources):
        raise Exception(f'Rust sources of the writer not found -> {writer.sources}')

    return out

# ################################################################################################################################

def _get_reference_names(source:'SourceFile') -> 'line_name_list':
    """ Returns the line and the dotted name of each name and each chain of attributes in a source file,
    with the names that the file imported resolved to their full names.
    """
    tree = parse(source)

    if source.is_production:
        package_name = get_package_name(source)
    else:
        package_name = ModuleCtx.Test_Package

    aliases = get_import_aliases(tree, package_name)
    out:'line_name_list' = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Name, ast.Attribute)):
            out.append((node.lineno, get_dotted_name(node, aliases)))

    return out

# ################################################################################################################################

def _get_checked_statements(writer:'RustWriter', tree:'ast.Module') -> 'strset':
    """ Returns the names of the statements in the list that the entry function checks against the guard.
    """
    out:'strset' = set()

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == writer.statements_name:
                    if isinstance(node.value, ast.List):
                        for element in node.value.elts:
                            if isinstance(element, ast.Name):
                                out.add(element.id)

    return out

# ################################################################################################################################

def _add_given_statements(writer:'RustWriter', config:'ast.Dict', out:'strset') -> 'None':
    """ Adds the names of the statements that a configuration gives the writer under the keys of its statements,
    including those of the configurations nested in it.
    """
    for key, value in zip(config.keys, config.values):
        if isinstance(value, ast.Dict):
            _add_given_statements(writer, value, out)

        elif isinstance(key, ast.Constant) and isinstance(value, ast.Name):
            if key.value in writer.statement_keys:
                out.add(value.id)

# ################################################################################################################################

def _get_given_statements(writer:'RustWriter', tree:'ast.Module') -> 'strset':
    """ Returns the names of the statements that the module gives the writer when it builds it.
    """
    out:'strset' = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if writer.class_name.endswith('.' + node.func.id):
                config = node.args[0]

                if isinstance(config, ast.Dict):
                    _add_given_statements(writer, config, out)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('writer', Rust_Writers, ids=_writer_ids)
def test_writer_built_only_by_its_module(writer:'RustWriter') -> 'None':
    """ A Rust writer is built only by the module that defines it, and no other module reaches the instance
    that the module built.
    """
    findings:'strlist' = []

    for is_production in (True, False):
        for source in get_python_files(is_production=is_production):
            is_writer_module = source.relative_path == writer.path and not source.is_linked

            for line, name in _get_reference_names(source):
                if name == writer.class_name and not is_writer_module:
                    findings.append(f'{source.path}:{line} -> {name}')

                if name == writer.instance:
                    findings.append(f'{source.path}:{line} -> {name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

@pytest.mark.parametrize('writer', Rust_Writers, ids=_writer_ids)
def test_writer_called_only_after_the_guard(writer:'RustWriter') -> 'None':
    """ The method of a Rust writer that writes rows is called only by the entry function of its module,
    after the entry function checks the statements of the writer against the guard of the write path.
    """
    source = _get_writer_source(writer)

    write_lines:'list[int]' = []
    guard_lines:'list[int]' = []
    findings:'strlist' = []

    for call in get_calls(source):

        if call.name.endswith('.' + writer.method):
            if call.qualname == writer.entry:
                write_lines.append(call.line)
            else:
                findings.append(f'{source.path}:{call.line} -> {call.qualname}')

        if call.name == Rust_Writer_Guard and call.qualname == writer.entry:
            guard_lines.append(call.line)

    assert not findings, '\n'.join(findings)
    assert write_lines
    assert guard_lines
    assert max(guard_lines) < min(write_lines)

# ################################################################################################################################

@pytest.mark.parametrize('writer', Rust_Writers, ids=_writer_ids)
def test_writer_runs_only_checked_statements(writer:'RustWriter') -> 'None':
    """ Each statement that the module gives a Rust writer is one that the entry function checks against the guard,
    and the Rust code of the writer runs only those statements, never a statement of its own.
    """
    tree = parse(_get_writer_source(writer))

    checked = _get_checked_statements(writer, tree)
    given = _get_given_statements(writer, tree)

    assert len(given) == len(writer.statement_keys)
    assert given == checked

    findings:'strlist' = []
    prepared:'strset' = set()

    for rust_source in _get_rust_sources(writer):
        text = remove_test_modules(rust_source.read())

        for match in ModuleCtx.Statement_Literal.finditer(text):
            line = get_line(text, match.start())
            findings.append(f'{rust_source.path}:{line} -> {match.group(1)}')

        for match in ModuleCtx.Statement_Field.finditer(text):
            prepared.add(match.group(1))

    assert not findings, '\n'.join(findings)
    assert prepared == set(writer.statement_keys)

# ################################################################################################################################
# ################################################################################################################################
