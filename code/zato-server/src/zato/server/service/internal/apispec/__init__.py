# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps

# Zato
from zato.server.apispec import Generator
from zato.server.service import Bool, Service

# ################################################################################################################################

class GetAPISpec(Service):
    """ Returns API specifications for all services.
    """
    class SimpleIO:
        input_optional = ('cluster_id', 'query', Bool('return_internal'), 'format')

    def handle(self):
        cluster_id = self.request.input.get('cluster_id')
        if self.request.input.get('return_internal'):
            ignore_prefix = ''
        else:
            ignore_prefix = 'zato'

        if cluster_id and cluster_id != self.server.cluster_id:
            raise ValueError('Input cluster ID `%s` different than ours `%s`', cluster_id, self.server.cluster_id)

        data = Generator(self.server.service_store.services, self.server.sio_config,
            self.request.input.query).get_info(ignore_prefix=ignore_prefix)

        out = self.invoke('apispec.get-sphinx', {'data': data})

        self.response.payload = dumps(out)

# ################################################################################################################################
