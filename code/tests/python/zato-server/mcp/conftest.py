# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from importlib import import_module

# pytest
import pytest

# Zato
from zato.common.pubsub.sql.config import ModuleCtx as PubSubConfigCtx
from zato.common.pubsub.sql.schema import pubsub_db_file_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_

    any_ = any_
    MonkeyPatch = MonkeyPatch
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# Make the suite's own helper modules, e.g. connection_stubs, importable by name
_this_directory = os.path.dirname(__file__)
sys.path.insert(0, _this_directory)

# ################################################################################################################################
# ################################################################################################################################

class _NoCheckpointer:
    """ Takes the place of the background checkpoints of the pub/sub database, which play no part in the sessions.
    """

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        pass

    def start(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def pubsub_db_path(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'str':
    """ Points the pub/sub database, which holds the MCP sessions, at a file of the test.
    """
    out = str(tmp_path / pubsub_db_file_name)

    monkeypatch.setenv(PubSubConfigCtx.Env_Path, out)
    engine_module = import_module('zato.common.db_env.engine')
    monkeypatch.setattr(engine_module, 'WALCheckpointer', _NoCheckpointer)

    return out

# ################################################################################################################################
# ################################################################################################################################
