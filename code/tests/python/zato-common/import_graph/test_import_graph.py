# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.util.import_graph import ImportGraph

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import strlist, strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The name of the directory that a project adds to sys.path
_root_name = 'src'

# ################################################################################################################################
# ################################################################################################################################

class _Project:
    """ A project tree under a temporary directory along with the import graph of its files.
    """

    def __init__(self, tmp_path:'Path', files:'strstrdict') -> 'None':

        # The graph keys files by their real paths
        base_directory = os.path.realpath(tmp_path)
        self.root = os.path.join(base_directory, _root_name)

        for relative_path, source in files.items():
            path = self.get_path(relative_path)
            directory = os.path.dirname(path)
            os.makedirs(directory, exist_ok=True)

            with open(path, 'w') as source_file:
                _ = source_file.write(source)

        self.graph = ImportGraph.build([self.root])

# ################################################################################################################################

    def get_path(self, relative_path:'str') -> 'str':
        parts = relative_path.split('/')
        out = os.path.join(self.root, *parts)
        return out

# ################################################################################################################################

    def get_relative_path(self, path:'str') -> 'str':
        relative_path = os.path.relpath(path, self.root)
        out = relative_path.replace(os.sep, '/')
        return out

# ################################################################################################################################

    def get_imports(self, relative_path:'str') -> 'strset':
        """ Returns the files that the given file imports, relative to the root.
        """
        out:'strset' = set()

        path = self.get_path(relative_path)

        if imported_paths := self.graph.imports.get(path):
            for imported_path in imported_paths:
                imported_relative_path = self.get_relative_path(imported_path)
                out.add(imported_relative_path)

        return out

# ################################################################################################################################

    def get_ordered_importers(self, relative_path:'str') -> 'strlist':
        """ Returns the files that import the given one, directly or not, in the order they are reloaded in.
        """
        out:'strlist' = []

        path = self.get_path(relative_path)
        importers = self.graph.get_ordered_importers(path)

        for importer in importers:
            importer_relative_path = self.get_relative_path(importer)
            out.append(importer_relative_path)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_imports_of_orders(tmp_path:'Path', source:'str', extra_files:'strstrdict | None'=None) -> 'strset':
    """ Builds a project with a common package and a service module with the given source,
    and returns what the service module imports.
    """
    files = {
        'common/__init__.py': '',
        'common/models.py': 'Customer = 1\nOrder = 2\n',
        'services/orders.py': source,
    }

    if extra_files:
        files.update(extra_files)

    project = _Project(tmp_path, files)

    out = project.get_imports('services/orders.py')
    return out

# ################################################################################################################################
# ################################################################################################################################

_common_models = {'common/__init__.py', 'common/models.py'}

# ################################################################################################################################
# ################################################################################################################################

def test_import_of_a_submodule_imports_its_package(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'import common.models\n')
    assert imports == _common_models

def test_import_with_an_alias(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'import common.models as models\n')
    assert imports == _common_models

def test_import_of_several_modules(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'import common.models, util.dates\n', {'util/dates.py': ''})
    assert imports == {'common/__init__.py', 'common/models.py', 'util/dates.py'}

def test_from_import_of_an_attribute(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'from common.models import Customer\n')
    assert imports == _common_models

def test_from_import_of_a_submodule(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'from common import models\n')
    assert imports == _common_models

def test_from_import_of_a_package_attribute(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'from common import Customer\n')
    assert imports == {'common/__init__.py'}

def test_star_import(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'from common.models import *\n')
    assert imports == _common_models

def test_parenthesized_import_over_several_lines(tmp_path:'Path') -> 'None':
    source = 'from common.models import (\n    Customer,\n    Order,\n)\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == _common_models

def test_import_with_a_backslash_continuation(tmp_path:'Path') -> 'None':
    source = 'from common.models import Customer, \\\n    Order\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == _common_models

# ################################################################################################################################
# ################################################################################################################################

def test_relative_import_of_a_sibling_module(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/__init__.py': '',
        'common/models.py': '',
        'common/api.py': 'from . import models\n',
    })

    assert project.get_imports('common/api.py') == _common_models

def test_relative_import_from_a_sibling_module(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/__init__.py': '',
        'common/models.py': '',
        'common/api.py': 'from .models import Customer\n',
    })

    assert project.get_imports('common/api.py') == _common_models

def test_relative_import_from_a_parent_package(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/__init__.py': '',
        'common/models.py': '',
        'common/billing/__init__.py': '',
        'common/billing/invoices.py': 'from ..models import Customer\n',
    })

    assert project.get_imports('common/billing/invoices.py') == _common_models

def test_relative_import_in_a_package_init(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/__init__.py': 'from .models import Customer\n',
        'common/models.py': '',
    })

    assert project.get_imports('common/__init__.py') == {'common/models.py'}

def test_relative_import_above_the_top_level_package(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/__init__.py': '',
        'common/api.py': 'from ...models import Customer\n',
        'models.py': '',
    })

    assert project.get_imports('common/api.py') == set()

# ################################################################################################################################
# ################################################################################################################################

def test_import_in_a_module_level_if(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'import sys\nif sys.platform:\n    import common.models\n')
    assert imports == _common_models

def test_import_in_a_try_block(tmp_path:'Path') -> 'None':
    source = 'try:\n    import common.models\nexcept ImportError:\n    pass\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == _common_models

def test_import_in_an_except_handler(tmp_path:'Path') -> 'None':
    source = 'try:\n    import json\nexcept ImportError:\n    import common.models\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == _common_models

def test_import_in_a_with_block(tmp_path:'Path') -> 'None':
    source = 'import contextlib\nwith contextlib.suppress(ImportError):\n    import common.models\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == _common_models

def test_import_in_a_class_body(tmp_path:'Path') -> 'None':
    source = 'class Orders:\n    from common.models import Customer\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == _common_models

def test_import_in_a_function_is_not_counted(tmp_path:'Path') -> 'None':
    source = 'def handle():\n    import common.models\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == set()

def test_import_in_a_method_is_not_counted(tmp_path:'Path') -> 'None':
    source = 'class Orders:\n    def handle(self):\n        import common.models\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == set()

def test_import_under_if_zero_is_not_counted(tmp_path:'Path') -> 'None':
    source = 'if 0:\n    from common.models import Customer\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == set()

def test_import_under_type_checking_is_not_counted(tmp_path:'Path') -> 'None':
    source = 'from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from common.models import Customer\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == set()

def test_import_under_typing_type_checking_is_not_counted(tmp_path:'Path') -> 'None':
    source = 'import typing\nif typing.TYPE_CHECKING:\n    from common.models import Customer\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == set()

def test_import_in_the_else_branch_of_if_zero(tmp_path:'Path') -> 'None':
    source = 'if 0:\n    import json\nelse:\n    from common.models import Customer\n'
    imports = _get_imports_of_orders(tmp_path, source)
    assert imports == _common_models

# ################################################################################################################################
# ################################################################################################################################

def test_service_module_names(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'services/orders.py': '',
    })

    path = project.get_path('services/orders.py')
    names = project.graph.get_module_names(path)

    assert names == ['services.orders', 'orders']

def test_service_module_imported_by_either_name(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'services/orders.py': '',
        'services/billing.py': 'import orders\n',
        'services/shipping.py': 'from services.orders import Order\n',
    })

    assert project.get_imports('services/billing.py') == {'services/orders.py'}
    assert project.get_imports('services/shipping.py') == {'services/orders.py'}

def test_modules_outside_of_the_project_produce_no_edges(tmp_path:'Path') -> 'None':
    imports = _get_imports_of_orders(tmp_path, 'import json\nimport os.path\nfrom collections import OrderedDict\n')
    assert imports == set()

def test_module_names_of_a_file_outside_of_the_roots(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'services/orders.py': '',
    })

    path = os.path.join(str(tmp_path), 'archive', 'src', 'common', 'models.py')
    names = project.graph.get_module_names(path)

    assert names == ['common.models']

# ################################################################################################################################
# ################################################################################################################################

def test_indirect_importers_follow_what_they_import(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/models.py': 'Customer = 1\n',
        'common/api.py': 'from common.models import Customer\n',
        'services/orders.py': 'import common.api\n',
    })

    importers = project.get_ordered_importers('common/models.py')
    assert importers == ['common/api.py', 'services/orders.py']

def test_diamond_returns_each_importer_once(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/shared.py': '',
        'common/left.py': 'import common.shared\n',
        'common/right.py': 'import common.shared\n',
        'services/orders.py': 'import common.left\nimport common.right\n',
    })

    importers = project.get_ordered_importers('common/shared.py')
    assert importers == ['common/left.py', 'common/right.py', 'services/orders.py']

def test_cycle_terminates_and_returns_both_members(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/models.py': '',
        'services/first.py': 'import common.models\nimport services.second\n',
        'services/second.py': 'import services.first\n',
        'services/orders.py': 'import services.second\n',
    })

    importers = project.get_ordered_importers('common/models.py')
    assert importers == ['services/first.py', 'services/second.py', 'services/orders.py']

def test_cycle_with_the_deployed_module(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'services/first.py': 'import services.second\n',
        'services/second.py': 'import services.first\n',
    })

    importers = project.get_ordered_importers('services/first.py')
    assert importers == ['services/second.py']

def test_module_without_importers(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/models.py': '',
        'services/orders.py': 'import json\n',
    })

    importers = project.get_ordered_importers('common/models.py')
    assert importers == []

def test_file_with_a_syntax_error_is_skipped(tmp_path:'Path') -> 'None':

    project = _Project(tmp_path, {
        'common/models.py': '',
        'common/api.py': 'import common.models\n',
        'services/broken.py': 'import common.models\ndef handle(:\n',
    })

    assert project.get_imports('services/broken.py') == set()

    importers = project.get_ordered_importers('common/models.py')
    assert importers == ['common/api.py']

# ################################################################################################################################
# ################################################################################################################################
