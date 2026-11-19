# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import os
from dataclasses import dataclass
from logging import getLogger

# Zato
from zato.common.typing_ import dict_, list_, set_
from zato.common.util.python_ import get_module_name_by_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

statementlist  = list_[ast.stmt]
importnodelist = list_['ast.Import | ast.ImportFrom']
strsetdict_    = dict_[str, set_[str]]
strintdict     = dict_[str, int]
strlistlist    = list_[list_[str]]
modulefiledict = dict_[str, 'ModuleFile']
nodetypedict   = dict_[type, 'any_']

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Python_Suffix   = '.py'
    Package_Init    = '__init__'
    Cache_Directory = '__pycache__'
    Type_Checking   = 'TYPE_CHECKING'
    Star            = '*'
    Name_Separator  = '.'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ModuleFile:

    # The real path of the file
    path: 'str'

    # Dotted names relative to each root that contains the file, the first one is its primary name
    root_names: 'strlist'

    # Every name the file can be imported by, the primary one first
    names: 'strlist'

    # Whether the file is the __init__.py of a package
    is_package: 'bool'

# ################################################################################################################################
# ################################################################################################################################

def _is_false_constant(test:'any_') -> 'bool':
    out = not test.value
    return out

def _is_type_checking_name(test:'any_') -> 'bool':
    out = test.id == ModuleCtx.Type_Checking
    return out

def _is_type_checking_attribute(test:'any_') -> 'bool':
    out = test.attr == ModuleCtx.Type_Checking
    return out

# The tests of an if statement whose body never executes - `if 0:`, `if False:` and `if TYPE_CHECKING:`
_never_executed_tests:'nodetypedict' = {
    ast.Constant:  _is_false_constant,
    ast.Name:      _is_type_checking_name,
    ast.Attribute: _is_type_checking_attribute,
}

# ################################################################################################################################

def _is_never_executed(test:'ast.expr') -> 'bool':

    if is_never_executed := _never_executed_tests.get(type(test)):
        out = is_never_executed(test)
    else:
        out = False

    return out

# ################################################################################################################################

def _get_if_children(statement:'any_') -> 'statementlist':

    # The body of a block that never executes contributes no imports, while its else branch does ..
    if _is_never_executed(statement.test):
        out = statement.orelse

    # .. otherwise, both branches may execute.
    else:
        out = statement.body + statement.orelse

    return out

def _get_try_children(statement:'any_') -> 'statementlist':

    out = statement.body + statement.orelse + statement.finalbody

    for handler in statement.handlers:
        out = out + handler.body

    return out

def _get_loop_children(statement:'any_') -> 'statementlist':
    out = statement.body + statement.orelse
    return out

def _get_body(statement:'any_') -> 'statementlist':
    out = statement.body
    return out

# The statements whose nested blocks execute when a module is imported, function bodies are not among them
_child_statements:'nodetypedict' = {
    ast.If:       _get_if_children,
    ast.Try:      _get_try_children,
    ast.TryStar:  _get_try_children,
    ast.For:      _get_loop_children,
    ast.While:    _get_loop_children,
    ast.With:     _get_body,
    ast.ClassDef: _get_body,
}

# ################################################################################################################################

def _collect_import_nodes(statements:'statementlist') -> 'importnodelist':
    """ Returns every import statement that executes when a module with the given top-level statements is imported.
    """
    out:'importnodelist' = []
    pending:'statementlist' = []
    pending.extend(statements)

    while pending:
        statement = pending.pop()

        # An import statement is what we are looking for ..
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            out.append(statement)

        # .. while a block may contain more of them.
        elif get_children := _child_statements.get(type(statement)):
            children = get_children(statement)
            pending.extend(children)

    return out

# ################################################################################################################################

def _get_root_name(path:'str', root:'str') -> 'str':
    """ Returns the dotted name a file is imported by when the root is in sys.path, or an empty string if it cannot be.
    """
    relative_path = os.path.relpath(path, root)
    parts = relative_path.split(os.sep)

    # The file's name becomes the last part of the module's name, unless it is a package's __init__.py ..
    file_name = parts.pop()
    stem, _ = os.path.splitext(file_name)

    if stem != ModuleCtx.Package_Init:
        parts.append(stem)

    # .. a file outside the root or a directory that is not an identifier cannot be imported from the root ..
    for part in parts:
        if not part.isidentifier():
            out = ''
            break

    # .. otherwise, the parts are the name.
    else:
        out = ModuleCtx.Name_Separator.join(parts)

    return out

# ################################################################################################################################

def _add_with_parents(name:'str', out:'strset') -> 'None':
    """ Adds a module's name and the names of all of its parent packages, each of which an import executes.
    """
    parts = name.split(ModuleCtx.Name_Separator)
    parts_count = len(parts)

    for index in range(1, parts_count + 1):
        name_parts = parts[:index]
        parent_name = ModuleCtx.Name_Separator.join(name_parts)
        out.add(parent_name)

# ################################################################################################################################

def _resolve_relative(name:'str', is_package:'bool', level:'int', module:'str | None') -> 'str':
    """ Returns the absolute name that a relative import in the module of the given name refers to,
    or an empty string if the import reaches above the top-level package.
    """
    parts = name.split(ModuleCtx.Name_Separator)

    # A module that is not a package resolves relative imports against the package it is in ..
    if not is_package:
        _ = parts.pop()

    # .. each dot past the first one goes one package up ..
    levels_up = level - 1
    parts_count = len(parts)

    if levels_up >= parts_count:
        out = ''

    # .. and the module after the dots is relative to the package found.
    else:
        kept_count = parts_count - levels_up
        kept_parts = parts[:kept_count]
        out = ModuleCtx.Name_Separator.join(kept_parts)

        if module:
            out = f'{out}.{module}'

    return out

# ################################################################################################################################
# ################################################################################################################################

class _ComponentSearch:
    """ Finds the strongly connected components of a set of modules with Tarjan's algorithm,
    each component after every component it imports from.
    """

    def __init__(self, graph:'ImportGraph', nodes:'strset') -> 'None':
        self.graph = graph
        self.nodes = nodes
        self.counter = 0
        self.index_by_node:'strintdict' = {}
        self.low_link:'strintdict' = {}
        self.stack:'strlist' = []
        self.on_stack:'strset' = set()
        self.components:'strlistlist' = []

# ################################################################################################################################

    def get_components(self) -> 'strlistlist':

        for node in sorted(self.nodes):
            if node not in self.index_by_node:
                self._visit(node)

        out = self.components
        return out

# ################################################################################################################################

    def _get_dependencies(self, node:'str') -> 'strlist':

        out:'strlist' = []

        if dependencies := self.graph.imports.get(node):
            for dependency in sorted(dependencies):
                if dependency in self.nodes:
                    out.append(dependency)

        return out

# ################################################################################################################################

    def _enter(self, node:'str') -> 'None':
        self.index_by_node[node] = self.counter
        self.low_link[node] = self.counter
        self.counter += 1
        self.stack.append(node)
        self.on_stack.add(node)

# ################################################################################################################################

    def _visit(self, start:'str') -> 'None':

        # Each entry is a module with the dependencies it has yet to be checked against ..
        self._enter(start)
        work = [(start, iter(self._get_dependencies(start)))]

        while work:
            node, dependencies = work[-1]

            # .. a dependency not seen before is entered first ..
            for dependency in dependencies:
                if dependency not in self.index_by_node:
                    self._enter(dependency)
                    dependency_list = self._get_dependencies(dependency)
                    work.append((dependency, iter(dependency_list)))
                    break

                # .. one that is still on the stack belongs to the same component ..
                elif dependency in self.on_stack:
                    dependency_index = self.index_by_node[dependency]
                    self.low_link[node] = min(self.low_link[node], dependency_index)

            # .. once all of a module's dependencies are checked, its parent learns of its low link ..
            else:
                _ = work.pop()

                if work:
                    parent, _ = work[-1]
                    self.low_link[parent] = min(self.low_link[parent], self.low_link[node])

                # .. and a module that is the root of a component closes it.
                if self.low_link[node] == self.index_by_node[node]:
                    self._close_component(node)

# ################################################################################################################################

    def _close_component(self, root:'str') -> 'None':

        component:'strlist' = []

        while True:
            member = self.stack.pop()
            self.on_stack.discard(member)
            component.append(member)

            if member == root:
                break

        self.components.append(component)

# ################################################################################################################################
# ################################################################################################################################

class ImportGraph:
    """ The import dependencies between the Python files under a list of hot-deployment roots.
    """

    def __init__(self) -> 'None':
        self.files:'modulefiledict' = {}
        self.paths_by_name:'strsetdict_' = {}
        self.imports:'strsetdict_' = {}
        self.importers:'strsetdict_' = {}

# ################################################################################################################################

    @classmethod
    def build(class_, roots:'strlist') -> 'ImportGraph':
        """ Reads every Python file under the given roots and the import statements in each of them.
        The first root that contains a file gives the file its primary name.
        """
        out = class_()
        out._add_files(roots)

        for path in sorted(out.files):
            out._add_edges(path)

        return out

# ################################################################################################################################

    def _add_files(self, roots:'strlist') -> 'None':

        real_roots:'strlist' = []

        # Roots from the configuration may point to directories that do not exist ..
        for root in roots:
            if os.path.isdir(root):
                root = os.path.realpath(root)
                if root not in real_roots:
                    real_roots.append(root)

        # .. each Python file of each root that does is read ..
        for root in real_roots:
            for directory, directory_names, file_names in os.walk(root):

                if ModuleCtx.Cache_Directory in directory_names:
                    directory_names.remove(ModuleCtx.Cache_Directory)

                for file_name in sorted(file_names):
                    if file_name.endswith(ModuleCtx.Python_Suffix):
                        path = os.path.join(directory, file_name)
                        if path not in self.files:
                            self.files[path] = self._new_module_file(path, real_roots)

        # .. and the files can be found by any of their names.
        for path, module_file in self.files.items():
            for name in module_file.names:
                paths = self.paths_by_name.setdefault(name, set())
                paths.add(path)

# ################################################################################################################################

    def _new_module_file(self, path:'str', roots:'strlist') -> 'ModuleFile':

        root_names:'strlist' = []

        for root in roots:
            if name := _get_root_name(path, root):
                if name not in root_names:
                    root_names.append(name)

        # The service store names modules in its own way, which is a name the file is known by too
        names:'strlist' = []
        names.extend(root_names)

        store_name = get_module_name_by_path(path)
        if store_name not in names:
            names.append(store_name)

        file_name = os.path.basename(path)
        stem, _ = os.path.splitext(file_name)

        out = ModuleFile()
        out.path = path
        out.root_names = root_names
        out.names = names
        out.is_package = stem == ModuleCtx.Package_Init

        return out

# ################################################################################################################################

    def _add_edges(self, path:'str') -> 'None':

        module_file = self.files[path]

        # A file that cannot be parsed contributes no edges ..
        try:
            with open(path, 'rb') as source_file:
                source = source_file.read()
            tree = ast.parse(source, path)
        except (OSError, SyntaxError, ValueError) as e:
            logger.warning('Could not read the imports of `%s` -> %s', path, e)

        # .. while each name that another one imports points to the files known by that name.
        else:
            import_nodes = _collect_import_nodes(tree.body)

            for node in import_nodes:
                imported_names = self._get_imported_names(module_file, node)

                for name in imported_names:
                    if target_paths := self.paths_by_name.get(name):
                        for target_path in target_paths:
                            if target_path != path:
                                self._add_edge(path, target_path)

# ################################################################################################################################

    def _add_edge(self, importer:'str', imported:'str') -> 'None':

        imported_paths = self.imports.setdefault(importer, set())
        imported_paths.add(imported)

        importer_paths = self.importers.setdefault(imported, set())
        importer_paths.add(importer)

# ################################################################################################################################

    def _get_imported_names(self, module_file:'ModuleFile', node:'ast.Import | ast.ImportFrom') -> 'strset':

        out:'strset' = set()

        # `import a.b.c` executes a, a.b and a.b.c ..
        if isinstance(node, ast.Import):
            for alias in node.names:
                _add_with_parents(alias.name, out)

        # .. `from a.b import c` executes a and a.b, and also a.b.c if c is a module.
        else:
            from_bases = self._get_from_bases(module_file, node)

            for base in from_bases:
                _add_with_parents(base, out)

                for alias in node.names:
                    if alias.name != ModuleCtx.Star:
                        out.add(f'{base}.{alias.name}')

        return out

# ################################################################################################################################

    def _get_from_bases(self, module_file:'ModuleFile', node:'ast.ImportFrom') -> 'strlist':
        """ Returns the absolute names that the module part of a `from ... import` statement refers to.
        """
        out:'strlist' = []

        # An absolute import names its module directly ..
        if node.level == 0:
            if node.module:
                out.append(node.module)

        # .. while a relative one is resolved against the packages the importing file is in.
        else:
            for name in module_file.root_names:
                if base := _resolve_relative(name, module_file.is_package, node.level, node.module):
                    if base not in out:
                        out.append(base)

        return out

# ################################################################################################################################

    def get_module_names(self, path:'str') -> 'strlist':
        """ Returns every name the file at the given path can be imported by, the primary one first.
        """
        path = os.path.realpath(path)

        # A file outside of the roots, e.g. one extracted from an archive, is known only by its service store name
        if module_file := self.files.get(path):
            out:'strlist' = []
            out.extend(module_file.names)
        else:
            store_name = get_module_name_by_path(path)
            out = [store_name]

        return out

# ################################################################################################################################

    def get_ordered_importers(self, path:'str') -> 'strlist':
        """ Returns every file that imports the given one, directly or through other files, each one once,
        and each one after all the files it imports. The members of an import cycle follow one another in path order.
        """
        path = os.path.realpath(path)

        # Collect the importers of the file, the importers of those and so on ..
        affected:'strset' = set()
        pending:'strlist' = [path]

        while pending:
            current = pending.pop()

            if importers := self.importers.get(current):
                for importer in sorted(importers):
                    if importer not in affected:
                        affected.add(importer)
                        pending.append(importer)

        # .. order them along with the file itself, which is what they depend on ..
        nodes:'strset' = set()
        nodes.update(affected)
        nodes.add(path)

        search = _ComponentSearch(self, nodes)
        components = search.get_components()

        # .. and return all of them except for the file, which its own deployment has already reloaded.
        out:'strlist' = []

        for component in components:
            for member in sorted(component):
                if member != path:
                    out.append(member)

        return out

# ################################################################################################################################
# ################################################################################################################################
