# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast

# Zato
from zato.common.test.sql_conformance.python_ast import get_dotted_name, get_import_aliases, parse
from zato.common.test.sql_conformance.sources import get_python_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The packages of the product that make up its database layer
    Database_Packages = (
        'zato.common.audit_log',
        'zato.common.db_env',
        'zato.common.odb',
        'zato.common.pubsub.sql',
        'zato.common.rule_engine.sql',
    )

    # The method that creates an instance without running its constructor
    New_Method = '__new__'

    # The fixture of pytest that replaces attributes
    Monkeypatch_Name = 'monkeypatch'
    Setattr_Method = 'setattr'

# ################################################################################################################################
# ################################################################################################################################

def _is_database_name(name:'str') -> 'bool':
    """ Whether a dotted name is a module of the database layer of the product or a class or an attribute of one.
    """
    for package in ModuleCtx.Database_Packages:
        if name == package or name.startswith(package + '.'):
            return True

    return False

# ################################################################################################################################

def _is_database_target(node:'ast.expr', aliases:'strdict') -> 'bool':
    """ Whether an expression names a module of the database layer of the product or a class or an attribute of one.
    A name that the module does not import cannot be resolved and is not taken to be one.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out = _is_database_name(node.value)

    elif isinstance(node, ast.Name) and node.id not in aliases:
        out = False

    elif isinstance(node, (ast.Name, ast.Attribute)):
        name = get_dotted_name(node, aliases)
        out = _is_database_name(name)

    else:
        out = False

    return out

# ################################################################################################################################

def _get_constructor_skips(tree:'ast.Module', aliases:'strdict') -> 'list[int]':
    """ Returns the line of each instance of a class of the database layer that is created without its constructor.
    """
    out:'list[int]' = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue

        if node.func.attr != ModuleCtx.New_Method or not node.args:
            continue

        # Both object.__new__(class_) and class_.__new__(class_) name the class in their first argument
        if _is_database_target(node.args[0], aliases):
            out.append(node.lineno)

    return out

# ################################################################################################################################

def _get_patched_internals(tree:'ast.Module', aliases:'strdict') -> 'list[int]':
    """ Returns the line of each attribute of a module or a class of the database layer that monkeypatch replaces.
    """
    out:'list[int]' = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue

        if node.func.attr != ModuleCtx.Setattr_Method or not node.args:
            continue

        receiver = node.func.value

        if not (isinstance(receiver, ast.Name) and receiver.id == ModuleCtx.Monkeypatch_Name):
            continue

        # The target is either an object or the dotted path of an attribute
        if _is_database_target(node.args[0], aliases):
            out.append(node.lineno)

    return out

# ################################################################################################################################

def test_no_constructor_skips_or_patched_internals() -> 'None':
    """ Test code creates each instance of a class of the database layer through its constructor and never replaces
    an attribute of a module or a class of the database layer, so that every test writes through the code
    a production system writes through.
    """
    findings:'strlist' = []

    for source in get_python_files(is_production=False):
        if source.is_linked:
            continue

        tree = parse(source)
        aliases = get_import_aliases(tree, '')

        for line in _get_constructor_skips(tree, aliases):
            findings.append(f'{source.path}:{line} -> __new__')

        for line in _get_patched_internals(tree, aliases):
            findings.append(f'{source.path}:{line} -> monkeypatch.setattr')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
