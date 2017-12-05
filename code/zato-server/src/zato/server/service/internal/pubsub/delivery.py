# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.server.pubsub.task import PubSubTool
from zato.server.service.internal import AdminService

# ################################################################################################################################

class NotifyPubSubMessage(AdminService):
    """ Notifies pubsub about new messages available. It is guaranteed that this service will be always invoked
    on the server where each sub_key from sub_key_list exists.
    """
    def handle(self):
        # The request that we have on input needs to be sent to a pubsub_tool for each sub_key,
        # even if it is possibly the same pubsub_tool for more than one input sub_key.
        request = self.request.raw_request['request']

        for sub_key in request['sub_key_list']:
            pubsub_tool = self.pubsub.pubsub_tool_by_sub_key[sub_key]
            pubsub_tool.handle_new_messages(self.cid, request['has_gd'], [sub_key], request['non_gd_msg_list'])

# ################################################################################################################################

class CreateDeliveryTask(AdminService):
    """ Starts a new delivery task for endpoints other than WebSockets (which are handled separately).
    """
    def handle(self):
        config = self.request.raw_request
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
        pubsub_tool = PubSubTool(self.pubsub, self.server, PUBSUB.ENDPOINT_TYPE.REST.id)

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

class DeliverMessage(AdminService):
    """ Callback service invoked by delivery tasks for each message that needs to be delivered to a given endpoint.
    """
    def handle(self):
        self.logger.warn('111 %s', self.request.raw_request)

# ################################################################################################################################
