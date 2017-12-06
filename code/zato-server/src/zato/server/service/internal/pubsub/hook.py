# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common import PUBSUB
from zato.common.util import is_class_pubsub_hook
from zato.common.odb.model import PubSubSubscription, PubSubTopic
from zato.common.odb.query import pubsub_hook_service
from zato.server.service import PubSubHook
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

hook_type_model = {
    PUBSUB.HOOK_TYPE.PUB: PubSubTopic,
    PUBSUB.HOOK_TYPE.SUB: PubSubSubscription,
}

# ################################################################################################################################

class GetHookService(AdminService):
    """ Returns ID and name of a hook service assigned to endpoint, if any is assigned at all.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'endpoint_id', 'hook_type')
        output_optional = ('id', 'name')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = pubsub_hook_service(session, self.request.input.cluster_id, self.request.input.endpoint_id,
                hook_type_model[self.request.input.hook_type])

# ################################################################################################################################

class GetHookServiceList(AdminService):
    """ Returns a list of pub/sub hook services currently deployed on this server.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id',)
        output_optional = ('id', 'name')
        output_repeated = True
        request_elem = 'zato_pubsub_get_hook_service_list_request'
        response_elem = 'zato_pubsub_get_hook_service_list_response'

    def handle(self):
        out = []

        for impl_name, details in self.server.service_store.services.iteritems():

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

# ################################################################################################################################

