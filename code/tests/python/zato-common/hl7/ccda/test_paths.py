# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Where the converter is looked for - next to the Python binary unless the environment variable points elsewhere,
# and what counts as installed, which is the binary together with the C-CDA templates.

# stdlib
import os
import sys

# Zato
from zato.common.api import HL7
from zato.common.hl7.ccda.paths import get_binary_path, get_converter_dir, get_templates_dir, is_converter_installed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA

# ################################################################################################################################
# ################################################################################################################################

def _install(converter_dir:'any_', *, with_binary:'bool'=True, with_templates:'bool'=True) -> 'None':
    """ Lays out a converter directory with whichever of its parts are asked for.
    """
    if with_binary:
        _ = (converter_dir / _ccda.Binary_Name).write_bytes(b'')

    if with_templates:
        (converter_dir / _ccda.Templates_Dir_Name / _ccda.Templates_Set_Name).mkdir(parents=True)

# ################################################################################################################################
# ################################################################################################################################

def test_the_default_directory_is_next_to_the_python_binary(monkeypatch:'any_') -> 'None':
    monkeypatch.delenv(_ccda.Env_Dir, raising=False)

    expected = os.path.join(os.path.dirname(sys.executable), _ccda.Default_Dir_Name)
    assert get_converter_dir() == expected

# ################################################################################################################################

def test_the_environment_variable_names_the_directory(monkeypatch:'any_', tmp_path:'any_') -> 'None':
    monkeypatch.setenv(_ccda.Env_Dir, str(tmp_path))

    assert get_converter_dir() == str(tmp_path)
    assert get_binary_path() == os.path.join(str(tmp_path), _ccda.Binary_Name)
    assert get_templates_dir() == os.path.join(str(tmp_path), _ccda.Templates_Dir_Name, _ccda.Templates_Set_Name)

# ################################################################################################################################

def test_installed_means_both_the_binary_and_the_templates(monkeypatch:'any_', tmp_path:'any_') -> 'None':
    monkeypatch.setenv(_ccda.Env_Dir, str(tmp_path))
    assert is_converter_installed() is False

    _install(tmp_path, with_templates=False)
    assert is_converter_installed() is False

    _install(tmp_path, with_binary=False)
    assert is_converter_installed() is True

# ################################################################################################################################

def test_templates_alone_are_not_an_installation(monkeypatch:'any_', tmp_path:'any_') -> 'None':
    monkeypatch.setenv(_ccda.Env_Dir, str(tmp_path))

    _install(tmp_path, with_binary=False)
    assert is_converter_installed() is False

# ################################################################################################################################
# ################################################################################################################################
