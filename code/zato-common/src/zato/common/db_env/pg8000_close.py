# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The close of the connections that the pool of SQLAlchemy discards. A connection whose session PostgreSQL ended already,
# e.g. one that a server taking over terminated, raises InterfaceError while pg8000 announces the end of the session
# over its broken socket, after pg8000 has released the socket. Such a connection has nothing left to close.

# stdlib
from logging import getLogger

# pg8000
from pg8000.exceptions import InterfaceError

# SQLAlchemy
from sqlalchemy.dialects.postgresql.pg8000 import PGDialect_pg8000

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _do_close(self:'any_', dbapi_connection:'any_') -> 'None':
    """ Closes a connection of pg8000, one whose session ended already included.
    """
    try:
        dbapi_connection.close()

    # pg8000 raises InterfaceError only for a connection that is closed already or whose socket broke during the close,
    # and it has released the socket in both cases.
    except InterfaceError as e:
        logger.debug('Connection closed after its session had ended -> %s', e)

# ################################################################################################################################

def install() -> 'None':
    """ Makes the pg8000 dialect close the connections whose sessions ended already without an error,
    which the pool of SQLAlchemy would log with its traceback otherwise. The terminate of a connection runs this close too.
    """
    dialect_class:'any_' = PGDialect_pg8000
    dialect_class.do_close = _do_close

# ################################################################################################################################
# ################################################################################################################################
