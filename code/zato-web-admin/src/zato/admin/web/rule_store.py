# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.db_env.database import get_database_engine
from zato.common.rule_engine.changes import ChangePublisher
from zato.common.rule_engine.sql import RuleSQLBackend
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

# ################################################################################################################################
# ################################################################################################################################

# One engine and one facade serve every alerting view in the process - in-process Python calls,
# no HTTP hop between web-admin and the rule store.
_engine:'Engine | None' = None
_backend:'RuleSQLBackend | None' = None

# ################################################################################################################################
# ################################################################################################################################

def init_storage() -> 'None':
    """ Opens the Zato database, which holds the rule engine tables, and creates the typed SQL facade. Idempotent.
    """
    global _engine, _backend

    # A repeated call means everything already exists ..
    if _backend:
        return

    # .. the engine creates the tables on first run ..
    engine = get_database_engine()

    # .. and the facade stays in the module for every view to share.
    _engine = engine
    _backend = RuleSQLBackend.from_engine(engine)

    # Every committed write announces itself on the change stream, which is how
    # server processes keep their loaded rulesets correct with no polling.
    _backend.set_change_publisher(ChangePublisher())

    # A new environment gains the alerting vocabulary and the default alert rules -
    # a store that already holds them keeps what it has.
    ensure_alerting_definitions(_backend)

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
# ################################################################################################################################
