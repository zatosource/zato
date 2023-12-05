# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, select

# ################################################################################################################################
# ################################################################################################################################

def get_object_list_by_name_pattern(session:'SASession', pattern:'str', is_channel:'bool') -> 'anylist':
    """ Returns objects matching the input query.
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
