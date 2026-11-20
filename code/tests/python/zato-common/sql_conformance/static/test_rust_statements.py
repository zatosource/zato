# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Zato
from zato.common.test.sql_conformance.rust_source import get_line, get_test_module_paths, remove_test_modules
from zato.common.test.sql_conformance.sources import get_rust_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.sql_conformance.sources import SourceFile
    from zato.common.typing_ import strlist

    SourceFile = SourceFile

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The crate of the active-standby node
    Crate_Source_Dir = 'code/zato-rust/zato_ha_core/src/'

    # A statement given as a literal to a method that runs it
    Statement_Call = re.compile(
        r'\.(?:execute|execute_batch|query|query_row|query_one|query_opt|prepare|prepare_cached|batch_execute|simple_query)' +
        r'\s*\(\s*"((?:[^"\\]|\\.)*)"')

    # A statement kept in a constant
    Statement_Constant = re.compile(r'\bconst\s+\w+\s*:\s*&(?:\'static\s+)?str\s*=\s*"((?:[^"\\]|\\.)*)"')

    # The first keyword of an SQL statement
    SQL_Keyword = re.compile(
        r'^\s*(insert|update|delete|replace|create|drop|alter|truncate|copy|merge|upsert|vacuum|reindex|begin|commit|end|' +
        r'rollback|savepoint|release|attach|detach|pragma|select|show|with|set|analyze|lock|do|call)\b', re.IGNORECASE)

    # The statements that the node may run - pragmas, which include the checkpoint, the write lock of the takeover
    # check that it always rolls back, and the reads of the probes
    Allowed_Statements = re.compile(r'^\s*(?:pragma\b|begin\s+immediate\b|rollback\b|select\b|show\b)', re.IGNORECASE)

# ################################################################################################################################
# ################################################################################################################################

def test_node_writes_no_rows() -> 'None':
    """ The active-standby node runs only pragmas, a write lock that it rolls back and reads, so that it never writes rows
    of the Zato database itself.
    """
    sources:'list[SourceFile]' = []

    for source in get_rust_files():
        if not source.is_linked:
            if source.relative_path.startswith(ModuleCtx.Crate_Source_Dir):
                sources.append(source)

    test_module_paths = get_test_module_paths(sources)
    findings:'strlist' = []
    statement_count = 0

    for source in sources:
        if source.path in test_module_paths:
            continue

        text = source.read()
        text = remove_test_modules(text)

        for pattern in (ModuleCtx.Statement_Call, ModuleCtx.Statement_Constant):
            for match in pattern.finditer(text):
                statement = match.group(1)

                if pattern is ModuleCtx.Statement_Constant:
                    if not ModuleCtx.SQL_Keyword.match(statement):
                        continue

                statement_count += 1

                if not ModuleCtx.Allowed_Statements.match(statement):
                    line = get_line(text, match.start())
                    findings.append(f'{source.path}:{line} -> {statement}')

    assert statement_count
    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
