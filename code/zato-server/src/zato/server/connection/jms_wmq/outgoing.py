# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.exception import ConnectorClosedException, IBMMQException

# ################################################################################################################################

if 0:
    from zato.server.service import Service

    Service = Service

# ################################################################################################################################

class WMQFacade:
    """ A IBM MQ facade for services so they aren't aware that sending WMQ
    messages actually requires us to use the Zato broker underneath.
    """

# ################################################################################################################################

    def __init__(self, service):
        # Current service on whose behalf we execute
        self.service = service # type: Service

# ################################################################################################################################

    def send(self, msg, outconn_name, queue_name, correlation_id='', msg_id='', reply_to='', expiration=None, priority=None,
        delivery_mode=None, raise_on_error=True):
        """ Puts a message on an IBM MQ MQ queue.
        """
        try:
            return self.service.server.connector_ibm_mq.send_wmq_message({
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
        except ConnectorClosedException as e:
            msg = 'IBM MQ connector is unavailable ({} -> {}); `{}'.format(outconn_name, queue_name, e.inner_exc.args[0])
            if raise_on_error:
                raise IBMMQException(msg)
            else:
                self.service.logger.info(msg)

# ################################################################################################################################

    def conn(self):
        """ Returns self. Added to make the facade look like other outgoing connection wrappers.
        """
        return self

# ################################################################################################################################
