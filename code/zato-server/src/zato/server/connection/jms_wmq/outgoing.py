# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib

# ################################################################################################################################

class WMQFacade(object):
    """ A IBM MQ facade for services so they aren't aware that sending WMQ
    messages actually requires us to use the Zato broker underneath.
    """

# ################################################################################################################################

    def __init__(self, service):
        self.service = service # Current service on whose behalf we execute

# ################################################################################################################################

    def send(self, msg, outconn_name, queue_name, correlation_id='', msg_id='', reply_to='', expiration=None, priority=None,
        delivery_mode=None):
        """ Puts a message on an IBM MQ MQ queue.
        """
        return self.service.server.send_wmq_message({
            'data': msg,
            'outconn_name': outconn_name,
            'queue_name': queue_name,
            'correlation_id': correlation_id,
            'msg_id': msg_id,
            'reply_to': reply_to,
            'expiration': expiration,
            'priority': priority,
            'delivery_mode': delivery_mode,
        })

# ################################################################################################################################

    def conn(self):
        """ Returns self. Added to make the facade look like other outgoing connection wrappers.
        """
        return self

# ################################################################################################################################
