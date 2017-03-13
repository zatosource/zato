# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime
from traceback import format_exc
from urlparse import urlparse

# Zato
from zato.common import CHANNEL, DATA_FORMAT, PUB_SUB, ZatoException
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointRole, PubSubEndpointOwner, PubSubOwner, PubSubSubscription, \
     PubSubSubscriptionItem
from zato.common.util import new_cid
from zato.server.service import Dict, Service

# ################################################################################################################################

class CommonSimpleIO:
    input_required = ('name',)
    input_optional = ('callback', 'api_key_header', 'api_key', 'pattern', Dict('patterns'))
    output_optional = ('sub_key', 'message')

# ################################################################################################################################

class Subscribe(Service):
    """ Subscribes either external or internal endpoints to patterns.
    """
    class SimpleIO(CommonSimpleIO):
        input_required = CommonSimpleIO.input_required + ('is_internal',)
        input_optional = CommonSimpleIO.input_optional + ('owner_parent_id',)

    def handle(self):
        input = self.request.input
        data_format = input.get('data_format', DATA_FORMAT.JSON)
        cluster_id = self.server.cluster_id
        sub_key = new_cid()

        self.logger.warn('\n' + str(self.request.input))

        # Look up owner by name of create the owner if that name doesn't exist yet.
        with closing(self.odb.session()) as session:

            # Get parent owner first - may be provided on input by ID or implicitly through is_external flag.
            if input.owner_parent_id:
                parent = session.query(PubSubOwner).\
                    filter(PubSubOwner.id==input.owner_parent_id).\
                    filter(PubSubOwner.cluster_id==cluster_id).\
                    one()
            else:
                parent = session.query(PubSubOwner).\
                    filter(PubSubOwner.name=='user.root').\
                    filter(PubSubOwner.parent_id.is_(None)).\
                    filter(PubSubOwner.cluster_id==cluster_id).\
                    one()

            # Ok, we have the parent owner, now find the owner itself.
            owner = session.query(PubSubOwner).\
                filter(PubSubOwner.name==input.name).\
                filter(PubSubOwner.parent_id==parent.id).\
                filter(PubSubOwner.cluster_id==cluster_id).\
                first()

            # No such owner, so we must create it now
            if not owner:
                owner = PubSubOwner()
                owner.is_internal = input.is_internal
                owner.name = input.name
                owner.parent_id = parent.id
                owner.cluster_id = cluster_id

            # Create an endpoint and make it belong to the newly created owner.
            endpoint = PubSubEndpoint()
            endpoint.is_internal = input.is_internal
            endpoint.cluster_id = cluster_id

            endpoint_owner = PubSubEndpointOwner()
            endpoint_owner.endpoint = endpoint
            endpoint_owner.owner = owner
            endpoint_owner.role = PUB_SUB.OWNER_ROLE.OWNER

            # Make the endpoint a subscriber to the subscription pattern that we will soon create
            endpoint_role = PubSubEndpointRole()
            endpoint_role.endpoint = endpoint
            endpoint_role.role = PUB_SUB.ENDPOINT_ROLE.SUBSCRIBER
            endpoint_role.cluster_id = cluster_id

            subscription = PubSubSubscription()
            subscription.creation_time = datetime.utcnow()
            subscription.sub_key = sub_key
            subscription.is_active = True
            subscription.is_internal = input.is_internal
            subscription.protocol = PUB_SUB.PROTOCOL.HTTP_SOAP # TODO: Add AMQP
            subscription.data_format = data_format
            subscription.is_durable = True
            subscription.has_gd = False # TODO: Add GD
            subscription.endpoint = endpoint
            subscription.cluster_id = cluster_id

            if input.callback:
                # TODO: Create HTTP outconn
                parsed = urlparse(input.callback)

                if parsed.username and not parsed.password:
                    raise ZatoException(self.cid, 'Password is required if username is')

                print(333, parsed)
                print(333, parsed.username)
                print(333, parsed.password)

            subscription_item = PubSubSubscriptionItem()
            subscription_item.is_active = True
            subscription_item.by_msg_attr = True
            subscription_item.by_pub_attr = False
            subscription_item.has_glob = '*' in input.pattern
            subscription_item.key = 'default'
            subscription_item.value = 'dummy-{}'.format(self.time.utcnow())

            session.add(owner)
            session.add(endpoint)
            session.add(endpoint_owner)
            session.add(endpoint_role)
            session.add(subscription)
            session.add(subscription_item)

            #session.commit()

            self.logger.info('Created a new subscription `%s`', sub_key)

        #self.response.payload = ''

# ################################################################################################################################

class ExternalSubscribe(Service):
    """ Lets external endpoints subscribe using HTTP.
    """
    class SimpleIO(CommonSimpleIO):
        pass

    def handle(self):
        input = self.request.input
        input.is_internal = False

        try:
            self.response.payload = self.invoke(Subscribe.get_name(), input)
        except ZatoException, e:
            self.response.payload.message = e.message

# ################################################################################################################################
