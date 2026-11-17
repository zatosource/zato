# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The write primitives of production code, each with the function it is in and the tables it writes to when the statement
# names them. A source is parsed, never imported or run.

# stdlib
import ast
import re
from dataclasses import dataclass
from functools import cache

# Zato
from zato.common.test.durability.python_ast import get_dotted_name, get_import_aliases, get_module_name, parse
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

    # The methods of an ORM session that write, and the words of a receiver that make it a session
    Session_Methods = ('add', 'add_all', 'merge', 'delete', 'bulk_insert_mappings', 'bulk_save_objects', 'bulk_update_mappings')
    Session_Words = ('session',)

    # The commit of a session, of a connection or of a transaction, and the words of a receiver that make it one of them
    Commit_Method = 'commit'
    Commit_Words = ('session', 'conn', 'transaction')

    # The start of a transaction on an engine, and the word of a receiver that makes it an engine
    Begin_Method = 'begin'
    Begin_Words = ('engine',)

    # The methods that run a statement, and the word of a receiver that makes it a cursor of the driver
    Execute_Methods = ('execute', 'executemany')
    Cursor_Words = ('cursor',)

    # The methods that write whatever their receiver and their arguments
    Unconditional_Methods = ('exec_driver_sql', 'raw_connection', 'create_all', 'drop_all')

    # The functions that write whatever their arguments, each by its full dotted name
    Write_Functions = (
        'zato.common.db_env.pg8000_copy.copy_rows',
        'sqlite3.connect',
        'sqlite3.dbapi2.connect',
    )

    # The constructs of SQLAlchemy that build a write statement, by the last part of their names
    Construct_Names = ('insert', 'update', 'delete')

    # The first keyword of a statement that writes rows or changes the schema
    Write_Keyword = re.compile(
        r'^\s*(?:insert|update|delete|replace|upsert|merge|create|drop|alter|truncate|vacuum|reindex)\b', re.IGNORECASE)

    # The table that a statement writes to, after its keyword
    Statement_Table = re.compile(
        r'\b(?:insert\s+(?:or\s+\w+\s+)?into|replace\s+into|update(?:\s+or\s+\w+)?|delete\s+from|truncate(?:\s+table)?|'
        r'alter\s+table|drop\s+table(?:\s+if\s+exists)?|create\s+(?:unique\s+)?index(?:\s+if\s+not\s+exists)?\s+\w+\s+on|'
        r'create\s+table(?:\s+if\s+not\s+exists)?)\s+["`]?(\w+)',
        re.IGNORECASE)

    # The name of the call that defines a table and the attribute of a model class that names its table
    Table_Call = 'Table'
    Table_Name_Attribute = '__tablename__'

    # The name of the function that wraps a statement literal in SQLAlchemy
    Text_Function = 'text'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WriteSite:

    # The file the primitive is in and the dotted name of its module
    source: 'SourceFile'
    module_name: str

    # The qualified name of the function or class the primitive is in, empty at the level of the module
    qualname: str

    # The primitive, as the name of the method or of the function that writes
    primitive: str

    # The line of the primitive
    line: int

    # The tables that the statement names, empty if it names none that can be read from the source
    tables: 'strlist'

write_site_list = list[WriteSite]

# ################################################################################################################################
# ################################################################################################################################

def _get_receiver_text(call:'ast.Call') -> 'str':
    """ Returns the source of the object whose method a call invokes, in lower case.
    """
    func = call.func

    if isinstance(func, ast.Attribute):
        out = ast.unparse(func.value)
        out = out.lower()
    else:
        out = ''

    return out

# ################################################################################################################################

def _has_word(text:'str', words:'tuple[str, ...]') -> 'bool':
    for word in words:
        if word in text:
            return True
    return False

# ################################################################################################################################

def _get_string(node:'ast.expr') -> 'str':
    """ Returns the text of a string literal or of the literal parts of an f-string, or an empty string for any other node.
    """
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return node.value

    if isinstance(node, ast.JoinedStr):
        parts:'strlist' = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
            else:
                parts.append('x')
        out = ''.join(parts)
        return out

    return ''

# ################################################################################################################################
# ################################################################################################################################

class _Scope:
    """ The assignments of one function, of one class or of the module, by the name they assign to,
    in the order of the source.
    """
    def __init__(self) -> 'None':
        self.values:'dict[str, list[ast.expr]]' = {}

    def add(self, name:'str', value:'ast.expr') -> 'None':
        if name not in self.values:
            self.values[name] = []
        self.values[name].append(value)

# ################################################################################################################################

@cache
def get_table_names() -> 'strdict':
    """ Returns the name of each table that production code defines, by the full dotted name of the object that defines it -
    a table built with Table or a model class with its table name.
    """
    out:'strdict' = {}

    for source in get_python_files(is_production=True):
        module_name = get_module_name(source)
        tree = parse(source)

        for node in tree.body:

            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    call_name = get_dotted_name(node.value.func, {})
                    if call_name.endswith(ModuleCtx.Table_Call):
                        if node.value.args:
                            table_name = _get_string(node.value.args[0])
                            if table_name:
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        out[f'{module_name}.{target.id}'] = table_name

            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id == ModuleCtx.Table_Name_Attribute:
                                    table_name = _get_string(item.value)
                                    if table_name:
                                        out[f'{module_name}.{node.name}'] = table_name

    return out

# ################################################################################################################################
# ################################################################################################################################

class _SiteCollector(ast.NodeVisitor):
    """ Collects each write primitive of a module with the function it is in.
    """
    def __init__(self, source:'SourceFile', tree:'ast.Module') -> 'None':
        self.source = source
        self.module_name = get_module_name(source)
        self.aliases = get_import_aliases(tree)
        self.table_names = get_table_names()

        self.scopes:'strlist' = []
        self.assignments:'list[_Scope]' = [self._collect_assignments(tree.body)]
        self.class_assignments:'dict[str, _Scope]' = self._collect_class_assignments(tree)

        self.sites:'write_site_list' = []

# ################################################################################################################################

    def _collect_assignments(self, body:'list[ast.stmt]') -> '_Scope':
        """ Returns the assignments to plain names in a body, including those nested in its blocks.
        """
        out = _Scope()

        for statement in body:
            for node in ast.walk(statement):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node is not statement:
                        continue
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            out.add(target.id, node.value)
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        if node.value is not None:
                            out.add(node.target.id, node.value)

        return out

# ################################################################################################################################

    def _collect_class_assignments(self, tree:'ast.Module') -> 'dict[str, _Scope]':
        """ Returns the assignments of each class of the module, by the name of the class.
        """
        out:'dict[str, _Scope]' = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                scope = _Scope()
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                scope.add(target.id, item.value)
                out[node.name] = scope

        return out

# ################################################################################################################################

    def _get_values(self, node:'ast.expr') -> 'list[ast.expr]':
        """ Returns each value that a name or a class attribute is assigned in the source, in the order of the source,
        or an empty list if it is assigned none.
        """
        if isinstance(node, ast.Name):
            for scope in reversed(self.assignments):
                if node.id in scope.values:
                    return scope.values[node.id]

        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                owner = node.value.id
                if owner in self.class_assignments:
                    scope = self.class_assignments[owner]
                    if node.attr in scope.values:
                        return scope.values[node.attr]

                elif owner == 'self':
                    for scope in self.class_assignments.values():
                        if node.attr in scope.values:
                            return scope.values[node.attr]

        return []

# ################################################################################################################################

    def _resolve(self, node:'ast.expr') -> 'ast.expr':
        """ Returns the last value that a name or a class attribute is assigned in the source, or the node itself.
        """
        values = self._get_values(node)

        if values:
            out = values[-1]
        else:
            out = node

        return out

# ################################################################################################################################

    def _get_table_name(self, node:'ast.expr') -> 'str':
        """ Returns the name of the table that an object of the source defines, or an empty string if it is not known.
        """
        dotted_name = get_dotted_name(node, self.aliases)

        if dotted_name in self.table_names:
            return self.table_names[dotted_name]

        local_name = f'{self.module_name}.{dotted_name}'

        if local_name in self.table_names:
            return self.table_names[local_name]

        return ''

# ################################################################################################################################

    def _get_construct_tables(self, node:'ast.expr', visited:'set[int]') -> 'strlist | None':
        """ Returns the tables of an SQLAlchemy write construct, or None if the node is not one. A statement built
        over several assignments to one name is followed through each of them.
        """
        if id(node) in visited:
            return None

        visited.add(id(node))

        # A name is a construct if any of the values assigned to it is one ..
        if isinstance(node, ast.Name):
            for value in self._get_values(node):
                out = self._get_construct_tables(value, visited)
                if out is not None:
                    return out
            return None

        if not isinstance(node, ast.Call):
            return None

        func = node.func

        # .. a method of a table, as in table.insert(), is one ..
        if isinstance(func, ast.Attribute):
            if func.attr in ModuleCtx.Construct_Names:
                out = []
                table_name = self._get_table_name(func.value)
                if table_name:
                    out.append(table_name)
                return out

            # .. as is a method of a construct, as in insert(table).values() ..
            out = self._get_construct_tables(func.value, visited)
            return out

        # .. and so is a function of SQLAlchemy, as in insert(table).
        if isinstance(func, ast.Name):
            if func.id in ModuleCtx.Construct_Names:
                out = []
                if node.args:
                    table_name = self._get_table_name(node.args[0])
                    if table_name:
                        out.append(table_name)
                return out

        return None

# ################################################################################################################################

    def _get_statement_tables(self, node:'ast.expr') -> 'strlist | None':
        """ Returns the tables of a statement literal that writes, or None if the node is not one.
        """
        if isinstance(node, ast.Call):
            if get_dotted_name(node.func, {}).endswith(ModuleCtx.Text_Function):
                if node.args:
                    node = self._resolve(node.args[0])

        text = _get_string(node)

        if not ModuleCtx.Write_Keyword.match(text):
            return None

        out = ModuleCtx.Statement_Table.findall(text)
        return out

# ################################################################################################################################

    def _is_literal(self, node:'ast.expr') -> 'bool':
        """ Returns whether a statement is a literal that the source spells out, directly or through text().
        """
        node = self._resolve(node)

        if isinstance(node, ast.Call):
            if get_dotted_name(node.func, {}).endswith(ModuleCtx.Text_Function):
                if node.args:
                    node = self._resolve(node.args[0])

        out = bool(_get_string(node))
        return out

# ################################################################################################################################

    def _get_write_tables(self, node:'ast.expr') -> 'strlist | None':
        """ Returns the tables of a statement that writes, or None if the statement does not write.
        """
        out = self._get_construct_tables(node, set())

        if out is None:
            out = self._get_statement_tables(self._resolve(node))

        return out

# ################################################################################################################################

    def _add(self, call:'ast.Call', primitive:'str', tables:'strlist') -> 'None':
        item = WriteSite()
        item.source = self.source
        item.module_name = self.module_name
        item.qualname = '.'.join(self.scopes)
        item.primitive = primitive
        item.line = call.lineno
        item.tables = tables
        self.sites.append(item)

# ################################################################################################################################

    def _visit_function(self, node:'ast.FunctionDef | ast.AsyncFunctionDef') -> 'None':
        self.scopes.append(node.name)
        self.assignments.append(self._collect_assignments(node.body))
        self.generic_visit(node)
        _ = self.assignments.pop()
        _ = self.scopes.pop()

    def visit_ClassDef(self, node:'ast.ClassDef') -> 'None':
        self.scopes.append(node.name)
        self.generic_visit(node)
        _ = self.scopes.pop()

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

# ################################################################################################################################

    def visit_Call(self, node:'ast.Call') -> 'None':
        self._collect_call(node)
        self.generic_visit(node)

# ################################################################################################################################

    def _collect_call(self, node:'ast.Call') -> 'None':
        func = node.func

        # A function that writes whatever its arguments ..
        function_name = get_dotted_name(func, self.aliases)

        if function_name in ModuleCtx.Write_Functions:
            self._add(node, function_name, [])
            return

        if not isinstance(func, ast.Attribute):
            return

        method = func.attr
        receiver = _get_receiver_text(node)

        # .. a method that writes whatever its receiver ..
        if method in ModuleCtx.Unconditional_Methods:
            tables:'strlist' = []
            if node.args:
                statement_tables = self._get_write_tables(node.args[0])
                if statement_tables:
                    tables = statement_tables
            self._add(node, method, tables)

        # .. a method of a session ..
        elif method in ModuleCtx.Session_Methods:
            if _has_word(receiver, ModuleCtx.Session_Words):
                self._add(node, method, [])

        # .. a commit ..
        elif method == ModuleCtx.Commit_Method:
            if _has_word(receiver, ModuleCtx.Commit_Words):
                self._add(node, method, [])

        # .. a transaction of an engine ..
        elif method == ModuleCtx.Begin_Method:
            if _has_word(receiver, ModuleCtx.Begin_Words):
                self._add(node, method, [])

        # .. and a statement that writes, or a statement of a cursor of the driver that the source does not spell out.
        elif method in ModuleCtx.Execute_Methods:
            if node.args:
                statement = node.args[0]
                tables_or_none = self._get_write_tables(statement)
                if tables_or_none is not None:
                    self._add(node, method, tables_or_none)
                elif _has_word(receiver, ModuleCtx.Cursor_Words):
                    if not self._is_literal(statement):
                        self._add(node, method, [])

# ################################################################################################################################
# ################################################################################################################################

def get_module_sites(source:'SourceFile') -> 'write_site_list':
    """ Returns each write primitive of one source file.
    """
    tree = parse(source)

    collector = _SiteCollector(source, tree)
    collector.visit(tree)

    out = collector.sites
    return out

# ################################################################################################################################

@cache
def get_write_sites() -> 'write_site_list':
    """ Returns each write primitive of production code, of the installation and of each linked repository.
    """
    out:'write_site_list' = []

    for source in get_python_files(is_production=True):
        out.extend(get_module_sites(source))

    return out

# ################################################################################################################################

def get_site_functions() -> 'set[tuple[str, str]]':
    """ Returns each function that holds at least one write primitive, by its module and its qualified name.
    """
    out:'set[tuple[str, str]]' = set()

    for site in get_write_sites():
        out.add((site.module_name, site.qualname))

    return out

# ################################################################################################################################
# ################################################################################################################################
