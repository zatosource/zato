# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Zato
from zato.common.test.durability.python_ast import get_calls, get_module_name
from zato.common.test.durability.rust_source import get_enclosing_function, get_line, remove_test_modules
from zato.common.test.durability.sources import get_python_files, get_rust_files

# Local
from registry import Customer_Engine_Sites, Engine_Constructors, ModuleCtx as RegistryModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The opening of a SQLite file by rusqlite
    Rust_SQLite_Open = re.compile(r'\bConnection::open\w*\s*\(')

    # The connection of tokio-postgres, in a module that uses it
    Rust_PostgreSQL_Crate = 'tokio_postgres'
    Rust_PostgreSQL_Connect = re.compile(r'\.connect\s*\(')

    # The Rust functions that may open a database, each by its file and its name - the two that open the SQLite file
    # of the active-standby node with its settings and the probe of the PostgreSQL primary, which only reads.
    Rust_Engine_Functions = RegistryModuleCtx.Rust_Setting_Functions + (
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

        if module_name == RegistryModuleCtx.Engine_Factory_Module:
            continue

        for call in get_calls(source):
            if call.name in Engine_Constructors:
                site = (module_name, call.qualname)
                if site not in Customer_Engine_Sites:
                    findings.append(f'{source.path}:{call.line} -> {module_name} {call.qualname} {call.name}')

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
    with its settings and in the probe of the PostgreSQL primary.
    """
    findings:'strlist' = []

    for source in get_rust_files():
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
# ################################################################################################################################
