# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import re
from textwrap import dedent

# Zato
from zato.common.test.durability.linked import get_linked_entries, ModuleCtx as LinkedModuleCtx
from zato.common.test.durability.python_ast import get_calls, get_dotted_name, get_import_aliases, get_module_name, \
    get_package_name, get_references, parse
from zato.common.test.durability.sources import get_python_files, get_source_files
from zato.common.typing_ import cast_

# Local
from registry import Audit_Log_Schema_Path, Audit_Tables_Name, Audit_Tables_Not_Guarded, Direct_SQL_Purposes, \
    Mechanism_Functions, Mechanism_Name, Mechanism_Prefix, Run_Seed_Name, Run_Seed_Path, Write_Path_Mark_Tests, \
    Write_Path_Markers, Write_Path_Module, Write_Path_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.durability.sources import SourceFile
    from zato.common.typing_ import anylist, strdict, strlist

    SourceFile = SourceFile

    site_mechanisms = dict[tuple[str, str], str]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The constructor of an SQLAlchemy table, whose first argument is the name of the table
    Table_Constructors = ('sqlalchemy.Table', 'sqlalchemy.schema.Table', 'sqlalchemy.sql.schema.Table')

    # The package against which the imports of a test module are resolved, as test modules are imported
    # from their own directories, by absolute names
    Test_Package = ''

    # The names through which code marks its work as that of a mechanism
    Mark_Names = frozenset(Write_Path_Markers + (Mechanism_Name,))

    # A statement that creates or removes an object of a database, in the text of a statement
    # with each value of an f-string standing in as an empty placeholder
    DDL_Verb = r'\b(create|drop)\s+(unlogged\s+|temporary\s+|temp\s+|unique\s+)?'
    DDL_Object = r'(table|index|trigger|view|sequence|schema|extension|database|type|function)\b'
    DDL_Statement = re.compile(DDL_Verb + DDL_Object, re.IGNORECASE)

    # The methods of SQLAlchemy that create or remove a table, an index or a whole schema
    DDL_Methods = frozenset({'create', 'drop', 'create_all', 'drop_all'})

    # The position of the function among the arguments of run_seed
    Seed_Function_Position = 1

    # The member of Mechanism of a seed
    Seed_Member = 'Seed'

# ################################################################################################################################
# ################################################################################################################################

def _get_mechanism_functions() -> 'site_mechanisms':
    """ Returns the mechanism of each function that runs one, of this installation and of the linked repositories.
    """
    entries:'anylist' = list(Mechanism_Functions)
    entries.extend(get_linked_entries(LinkedModuleCtx.Mechanism_Functions))

    out:'site_mechanisms' = {}

    for module_name, qualname, mechanism in entries:
        out[module_name, qualname] = mechanism

    return out

# ################################################################################################################################

def _get_mechanism(call:'ast.Call', aliases:'dict[str, str]') -> 'str':
    """ Returns the member of Mechanism that a call marks its work with, or an empty name if the call passes on
    a mechanism it received.
    """
    name = get_dotted_name(call.args[0], aliases)

    if name.startswith(Mechanism_Prefix):
        out = name.removeprefix(Mechanism_Prefix)
    else:
        out = ''

    return out

# ################################################################################################################################

def _get_production_sources() -> 'list[SourceFile]':
    out:'list[SourceFile]' = []

    for source in get_python_files(is_production=True):
        if get_module_name(source) != Write_Path_Module:
            out.append(source)

    return out

# ################################################################################################################################

def test_marker_only_in_mechanism_functions() -> 'None':
    """ Only the functions that run a mechanism mark their work as that of one, each with its own mechanism, so that
    no other production code obtains the right to write to the Zato database by marking its work on its own.
    """
    mechanism_functions = _get_mechanism_functions()
    findings:'strlist' = []

    for source in _get_production_sources():
        module_name = get_module_name(source)
        tree = parse(source)
        aliases = get_import_aliases(tree, get_package_name(source))

        # Each reference to a marker is within a function that runs a mechanism ..
        for reference in get_references(source):
            if reference.name in Write_Path_Markers:
                site = (module_name, reference.qualname)
                if site not in mechanism_functions:
                    findings.append(f'{source.path}:{reference.line} -> {module_name} {reference.qualname}')

        # .. which marks its work with its own mechanism.
        for call in get_calls(source):
            if call.name in Write_Path_Markers:
                site = (module_name, call.qualname)
                if site in mechanism_functions:
                    mechanism = _get_mechanism(call.node, aliases)
                    expected = mechanism_functions[site]
                    if mechanism != expected:
                        findings.append(f'{source.path}:{call.line} -> {call.qualname} `{mechanism}` != `{expected}`')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def test_mechanism_functions_exist() -> 'None':
    """ Each listed function still marks its work, so that no entry outlives its function.
    """
    found:'set[tuple[str, str]]' = set()

    for source in _get_production_sources():
        module_name = get_module_name(source)

        for reference in get_references(source):
            if reference.name in Write_Path_Markers:
                site = (module_name, reference.qualname)
                found.add(site)

    missing = set(_get_mechanism_functions()) - found
    assert not missing, missing

# ################################################################################################################################

def _get_source(relative_path:'str') -> 'SourceFile':
    for source in get_source_files():
        if not source.is_linked:
            if source.relative_path == relative_path:
                return source

    raise KeyError(relative_path)

# ################################################################################################################################

def _get_schema_tables() -> 'set[str]':
    """ Returns the name of each table of the schema of the audit log.
    """
    source = _get_source(Audit_Log_Schema_Path)
    out:'set[str]' = set()

    for call in get_calls(source):
        if call.name in ModuleCtx.Table_Constructors:
            first_argument = call.node.args[0]
            if isinstance(first_argument, ast.Constant):
                table_name = cast_('str', first_argument.value)
                out.add(table_name)

    return out

# ################################################################################################################################

def _get_guarded_tables() -> 'set[str]':
    """ Returns the tables of the audit log that the write path guards, as its source lists them.
    """
    source = _get_source(Write_Path_Path)
    tree = parse(source)

    out:'set[str]' = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == Audit_Tables_Name:
                    for item in ast.walk(node.value):
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            out.add(item.value)

    return out

# ################################################################################################################################

def test_audit_tables_of_the_guard() -> 'None':
    """ The write path guards every table of the audit log but the alerts, so that a new table of the audit log
    receives the protection at the time it is created.
    """
    schema_tables = _get_schema_tables()
    expected = schema_tables - set(Audit_Tables_Not_Guarded)

    assert schema_tables
    assert _get_guarded_tables() == expected

# ################################################################################################################################

def _get_aliases(source:'SourceFile', tree:'ast.Module') -> 'strdict':
    """ Returns the full dotted name of each name that a module of production code or of the tests imports.
    """
    if source.is_production:
        package_name = get_package_name(source)
    else:
        package_name = ModuleCtx.Test_Package

    out = get_import_aliases(tree, package_name)
    return out

# ################################################################################################################################

def _get_top_level_nodes(tree:'ast.Module') -> 'list[tuple[str, ast.AST]]':
    """ Returns each node of a module with the name of the function or class at the top level of the module
    that it is in, or with an empty name at the level of the module.
    """
    out:'list[tuple[str, ast.AST]]' = []

    for statement in tree.body:

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = statement.name
        else:
            name = ''

        for node in ast.walk(statement):
            out.append((name, node))

    return out

# ################################################################################################################################

def _get_mark_findings(tree:'ast.Module', aliases:'strdict', relative_path:'str', seed_sites:'set[tuple[str, str]]') -> 'strlist':
    """ Returns the line and the name of each mark of a mechanism in a module of test code that is not a seed function
    marking its work with the seed mechanism.
    """
    seed_member = Mechanism_Prefix + ModuleCtx.Seed_Member
    out:'strlist' = []

    for function_name, node in _get_top_level_nodes(tree):

        if not isinstance(node, (ast.Name, ast.Attribute)):
            continue

        name = get_dotted_name(node, aliases)
        is_member = name.startswith(Mechanism_Prefix)

        if not (name in ModuleCtx.Mark_Names or is_member):
            continue

        # A function of the package of direct writes that runs a seed marks its work with the seed mechanism alone ..
        if (relative_path, function_name) in seed_sites:
            if is_member and name != seed_member:
                out.append(f'{node.lineno} -> {function_name} `{name}` != `{seed_member}`')

        # .. and no other test code marks its work at all.
        else:
            out.append(f'{node.lineno} -> {name}')

    return out

# ################################################################################################################################

def test_no_marks_in_test_code() -> 'None':
    """ No test of this installation or of a linked repository marks its work as that of a mechanism, apart from
    the tests of the guard of the write path and the functions of the package of direct writes that run a seed,
    each with the seed mechanism, so that every other test writes through a mechanism of the product or through
    a seed function, and never obtains the right to write on its own.
    """
    exempt_paths = {relative_path for relative_path, _ in Write_Path_Mark_Tests}

    direct_sql_entries:'anylist' = list(Direct_SQL_Purposes)
    direct_sql_entries.extend(get_linked_entries(LinkedModuleCtx.Direct_SQL_Purposes))
    seed_sites = {(relative_path, function_name) for relative_path, function_name, _ in direct_sql_entries}

    findings:'strlist' = []

    for source in get_python_files(is_production=False):

        if not source.is_linked and source.relative_path in exempt_paths:
            continue

        tree = parse(source)
        aliases = _get_aliases(source, tree)

        for finding in _get_mark_findings(tree, aliases, source.relative_path, seed_sites):
            findings.append(f'{source.path}:{finding}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def _get_statement_text(node:'ast.Constant | ast.JoinedStr') -> 'str':
    """ Returns the text of a string, with each value of an f-string replaced by an empty placeholder.
    """
    if isinstance(node, ast.Constant):
        out = cast_('str', node.value)
    else:
        parts:'strlist' = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(cast_('str', value.value))
            else:
                parts.append('{}')
        out = ''.join(parts)

    return out

# ################################################################################################################################

def _get_ddl_lines(function:'ast.FunctionDef') -> 'list[int]':
    """ Returns the line of each statement text and of each call of SQLAlchemy in a function that creates
    or removes an object of a database, each line once, as the text of an f-string is visited again in its parts.
    """
    lines:'set[int]' = set()

    for node in ast.walk(function):

        if isinstance(node, ast.JoinedStr) or (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            text = _get_statement_text(node)
            if ModuleCtx.DDL_Statement.search(text):
                lines.add(node.lineno)

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ModuleCtx.DDL_Methods:
                lines.add(node.lineno)

    out = sorted(lines)
    return out

# ################################################################################################################################

def _get_functions(tree:'ast.Module', name:'str') -> 'list[ast.FunctionDef]':
    """ Returns each function of a module of the given name, at any level of nesting.
    """
    out:'list[ast.FunctionDef]' = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            out.append(node)

    return out

# ################################################################################################################################

def _get_seed_functions(
    source:'SourceFile',
    tree:'ast.Module',
    argument:'ast.expr',
    aliases:'strdict',
    sources_by_module:'dict[str, tuple[SourceFile, ast.Module]]',
) -> 'tuple[SourceFile, list[ast.FunctionDef]]':
    """ Returns the file and the definitions of the function that a call of run_seed receives, defined in the module
    of the call or imported from a module of production code, and no definitions for any other function.
    """
    if isinstance(argument, ast.Name) and argument.id not in aliases:
        out = (source, _get_functions(tree, argument.id))
        return out

    full_name = get_dotted_name(argument, aliases)
    module_name, _, function_name = full_name.rpartition('.')

    if module_name in sources_by_module:
        function_source, function_tree = sources_by_module[module_name]
        out = (function_source, _get_functions(function_tree, function_name))
    else:
        out = (source, [])

    return out

# ################################################################################################################################

def _is_run_seed(source:'SourceFile', call:'ast.Call', aliases:'strdict') -> 'bool':
    """ Says whether a call runs a seed, through its full name or through the name it has within its own module.
    """
    name = get_dotted_name(call.func, aliases)

    if name == Run_Seed_Name:
        out = True
    else:
        _, _, local_name = Run_Seed_Name.rpartition('.')
        out = not source.is_linked and source.relative_path == Run_Seed_Path and name == local_name

    return out

# ################################################################################################################################

def test_seed_functions_create_no_objects() -> 'None':
    """ No function that run_seed receives creates or removes a table, an index or any other object of a database,
    apart from those of the files that create the scratch tables of a seed, so that the seed mechanism writes
    seed rows alone and never changes the schema of the system under test.
    """
    scratch_paths:'set[str]' = set()

    for relative_path, _ in get_linked_entries(LinkedModuleCtx.Seed_Scratch_Tables):
        scratch_paths.add(relative_path)

    parsed:'list[tuple[SourceFile, ast.Module, strdict]]' = []
    sources_by_module:'dict[str, tuple[SourceFile, ast.Module]]' = {}

    for source in get_python_files(is_production=True) + get_python_files(is_production=False):
        tree = parse(source)
        aliases = _get_aliases(source, tree)
        parsed.append((source, tree, aliases))

        if source.is_production:
            module_name = get_module_name(source)
            sources_by_module[module_name] = (source, tree)

    findings:'strlist' = []
    call_count = 0

    for source, tree, aliases in parsed:
        for node in ast.walk(tree):

            if not isinstance(node, ast.Call):
                continue

            if not _is_run_seed(source, node, aliases):
                continue

            call_count += 1

            argument = node.args[ModuleCtx.Seed_Function_Position]
            function_source, functions = _get_seed_functions(source, tree, argument, aliases, sources_by_module)

            # .. a function that cannot be found is a finding of its own, as nothing proves what it runs ..
            if not functions:
                findings.append(f'{source.path}:{node.lineno} -> unresolved seed function')
                continue

            # .. and the scratch tables of a seed are created and removed in the files declared for them alone.
            if function_source.is_linked and function_source.relative_path in scratch_paths:
                continue

            for function in functions:
                for line in _get_ddl_lines(function):
                    findings.append(f'{function_source.path}:{line} -> {function.name} creates or removes an object')

    assert call_count
    assert not findings, '\n'.join(findings)

# ################################################################################################################################

def _parse_sample(sample:'str') -> 'tuple[ast.Module, strdict]':
    """ Returns the syntax tree of a sample of test code, with the names it imports.
    """
    tree = ast.parse(dedent(sample))
    aliases = get_import_aliases(tree, ModuleCtx.Test_Package)

    out = (tree, aliases)
    return out

# ################################################################################################################################

def test_marks_in_test_code_are_found() -> 'None':
    """ The check of the marks in test code finds a mark set directly, through a module alias, by running a function
    in a mechanism, and by a seed function with a mechanism other than the seed, and accepts a seed function
    that marks its work with the seed mechanism.
    """
    sample_path = 'code/tests/python/zato-common/sample/test_sample.py'
    seed_sites = {(sample_path, 'seed_sample')}

    direct = """
        from zato.common.db_env.write_path import Mechanism, write_path

        def test_sample():
            with write_path(Mechanism.Serialized_Write):
                pass
    """

    module_alias = """
        from zato.common.db_env import write_path as wp

        def test_sample(func):
            wp.run_in_write_path(wp.Mechanism.Maintenance, func, ())
    """

    seed_with_another = """
        from zato.common.db_env.write_path import Mechanism, write_path

        def seed_sample():
            with write_path(Mechanism.Group_Commit):
                pass
    """

    seed_with_seed = """
        from zato.common.db_env.write_path import Mechanism, write_path

        def seed_sample():
            with write_path(Mechanism.Seed):
                pass
    """

    for sample in (direct, module_alias, seed_with_another):
        tree, aliases = _parse_sample(sample)
        assert _get_mark_findings(tree, aliases, sample_path, seed_sites), sample

    tree, aliases = _parse_sample(seed_with_seed)
    assert not _get_mark_findings(tree, aliases, sample_path, seed_sites)

# ################################################################################################################################

def test_objects_of_seed_functions_are_found() -> 'None':
    """ The check of the seed functions finds a table, an index and a trigger created or removed by the text
    of a statement, in an f-string as well, and a table or a whole schema created or removed through SQLAlchemy,
    and accepts a seed function that inserts rows alone.
    """
    samples = {
        'drop_table':       "connection.exec_driver_sql(f'drop table if exists {name}')",
        'create_index':     "connection.exec_driver_sql('CREATE UNIQUE INDEX idx_sample ON sample (id)')",
        'drop_trigger':     "connection.exec_driver_sql(f'drop trigger if exists {prefix}_insert')",
        'create_temporary': "connection.exec_driver_sql('create temporary table sample as select 1')",
        'table_drop':       'sample_table.drop(connection)',
        'create_all':       'metadata.create_all(connection)',
    }

    for name, statement in samples.items():
        sample = f"""
            def {name}(connection):
                {statement}
        """
        tree, _ = _parse_sample(sample)
        function = _get_functions(tree, name)[0]
        assert _get_ddl_lines(function), name

    inserts = """
        def insert_rows(connection, table, rows):
            connection.execute(table.insert(), rows)
            connection.exec_driver_sql('insert into sample (id) values (1)')
    """

    tree, _ = _parse_sample(inserts)
    function = _get_functions(tree, 'insert_rows')[0]
    assert not _get_ddl_lines(function)

# ################################################################################################################################
# ################################################################################################################################
