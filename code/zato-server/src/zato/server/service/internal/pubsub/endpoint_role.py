# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import PUB_SUB
from zato.common.odb.model import PubSubEndpointRole
from zato.common.odb.query import pubsub_endpoint_role_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub endpoint/role pairs.
    """
    name = 'zato.pubsub.endpoint-owner.get-list'
    _filter_by = PubSubEndpointRole.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_endpoint_role_get_list_request'
        response_elem = 'zato_pubsub_endpoint_role_get_list_response'
        input_required = ('cluster_id',)
        input_optional = ('endpoint_id',)
        output_required = ('id', 'role', 'endpoint_id')

    def get_data(self, session):
        input = self.request.input
        return self._search(pubsub_endpoint_role_list, session, input.cluster_id, input.endpoint_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a pub/sub endpoint/role pair.
    """
    name = 'zato.pubsub.endpoint-owner.create'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_endpoint_role_create_request'
        response_elem = 'zato_pubsub_endpoint_role_create_response'
        input_required = ('cluster_id', 'endpoint_id', 'role')
        output_required = ('id',)

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:

            try:
                item = PubSubEndpointRole()
                item.cluster_id = input.cluster_id
                item.endpoint_id = input.endpoint_id
                item.role = input.role

                session.add(item)
                session.commit()

                input.action = PUB_SUB.ENDPOINT_ROLE_CREATE.value
                input.id = item.id
                self.broker_client.publish(input)

                self.response.payload.id = item.id

            except Exception, e:
                self.logger.error('Could not create a pub/sub endpoint/role pair, e:`%s`', format_exc(e))
                session.rollback()

                raise

# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub endpoint/role pair.
    """
    name = 'zato.pubsub.endpoint-owner.edit'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_endpoint_role_create_request'
        response_elem = 'zato_pubsub_endpoint_role_create_response'
        input_required = ('id', 'cluster_id', 'endpoint_id', 'role')
        output_required = ('id',)

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:

            try:
                item = session.query(PubSubEndpointRole).filter_by(id=input.id).one()
                item.cluster_id = input.cluster_id
                item.endpoint_id = input.endpoint_id
                item.role = input.role

                session.add(item)
                session.commit()

                input.action = PUB_SUB.ENDPOINT_ROLE_EDIT.value
                input.id = item.id
                self.broker_client.publish(input)

                self.response.payload.id = item.id

            except Exception, e:
                self.logger.error('Could not update a pub/sub endpoint/role pair, e:`%s`', format_exc(e))
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub endpoint/role pair.
    """
    name = 'zato.pubsub.endpoint-owner.delete'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_endpoint_role_delete_request'
        response_elem = 'zato_pubsub_endpoint_role_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(PubSubEndpointRole).\
                    filter(PubSubEndpointRole.id==self.request.input.id).\
                    one()

                item_id = item.id

                session.delete(item)
                session.commit()

                self.broker_client.publish({
                    'action': PUB_SUB.ENDPOINT_ROLE_DELETE.value,
                    'id':item_id,
                })

            except Exception, e:
                session.rollback()
                self.logger.error('Could not delete the pub/sub endpoint/role pair, e:`%s`', format_exc(e))

                raise

# ################################################################################################################################
