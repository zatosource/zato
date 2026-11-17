# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# typing-extensions
from typing_extensions import TypeAlias

# Local
from .database import create_session_factory, SessionFactory
from .definitions import DefinitionStore
from .search import ContentSearch
from .versions import VersionStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.rule_engine.changes import ChangePublisher

    ChangePublisher = ChangePublisher
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

backend_type:TypeAlias = type['RuleSQLBackend']

# ################################################################################################################################
# ################################################################################################################################

class RuleSQLBackend:
    """ Pure-SQL entry point for rule definitions, their versions and content search.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        # Retain the one session boundary shared by the complete backend ..
        self.session_factory = session_factory

        # .. and expose each write pattern through its focused repository.
        self.definitions = DefinitionStore(session_factory)
        self.versions    = VersionStore(session_factory)
        self.search      = ContentSearch(session_factory)

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

    def set_change_publisher(self, change_publisher:'ChangePublisher') -> 'None':
        """ Makes every committed write of the mutating stores announce itself on the change stream.
        Dashboard installs this once at startup, so server caches learn of each change the moment it lands.
        """
        self.definitions.change_publisher = change_publisher
        self.versions.change_publisher = change_publisher

# ################################################################################################################################
# ################################################################################################################################
