# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast

# Zato
from zato.common.test.durability.python_ast import get_dotted_name, get_import_aliases, parse
from zato.common.test.durability.sources import get_python_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The top-level package of the product
    Product_Prefix = 'zato.'

    # The package of the helpers of the tests, which is not product code
    Test_Helper_Prefix = 'zato.common.test.'

    # The method that creates an instance without running its constructor
    New_Method = '__new__'

    # The base class whose __new__ creates an instance of any class it is given
    Object_Name = 'object'

    # The fixture of pytest that replaces attributes
    Monkeypatch_Name = 'monkeypatch'
    Setattr_Method = 'setattr'

# ################################################################################################################################
# ################################################################################################################################

def _is_product_name(name:'str') -> 'bool':
    out = name.startswith(ModuleCtx.Product_Prefix) and not name.startswith(ModuleCtx.Test_Helper_Prefix)
    return out

# ################################################################################################################################

def _get_local_classes(tree:'ast.Module') -> 'set[str]':
    """ Returns the name of each class that a module of the tests defines itself.
    """
    out:'set[str]' = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            out.add(node.name)

    return out

# ################################################################################################################################

def _is_product_class(node:'ast.expr', aliases:'strdict', local_classes:'set[str]') -> 'bool':
    """ Whether an expression names a class of the product, which a class that the tests define is not.
    A class given through a variable is taken to be one of the product, because it cannot be told apart.
    """
    if isinstance(node, ast.Name) and node.id in local_classes:
        out = False
    elif isinstance(node, ast.Name) and node.id not in aliases:
        out = True
    elif isinstance(node, (ast.Name, ast.Attribute)):
        name = get_dotted_name(node, aliases)
        out = _is_product_name(name)
    else:
        out = True

    return out

# ################################################################################################################################

def _get_constructor_skips(tree:'ast.Module', aliases:'strdict') -> 'list[int]':
    """ Returns the line of each instance of a class of the product that is created without its constructor.
    """
    local_classes = _get_local_classes(tree)
    out:'list[int]' = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue

        if node.func.attr != ModuleCtx.New_Method or not node.args:
            continue

        # Both object.__new__(class_) and class_.__new__(class_) name the class in their first argument
        if _is_product_class(node.args[0], aliases, local_classes):
            out.append(node.lineno)

    return out

# ################################################################################################################################

def _get_patched_internals(tree:'ast.Module', aliases:'strdict') -> 'list[int]':
    """ Returns the line of each attribute of a module or of a class of the product that monkeypatch replaces.
    """
    local_classes = _get_local_classes(tree)
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
        target = node.args[0]

        if isinstance(target, ast.Constant) and isinstance(target.value, str):
            is_product = _is_product_name(target.value)

        elif isinstance(target, (ast.Name, ast.Attribute)):
            if isinstance(target, ast.Name) and target.id in local_classes:
                is_product = False
            else:
                is_product = _is_product_name(get_dotted_name(target, aliases))

        else:
            is_product = False

        if is_product:
            out.append(node.lineno)

    return out

# ################################################################################################################################

def test_no_constructor_skips_or_patched_internals() -> 'None':
    """ Test code creates each instance of a class of the product through its constructor and never replaces
    an attribute of a module or of a class of the product, so that every test runs the code a production system runs.
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
