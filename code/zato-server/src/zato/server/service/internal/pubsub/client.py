# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import PubSubPermission
from zato.common.odb.query import pubsub_permission_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub permissions (client assignments).
    """

    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_get_list_request'
        response_elem = 'zato_pubsub_permission_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'pattern', 'access_type'

    def get_data(self, session):
        return elems_with_opaque(pubsub_permission_list(session, self.request.input.cluster_id, False))

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub permission (client assignment).
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_create_request'
        response_elem = 'zato_pubsub_permission_create_response'
        input_required = 'sec_base_id', 'pattern', 'access_type'
        input_optional = 'cluster_id'
        output_required = 'id'

    def handle(self):
        input = self.request.input
        cluster_id = self.server.cluster_id

        # Validate patterns
        if not input.pattern or not input.pattern.strip():
            raise Exception('At least one pattern is required')
        
        patterns = [p.strip() for p in input.pattern.split('\n') if p.strip()]
        if not patterns:
            raise Exception('At least one valid pattern is required')

        with closing(self.odb.session()) as session:
            try:
                # Check if permission already exists for this security definition and pattern combination
                existing_perm = session.query(PubSubPermission).\
                    filter(PubSubPermission.cluster_id==cluster_id).\
                    filter(PubSubPermission.sec_base_id==input.sec_base_id).\
                    filter(PubSubPermission.pattern==input.pattern).\
                    filter(PubSubPermission.access_type==input.access_type).first()

                if existing_perm:
                    raise Exception('Permission already exists for this security definition, pattern combination and access type')

                # Create the permission
                permission = PubSubPermission()
                permission.sec_base_id = input.sec_base_id
                permission.access_type = input.access_type
                permission.pattern = '\n'.join(patterns)
                permission.cluster_id = cluster_id

                set_instance_opaque_attrs(permission, input)

                session.add(permission)
                session.commit()

            except Exception:
                session.rollback()
                raise
            else:
                input.id = permission.id
                input.action = PUBSUB.PERMISSION_CREATE.value
                self.broker_client.publish(input)

                self.response.payload.id = permission.id

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing pub/sub permission (client assignment).
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_edit_request'
        response_elem = 'zato_pubsub_permission_edit_response'
        input_required = 'id', 'pattern', 'access_type'
        input_optional = 'cluster_id'
        output_required = 'id'

    def handle(self):
        input = self.request.input
        cluster_id = self.server.cluster_id

        # Validate patterns
        if not input.pattern or not input.pattern.strip():
            raise Exception('At least one pattern is required')
        
        patterns = [p.strip() for p in input.pattern.split('\n') if p.strip()]
        if not patterns:
            raise Exception('At least one valid pattern is required')

        with closing(self.odb.session()) as session:
            try:
                permission = session.query(PubSubPermission).filter_by(id=input.id).one()

                # Update permission fields only
                permission.access_type = input.access_type
                permission.pattern = '\n'.join(patterns)

                set_instance_opaque_attrs(permission, input)

                session.commit()

            except Exception:
                session.rollback()
                raise
            else:
                input.action = PUBSUB.PERMISSION_EDIT.value
                self.broker_client.publish(input)

                self.response.payload.id = permission.id

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub permission (client assignment).
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_delete_request'
        response_elem = 'zato_pubsub_permission_delete_response'

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                permission = session.query(PubSubPermission).\
                    filter(PubSubPermission.id==self.request.input.id).\
                    one()

                session.delete(permission)
                session.commit()
            except Exception:
                session.rollback()
                raise
            else:
                self.request.input.action = PUBSUB.PERMISSION_DELETE.value
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
