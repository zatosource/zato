# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.rule_engine.changes import ChangePublisher
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Default_DB_URL, Env_DB_URL
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

# ################################################################################################################################
# ################################################################################################################################

# SQLite connections travel between the pooled sessions of one process, hence the flag.
_sqlite_connect_args = {'check_same_thread': False}

# One engine and one facade serve every alerting view in the process - in-process Python calls,
# no HTTP hop between web-admin and the rule store.
_engine:'Engine | None' = None
_backend:'RuleSQLBackend | None' = None

# ################################################################################################################################
# ################################################################################################################################

def init_storage() -> 'None':
    """ Creates the SQLAlchemy engine over the rule engine's database, the tables in it
    and the typed SQL facade. Idempotent.
    """
    global _engine, _backend

    # A repeated call means everything already exists ..
    if _backend:
        return

    # .. the URL is the same one the rule engine dashboard reads ..
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
