# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps

# Zato
from zato.server.apispec import Generator
from zato.server.service import Service

# ################################################################################################################################

class GetAPISpec(Service):
    """ Returns API specifications for all services.
    """
    class SimpleIO:
        input_optional = ('cluster_id', 'query',)

    def handle(self):
        cluster_id = self.request.input.get('cluster_id')

        if cluster_id and cluster_id != self.server.cluster_id:
            raise ValueError('Input cluster ID `%s` different than ours `%s`', cluster_id, self.server.cluster_id)

        self.response.payload = dumps(Generator(self.server.service_store.services, self.request.input.query).get_info())

# ################################################################################################################################
