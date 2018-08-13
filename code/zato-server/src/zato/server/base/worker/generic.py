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

    def on_broker_msg_GENERIC_CONNECTION_DELETE(self, msg):
        found = False
        for conn_type, value in self.generic_conn_api.items():
            if found:
                break
            for item in value:
                if found:
                    break
                if isinstance(item, dict):
                    for conn_config in item.values():
                        if conn_config['id'] == msg.id:
                            found = conn_config
                            break

        if not found:
            raise Exception('Could not find configuration matching input message `{}`'.format(msg))
        else:
            found.conn.delete()

# ################################################################################################################################
