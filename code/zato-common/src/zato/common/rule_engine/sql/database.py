# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Any, Callable

# SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.db_env.engine import call_database

# ################################################################################################################################
# ################################################################################################################################

any_:TypeAlias = Any
anytuple:TypeAlias = tuple[Any, ...]
callable_:TypeAlias = Callable[..., Any]

# ################################################################################################################################
# ################################################################################################################################

class SessionFactory:
    """ Opens the sessions of the rule engine, whose loaded values remain readable after a transaction commits,
    and runs each write transaction as a serialized write of the Zato database.
    """

    def __init__(self, engine:'Engine') -> 'None':
        self.engine = engine
        self._sessionmaker = sessionmaker(bind=engine, expire_on_commit=False)

# ################################################################################################################################

    def __call__(self) -> 'Session':
        out = self._sessionmaker()
        return out

# ################################################################################################################################

    def write(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs func with a session and the given arguments in one write transaction and returns what func returns.
        """
        out = call_database(self.engine, self._run_write, func, args)
        return out

# ################################################################################################################################

    def _run_write(self, func:'callable_', args:'anytuple') -> 'any_':
        session = self._sessionmaker()

        try:
            with session.begin():
                out = func(session, *args)

        # The session is released whether the transaction committed or not
        finally:
            session.close()

        return out

# ################################################################################################################################
# ################################################################################################################################

def create_session_factory(engine:'Engine') -> 'SessionFactory':
    """ Creates the session factory of the rule engine over an engine.
    """
    out = SessionFactory(engine)
    return out

# ################################################################################################################################
# ################################################################################################################################
