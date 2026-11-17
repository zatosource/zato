# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The references to the functions of the write sites across production code. A method is referenced through an attribute
# of its name on any object, and a function of a module through its name in its own module, through the name under which
# another module imports it, or through an attribute of its module. A source is parsed, never imported or run.

# stdlib
import ast
from dataclasses import dataclass
from functools import cache

# Zato
from zato.common.test.durability.python_ast import get_dotted_name, get_import_aliases, get_module_name, get_package_name, \
     parse
from zato.common.test.durability.sources import get_python_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.durability.sources import SourceFile
    from zato.common.typing_ import strdict, strlist

    SourceFile = SourceFile

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The receivers through which a class refers to its own methods
    Own_Receivers = ('self', 'cls')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Reference:

    # The file of the reference and the dotted name of its module
    source: 'SourceFile'
    module_name: str

    # The qualified name of the function or class the reference is in, empty at the level of the module
    qualname: str

    # The line of the reference
    line: int

    # Whether the reference is called directly
    is_called: bool

    # The full dotted name of the call that the reference is an argument of, empty if it is not an argument of a call
    argument_of: str

    # The source of the object whose attribute the reference is, empty for a plain name
    receiver: str

reference_list = list[Reference]

# ################################################################################################################################
# ################################################################################################################################

class _ReferenceCollector(ast.NodeVisitor):
    """ Collects each name and each attribute of a module that may refer to a function, with what uses it.
    """
    def __init__(self, source:'SourceFile', tree:'ast.Module') -> 'None':
        self.source = source
        self.module_name = get_module_name(source)
        self.aliases:'strdict' = get_import_aliases(tree, get_package_name(source))
        self.scopes:'strlist' = []

        # Each name or attribute, by the name it carries, with the name it resolves to and whether it is an attribute
        self.items:'list[tuple[str, str, bool, Reference]]' = []

        self.parents:'dict[ast.AST, ast.AST]' = {}

        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                self.parents[child] = parent

    def _visit_scope(self, node:'ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef') -> 'None':
        self.scopes.append(node.name)
        self.generic_visit(node)
        _ = self.scopes.pop()

    visit_FunctionDef = _visit_scope
    visit_AsyncFunctionDef = _visit_scope
    visit_ClassDef = _visit_scope

    def _add(self, node:'ast.Name | ast.Attribute', name:'str', resolved_name:'str') -> 'None':
        item = Reference()
        item.source = self.source
        item.module_name = self.module_name
        item.qualname = '.'.join(self.scopes)
        item.line = node.lineno
        item.is_called = False
        item.argument_of = ''

        parent = self.parents[node]

        if isinstance(parent, ast.Call):
            if parent.func is node:
                item.is_called = True
            else:
                item.argument_of = get_dotted_name(parent.func, self.aliases)

        elif isinstance(parent, ast.keyword):
            call = self.parents[parent]
            if isinstance(call, ast.Call):
                item.argument_of = get_dotted_name(call.func, self.aliases)

        is_attribute = isinstance(node, ast.Attribute)

        if isinstance(node, ast.Attribute):
            item.receiver = ast.unparse(node.value)
        else:
            item.receiver = ''

        self.items.append((name, resolved_name, is_attribute, item))

    def visit_Name(self, node:'ast.Name') -> 'None':
        if node.id in self.aliases:
            resolved_name = self.aliases[node.id]
        else:
            resolved_name = f'{self.module_name}.{node.id}'
        self._add(node, node.id, resolved_name)

    def visit_Attribute(self, node:'ast.Attribute') -> 'None':
        resolved_name = get_dotted_name(node, self.aliases)
        self._add(node, node.attr, resolved_name)
        self.generic_visit(node)

# ################################################################################################################################
# ################################################################################################################################

@cache
def _get_items_by_name() -> 'dict[str, list[tuple[str, bool, Reference]]]':
    """ Returns each name and each attribute of production code with its reference, by the name it carries.
    """
    out:'dict[str, list[tuple[str, bool, Reference]]]' = {}

    for source in get_python_files(is_production=True):
        tree = parse(source)
        collector = _ReferenceCollector(source, tree)
        collector.visit(tree)

        for name, resolved_name, is_attribute, reference in collector.items:
            if name not in out:
                out[name] = []
            out[name].append((resolved_name, is_attribute, reference))

    return out

# ################################################################################################################################

def get_references(module_name:'str', qualname:'str') -> 'reference_list':
    """ Returns each reference to a function of a module, a method by its name on any object other than the instance
    or the class of another class, and a function of the module by the full dotted name it resolves to.
    """
    class_name, _, function_name = qualname.rpartition('.')
    full_name = f'{module_name}.{qualname}'
    class_prefix = f'{class_name}.'

    out:'reference_list' = []
    items_by_name = _get_items_by_name()

    if function_name not in items_by_name:
        return out

    for resolved_name, is_attribute, reference in items_by_name[function_name]:
        if class_name:
            if is_attribute:
                if reference.receiver in ModuleCtx.Own_Receivers:
                    if reference.module_name == module_name:
                        if reference.qualname.startswith(class_prefix):
                            out.append(reference)
                else:
                    out.append(reference)
        elif resolved_name == full_name:
            out.append(reference)

    return out

# ################################################################################################################################
# ################################################################################################################################
