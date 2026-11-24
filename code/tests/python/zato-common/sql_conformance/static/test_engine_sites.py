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
from registry import Customer_Engine_Sites, Engine_Constructors, External_Database_Tests, ModuleCtx as RegistryModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, strlist

    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The functions of SQLAlchemy that build an engine, which the tests leave to the engine factory
    Test_Engine_Constructors = frozenset({
        'sqlalchemy.create_engine',
        'sqlalchemy.engine.create_engine',
        'sqlalchemy.ext.asyncio.create_async_engine',
    })

    # The connection of tokio-postgres, in a module that uses it, other than a call of a method of the same type
    Rust_PostgreSQL_Crate = 'tokio_postgres'
    Rust_PostgreSQL_Connect = re.compile(r'(?<!\bself)\.connect\s*\(')

    # The Rust functions that may open a database, each by its file and its name - the probe of the PostgreSQL primary,
    # which only reads.
    Rust_Engine_Functions = (
        ('code/zato-rust/zato_ha_core/src/postgresql.rs', 'connect'),
    )

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
    or zato_database_engine, so that each test runs with the settings of durability of production. The tests of external
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
    """ The Rust code opens a database only in the probe of the PostgreSQL primary.
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

        indexes:'intlist' = []

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
# ################################################################################################################################
