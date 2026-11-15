# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import inspect
import pkgutil
from importlib import import_module

# Zato
from zato.common.typing_ import cast_
from zato.server.service import Service
from zato.server.service.internal import ServerFunctionInvoker
from zato.server.service.internal.security import basic_auth
import zato.server.service.internal as internal_package

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from types import ModuleType
    from zato.common.typing_ import anydict, strlist, strset

    anydict = anydict
    ModuleType = ModuleType
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# What the source of a service contains if it publishes the event of a change
_publish_calls = ('config_dispatcher.publish(', 'config_dispatcher.relay_only(')

# ################################################################################################################################
# ################################################################################################################################

def _iter_internal_modules() -> 'list[ModuleType]':
    out:'list[ModuleType]' = []

    for module_info in pkgutil.walk_packages(internal_package.__path__, internal_package.__name__ + '.'):
        module = import_module(module_info.name)
        out.append(module)

    return out

# ################################################################################################################################

def _get_publishing_helpers(source:'str') -> 'strset':
    """ Returns the names of the module-level functions of a module that publish the event of a change.
    """
    out:'strset' = set()
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            segment = cast_('str', ast.get_source_segment(source, node))
            if any(call in segment for call in _publish_calls):
                out.add(node.name)

    return out

# ################################################################################################################################

def _get_unmarked_publishers() -> 'strlist':
    """ Returns the services that publish the event of a change and are not marked as changing configuration.
    """
    out:'strlist' = []

    for module in _iter_internal_modules():
        # An empty module has no source that inspect returns, so its file is read instead
        module_path = cast_('str', module.__file__)

        with open(module_path) as module_file:
            module_source = module_file.read()

        helpers = _get_publishing_helpers(module_source)

        for _, class_ in inspect.getmembers(module, inspect.isclass):

            if class_.__module__ != module.__name__:
                continue

            if not issubclass(class_, Service):
                continue

            class_source = inspect.getsource(class_)
            is_direct = any(call in class_source for call in _publish_calls)
            is_through_helper = any(f'{helper}(' in class_source for helper in helpers)

            if (is_direct or is_through_helper) and not class_.changes_config:
                out.append(f'{module.__name__}.{class_.__name__}')

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_service_changes_no_configuration_by_default() -> 'None':
    assert Service.changes_config is False

# ################################################################################################################################

def test_the_services_built_by_the_metaclasses_are_marked() -> 'None':
    assert basic_auth.Create.changes_config is True
    assert basic_auth.Edit.changes_config is True
    assert basic_auth.Delete.changes_config is True

# ################################################################################################################################

def test_every_service_that_publishes_a_change_is_marked() -> 'None':
    unmarked = _get_unmarked_publishers()
    assert unmarked == []

# ################################################################################################################################

def test_the_server_invoker_changes_configuration_for_a_reload_only() -> 'None':
    service = ServerFunctionInvoker()

    service.request.raw = {'func_name': 'reload_config'}
    assert service.is_config_change() is True

    service.request.raw = {'func_name': 'get_logging'}
    assert service.is_config_change() is False

    service.request.raw = {'func_name': 'import_enmasse'}
    assert service.is_config_change() is False

# ################################################################################################################################
# ################################################################################################################################
