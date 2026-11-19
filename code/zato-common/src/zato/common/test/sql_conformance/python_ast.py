# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The parsing of Python sources for the static scans of SQL conformance. A source is parsed, never imported or run.

# stdlib
import ast
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.sql_conformance.sources import SourceFile
    from zato.common.typing_ import strdict, strlist

    SourceFile = SourceFile

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Package_Module_Suffix = '/__init__.py'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CallSite:

    # The file the call is in
    source: 'SourceFile'

    # The line of the call
    line: int

    # The qualified name of the function or class the call is in, empty at the level of the module
    qualname: str

    # The dotted name of what is called, with the names that the module imported resolved to their full names
    name: str

    # The node of the call
    node: ast.Call

call_site_list = list[CallSite]

@dataclass(init=False)
class NameReference:

    # The file the reference is in
    source: 'SourceFile'

    # The line of the reference
    line: int

    # The qualified name of the function or class the reference is in, empty at the level of the module
    qualname: str

    # The dotted name referred to, with the names that the module imported resolved to their full names
    name: str

name_reference_list = list[NameReference]

# ################################################################################################################################
# ################################################################################################################################

def get_import_aliases(tree:'ast.Module', package_name:'str') -> 'strdict':
    """ Returns the full dotted name of each name that a module imports, by the name under which the module uses it.
    A relative import is resolved against the package of the module.
    """
    out:'strdict' = {}
    package_parts = package_name.split('.')

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    out[alias.asname] = alias.name
                else:
                    top_level_name, _, _ = alias.name.partition('.')
                    out[top_level_name] = top_level_name

        elif isinstance(node, ast.ImportFrom):

            # Each dot of a relative import beyond the first one ascends one package
            if node.level:
                base_parts = package_parts[:len(package_parts) - node.level + 1]
                if node.module:
                    base_parts.append(node.module)
                module = '.'.join(base_parts)
            else:
                module = node.module

            if module:
                for alias in node.names:
                    if alias.asname:
                        local_name = alias.asname
                    else:
                        local_name = alias.name
                    out[local_name] = f'{module}.{alias.name}'

    return out

# ################################################################################################################################

def get_dotted_name(node:'ast.expr', aliases:'strdict') -> 'str':
    """ Returns the dotted name of a name or of a chain of attributes, with its first part resolved through the imports,
    or an empty string for any other expression.
    """
    parts:'strlist' = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if isinstance(node, ast.Name):
        root = aliases.get(node.id, node.id)
        parts.append(root)
        parts.reverse()
        out = '.'.join(parts)
    else:
        out = ''

    return out

# ################################################################################################################################

class _CallCollector(ast.NodeVisitor):
    """ Collects each call of a module with the qualified name of the function or class it is in.
    """
    def __init__(self, source:'SourceFile', aliases:'strdict') -> 'None':
        self.source = source
        self.aliases = aliases
        self.scopes:'strlist' = []
        self.calls:'call_site_list' = []

    def _visit_scope(self, node:'ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef') -> 'None':
        self.scopes.append(node.name)
        self.generic_visit(node)
        _ = self.scopes.pop()

    visit_FunctionDef = _visit_scope
    visit_AsyncFunctionDef = _visit_scope
    visit_ClassDef = _visit_scope

    def visit_Call(self, node:'ast.Call') -> 'None':
        item = CallSite()
        item.source = self.source
        item.line = node.lineno
        item.qualname = '.'.join(self.scopes)
        item.name = get_dotted_name(node.func, self.aliases)
        item.node = node
        self.calls.append(item)

        self.generic_visit(node)

# ################################################################################################################################

class _ReferenceCollector(ast.NodeVisitor):
    """ Collects each name and each chain of attributes of a module with the qualified name of the function or class it is in.
    """
    def __init__(self, source:'SourceFile', aliases:'strdict') -> 'None':
        self.source = source
        self.aliases = aliases
        self.scopes:'strlist' = []
        self.references:'name_reference_list' = []

    def _visit_scope(self, node:'ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef') -> 'None':
        self.scopes.append(node.name)
        self.generic_visit(node)
        _ = self.scopes.pop()

    visit_FunctionDef = _visit_scope
    visit_AsyncFunctionDef = _visit_scope
    visit_ClassDef = _visit_scope

    def _add(self, node:'ast.Name | ast.Attribute') -> 'None':
        item = NameReference()
        item.source = self.source
        item.line = node.lineno
        item.qualname = '.'.join(self.scopes)
        item.name = get_dotted_name(node, self.aliases)
        self.references.append(item)

        self.generic_visit(node)

    visit_Name = _add
    visit_Attribute = _add

# ################################################################################################################################

def parse(source:'SourceFile') -> 'ast.Module':
    """ Returns the syntax tree of a source file.
    """
    text = source.read()
    out = ast.parse(text, filename=source.path)
    return out

# ################################################################################################################################

def get_calls(source:'SourceFile') -> 'call_site_list':
    """ Returns each call in a source file.
    """
    tree = parse(source)
    aliases = get_import_aliases(tree, get_package_name(source))

    collector = _CallCollector(source, aliases)
    collector.visit(tree)

    out = collector.calls
    return out

# ################################################################################################################################

def get_references(source:'SourceFile') -> 'name_reference_list':
    """ Returns each name and each chain of attributes in a source file, a chain together with each shorter chain within it.
    """
    tree = parse(source)
    aliases = get_import_aliases(tree, get_package_name(source))

    collector = _ReferenceCollector(source, aliases)
    collector.visit(tree)

    out = collector.references
    return out

# ################################################################################################################################

def get_module_name(source:'SourceFile') -> 'str':
    """ Returns the dotted name of the module of a production source file, from the directory under its source root.
    """
    relative_path = source.path.rsplit('/src/', 1)[1]
    relative_path = relative_path.removesuffix('.py')
    relative_path = relative_path.removesuffix('/__init__')

    out = relative_path.replace('/', '.')
    return out

# ################################################################################################################################

def get_package_name(source:'SourceFile') -> 'str':
    """ Returns the dotted name of the package that a production source file belongs to, against which its relative
    imports are resolved - the module itself for the __init__ module of a package.
    """
    out = get_module_name(source)

    if not source.path.endswith(ModuleCtx.Package_Module_Suffix):
        out = out.rpartition('.')[0]

    return out

# ################################################################################################################################
# ################################################################################################################################
