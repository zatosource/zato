# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import re

# Zato
from zato.common.test.sql_conformance.python_ast import get_calls, get_dotted_name, get_import_aliases, get_package_name, parse
from zato.common.test.sql_conformance.rust_source import get_line, remove_test_modules
from zato.common.test.sql_conformance.sources import get_python_files, get_rust_files

# Local
from registry import Rust_Writer_Class, Rust_Writer_Entry, Rust_Writer_Guard, Rust_Writer_Instance, Rust_Writer_Method, \
    Rust_Writer_Path, Rust_Writer_Source, Rust_Writer_Statement_Keys, Rust_Writer_Statements_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.sql_conformance.sources import SourceFile
    from zato.common.typing_ import strlist, strset

    SourceFile = SourceFile
    strset = strset

    line_name_list = list[tuple[int, str]]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The package against which the imports of a test module are resolved, as test modules are imported
    # from their own directories, by absolute names
    Test_Package = ''

    # A statement given as a literal to a method of rusqlite that runs or prepares it
    Statement_Literal = re.compile(
        r'\.(?:execute|execute_batch|query|query_row|query_one|prepare|prepare_cached)\s*\(\s*"((?:[^"\\]|\\.)*)"')

    # A statement of the writer that a method of rusqlite prepares, by its key among the statements of the writer
    Statement_Field = re.compile(r'\.prepare(?:_cached)?\s*\(\s*&statements\.(\w+)\s*\)')

# ################################################################################################################################
# ################################################################################################################################

def _get_writer_source() -> 'SourceFile':
    """ Returns the module that builds the writer.
    """
    for source in get_python_files(is_production=True):
        if source.relative_path == Rust_Writer_Path and not source.is_linked:
            return source

    raise Exception(f'Module of the writer not found -> {Rust_Writer_Path}')

# ################################################################################################################################

def _get_rust_source() -> 'SourceFile':
    """ Returns the Rust file whose code runs the statements of the writer.
    """
    for source in get_rust_files():
        if source.relative_path == Rust_Writer_Source and not source.is_linked:
            return source

    raise Exception(f'Rust source of the writer not found -> {Rust_Writer_Source}')

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

def _get_checked_statements(tree:'ast.Module') -> 'strset':
    """ Returns the names of the statements in the list that the entry function checks against the guard.
    """
    out:'strset' = set()

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == Rust_Writer_Statements_Name:
                    if isinstance(node.value, ast.List):
                        for element in node.value.elts:
                            if isinstance(element, ast.Name):
                                out.add(element.id)

    return out

# ################################################################################################################################

def _get_given_statements(tree:'ast.Module') -> 'strset':
    """ Returns the names of the statements that the module gives the writer when it builds it.
    """
    out:'strset' = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if Rust_Writer_Class.endswith('.' + node.func.id):
                config = node.args[0]

                if isinstance(config, ast.Dict):
                    for key, value in zip(config.keys, config.values):
                        if isinstance(key, ast.Constant) and isinstance(value, ast.Name):
                            if key.value in Rust_Writer_Statement_Keys:
                                out.add(value.id)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_writer_built_only_by_its_module() -> 'None':
    """ The writer of the audit log in Rust is built only by the module that defines it, and no other module
    reaches the instance that the module built.
    """
    findings:'strlist' = []

    for is_production in (True, False):
        for source in get_python_files(is_production=is_production):
            is_writer_module = source.relative_path == Rust_Writer_Path and not source.is_linked

            for line, name in _get_reference_names(source):
                if name == Rust_Writer_Class and not is_writer_module:
                    findings.append(f'{source.path}:{line} -> {name}')

                if name == Rust_Writer_Instance:
                    findings.append(f'{source.path}:{line} -> {name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_writer_called_only_after_the_guard() -> 'None':
    """ The method of the writer that writes rows is called only by the entry function of its module,
    after the entry function checks the statements of the writer against the guard of the write path.
    """
    source = _get_writer_source()

    write_lines:'list[int]' = []
    guard_lines:'list[int]' = []
    findings:'strlist' = []

    for call in get_calls(source):

        if call.name.endswith('.' + Rust_Writer_Method):
            if call.qualname == Rust_Writer_Entry:
                write_lines.append(call.line)
            else:
                findings.append(f'{source.path}:{call.line} -> {call.qualname}')

        if call.name == Rust_Writer_Guard and call.qualname == Rust_Writer_Entry:
            guard_lines.append(call.line)

    assert not findings, '\n'.join(findings)
    assert write_lines
    assert guard_lines
    assert max(guard_lines) < min(write_lines)

# ################################################################################################################################

def test_writer_runs_only_checked_statements() -> 'None':
    """ Each statement that the module gives the writer is one that the entry function checks against the guard,
    and the Rust code of the writer runs only those statements, never a statement of its own.
    """
    tree = parse(_get_writer_source())

    checked = _get_checked_statements(tree)
    given = _get_given_statements(tree)

    assert len(given) == len(Rust_Writer_Statement_Keys)
    assert given == checked

    rust_source = _get_rust_source()
    text = remove_test_modules(rust_source.read())

    findings:'strlist' = []

    for match in ModuleCtx.Statement_Literal.finditer(text):
        line = get_line(text, match.start())
        findings.append(f'{rust_source.path}:{line} -> {match.group(1)}')

    prepared:'strset' = set()

    for match in ModuleCtx.Statement_Field.finditer(text):
        prepared.add(match.group(1))

    assert not findings, '\n'.join(findings)
    assert prepared == set(Rust_Writer_Statement_Keys)

# ################################################################################################################################
# ################################################################################################################################
