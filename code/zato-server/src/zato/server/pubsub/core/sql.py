# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.odb.query.pubsub.delivery import \
    confirm_pubsub_msg_delivered     as _confirm_pubsub_msg_delivered, \
    get_delivery_server_for_sub_key  as _get_delivery_server_for_sub_key, \
    get_sql_messages_by_msg_id_list  as _get_sql_messages_by_msg_id_list, \
    get_sql_messages_by_sub_key      as _get_sql_messages_by_sub_key, \
    get_sql_msg_ids_by_sub_key       as _get_sql_msg_ids_by_sub_key
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anytuple, callable_, intset, strlist

# ################################################################################################################################
# ################################################################################################################################

class SQLAPI:

    def __init__(
        self,
        cluster_id,       # type: int
        new_session_func, # type: callable_
    ) -> 'None':
        self.cluster_id = cluster_id
        self.new_session_func = new_session_func

# ################################################################################################################################

    def get_delivery_server_for_sub_key(self, sub_key:'str', is_wsx:'bool') -> 'any_':
        with closing(self.new_session_func()) as session:
            return _get_delivery_server_for_sub_key(session, self.cluster_id, sub_key, is_wsx)

# ################################################################################################################################

    def get_sql_messages_by_sub_key(
        self,
        session,      # type: any_
        sub_key_list, # type: strlist
        last_sql_run, # type: float
        pub_time_max, # type: float
        ignore_list   # type: intset
    ) -> 'anytuple':
        """ Returns all SQL messages queued up for all keys from sub_key_list.
        """
        if not session:
            session = self.new_session_func()
            needs_close = True
        else:
            needs_close = False

        try:
            return _get_sql_messages_by_sub_key(session, self.cluster_id, sub_key_list,
                last_sql_run, pub_time_max, ignore_list)
        finally:
            if needs_close:
                session.close()

# ################################################################################################################################

    def get_initial_sql_msg_ids_by_sub_key(
        self,
        session:'SASession',
        sub_key:'str',
        pub_time_max:'float'
    ) -> 'anytuple':

        query = _get_sql_msg_ids_by_sub_key(session, self.cluster_id, sub_key, 0.0, pub_time_max)
        return query.all()

# ################################################################################################################################

    def get_sql_messages_by_msg_id_list(
        self,
        session,      # type: any_
        sub_key,      # type: str
        pub_time_max, # type: float
        msg_id_list   # type: strlist
    ) -> 'anytuple':

        query = _get_sql_messages_by_msg_id_list(session, self.cluster_id, sub_key, pub_time_max, msg_id_list)
        return query.all()

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(
        self,
        sub_key,                  # type: str
        delivered_pub_msg_id_list # type: strlist
    ) -> 'None':
        """ Sets in SQL delivery status of a given message to True.
        """
        with closing(self.new_session_func()) as session:
            _confirm_pubsub_msg_delivered(session, self.cluster_id, sub_key, delivered_pub_msg_id_list, utcnow_as_ms())
            session.commit()

# ################################################################################################################################
# ################################################################################################################################
