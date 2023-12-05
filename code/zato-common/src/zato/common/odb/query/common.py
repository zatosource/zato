# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import CONNECTION
from zato.common.odb.model import HTTPSOAP, PubSubTopic

# SQLAlchemy
from sqlalchemy import and_, select

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Column
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.odb.model.base import Base as BaseTable
    from zato.common.typing_ import any_, anylist, anylistnone, intlist, strlist
    Column = Column

# ################################################################################################################################
# ################################################################################################################################

RESTTable:'any_' = HTTPSOAP.__table__
TopicTable:'any_' = PubSubTopic.__table__

# ################################################################################################################################
# ################################################################################################################################

def get_object_list_by_where(
    session:'SASession',
    table:'BaseTable',
    where_list:'str | anylistnone'
) -> 'anylist':
    """ Returns ODB objects matching the input query.
    """
    # Local variables
    where_list = where_list or []
    where_list = where_list if isinstance(where_list, list) else [where_list]

    q = select([
        table.c.id,
        table.c.name,
        ]).\
        where(and_(*where_list))

    result:'anylist' = session.execute(q).fetchall()
    return result

# ################################################################################################################################

def get_object_list_by_name_pattern(
    session:'SASession',
    table:'BaseTable',
    pattern:'str',
    extra_where_list:'str | anylistnone'
) -> 'anylist':
    """ Returns ODB objects matching the input query.
    """
    # Local variables
    extra_where_list = extra_where_list or []
    extra_where_list = extra_where_list if isinstance(extra_where_list, list) else [extra_where_list]

    name_where:'any_' = table.c.name.contains(pattern)

    where_list = [name_where]
    where_list.extend(extra_where_list)

    result = get_object_list_by_where(session, table, where_list)
    return result

# ################################################################################################################################

def get_rest_list_by_name_pattern(session:'SASession', pattern:'str', is_channel:'bool',) -> 'anylist':
    """ Returns REST objects matching the pattern.
    """
    # Local variables
    table:'BaseTable' = RESTTable

    # Find out whether we need channels or outgoing connections ..
    if is_channel:
        connection = CONNECTION.CHANNEL
    else:
        connection = CONNECTION.OUTGOING

    # .. build an addition where part depending on what we need ..
    connection_where:'any_' = RESTTable.c.connection == connection

    result = get_object_list_by_name_pattern(session, table, pattern, connection_where)
    return result

# ################################################################################################################################

def get_rest_channel_list_by_name_pattern(session:'SASession', pattern:'str') -> 'anylist':
    """ Returns REST channels matching the pattern.
    """
    result = get_rest_list_by_name_pattern(session, pattern, True)
    return result

# ################################################################################################################################

def get_rest_outgoing_list_by_name_pattern(session:'SASession', pattern:'str') -> 'anylist':
    """ Returns REST outgoing connections matching the pattern.
    """
    result = get_rest_list_by_name_pattern(session, pattern, False)
    return result

# ################################################################################################################################

def get_topic_list_by_id_list(session:'SASession', topic_id_list:'intlist') -> 'anylist':
    """ Returns topics matching the input list of IDs.
    """
    where = TopicTable.c.id.in_(topic_id_list)
    result = get_object_list_by_where(session, TopicTable, where)
    return result

# ################################################################################################################################

def get_topic_list_by_name_list(session:'SASession', topic_name_list:'strlist') -> 'anylist':
    """ Returns topics matching the input list of names.
    """
    where = TopicTable.c.name.in_(topic_name_list)
    result = get_object_list_by_where(session, TopicTable, where)
    return result

# ################################################################################################################################

def get_topic_list_by_name_pattern(session:'SASession', pattern:'str') -> 'anylist':
    """ Returns topics matching the input list of names.
    """
    where = TopicTable.c.name.contains(pattern)
    result = get_object_list_by_where(session, TopicTable, where)
    return result

# ################################################################################################################################
# ################################################################################################################################
