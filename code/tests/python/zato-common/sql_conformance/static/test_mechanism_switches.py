# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast

# Zato
from zato.common.test.sql_conformance.python_ast import get_module_name, get_references, parse
from zato.common.test.sql_conformance.sources import get_python_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The attributes and parameters that hold a mechanism of the write path, which production code never finds absent
    Mechanism_Names = frozenset({'audit_log', 'commit_queue', 'guard', 'writer'})

    # The packages of the write path, in which a mechanism is never tested for its presence either
    Write_Path_Packages = (
        'zato.common.audit_log.',
        'zato.common.db_env.',
        'zato.common.pubsub.',
        'zato.server.base.parallel.',
    )

    # The prefix of the environment variables that only the drivers of the tests read
    Test_Variable_Prefix = 'Zato_Test_'

    # The modules of the write path whose behavior no environment variable changes
    Modules_Without_Environment = (
        'zato.common.db_env.connection',
        'zato.common.db_env.commit_queue',
        'zato.common.sqlite_connection',
        'zato.common.pubsub.sql.generation',
    )

    # The names through which a module reads its environment
    Environment_Readers = frozenset({'os.environ', 'os.getenv', 'os.environb', 'os.getenvb'})

# ################################################################################################################################
# ################################################################################################################################

def _get_terminal_name(node:'ast.expr') -> 'str':
    """ Returns the name of a variable or the last attribute of a chain, or an empty string for any other expression.
    """
    if isinstance(node, ast.Name):
        out = node.id
    elif isinstance(node, ast.Attribute):
        out = node.attr
    else:
        out = ''

    return out

# ################################################################################################################################

def _is_none(node:'ast.expr') -> 'bool':
    out = isinstance(node, ast.Constant) and node.value is None
    return out

# ################################################################################################################################

def _is_in_write_path(module_name:'str') -> 'bool':
    out = module_name.startswith(ModuleCtx.Write_Path_Packages)
    return out

# ################################################################################################################################

def _get_presence_tests(tree:'ast.Module') -> 'list[ast.expr]':
    """ Returns each expression that a condition tests for truth, with a negation removed.
    """
    out:'list[ast.expr]' = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp, ast.While, ast.Assert)):
            out.append(node.test)
        elif isinstance(node, ast.BoolOp):
            out.extend(node.values)

    for index, item in enumerate(out):
        if isinstance(item, ast.UnaryOp) and isinstance(item.op, ast.Not):
            out[index] = item.operand

    return out

# ################################################################################################################################

def test_no_mechanism_compared_with_none() -> 'None':
    """ No production code compares a mechanism of the write path with None, and no code of the write path tests one
    for its presence, so that no branch runs a write without its mechanism.
    """
    findings:'strlist' = []

    for source in get_python_files(is_production=True):
        module_name = get_module_name(source)
        tree = parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                operands = [node.left, *node.comparators]
                if any(_is_none(item) for item in operands):
                    for item in operands:
                        if _get_terminal_name(item) in ModuleCtx.Mechanism_Names:
                            findings.append(f'{source.path}:{node.lineno} -> {ast.unparse(node)}')

        if _is_in_write_path(module_name):
            for item in _get_presence_tests(tree):
                if _get_terminal_name(item) in ModuleCtx.Mechanism_Names:
                    findings.append(f'{source.path}:{item.lineno} -> {ast.unparse(item)}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_no_test_variables_in_production() -> 'None':
    """ No production code reads an environment variable that only the drivers of the tests set.
    """
    findings:'strlist' = []

    for source in get_python_files(is_production=True):
        tree = parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value.startswith(ModuleCtx.Test_Variable_Prefix):
                    findings.append(f'{source.path}:{node.lineno} -> {node.value}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_no_environment_in_write_path_modules() -> 'None':
    """ The modules of the connections, of the group commit and of the generation fence
    read no environment variable, so that nothing outside the code changes how a write becomes durable.
    """
    findings:'strlist' = []

    for source in get_python_files(is_production=True):
        module_name = get_module_name(source)

        if module_name in ModuleCtx.Modules_Without_Environment:
            for reference in get_references(source):
                if reference.name in ModuleCtx.Environment_Readers:
                    findings.append(f'{source.path}:{reference.line} -> {reference.name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
