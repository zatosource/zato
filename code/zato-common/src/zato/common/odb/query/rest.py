# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import CONNECTION
from zato.common.odb.model import HTTPSOAP

# SQLAlchemy
from sqlalchemy import and_, select

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Column
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist
    Column = Column

# ################################################################################################################################
# ################################################################################################################################

RESTTable = HTTPSOAP.__table__

# ################################################################################################################################
# ################################################################################################################################

def _get_rest_list_by_name_pattern(session:'SASession', pattern:'str', is_channel:'bool') -> 'anylist':
    """ Returns REST objects matching the input query.
    """
    if is_channel:
        connection = CONNECTION.CHANNEL
    else:
        connection = CONNECTION.OUTGOING

    name_where = RESTTable.c.name.contains(pattern)
    connection_where = RESTTable.c.connection == connection

    q = select([
        RESTTable.c.id,
        RESTTable.c.name,
        ]).\
        where(and_(
            name_where,
            connection_where
        ))

    result = session.execute(q).fetchall()
    return result

# ################################################################################################################################

def get_rest_channel_list_by_name_pattern(session:'SASession', pattern:'str') -> 'anylist':
    """ Returns REST channels matching the pattern.
    """
    result = _get_rest_list_by_name_pattern(session, pattern, True)
    return result

# ################################################################################################################################

def get_rest_outgoing_list_by_name_pattern(session:'SASession', pattern:'str') -> 'anylist':
    """ Returns REST outgoing connections matching the pattern.
    """
    result = _get_rest_list_by_name_pattern(session, pattern, False)
    return result

# ################################################################################################################################
# ################################################################################################################################
