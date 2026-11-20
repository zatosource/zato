# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The line numbers of classes that ServiceStore records for each deployed service, which ClassLines computes
# from one parse of each source file, compared with those of inspect.findsource.

# stdlib
import inspect
import sys
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pkgutil import walk_packages

# pytest
import pytest

# Zato
import zato.server.service.internal as internal_services
from zato.server.service.class_lines import ClassLines

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anylist, module_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Module_Name = 'zato_test_class_lines_module'
    File_Name = 'zato_test_class_lines_module.py'

    Source = '''
import functools

def decorate(class_):
    return class_

class Plain:
    pass

@decorate
@functools.total_ordering
class Decorated:
    def __eq__(self, other):
        return True
    def __lt__(self, other):
        return False

class Outer:
    class Inner:
        class Innermost:
            pass

def make_local():
    class Local:
        pass
    return Local

async def make_async_local():
    class AsyncLocal:
        pass
    return AsyncLocal

if True:
    class Redefined:
        pass
else:
    class Redefined:
        pass
'''

    # The same module with two lines more above every class
    Changed_Source = '\n\n' + Source

# ################################################################################################################################
# ################################################################################################################################

def _load_module(tmp_path:'Path', source:'str') -> 'module_':
    """ Writes the source as a module file and imports it under the name of the test module.
    """
    path = tmp_path / ModuleCtx.File_Name
    _ = path.write_text(source)

    # The module is registered so that inspect finds its file by the name of the module of each class.
    spec = spec_from_file_location(ModuleCtx.Module_Name, path)
    assert spec is not None
    assert spec.loader is not None

    out = module_from_spec(spec)
    sys.modules[ModuleCtx.Module_Name] = out
    spec.loader.exec_module(out)

    return out

# ################################################################################################################################

def _get_classes(module:'module_') -> 'anylist':
    """ Returns every class that the test module defines, including the nested ones and those of functions.
    """
    local = module.make_local()

    # The coroutine is driven by hand, as it returns without awaiting anything.
    coroutine = module.make_async_local()
    with pytest.raises(StopIteration) as stop:
        coroutine.send(None)
    async_local = stop.value.value

    out = [
        module.Plain,
        module.Decorated,
        module.Outer,
        module.Outer.Inner,
        module.Outer.Inner.Innermost,
        local,
        async_local,
        module.Redefined,
    ]
    return out

# ################################################################################################################################

def _get_internal_service_classes() -> 'anylist':
    """ Returns every class defined in the modules of the internal services, which the server deploys at each start.
    """
    out = []

    for module_info in walk_packages(internal_services.__path__, internal_services.__name__ + '.'):
        module = import_module(module_info.name)

        for name in sorted(dir(module)):
            item = getattr(module, name)
            if inspect.isclass(item) and inspect.getmodule(item) is module:
                out.append(item)

    return out

# ################################################################################################################################

def _assert_same_lines(class_lines:'ClassLines', classes:'anylist') -> 'None':
    """ Asserts that ClassLines and inspect.findsource give each class the same line number.
    """
    for class_ in classes:
        expected = inspect.findsource(class_)[1]
        actual = class_lines.get_line_number(class_)
        assert actual == expected, f'{class_.__qualname__}: {actual} != {expected}'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def module_cleanup() -> 'any_':
    """ Removes the test module from the registry of modules after each test.
    """
    yield
    _ = sys.modules.pop(ModuleCtx.Module_Name)

# ################################################################################################################################
# ################################################################################################################################

def test_internal_services_have_the_lines_of_inspect() -> 'None':
    classes = _get_internal_service_classes()
    assert classes

    _assert_same_lines(ClassLines(), classes)

# ################################################################################################################################

def test_nested_decorated_and_local_classes_have_the_lines_of_inspect(tmp_path:'Path', module_cleanup:'any_') -> 'None':
    module = _load_module(tmp_path, ModuleCtx.Source)
    _assert_same_lines(ClassLines(), _get_classes(module))

# ################################################################################################################################

def test_a_changed_source_is_parsed_again(tmp_path:'Path', module_cleanup:'any_') -> 'None':

    # The lines of the first version of the file are read ..
    class_lines = ClassLines()
    module = _load_module(tmp_path, ModuleCtx.Source)
    _assert_same_lines(class_lines, _get_classes(module))
    first_line = class_lines.get_line_number(module.Plain)

    # .. the file is replaced with one in which every class begins two lines lower ..
    changed = _load_module(tmp_path, ModuleCtx.Changed_Source)

    # .. and the same instance returns the new lines, not the ones of the first parse.
    _assert_same_lines(class_lines, _get_classes(changed))
    assert class_lines.get_line_number(changed.Plain) == first_line + 2

# ################################################################################################################################

def test_a_class_missing_from_the_source_raises_os_error(tmp_path:'Path', module_cleanup:'any_') -> 'None':

    # The class is created at run time, so no definition of it exists in the source of its module.
    _ = _load_module(tmp_path, ModuleCtx.Source)
    dynamic = type('Dynamic', (), {'__module__': ModuleCtx.Module_Name})

    with pytest.raises(OSError):
        _ = ClassLines().get_line_number(dynamic)

    with pytest.raises(OSError):
        _ = inspect.findsource(dynamic)

# ################################################################################################################################
# ################################################################################################################################
