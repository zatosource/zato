# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import re

# Zato
from zato.common.test.sql_conformance.python_ast import get_calls, get_dotted_name, get_import_aliases, get_module_name, parse
from zato.common.test.sql_conformance.rust_source import get_enclosing_function, get_line, get_test_module_paths, \
     remove_test_modules
from zato.common.test.sql_conformance.sources import get_python_files, get_rust_files

# Local
from registry import Customer_Engine_Sites, Engine_Constructors, External_Database_Tests, ModuleCtx as RegistryModuleCtx, \
    Rust_Writers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict, strtuple

    strstrdict = strstrdict
    strtuple = strtuple

    strtuple_list  = list[strtuple]
    strtuple_tuple = tuple[strtuple, ...]

# ################################################################################################################################
# ################################################################################################################################

def _get_rust_handle_functions() -> 'strtuple_tuple':
    """ Returns the function through which each Rust writer opens its connection over the handle of the driver,
    each function once.
    """
    out:'strtuple_list' = []

    for writer in Rust_Writers:
        if writer.handle_function not in out:
            out.append(writer.handle_function)

    return tuple(out)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The opening of a SQLite file, or of a connection over the handle of another library, by rusqlite
    Rust_SQLite_Open = re.compile(r'\bConnection::(?:open|from_handle)\w*\s*\(')

    # The functions of SQLAlchemy that build an engine, which the tests leave to the engine factory
    Test_Engine_Constructors = frozenset({
        'sqlalchemy.create_engine',
        'sqlalchemy.engine.create_engine',
        'sqlalchemy.ext.asyncio.create_async_engine',
    })

    # The connection of tokio-postgres, in a module that uses it, other than a call of a method of the same type
    Rust_PostgreSQL_Crate = 'tokio_postgres'
    Rust_PostgreSQL_Connect = re.compile(r'(?<!\bself)\.connect\s*\(')

    # The Rust functions that may open a database, each by its file and its name - the ones that open a connection
    # over the handle of the SQLite driver of Python for the Rust writers, and the probe of the PostgreSQL primary,
    # which only reads.
    Rust_Engine_Functions = _get_rust_handle_functions() + (
        ('code/zato-rust/zato_ha_core/src/postgresql.rs', 'connect'),
    )

    # A call of a function, other than its definition, by the name of the function
    Rust_Call_Pattern = r'(?<!\bfn )\b{}\s*\('

# ################################################################################################################################
# ################################################################################################################################

def test_python_engines_from_the_factory() -> 'None':
    """ Every engine and every connection of a database in production code is built by the engine factory,
    apart from the connections to the databases of the customers.
    """
    findings:'strlist' = []

    for source in get_python_files(is_production=True):
        module_name = get_module_name(source)

        if module_name in RegistryModuleCtx.Engine_Factory_Modules:
            continue

        for call in get_calls(source):
            if call.name in Engine_Constructors:
                site = (module_name, call.qualname)
                if site not in Customer_Engine_Sites:
                    findings.append(f'{source.path}:{call.line} -> {module_name} {call.qualname} {call.name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_test_engines_from_the_factory() -> 'None':
    """ Every engine of a database of Zato in test code is built by the engine factory, through get_database_engine
    or new_zato_engine, so that each test runs with the settings of durability of production. The tests of external
    databases are listed.
    """
    external_paths = {relative_path for relative_path, _ in External_Database_Tests}
    findings:'strlist' = []

    for source in get_python_files(is_production=False):
        if source.is_linked or source.relative_path in external_paths:
            continue

        tree = parse(source)
        aliases = get_import_aliases(tree, '')

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = get_dotted_name(node.func, aliases)
                if name in ModuleCtx.Test_Engine_Constructors:
                    findings.append(f'{source.path}:{node.lineno} -> {name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_python_customer_sites_exist() -> 'None':
    """ Each listed function that connects to the databases of the customers still builds an engine or a connection,
    so that no entry outlives its function.
    """
    found:'set[tuple[str, str]]' = set()

    for source in get_python_files(is_production=True):
        module_name = get_module_name(source)

        for call in get_calls(source):
            if call.name in Engine_Constructors:
                site = (module_name, call.qualname)
                found.add(site)

    missing = set(Customer_Engine_Sites) - found
    assert not missing, missing

# ################################################################################################################################

def test_rust_connections_only_in_their_functions() -> 'None':
    """ The Rust code opens a database only in the functions that open the SQLite file of the active-standby node
    with its settings, in the functions that open a connection over the handle of the SQLite driver of Python
    for the Rust writers, and in the probe of the PostgreSQL primary.
    """
    findings:'strlist' = []

    sources = get_rust_files()
    test_module_paths = get_test_module_paths(sources)

    for source in sources:

        # A module in a file of its own that only the tests compile is not production code ..
        if source.path in test_module_paths:
            continue

        # .. and neither is one within a file.
        text = source.read()
        text = remove_test_modules(text)

        indexes:'list[int]' = []

        for match in ModuleCtx.Rust_SQLite_Open.finditer(text):
            indexes.append(match.start())

        if ModuleCtx.Rust_PostgreSQL_Crate in text:
            for match in ModuleCtx.Rust_PostgreSQL_Connect.finditer(text):
                indexes.append(match.start())

        for index in indexes:
            function_name = get_enclosing_function(text, index)
            site = (source.relative_path, function_name)

            if source.is_linked or site not in ModuleCtx.Rust_Engine_Functions:
                line = get_line(text, index)
                findings.append(f'{source.path}:{line} -> {function_name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_rust_writers_open_through_their_handle_function() -> 'None':
    """ The Rust code of each Rust writer calls the function registered for the writer, through which it opens
    its connection over the handle of the SQLite driver of Python.
    """
    sources:'strstrdict' = {}

    for source in get_rust_files():
        if not source.is_linked:
            sources[source.relative_path] = remove_test_modules(source.read())

    findings:'strlist' = []

    for writer in Rust_Writers:
        _, function_name = writer.handle_function
        call_pattern = re.compile(ModuleCtx.Rust_Call_Pattern.format(re.escape(function_name)))

        is_called = False

        for relative_path in writer.sources:
            if call_pattern.search(sources[relative_path]):
                is_called = True

        if not is_called:
            findings.append(f'{writer.name} -> {function_name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
