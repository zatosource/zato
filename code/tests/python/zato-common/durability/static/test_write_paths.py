# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast

# Zato
from zato.common.test.durability.linked import get_linked_entries, ModuleCtx as LinkedModuleCtx
from zato.common.test.durability.python_ast import get_calls, get_dotted_name, get_import_aliases, get_module_name, \
    get_package_name, get_references, parse
from zato.common.test.durability.sources import get_python_files, get_source_files
from zato.common.typing_ import cast_

# Local
from registry import Audit_Log_Schema_Path, Audit_Tables_Name, Audit_Tables_Not_Guarded, Mechanism_Functions, \
    Mechanism_Prefix, Write_Path_Markers, Write_Path_Module, Write_Path_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.durability.sources import SourceFile
    from zato.common.typing_ import anylist, strlist

    SourceFile = SourceFile

    site_mechanisms = dict[tuple[str, str], str]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The constructor of an SQLAlchemy table, whose first argument is the name of the table
    Table_Constructors = ('sqlalchemy.Table', 'sqlalchemy.schema.Table', 'sqlalchemy.sql.schema.Table')

# ################################################################################################################################
# ################################################################################################################################

def _get_mechanism_functions() -> 'site_mechanisms':
    """ Returns the mechanism of each function that runs one, of this installation and of the linked repositories.
    """
    entries:'anylist' = list(Mechanism_Functions)
    entries.extend(get_linked_entries(LinkedModuleCtx.Mechanism_Functions))

    out:'site_mechanisms' = {}

    for module_name, qualname, mechanism in entries:
        out[module_name, qualname] = mechanism

    return out

# ################################################################################################################################

def _get_mechanism(call:'ast.Call', aliases:'dict[str, str]') -> 'str':
    """ Returns the member of Mechanism that a call marks its work with, or an empty name if the call passes on
    a mechanism it received.
    """
    name = get_dotted_name(call.args[0], aliases)

    if name.startswith(Mechanism_Prefix):
        out = name.removeprefix(Mechanism_Prefix)
    else:
        out = ''

    return out

# ################################################################################################################################

def _get_production_sources() -> 'list[SourceFile]':
    out:'list[SourceFile]' = []

    for source in get_python_files(is_production=True):
        if get_module_name(source) != Write_Path_Module:
            out.append(source)

    return out

# ################################################################################################################################

def test_marker_only_in_mechanism_functions() -> 'None':
    """ Only the functions that run a mechanism mark their work as that of one, each with its own mechanism, so that
    no other production code obtains the right to write to the Zato database by marking its work on its own.
    """
    mechanism_functions = _get_mechanism_functions()
    findings:'strlist' = []

    for source in _get_production_sources():
        module_name = get_module_name(source)
        tree = parse(source)
        aliases = get_import_aliases(tree, get_package_name(source))

        # Each reference to a marker is within a function that runs a mechanism ..
        for reference in get_references(source):
            if reference.name in Write_Path_Markers:
                site = (module_name, reference.qualname)
                if site not in mechanism_functions:
                    findings.append(f'{source.path}:{reference.line} -> {module_name} {reference.qualname}')

        # .. which marks its work with its own mechanism.
        for call in get_calls(source):
            if call.name in Write_Path_Markers:
                site = (module_name, call.qualname)
                if site in mechanism_functions:
                    mechanism = _get_mechanism(call.node, aliases)
                    expected = mechanism_functions[site]
                    if mechanism != expected:
                        findings.append(f'{source.path}:{call.line} -> {call.qualname} `{mechanism}` != `{expected}`')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_mechanism_functions_exist() -> 'None':
    """ Each listed function still marks its work, so that no entry outlives its function.
    """
    found:'set[tuple[str, str]]' = set()

    for source in _get_production_sources():
        module_name = get_module_name(source)

        for reference in get_references(source):
            if reference.name in Write_Path_Markers:
                site = (module_name, reference.qualname)
                found.add(site)

    missing = set(_get_mechanism_functions()) - found
    assert not missing, missing

# ################################################################################################################################

def _get_source(relative_path:'str') -> 'SourceFile':
    for source in get_source_files():
        if not source.is_linked:
            if source.relative_path == relative_path:
                return source

    raise KeyError(relative_path)

# ################################################################################################################################

def _get_schema_tables() -> 'set[str]':
    """ Returns the name of each table of the schema of the audit log.
    """
    source = _get_source(Audit_Log_Schema_Path)
    out:'set[str]' = set()

    for call in get_calls(source):
        if call.name in ModuleCtx.Table_Constructors:
            first_argument = call.node.args[0]
            if isinstance(first_argument, ast.Constant):
                table_name = cast_('str', first_argument.value)
                out.add(table_name)

    return out

# ################################################################################################################################

def _get_guarded_tables() -> 'set[str]':
    """ Returns the tables of the audit log that the write path guards, as its source lists them.
    """
    source = _get_source(Write_Path_Path)
    tree = parse(source)

    out:'set[str]' = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == Audit_Tables_Name:
                    for item in ast.walk(node.value):
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            out.add(item.value)

    return out

# ################################################################################################################################

def test_audit_tables_of_the_guard() -> 'None':
    """ The write path guards every table of the audit log but the alerts, so that a new table of the audit log
    receives the protection at the time it is created.
    """
    schema_tables = _get_schema_tables()
    expected = schema_tables - set(Audit_Tables_Not_Guarded)

    assert schema_tables
    assert _get_guarded_tables() == expected

# ################################################################################################################################
# ################################################################################################################################
