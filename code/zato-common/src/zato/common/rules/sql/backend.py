# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# typing-extensions
from typing_extensions import TypeAlias

# Local
from .database import create_session_factory, SessionFactory
from .decisions import CapturePolicy, DecisionStore
from .definitions import DefinitionStore
from .events import EventStore
from .reporting import RuleReporting
from .versions import VersionStore
from .writer import DecisionBatchWriter, DecisionWriterConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

backend_type:TypeAlias = type['RuleSQLBackend']

# ################################################################################################################################
# ################################################################################################################################

class RuleSQLBackend:
    """ Complete pure-SQL entry point for rule definitions, history, activity and decision persistence.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        # Retain the one session boundary shared by the complete backend ..
        self.session_factory = session_factory

        # .. and expose each write pattern through its focused repository.
        self.definitions = DefinitionStore(session_factory)
        self.versions    = VersionStore(session_factory)
        self.events      = EventStore(session_factory)
        self.decisions   = DecisionStore(session_factory)
        self.reporting   = RuleReporting(session_factory)

# ################################################################################################################################

    @classmethod
    def from_engine(backend_class:'backend_type', engine:'Engine') -> 'RuleSQLBackend':
        """ Builds the complete backend over an existing SQLAlchemy engine.
        """
        # Give every repository the same non-expiring session factory ..
        session_factory = create_session_factory(engine)

        # .. and return the one facade that owns them.
        out = backend_class(session_factory)
        return out

# ################################################################################################################################

    def decision_writer(
        self,
        *,
        capture_policy:'CapturePolicy | None' = None,
        config:'DecisionWriterConfig | None' = None,
        ) -> 'DecisionBatchWriter':
        """ Creates an asynchronous decision writer over this backend's session factory.
        """
        # Construct the configured capture policy or its module-level defaults ..
        if capture_policy is None:
            capture_policy = CapturePolicy()

        # .. construct the configured writer bounds or their module-level defaults ..
        if config is None:
            config = DecisionWriterConfig()

        # .. and return a writer that shares this backend's database.
        out = DecisionBatchWriter(self.session_factory, capture_policy, config)
        return out

# ################################################################################################################################
# ################################################################################################################################
