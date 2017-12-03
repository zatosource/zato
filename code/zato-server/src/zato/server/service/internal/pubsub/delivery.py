# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc

# Zato
from zato.server.service import AsIs, List
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class NotifyPubSubMessage(AdminService):
    """ Invoked with information about messages that need to be sent to a given enpoint's delivery task.
    It is guaranteed that it will be invoked on the same server that runs delivery tasks for all input sub_keys.
    For each non-GD messages given on input, or for each GD sub_key, invokes the corresponding delivery task
    which will in turn deliver them all to an endpoint the task is responsbile for.
    """
    class SimpleIO(AdminSIO):
        output_required = ('status_code',)

    def handle(self):
        self.logger.warn('NOTIFY %s', self.request.raw_request)
        self.response.payload.status_code = 'OK'

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from json import dumps, loads

# Bunch
from bunch import bunchify

# Zato
from zato.common import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.server.pubsub import PubSub
from zato.server.pubsub.task import PubSubTool
from zato.server.service import List
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class CreateDeliveryTask(AdminService):
    """ Starts a new delivery task for endpoints other than WebSockets (which are handled separately).
    """
    def handle(self):
        config = bunchify(loads(self.request.raw_request))
        func = getattr(self, '_handle_{}'.format(config.endpoint_type))
        func(config)

# ################################################################################################################################

    def _handle_amqp(self, config):
        pass

# ################################################################################################################################

    def _handle_files(self, config):
        pass

# ################################################################################################################################

    def _handle_ftp(self, config):
        pass

# ################################################################################################################################

    def _handle_rest(self, config):

        # Creates a pubsub_tool that will handle this subscription and registers it with pubsub
        pubsub_tool = PubSubTool(self.pubsub, self.server)

        # Makes this sub_key known to pubsub
        pubsub_tool.add_sub_key(config.sub_key)

        # Update in-RAM state of workers
        self.broker_client.publish({
            'action': BROKER_MSG_PUBSUB.SUB_KEY_SERVER_SET.value,
            'cluster_id': self.server.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'sub_key': config.sub_key,
            'endpoint_type': PUBSUB.ENDPOINT_TYPE.REST.id
        })

# ################################################################################################################################

    def _handle_service(self, config):
        pass

# ################################################################################################################################

    def _handle_sms_twilio(self, config):
        pass

# ################################################################################################################################

    def _handle_smtp(self, config):
        pass

# ################################################################################################################################

    def _handle_soap(self, config):
        pass

# ################################################################################################################################
'''
