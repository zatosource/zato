# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.rule_engine.api import RulesManager
from zato.common.rule_engine.changes import ChangePublisher
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.typing_ import cast_
from zato.rule_engine_dashboard.app.settings import Default_DB_URL, Env_DB_URL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

# ################################################################################################################################
# ################################################################################################################################

# SQLite connections travel between the pooled sessions of one process, hence the flag.
_sqlite_connect_args = {'check_same_thread': False}

# One engine, one facade and one hot-reloadable manager serve every view in the process.
_engine:'Engine | None' = None
_backend:'RuleSQLBackend | None' = None
_manager:'RulesManager | None' = None

# ################################################################################################################################
# ################################################################################################################################

def init_storage() -> 'None':
    """ Creates the SQLAlchemy engine over the shared database, the rule-engine tables in it,
    the typed SQL facade and the rules manager. Idempotent.
    """
    global _engine, _backend, _manager

    # A repeated call means everything already exists ..
    if _backend:
        return

    # .. the URL is the same one Django keeps its own tables under ..
    if url := os.environ.get(Env_DB_URL):
        pass
    else:
        url = Default_DB_URL

    # .. SQLite connections have to be usable across threads ..
    if url.startswith('sqlite'):
        engine = create_database_engine(url, connect_args=_sqlite_connect_args)
    else:
        engine = create_database_engine(url)

    # .. the tables come into being on first run and every later call is a no-op ..
    create_schema(engine)

    # .. and the facade plus the manager stay in the module for every view to share.
    _engine = engine
    _backend = RuleSQLBackend.from_engine(engine)
    _manager = RulesManager()

    # Every committed write announces itself on the change stream, which is how
    # server processes keep their invocation caches correct with no polling.
    _backend.set_change_publisher(ChangePublisher())

# ################################################################################################################################

def get_engine() -> 'Engine':
    """ Returns the shared SQLAlchemy engine, initializing storage on first use.
    """
    if _engine is None:
        init_storage()

    out = cast_('Engine', _engine)
    return out

# ################################################################################################################################

def get_backend() -> 'RuleSQLBackend':
    """ Returns the typed SQL facade, initializing storage on first use.
    """
    if _backend is None:
        init_storage()

    out = cast_('RuleSQLBackend', _backend)
    return out

# ################################################################################################################################

def get_manager() -> 'RulesManager':
    """ Returns the process-wide rules manager, initializing storage on first use.
    """
    if _manager is None:
        init_storage()

    out = cast_('RulesManager', _manager)
    return out

# ################################################################################################################################
# ################################################################################################################################
