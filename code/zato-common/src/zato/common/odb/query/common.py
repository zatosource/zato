# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
    from zato.common.typing_ import any_, anylist, anylistnone, strlist
    Column = Column

# ################################################################################################################################
# ################################################################################################################################

RESTTable:'any_' = HTTPSOAP.__table__
TopicTable:'any_' = PubSubTopic.__table__

# ################################################################################################################################
# ################################################################################################################################

def get_object_list_by_columns(
    session:'SASession',
    columns:'anylist',
    order_by:'any_'=None
) -> 'anylist':
    """ Returns all ODB objects from a given table.
    """

    q = select(columns)
    if order_by is not None:
        q = q.order_by(order_by)

    result:'anylist' = session.execute(q).fetchall()
    return result

# ################################################################################################################################
# ################################################################################################################################

def get_object_list(
    session:'SASession',
    table:'BaseTable',
) -> 'anylist':
    """ Returns all ODB objects from a given table.
    """
    columns = [table.c.id, table.c.name]
    order_by = table.c.name.desc()
    result = get_object_list_by_columns(session, columns, order_by)
    return result

# ################################################################################################################################
# ################################################################################################################################

def get_object_list_by_where_impl(
    session:'SASession',
    table:'BaseTable',
    where_list:'str | anylistnone'
) -> 'anylist':
    """ Returns ODB objects matching the input query.
    """
    # Local variables
    where_list = where_list if where_list is not None else []
    where_list = where_list if isinstance(where_list, list) else [where_list]

    q = select([
        table.c.id,
        table.c.name,
        ]).\
        where(and_(*where_list))

    result:'anylist' = session.execute(q).fetchall()
    return result

# ################################################################################################################################

def get_object_list_by_where(
    session:'SASession',
    table:'BaseTable',
    value:'str | strlist',
    extra_where_list:'str | anylistnone',
    attr_name:'str',
    attr_func:'str',
) -> 'anylist':
    """ Returns ODB objects matching the input query.
    """
    # Local variables
    extra_where_list = extra_where_list or []
    extra_where_list = extra_where_list if isinstance(extra_where_list, list) else [extra_where_list]

    attr = getattr(table.c, attr_name)
    func = getattr(attr, attr_func)

    name_where:'any_' = func(value)

    where_list = [name_where]
    where_list.extend(extra_where_list)

    result = get_object_list_by_where_impl(session, table, where_list)
    return result

# ################################################################################################################################

def get_object_list_by_id_list(
    session:'SASession',
    table:'BaseTable',
    object_name_list:'str',
    extra_where_list:'str | anylistnone'=None
) -> 'anylist':
    """ Returns ODB objects whose ID is equal to the ones from input.
    """
    # Parameters for the where criteria
    attr_name = 'id'
    attr_func = 'in_'

    result = get_object_list_by_where(session, table, object_name_list, extra_where_list, attr_name, attr_func)
    return result

# ################################################################################################################################

def get_object_list_by_name_list(
    session:'SASession',
    table:'BaseTable',
    object_name_list:'str',
    extra_where_list:'str | anylistnone'=None
) -> 'anylist':
    """ Returns ODB objects whose name is equal to the ones from input.
    """
    # Parameters for the where criteria
    attr_name = 'name'
    attr_func = 'in_'

    result = get_object_list_by_where(session, table, object_name_list, extra_where_list, attr_name, attr_func)
    return result

# ################################################################################################################################

def get_object_list_by_name_contains(
    session:'SASession',
    table:'BaseTable',
    pattern:'str | strlist',
    extra_where_list:'str | anylistnone'=None
) -> 'anylist':
    """ Returns ODB objects whose name contains the input pattern.
    """
    # Parameters for the where criteria
    attr_name = 'name'
    attr_func = 'contains'

    result = get_object_list_by_where(session, table, pattern, extra_where_list, attr_name, attr_func)
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

    result = get_object_list_by_name_contains(session, table, pattern, connection_where)
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
# ################################################################################################################################
