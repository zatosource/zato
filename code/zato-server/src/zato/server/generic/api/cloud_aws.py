# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import AWS
from zato.common.typing_ import cast_
from zato.server.connection.cloud.aws import AWSClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Defaults for fields that the create path may not have supplied,
# e.g. when a connection is created directly through zato.generic.connection.create.
cloud_aws_config_defaults = {
    'region': AWS.Default.Region,
    'endpoint_url': '',
    'access_key_id': '',
    'pool_size': AWS.Default.Pool_Size,
}

# Values of these configuration keys may arrive as strings from opaque storage and need to be integers.
cloud_aws_int_config_keys = ['pool_size']

# ################################################################################################################################
# ################################################################################################################################

class CloudAWSWrapper(Wrapper):
    """ Wraps a queue of connections to AWS.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':

        # The queue reports this address in logs - prefer the custom endpoint if one is configured,
        # otherwise point to the connection's region.
        endpoint_url = config['endpoint_url']
        if not endpoint_url:
            region = config['region']
            endpoint_url = f'aws://{region}'
        config['auth_url'] = endpoint_url

        super(CloudAWSWrapper, self).__init__(config, 'AWS', server)

        # A single client shared by all the services that access this connection directly, e.g. through self.aws.
        # This is safe because boto3 sessions and clients are thread-safe and maintain their own HTTP connection pools.
        self.shared_client = AWSClient(config)

# ################################################################################################################################

    def add_client(self):

        try:
            conn = AWSClient(self.config)
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding an AWS client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('AWSClient', client)
            _:'any_' = client.ping()

# ################################################################################################################################

    def delete(self, ignored_reason:'strnone'=None):
        pass

# ################################################################################################################################
# ################################################################################################################################
