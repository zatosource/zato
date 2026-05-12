# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutconnGraphQLWrapper:
    """ Config holder for an outgoing GraphQL connection.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server
        logger.info('Outgoing GraphQL connection `%s` registered', config.name)

# ################################################################################################################################

    def delete(self) -> 'None':
        pass

# ################################################################################################################################

    def build_wrapper(self) -> 'None':
        pass

# ################################################################################################################################

    def ping(self) -> 'None':
        from zato.server.connection.facade import GraphQLInvoker
        logger.info('Pinging GraphQL connection `%s` at `%s`', self.config['name'], self.config['address'])
        GraphQLInvoker.ping_config(self.config)
        logger.info('GraphQL connection `%s` pinged successfully', self.config['name'])

# ################################################################################################################################
# ################################################################################################################################
