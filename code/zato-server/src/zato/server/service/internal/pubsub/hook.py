# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import PUBSUB
from zato.common.util.api import is_class_pubsub_hook
from zato.common.odb.model import PubSubSubscription, PubSubTopic
from zato.common.odb.query import pubsub_hook_service
from zato.server.service import PubSubHook
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

hook_type_model = {
    PUBSUB.HOOK_TYPE.BEFORE_PUBLISH: PubSubTopic,
    PUBSUB.HOOK_TYPE.BEFORE_DELIVERY: PubSubSubscription,
}

# ################################################################################################################################

class GetHookService(AdminService):
    """ Returns ID and name of a hook service assigned to endpoint, if any is assigned at all.
    """
    class SimpleIO(AdminSIO):
        input_required = 'cluster_id', 'endpoint_id', 'hook_type'
        output_optional = 'id', 'name'

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:

            data = pubsub_hook_service(session, self.request.input.cluster_id, self.request.input.endpoint_id,
                hook_type_model[self.request.input.hook_type])

            if data:
                self.response.payload = data

# ################################################################################################################################

class GetHookServiceList(AdminService):
    """ Returns a list of pub/sub hook services currently deployed on this server.
    """
    class SimpleIO(AdminSIO):
        input_required = 'cluster_id'
        output_optional = 'id', 'name'
        output_repeated = True
        request_elem = 'zato_pubsub_get_hook_service_list_request'
        response_elem = 'zato_pubsub_get_hook_service_list_response'

    def handle(self) -> 'None':
        out = []

        for impl_name, details in self.server.service_store.services.items():

            if is_class_pubsub_hook(details['service_class']):
                service_id = self.server.service_store.impl_name_to_id[impl_name]
                out.append({
                    'id': service_id,
                    'name': details['name'],
                })

        self.response.payload[:] = out

# ################################################################################################################################

class PubSubHookDemo(PubSubHook):
    """ A demo pub/sub hook which logs incoming topic and queue messages.
    """
    def before_publish(self) -> 'None':
        """ Invoked for each pub/sub message before it is published to a topic.
        """
        self.logger.info('Demo hook before_publish invoked for pub_msg_id:`%s`, data:`%s`',
            self.request.input.ctx.msg.pub_msg_id, self.request.input.ctx.msg.data)

    def before_delivery(self) -> 'None':
        """ Invoked for each pub/sub message before it is delivered to an endpoint.
        """
        self.logger.info('Demo hook before_delivery invoked for pub_msg_id:`%s`, data:`%s`',
            self.request.input.ctx.msg.pub_msg_id, self.request.input.ctx.msg.data)

# ################################################################################################################################
