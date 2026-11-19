# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib
import os
import sys

# pytest
import pytest

# Zato
from zato.common.util.python_ import import_module_by_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, generator_

    strgen = generator_[str, None, None]

# ################################################################################################################################
# ################################################################################################################################

# A package name that no other module of the environment uses
_package_name = 'zato_test_reload_billing'

# ################################################################################################################################
# ################################################################################################################################

def _write(path:'str', source:'str') -> 'None':
    with open(path, 'w') as source_file:
        _ = source_file.write(source)

# ################################################################################################################################

def _remove_package_modules() -> 'None':
    for name in list(sys.modules):
        if name.startswith(_package_name):
            del sys.modules[name]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def package_directory(tmp_path:'Path', monkeypatch:'any_') -> 'strgen':
    """ A package with a models module and an invoices module that imports it, importable from sys.path.
    """
    package_path = os.path.join(str(tmp_path), _package_name)
    os.makedirs(package_path)

    _write(os.path.join(package_path, '__init__.py'), '')
    _write(os.path.join(package_path, 'models.py'), 'Rate = 1\n')

    # A rewritten file of the same size within the same second would otherwise be loaded from its stale bytecode
    monkeypatch.setattr(sys, 'dont_write_bytecode', True)

    monkeypatch.syspath_prepend(str(tmp_path))
    _remove_package_modules()

    yield package_path

    _remove_package_modules()

# ################################################################################################################################
# ################################################################################################################################

def test_reload_replaces_the_module_under_its_name(package_directory:'str') -> 'None':

    models = importlib.import_module(f'{_package_name}.models')
    assert models.Rate == 1

    models_path = os.path.join(package_directory, 'models.py')
    _write(models_path, 'Rate = 2\n')

    _ = import_module_by_path(models_path, [f'{_package_name}.models'])

    reloaded = sys.modules[f'{_package_name}.models']
    assert reloaded.Rate == 2

# ################################################################################################################################

def test_reload_updates_the_parent_package_attribute(package_directory:'str') -> 'None':

    package = importlib.import_module(_package_name)
    _ = importlib.import_module(f'{_package_name}.models')

    models_path = os.path.join(package_directory, 'models.py')
    _write(models_path, 'Rate = 3\n')

    _ = import_module_by_path(models_path, [f'{_package_name}.models'])

    # This is what `from package import models` reads
    assert package.models.Rate == 3

# ################################################################################################################################

def test_reload_under_other_names_already_imported(package_directory:'str') -> 'None':

    _ = importlib.import_module(f'{_package_name}.models')
    sys.modules['zato_test_reload_models'] = sys.modules[f'{_package_name}.models']

    models_path = os.path.join(package_directory, 'models.py')
    _write(models_path, 'Rate = 4\n')

    try:
        _ = import_module_by_path(models_path, [f'{_package_name}.models', 'zato_test_reload_models', 'zato_test_not_imported'])

        assert sys.modules['zato_test_reload_models'].Rate == 4
        assert 'zato_test_not_imported' not in sys.modules

    finally:
        del sys.modules['zato_test_reload_models']

# ################################################################################################################################

def test_reload_imports_the_parent_package_first(package_directory:'str') -> 'None':

    models_path = os.path.join(package_directory, 'models.py')

    _ = import_module_by_path(models_path, [f'{_package_name}.models'])

    # This is what `import package.models` reads after the package is first imported by name
    package = sys.modules[_package_name]
    assert package.models.Rate == 1

# ################################################################################################################################

def test_reloaded_package_keeps_its_submodules(package_directory:'str') -> 'None':

    _ = importlib.import_module(f'{_package_name}.models')

    init_path = os.path.join(package_directory, '__init__.py')
    _write(init_path, 'Currency = "USD"\n')

    _ = import_module_by_path(init_path, [_package_name])

    package = sys.modules[_package_name]
    assert package.Currency == 'USD'
    assert package.models.Rate == 1

# ################################################################################################################################
# ################################################################################################################################
