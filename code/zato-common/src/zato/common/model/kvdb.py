# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class KVDB:
    def __init__(self):
        self.name = ''
        self.host = ''
        self.port = None # type: int
        self.db = 0
        self.use_redis_sentinels = False
        self.redis_sentinels = ''
        self.redis_sentinels_master = ''

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

# Zato
from zato.common.util import get_config
from zato.server.service import Bool, Int, Service, SIOElem
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Union as union
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class MyService(AdminService):
    name = 'kvdb1.get-list'

    class SimpleIO:
        input_optional = 'object_id', 'name'
        output_optional = 'name', 'host', Int('port'), 'db', Bool('use_redis_sentinels'), \
            'redis_sentinels', 'redis_sentinels_master'
        default_value = None

# ################################################################################################################################

    def get_data(self):

        # Response to produce
        out = []

        # For now, we only return one item containing data read from server.conf
        item = {
            'name': 'default'
        }

        repo_location = self.server.repo_location
        config_name   = 'server.conf'

        config = get_config(repo_location, config_name, bunchified=False)
        config = config['kvdb']

        for elem in self.SimpleIO.output_optional:

            # This will not exist in server.conf
            if elem == 'name':
                continue

            # Extract the embedded name or use it as is
            name = elem.name if isinstance(elem, SIOElem) else elem

            # Add it to output
            item[name] = config[name]

        # Add our only item to response
        out.append(item)

        return out

# ################################################################################################################################

    def handle(self):

        self.response.payload[:] = self.get_data()

# ################################################################################################################################
# ################################################################################################################################
'''
