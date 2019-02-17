# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.base.worker.common import WorkerImpl
from zato.server.generic.connection import GenericConnection

# ################################################################################################################################

class Generic(WorkerImpl):
    """ Handles broker messages destined for generic objects, such as connections.
    """
    def __init__(self):
        super(Generic, self).__init__()

# ################################################################################################################################

    def _find_conn_info(self, item_id):
        found_conn_dict = None
        found_name = None

        for conn_type, value in self.generic_conn_api.items():
            for conn_name, conn_dict in value.items():
                if conn_dict['id'] == item_id:
                    return conn_dict, value

        return found_conn_dict, found_name

# ################################################################################################################################

    def _delete_generic_connection(self, msg):

        conn_dict, conn_value = self._find_conn_info(msg.id)

        if not conn_dict:
            raise Exception('Could not find configuration matching input message `{}`'.format(msg))
        else:
            conn_dict.conn.delete()
            del conn_value[conn_dict['name']]

# ################################################################################################################################

    def _create_generic_connection(self, msg, needs_roundtrip=False, skip=None):

        # This roundtrip is needed to re-format msg in the format the underlying .from_bunch expects
        # in case this is a broker message rather than a startup one.
        if needs_roundtrip:
            conn = GenericConnection.from_dict(msg, skip)
            msg = conn.to_sql_dict(True)

        item = GenericConnection.from_bunch(msg)
        item_dict = item.to_dict(True)

        item_dict.queue_build_cap = self.server.fs_server_config.misc.queue_build_cap
        item_dict.auth_url = msg.address

        config_attr = self.generic_conn_api[item.type_]
        wrapper = self._generic_conn_handler[item.type_]

        config_attr[msg.name] = item_dict
        config_attr[msg.name].conn = wrapper(item_dict, self.server)
        config_attr[msg.name].conn.build_queue()

# ################################################################################################################################

    def reconnect_generic(self, conn_id):
        found_conn_dict, found_name = self._find_conn_info(conn_id)
        self.on_broker_msg_GENERIC_CONNECTION_EDIT(found_conn_dict, ['conn', 'parent'])

# ################################################################################################################################

    def on_broker_msg_GENERIC_CONNECTION_CREATE(self, msg):
        self._create_generic_connection(msg, True)

# ################################################################################################################################

    def on_broker_msg_GENERIC_CONNECTION_DELETE(self, msg):
        self._delete_generic_connection(msg)

# ################################################################################################################################

    def on_broker_msg_GENERIC_CONNECTION_EDIT(self, msg, skip=None):
        self._delete_generic_connection(msg)
        self._create_generic_connection(msg, True, skip)

# ################################################################################################################################
