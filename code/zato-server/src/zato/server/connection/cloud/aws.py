# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# boto3
from boto3.session import Session

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class AWSClient:
    """ A client for AWS APIs built around a boto3 session. Attribute access returns per-service API clients,
    e.g. client.s3 or client.sqs, while .client and .resource expose everything else that boto3 supports.
    All of our own attributes are prefixed with zato_ so that no AWS service name can ever be shadowed.
    """

    zato_region: 'str'
    zato_endpoint_url: 'str | None'
    zato_session: 'Session'
    zato_client_cache: 'stranydict'
    zato_resource_cache: 'stranydict'

    def __init__(self, config:'stranydict') -> 'None':

        # Extract the connection details ..
        self.zato_region = config['region']

        # .. an empty endpoint URL means the default, public AWS endpoints ..
        endpoint_url = config['endpoint_url']
        if not endpoint_url:
            endpoint_url = None
        self.zato_endpoint_url = endpoint_url

        # .. build the underlying boto3 session ..
        self.zato_session = Session(
            aws_access_key_id = config['access_key_id'],
            aws_secret_access_key = config['secret'],
            region_name = self.zato_region,
        )

        # .. and prepare caches for the per-service clients and resources.
        self.zato_client_cache = {}
        self.zato_resource_cache = {}

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':
        """ Unknown attributes are taken to be AWS service names, e.g. client.s3 is the same as client.client('s3').
        """

        # Never treat Python internals as AWS services, e.g. during copying or pickling.
        if name.startswith('_'):
            raise AttributeError(name)

        out = self.client(name)
        return out

# ################################################################################################################################

    def client(self, service_name:'str') -> 'any_':
        """ Returns a boto3 client for the given AWS service, creating and caching it first if needed.
        """

        # Build the client only if we do not have one for this service yet ..
        if service_name not in self.zato_client_cache:
            client = self.zato_session.client(service_name, endpoint_url=self.zato_endpoint_url)
            self.zato_client_cache[service_name] = client

        # .. and hand back the cached one.
        out = self.zato_client_cache[service_name]
        return out

# ################################################################################################################################

    def resource(self, service_name:'str') -> 'any_':
        """ Returns a boto3 resource for the given AWS service, creating and caching it first if needed.
        """

        # Build the resource only if we do not have one for this service yet ..
        if service_name not in self.zato_resource_cache:
            resource = self.zato_session.resource(service_name, endpoint_url=self.zato_endpoint_url)
            self.zato_resource_cache[service_name] = resource

        # .. and hand back the cached one.
        out = self.zato_resource_cache[service_name]
        return out

# ################################################################################################################################

    def ping(self) -> 'stranydict':
        """ Confirms that the credentials work by asking STS who we are.
        """
        sts = self.client('sts')

        out = sts.get_caller_identity()
        return out

# ################################################################################################################################
# ################################################################################################################################
