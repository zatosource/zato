# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import os
import re

# Zato
from zato.common.test.durability.linked import get_linked_entries, ModuleCtx as LinkedModuleCtx
from zato.common.test.durability.python_ast import get_dotted_name, get_import_aliases, parse
from zato.common.test.durability.sources import get_python_files, get_source_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.durability.sources import SourceFile, source_file_list
    from zato.common.typing_ import strlist, strset

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # This module, which names the outputs that it looks for
    Definition_Path = os.path.abspath(__file__)

    # The directory of the tests of the installation
    Tests_Dir = 'code/tests/'

    # The words in the path of a module that make it a performance suite
    Path_Words = ('perf', 'load', 'capacity', 'throughput', 'latency', 'bench', 'soak', 'stability', 'volume')

    # What separates the words of a path
    Path_Separators = re.compile(r'[/_\-.]')

    # The marker of a performance test
    Marker_Pattern = re.compile(r'\bperftest\b')

    # The function that records every performance figure
    Result_Function = 'report_result'

    # The tests of the gate of that function, which start a server with settings that the gate refuses
    Gate_Verification_Dir = 'code/tests/python/zato-common/durability/perf_gate/'

    # The configuration of pytest of a directory
    Conftest_Name = 'conftest.py'

    # The package of the product
    Product_Package = 'zato'

    # What a performance suite may import from the product - the server fixtures and their database, the resume protocol
    # of the suites, seed_rows for the data seeded before the server starts, the public clients and the reporting module.
    Allowed_Modules = (
        'zato.common.test.conftest_base_pubsub',
        'zato.common.test.pubsub_database',
        'zato.common.test.resume',
        'zato.common.test.direct_sql.seed',
        'zato.common.test.client',
        'zato.common.hl7.mllp.client',
        'zato.common.test.perf_report',
    )

    # The functions through which a conftest obtains a real server - the fixture of a single server
    # and the fixtures of the active-standby pairs
    Server_Fixtures = ('create_zato_server_fixture', 'create_session', 'build_pair')

    # A variable of Zato that a test may set, read only by the test driver
    Test_Variable_Prefix = 'Zato_Test_'

    # The name of a variable of Zato
    Variable_Pattern = re.compile(r'\bZato_[A-Za-z0-9_]+')

    # The names that change a server process or the process of a test in a way a production installation does not
    Process_Settings = ('LD_PRELOAD', 'GEVENT_', 'monkeypatch', 'server.conf')

    # The environment of the process
    Environ_Name = 'os.environ'
    Environ_Write_Methods = ('update', 'setdefault', 'pop', '__setitem__')

    # The suffixes of the files of a suite that may configure a server
    Configuration_Suffixes = ('.yaml', '.yml', '.conf', '.ini')

    # The outputs of performance figures other than the result function
    Figure_Outputs = ('Perf result', 'Traffic result', '[PERF]')
    Figure_Functions = ('record_property', 'get_report_path', 'print_perf', 'format_table')

# ################################################################################################################################
# ################################################################################################################################

def _is_test_source(source:'SourceFile') -> 'bool':
    """ Whether a file is a test of the installation or of a linked repository.
    """
    if source.is_production:
        out = False
    elif source.is_linked:
        out = True
    else:
        out = source.relative_path.startswith(ModuleCtx.Tests_Dir)

    return out

# ################################################################################################################################

def _has_path_word(relative_path:'str') -> 'bool':
    """ Whether a path contains one of the words of a performance suite.
    """
    lower_path = relative_path.lower()
    words = set(ModuleCtx.Path_Separators.split(lower_path))

    for word in ModuleCtx.Path_Words:
        if word in words:
            return True

    return False

# ################################################################################################################################

def _calls_result_function(tree:'ast.Module') -> 'bool':
    """ Whether a module calls the function that records performance figures.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == ModuleCtx.Result_Function:
                return True
            if isinstance(func, ast.Attribute) and func.attr == ModuleCtx.Result_Function:
                return True

    return False

# ################################################################################################################################

def _get_linked_roots() -> 'strlist':
    """ Returns the directory of each performance suite that a linked repository declares.
    """
    out:'strlist' = []

    for root in get_linked_entries(LinkedModuleCtx.Performance_Roots):
        out.append(root)

    return out

# ################################################################################################################################

def _is_under_linked_root(source:'SourceFile', linked_roots:'strlist') -> 'bool':
    """ Whether a file of a linked repository is under one of the performance roots that it declares.
    """
    if not source.is_linked:
        return False

    for root in linked_roots:
        if source.relative_path.startswith(root):
            return True

    return False

# ################################################################################################################################

def get_classified_sources() -> 'source_file_list':
    """ Returns each module of a performance suite with the conftest of its directory.
    """
    linked_roots = _get_linked_roots()
    classified_dirs:'strset' = set()
    out:'source_file_list' = []

    test_sources = [source for source in get_python_files(is_production=False) if _is_test_source(source)]

    for source in test_sources:

        if source.relative_path.startswith(ModuleCtx.Gate_Verification_Dir):
            continue

        text = source.read()

        is_classified = _has_path_word(source.relative_path) \
            or bool(ModuleCtx.Marker_Pattern.search(text)) \
            or _calls_result_function(parse(source)) \
            or _is_under_linked_root(source, linked_roots)

        if is_classified:
            out.append(source)
            classified_dirs.add(os.path.dirname(source.path))

    # The conftest of each directory of a performance suite configures that suite
    for source in test_sources:
        if os.path.basename(source.path) == ModuleCtx.Conftest_Name:
            if os.path.dirname(source.path) in classified_dirs and source not in out:
                out.append(source)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_type_only(node:'ast.stmt') -> 'bool':
    """ Whether a statement is a block of imports for type checkers only, which never runs.
    """
    out = isinstance(node, ast.If) and isinstance(node.test, ast.Constant) and node.test.value == 0
    return out

# ################################################################################################################################

def _get_runtime_imports(tree:'ast.Module') -> 'list[tuple[int, str]]':
    """ Returns the line and the module of each import that runs, without the blocks for type checkers.
    """
    out:'list[tuple[int, str]]' = []
    pending:'list[ast.AST]' = [tree]

    while pending:
        node = pending.pop()

        if isinstance(node, ast.stmt) and _is_type_only(node):
            continue

        if isinstance(node, ast.ImportFrom) and node.module:
            out.append((node.lineno, node.module))

        elif isinstance(node, ast.Import):
            for alias in node.names:
                out.append((node.lineno, alias.name))

        pending.extend(ast.iter_child_nodes(node))

    return out

# ################################################################################################################################

def _is_product_module(module_name:'str') -> 'bool':
    out = module_name == ModuleCtx.Product_Package or module_name.startswith(ModuleCtx.Product_Package + '.')
    return out

# ################################################################################################################################

def test_perf_suites_import_no_internal_code() -> 'None':
    """ A performance suite imports from the product only the server fixtures, seed_rows, the public clients
    and the reporting module, so that what it measures is a server driven through its public interfaces.
    """
    findings:'strlist' = []

    for source in get_classified_sources():
        tree = parse(source)

        for line, module_name in _get_runtime_imports(tree):
            if _is_product_module(module_name) and module_name not in ModuleCtx.Allowed_Modules:
                findings.append(f'{source.path}:{line} -> {module_name}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################

def _references_server_fixture(tree:'ast.Module') -> 'bool':
    """ Whether a module calls one of the functions that start a real server.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ModuleCtx.Server_Fixtures:
                return True
            if isinstance(func, ast.Attribute) and func.attr in ModuleCtx.Server_Fixtures:
                return True

    return False

# ################################################################################################################################

def test_perf_suites_on_a_real_server() -> 'None':
    """ The conftest of every directory of a performance suite obtains its server from the fixture of a single server
    or from the fixtures of the active-standby pairs.
    """
    conftest_by_dir:'dict[str, SourceFile]' = {}
    classified_dirs:'strset' = set()

    for source in get_classified_sources():
        directory = os.path.dirname(source.path)
        classified_dirs.add(directory)

        if os.path.basename(source.path) == ModuleCtx.Conftest_Name:
            conftest_by_dir[directory] = source

    findings:'strlist' = []

    for directory in sorted(classified_dirs):

        if directory not in conftest_by_dir:
            findings.append(f'{directory} -> no conftest')
            continue

        conftest = conftest_by_dir[directory]

        if not _references_server_fixture(parse(conftest)):
            findings.append(f'{conftest.path} -> no real server')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################

def _is_environ(node:'ast.expr', aliases:'dict[str, str]') -> 'bool':
    """ Whether an expression is the environment of the process.
    """
    if isinstance(node, (ast.Name, ast.Attribute)):
        out = get_dotted_name(node, aliases) == ModuleCtx.Environ_Name
    else:
        out = False

    return out

# ################################################################################################################################

def _get_variable_reads(tree:'ast.Module', aliases:'dict[str, str]') -> 'set[int]':
    """ Returns the id of each string constant that names a variable read from the environment.
    """
    out:'set[int]' = set()

    for node in ast.walk(tree):

        # The subscript of the environment, read rather than assigned ..
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load) and _is_environ(node.value, aliases):
            out.add(id(node.slice))

        # .. and the first argument of a read of it.
        elif isinstance(node, ast.Call) and node.args:
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == 'get' and _is_environ(func.value, aliases):
                out.add(id(node.args[0]))
            elif isinstance(func, (ast.Name, ast.Attribute)) and get_dotted_name(func, aliases) == 'os.getenv':
                out.add(id(node.args[0]))

    return out

# ################################################################################################################################

def _get_docstrings(tree:'ast.Module') -> 'set[int]':
    """ Returns the id of each string constant that is a docstring or another statement of its own.
    """
    out:'set[int]' = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            out.add(id(node.value))

    return out

# ################################################################################################################################

def _get_setting_findings(source:'SourceFile') -> 'strlist':
    """ Returns each setting that a module of a performance suite gives to a server or to its own process.
    """
    out:'strlist' = []

    tree = parse(source)
    aliases = get_import_aliases(tree, '')
    skipped = _get_variable_reads(tree, aliases) | _get_docstrings(tree)

    for node in ast.walk(tree):

        # A variable of Zato named anywhere but in a read of the environment or in a docstring is one that the suite sets ..
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in skipped:
            for match in ModuleCtx.Variable_Pattern.finditer(node.value):
                name = match.group(0)
                if not name.startswith(ModuleCtx.Test_Variable_Prefix):
                    out.append(f'{source.path}:{node.lineno} -> {name}')

            for name in ModuleCtx.Process_Settings:
                if name in node.value:
                    out.append(f'{source.path}:{node.lineno} -> {name}')

        # .. as is anything written to the environment of the process ..
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store) and _is_environ(node.value, aliases):
            out.append(f'{source.path}:{node.lineno} -> os.environ[...] =')

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ModuleCtx.Environ_Write_Methods and _is_environ(node.func.value, aliases):
                out.append(f'{source.path}:{node.lineno} -> os.environ.{node.func.attr}')

        # .. and any use of monkeypatch.
        elif isinstance(node, ast.Name) and node.id in ModuleCtx.Process_Settings:
            out.append(f'{source.path}:{node.lineno} -> {node.id}')

    return out

# ################################################################################################################################

def _get_configuration_findings(classified_dirs:'strset') -> 'strlist':
    """ Returns each variable of Zato that a configuration file of a performance suite sets.
    """
    out:'strlist' = []

    for source in get_source_files():

        if os.path.dirname(source.path) not in classified_dirs:
            continue

        if not source.path.endswith(ModuleCtx.Configuration_Suffixes):
            continue

        text = source.read()

        for match in ModuleCtx.Variable_Pattern.finditer(text):
            name = match.group(0)
            if not name.startswith(ModuleCtx.Test_Variable_Prefix):
                out.append(f'{source.path} -> {name}')

    return out

# ################################################################################################################################

def test_perf_suites_production_settings_only() -> 'None':
    """ A performance suite sets no variable of Zato other than those that only its driver reads, writes nothing
    to the environment of its process, patches nothing and changes no setting of the processes that it measures.
    """
    findings:'strlist' = []
    classified_dirs:'strset' = set()

    for source in get_classified_sources():
        classified_dirs.add(os.path.dirname(source.path))
        findings.extend(_get_setting_findings(source))

    findings.extend(_get_configuration_findings(classified_dirs))

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################

def test_perf_figures_through_the_result_function() -> 'None':
    """ No test emits a performance figure other than through the result function, which records it
    with the settings in force in the measured server.
    """
    findings:'strlist' = []
    classified = get_classified_sources()

    for source in get_python_files(is_production=False):

        if not _is_test_source(source) or source.path == ModuleCtx.Definition_Path:
            continue

        tree = parse(source)
        is_classified = source in classified

        for node in ast.walk(tree):

            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for output in ModuleCtx.Figure_Outputs:
                    if output in node.value:
                        findings.append(f'{source.path}:{node.lineno} -> {output}')

            # The functions that write figures elsewhere are known by their names in performance suites only
            elif is_classified and isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in ModuleCtx.Figure_Functions:
                    findings.append(f'{source.path}:{node.lineno} -> {func.id}')
                elif isinstance(func, ast.Attribute) and func.attr in ModuleCtx.Figure_Functions:
                    findings.append(f'{source.path}:{node.lineno} -> {func.attr}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
