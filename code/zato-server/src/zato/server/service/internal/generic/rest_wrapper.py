# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):

    name = 'dev.generic.rest-wrapper.get-list'

    def handle(self) -> 'None':

        # Our response to produce
        out = []

        # Our service to invoke
        service_name = 'zato.http-soap.get-list'

        # Filter by this wrapper type from input
        wrapper_type = self.request.raw_request['wrapper_type']

        response = self.invoke(service_name, {
            'cluster_id': self.server.cluster_id,
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
            'paginate': False,
        }, skip_response_elem=True)

        for item in response:
            if item.get('wrapper_type') == wrapper_type:
                out.append(item)

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):

    name = 'dev.generic.rest-wrapper.create'
    output = 'name'

    def handle(self) -> 'None':

        # Our service to invoke
        service_name = 'zato.http-soap.create'

        # Base requst to create a new wrapper ..
        request = {
            'cluster_id': self.server.cluster_id,
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
            'url_path': '/'
        }

        # .. extend it with our own extra input ..
        request.update(self.request.raw_request)

        # .. and send it to the service.
        response = self.invoke(service_name, request, skip_response_elem=True)
        self.response.payload.name = response['name']

# ################################################################################################################################
# ################################################################################################################################
