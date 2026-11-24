# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# pytest
import pytest

# Zato
from write_apis import count_rows, is_written, Write_APIs
from zato.common.test.zato_database import zato_database_engine

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('name', sorted(Write_APIs))
def test_write_visible_on_return(name:'str') -> 'None':
    """ What a write API writes is committed when the API returns - a connection of its own, opened before
    any other action of the caller, finds it.
    """
    api = Write_APIs[name](uuid4().hex)
    check = api.get_check()

    with zato_database_engine():
        api.prepare()
        api.write()

        assert is_written(check), f'{name} -> {check} -> {count_rows(check)}'

# ################################################################################################################################
# ################################################################################################################################
