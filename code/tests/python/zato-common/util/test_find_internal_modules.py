# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from types import ModuleType

# Zato
from zato.common.util.api import find_internal_modules

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import strlist
    Path = Path
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_root_name = 'test_root'

# ################################################################################################################################
# ################################################################################################################################

def _write_files(base:'Path', relative_paths:'strlist') -> 'str':
    """ Creates each of the files under the directory and returns the directory.
    """
    for relative_path in relative_paths:
        path = base / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text('')

    out = str(base)
    return out

# ################################################################################################################################

def _new_root(directories:'strlist') -> 'ModuleType':
    out = ModuleType(_root_name)
    out.__path__ = directories

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFindInternalModules:

    def test_single_directory(self, tmp_path:'Path') -> 'None':
        """ The package, its modules and its subpackages are found, and the root package is listed once.
        """
        directory = _write_files(tmp_path, ['__init__.py', 'first.py', 'sub/__init__.py', 'sub/second.py'])
        root = _new_root([directory])

        result = find_internal_modules(root)

        assert result == ['test_root', 'test_root.first', 'test_root.sub', 'test_root.sub.second']

    def test_every_path_entry(self, tmp_path:'Path') -> 'None':
        """ A package whose __path__ has several directories has the modules of each of them, and a subpackage
        present in more than one directory is listed once.
        """
        first = _write_files(tmp_path / 'first', ['__init__.py', 'one.py', 'shared/__init__.py', 'shared/a.py'])
        second = _write_files(tmp_path / 'second', ['__init__.py', 'two.py', 'shared/__init__.py', 'shared/b.py'])
        root = _new_root([first, second])

        result = find_internal_modules(root)

        assert result == [
            'test_root',
            'test_root.one',
            'test_root.shared',
            'test_root.shared.a',
            'test_root.shared.b',
            'test_root.two',
        ]

    def test_skipped_directories(self, tmp_path:'Path') -> 'None':
        """ Bytecode caches, hidden directories and files other than Python ones hold no modules.
        """
        directory = _write_files(tmp_path, [
            '__init__.py',
            'kept.py',
            '__pycache__/kept.cpython-312.py',
            '.hidden/module.py',
            'notes.txt',
        ])
        root = _new_root([directory])

        result = find_internal_modules(root)

        assert result == ['test_root', 'test_root.kept']

# ################################################################################################################################
# ################################################################################################################################
