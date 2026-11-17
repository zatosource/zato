# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.db_env.database import get_database_engine
from zato.common.rule_engine.api import RulesManager
from zato.common.rule_engine.changes import ChangePublisher
from zato.common.rule_engine.sql import RuleSQLBackend
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

# ################################################################################################################################
# ################################################################################################################################

# One engine, one facade and one hot-reloadable manager serve every view in the process.
_engine:'Engine | None' = None
_backend:'RuleSQLBackend | None' = None
_manager:'RulesManager | None' = None

# ################################################################################################################################
# ################################################################################################################################

def init_storage() -> 'None':
    """ Opens the Zato database, which holds the rule engine tables, and creates the typed SQL facade
    and the rules manager. Idempotent.
    """
    global _engine, _backend, _manager

    # A repeated call means everything already exists ..
    if _backend:
        return

    # .. the engine creates the tables on first run ..
    engine = get_database_engine()

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
