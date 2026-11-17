# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import re

# Zato
from zato.common.test.durability.linked import get_linked_entries, ModuleCtx as LinkedModuleCtx
from zato.common.test.durability.python_ast import get_dotted_name, get_import_aliases, parse
from zato.common.test.durability.sources import get_python_files

# Local
from registry import Direct_SQL_Purposes, External_Database_Tests, Write_Path_Tests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.durability.sources import SourceFile
    from zato.common.typing_ import strdict, strlist

    SourceFile = SourceFile

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The package of the tests in which alone they write to the Zato database and to config.db directly
    Direct_SQL_Marker = '/zato/common/test/direct_sql/'

    # The entry points of the write path, which the tests reach only through the package of direct writes
    Write_Path_Entries = frozenset({
        'zato.common.db_env.write_path.write_path',
        'zato.common.db_env.write_path.run_in_write_path',
        'zato.common.db_env.engine.call_database',
        'zato.common.db_env.engine.execute_write',
        'zato.common.audit_log.writes.write_audit',
        'zato.common.audit_log.writes.execute_audit_write',
    })

    # The methods that build a statement which changes the rows of a table
    Table_Write_Methods = frozenset({'insert', 'update', 'delete'})

    # The methods that run a statement
    Execute_Methods = frozenset({'execute', 'executemany', 'executescript', 'exec_driver_sql'})

    # The first keyword of a statement that changes rows or the schema
    Write_Statement = re.compile(r'^\s*(insert|update|delete|replace|create|drop|alter|truncate|copy)\b', re.IGNORECASE)

    # The statements that administer the database server of a test container, which change no table of a database
    Server_Statement = re.compile(r'^\s*(create|drop|alter)\s+(role|user|extension|tablespace|database)\b', re.IGNORECASE)

    # The functions that turn a literal into a statement
    Text_Functions = frozenset({'text', 'sqlalchemy.text', 'sqlalchemy.sql.text', 'sqlalchemy.sql.expression.text'})

# ################################################################################################################################
# ################################################################################################################################

def _is_direct_sql(source:'SourceFile') -> 'bool':
    out = ModuleCtx.Direct_SQL_Marker in source.path
    return out

# ################################################################################################################################

def _get_literal(node:'ast.expr') -> 'str':
    """ Returns the constant text of a string or of the constant parts of an f-string, or an empty string.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out = node.value
    elif isinstance(node, ast.JoinedStr):
        parts:'strlist' = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                break
        out = ''.join(parts)
    else:
        out = ''

    return out

# ################################################################################################################################

def _is_write_statement(node:'ast.expr', aliases:'strdict') -> 'bool':
    """ Whether an argument of a call that runs a statement is a statement that changes rows or the schema.
    """
    if isinstance(node, ast.Call):
        if get_dotted_name(node.func, aliases) in ModuleCtx.Text_Functions:
            if node.args:
                node = node.args[0]

    literal = _get_literal(node)

    if ModuleCtx.Server_Statement.match(literal):
        out = False
    else:
        out = bool(ModuleCtx.Write_Statement.match(literal))

    return out

# ################################################################################################################################

def _get_direct_writes(tree:'ast.Module', aliases:'strdict') -> 'list[int]':
    """ Returns the line of each statement that changes rows or the schema which a module builds or runs itself.
    """
    out:'list[int]' = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        method = node.func.attr
        receiver = ast.unparse(node.func.value).lower()

        # A table's own insert, update or delete ..
        if method in ModuleCtx.Table_Write_Methods and not node.args and 'table' in receiver:
            out.append(node.lineno)

        # .. or a literal statement that a connection or a cursor runs.
        elif method in ModuleCtx.Execute_Methods and node.args:
            if _is_write_statement(node.args[0], aliases):
                out.append(node.lineno)

    return out

# ################################################################################################################################

def _get_exempt_paths(entries:'tuple[tuple[str, str], ...]') -> 'set[str]':
    out = {relative_path for relative_path, _ in entries}
    return out

# ################################################################################################################################

def test_direct_writes_only_in_direct_sql() -> 'None':
    """ Test code writes to the Zato database and to config.db directly only in the package of direct writes,
    and reaches the mechanisms of the write path only from there, so that every other test proves the path
    that a production system takes. The tests of external databases and the tests of the write path itself are listed.
    """
    external_paths = _get_exempt_paths(External_Database_Tests)
    write_path_paths = _get_exempt_paths(Write_Path_Tests)
    findings:'strlist' = []

    for source in get_python_files(is_production=False):
        if source.is_linked or _is_direct_sql(source):
            continue

        tree = parse(source)
        aliases = get_import_aliases(tree, '')

        if source.relative_path not in write_path_paths:
            for node in ast.walk(tree):
                if isinstance(node, (ast.Name, ast.Attribute)):
                    name = get_dotted_name(node, aliases)
                    if name in ModuleCtx.Write_Path_Entries:
                        findings.append(f'{source.path}:{node.lineno} -> {name}')

        if source.relative_path not in external_paths and source.relative_path not in write_path_paths:
            for line in _get_direct_writes(tree, aliases):
                findings.append(f'{source.path}:{line} -> direct write')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_direct_sql_purposes() -> 'None':
    """ Each public function of the package of direct writes carries one registered purpose, and each registered
    function still exists.
    """
    entries = list(Direct_SQL_Purposes)
    entries.extend(get_linked_entries(LinkedModuleCtx.Direct_SQL_Purposes))

    registered = {(relative_path, function_name) for relative_path, function_name, _ in entries}
    found:'set[tuple[str, str]]' = set()

    for source in get_python_files(is_production=False):
        if not _is_direct_sql(source):
            continue

        tree = parse(source)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    found.add((source.relative_path, node.name))

    assert found == registered, (found - registered, registered - found)

# ################################################################################################################################
# ################################################################################################################################
