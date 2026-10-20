# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
from pytest import fixture

# Zato
from zato.common.file_transfer.spool import Env_Spool_Directory

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@fixture(autouse=True)
def spool_directory(tmp_path:'any_', monkeypatch:'any_') -> 'any_':
    """ The spool files each test creates go to that test's own temporary directory, which is also returned
    so a test can check what is left in it.
    """
    monkeypatch.setenv(Env_Spool_Directory, str(tmp_path))
    return tmp_path

# ################################################################################################################################
# ################################################################################################################################
