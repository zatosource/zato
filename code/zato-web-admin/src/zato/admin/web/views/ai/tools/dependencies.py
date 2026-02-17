# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
from logging import getLogger

# PyYAML
import yaml

if 0:
    from zato.common.typing_ import anydict, anylist

logger = getLogger(__name__)

is_dependency_checking_enabled = False

_config_yaml = """
providers:
  service:
    tool: deploy_service
    extract: ast
  security:
    tool: create_security
    field: name

consumers:
  service:
    - tool: create_channel_rest
      field: service
    - tool: create_scheduler
      field: service
  security:
    - tool: create_channel_rest
      field: security
    - tool: create_outgoing_rest
      field: security
    - tool: create_outgoing_soap
      field: security
"""

_config = None

def _get_config() -> 'anydict':
    global _config
    if _config is None:
        _config = yaml.safe_load(_config_yaml)
    return _config

def _extract_service_names_ast(code:'str') -> 'list':
    """ Extracts service names from Python code using AST.
    Finds classes with a 'name' class attribute.
    """
    out = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == 'name':
                                if isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
                                    out.append(item.value.value)
    except SyntaxError:
        pass
    return out

def _get_provided_names(tool_calls:'anylist') -> 'anydict':
    """ Returns a dict of {resource_type: set of names} that the tool calls will create.
    """
    config = _get_config()
    providers = config.get('providers', {})
    provided = {}

    for tc in tool_calls:
        tool_name = tc.get('name', '')
        arguments = tc.get('input', tc.get('args', {}))

        for resource_type, provider_config in providers.items():
            if provider_config.get('tool') == tool_name:
                if resource_type not in provided:
                    provided[resource_type] = set()

                extract_method = provider_config.get('extract')
                if extract_method == 'ast':
                    files = arguments.get('files', [])
                    for f in files:
                        code = f.get('code', '')
                        if code:
                            names = _extract_service_names_ast(code)
                            provided[resource_type].update(names)
                else:
                    field = provider_config.get('field')
                    if field:
                        value = arguments.get(field)
                        if value:
                            provided[resource_type].add(value)

    return provided

def _get_required_names(tool_call:'anydict') -> 'anydict':
    """ Returns a dict of {resource_type: set of names} that this tool call requires.
    """
    config = _get_config()
    consumers = config.get('consumers', {})
    required = {}

    tool_name = tool_call.get('name', '')
    arguments = tool_call.get('input', tool_call.get('args', {}))

    for resource_type, consumer_list in consumers.items():
        for consumer_config in consumer_list:
            if consumer_config.get('tool') == tool_name:
                field = consumer_config.get('field')
                if field:
                    value = arguments.get(field)
                    if value:
                        if resource_type not in required:
                            required[resource_type] = set()
                        required[resource_type].add(value)

    return required

def build_dependency_graph(tool_calls:'anylist') -> 'anydict':
    """ Builds a dependency graph for the given tool calls.
    Returns a dict of {tool_index: set of tool_indices it depends on}.
    """
    provided = _get_provided_names(tool_calls)
    logger.info('Dependency graph - provided names: %s', provided)

    provider_index = {}
    for resource_type, names in provided.items():
        for name in names:
            key = (resource_type, name)
            for i, tc in enumerate(tool_calls):
                tool_name = tc.get('name', '')
                config = _get_config()
                providers = config.get('providers', {})
                provider_config = providers.get(resource_type, {})
                if provider_config.get('tool') == tool_name:
                    arguments = tc.get('input', tc.get('args', {}))
                    if provider_config.get('extract') == 'ast':
                        files = arguments.get('files', [])
                        for f in files:
                            code = f.get('code', '')
                            if code:
                                names_in_file = _extract_service_names_ast(code)
                                if name in names_in_file:
                                    provider_index[key] = i
                                    break
                    else:
                        field = provider_config.get('field')
                        if field and arguments.get(field) == name:
                            provider_index[key] = i

    logger.info('Dependency graph - provider_index: %s', provider_index)

    dependencies = {}
    for i, tc in enumerate(tool_calls):
        dependencies[i] = set()
        required = _get_required_names(tc)
        logger.info('Dependency graph - tool %d (%s) requires: %s', i, tc.get('name', ''), required)
        for resource_type, names in required.items():
            for name in names:
                key = (resource_type, name)
                if key in provider_index:
                    dep_index = provider_index[key]
                    if dep_index != i:
                        dependencies[i].add(dep_index)
                        logger.info('Dependency graph - tool %d depends on tool %d for %s', i, dep_index, key)

    logger.info('Dependency graph - final dependencies: %s', dependencies)
    return dependencies

def topological_sort_waves(tool_calls:'anylist') -> 'anylist':
    """ Sorts tool calls into waves for parallel execution.
    Returns a list of lists, where each inner list contains indices that can run in parallel.
    """
    if not tool_calls:
        return []

    if not is_dependency_checking_enabled:
        return [list(range(len(tool_calls)))]

    dependencies = build_dependency_graph(tool_calls)
    remaining = set(range(len(tool_calls)))
    completed = set()
    waves = []

    while remaining:
        wave = []
        for i in remaining:
            deps = dependencies.get(i, set())
            if deps.issubset(completed):
                wave.append(i)

        if not wave:
            wave = list(remaining)
            logger.warning('Circular dependency detected, forcing execution of remaining tools: %s', wave)

        waves.append(wave)
        for i in wave:
            remaining.discard(i)
            completed.add(i)

    return waves
