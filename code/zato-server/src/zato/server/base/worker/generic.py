# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.base.worker.common import WorkerImpl

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

    def on_broker_msg_GENERIC_CONNECTION_DELETE(self, msg):
        self._delete_generic_connection(msg)

# ################################################################################################################################
