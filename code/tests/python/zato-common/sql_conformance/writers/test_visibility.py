# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from uuid import uuid4

# pytest
import pytest

# Zato
from write_apis import count_rows, is_written, Write_APIs
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.test.zato_database import file_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('name', sorted(Write_APIs))
def test_write_visible_on_return(tmp_path:'Path', name:'str') -> 'None':
    """ What a write API writes is committed when the API returns - a connection of its own, opened before
    any other action of the caller, finds it.
    """
    db_path = os.path.join(tmp_path, DatabaseEnv.File_Name)
    api = Write_APIs[name](uuid4().hex)
    check = api.get_check()

    with file_database_engine(tmp_path):
        api.prepare()
        api.write()

        assert is_written(db_path, check), f'{name} -> {check} -> {count_rows(db_path, check)}'

# ################################################################################################################################
# ################################################################################################################################
