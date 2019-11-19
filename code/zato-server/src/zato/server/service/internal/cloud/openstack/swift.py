# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import CLOUD
from zato.common.odb.model import OpenStackSwift
from zato.common.odb.query import cloud_openstack_swift_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of OpenStack Swift connections.
    """
    _filter_by = OpenStackSwift.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_cloud_openstack_swift_get_list_request'
        response_elem = 'zato_cloud_openstack_swift_get_list_response'
        input_required = ('cluster_id',)
        output_required = (
            'id', 'name', 'is_active', 'auth_url', 'retries', 'starting_backoff', 'max_backoff', 'auth_version', 'key', 'pool_size')
        output_optional = (
            'user', 'is_snet', 'tenant_name', 'should_validate_cert', 'cacert', 'should_retr_ratelimit', 'needs_tls_compr',
            'custom_options')

    def get_data(self, session):
        return self._search(cloud_openstack_swift_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new OpenStack Swift connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_cloud_openstack_swift_create_request'
        response_elem = 'zato_cloud_openstack_swift_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'auth_url', 'retries', 'starting_backoff', 'max_backoff',
            'auth_version', 'key', 'should_validate_cert', 'should_retr_ratelimit', 'needs_tls_compr', 'is_snet')
        input_optional = ('user', 'tenant_name', 'cacert', 'custom_options', 'pool_size')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(OpenStackSwift.id).\
                filter(OpenStackSwift.cluster_id==input.cluster_id).\
                filter(OpenStackSwift.name==input.name).\
                first()

            if existing_one:
                raise Exception('An OpenStack Swift connection [{0}] already exists on this cluster'.format(input.name))

            try:
                item = OpenStackSwift()
                for name in self.SimpleIO.input_required + self.SimpleIO.input_optional:
                    setattr(item, name, self.request.input.get(name))

                session.add(item)
                session.commit()

                input.action = CLOUD.OPENSTACK_SWIFT_CREATE_EDIT.value
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('OpenStack Swift connection could not created, e:`{}`', format_exc())
                session.rollback()

                raise

class Edit(AdminService):
    """ Updates an OpenStack Swift connection.
    """
    class SimpleIO(Create.SimpleIO):
        request_elem = 'zato_cloud_openstack_swift_edit_request'
        response_elem = 'zato_cloud_openstack_swift_edit_response'
        input_required = ('id',) + Create.SimpleIO.input_required

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(OpenStackSwift.id).\
                filter(OpenStackSwift.cluster_id==input.cluster_id).\
                filter(OpenStackSwift.name==input.name).\
                filter(OpenStackSwift.id!=input.id).\
                first()

            if existing_one:
                raise Exception('An OpenStack Swift connection [{0}] already exists on this cluster'.format(input.name))

            try:
                item = session.query(OpenStackSwift).filter_by(id=input.id).one()
                old_name = item.name

                for name in self.SimpleIO.input_required + self.SimpleIO.input_optional:
                    setattr(item, name, self.request.input.get(name))

                session.add(item)
                session.commit()

                input.action = CLOUD.OPENSTACK_SWIFT_CREATE_EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('OpenStack Swift connection could not updated, e:`{}`', format_exc())
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an OpenStack Swift connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_cloud_openstack_swift_delete_request'
        response_elem = 'zato_cloud_openstack_swift_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OpenStackSwift).\
                    filter(OpenStackSwift.id==self.request.input.id).\
                    one()

                session.delete(item)
                session.commit()

                msg = {'action': CLOUD.OPENSTACK_SWIFT_DELETE.value, 'name': item.name, 'id':item.id}
                self.broker_client.publish(msg)

            except Exception:
                session.rollback()
                self.logger.error('OpenStack Swift connection could not deleted, e:`{}`', format_exc())

                raise
