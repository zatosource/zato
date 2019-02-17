# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, OpenStackSecurity
from zato.common.odb.query import openstack_security_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of OpenStack definitions available.
    """
    _filter_by = OpenStackSecurity.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_openstack_get_list_request'
        response_elem = 'zato_security_openstack_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username')

    def get_data(self, session):
        return self._search(openstack_security_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new OpenStack definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_openstack_create_request'
        response_elem = 'zato_security_openstack_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'username')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(OpenStackSecurity).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(OpenStackSecurity.name==input.name).first()

                if existing_one:
                    raise Exception('OpenStack definition [{0}] already exists on this cluster'.format(input.name))

                auth = OpenStackSecurity(None, input.name, input.is_active, input.username, input.password, cluster)

                session.add(auth)
                session.commit()

            except Exception:
                msg = 'Could not create an OpenStack definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.id = auth.id
                input.action = SECURITY.OPENSTACK_CREATE.value
                input.sec_type = SEC_DEF_TYPE.OPENSTACK
                self.broker_client.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

class Edit(AdminService):
    """ Updates an OpenStack definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_openstack_edit_request'
        response_elem = 'zato_security_openstack_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'username')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(OpenStackSecurity).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(OpenStackSecurity.name==input.name).\
                    filter(OpenStackSecurity.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('OpenStack definition [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(OpenStackSecurity).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username

                session.add(definition)
                session.commit()

            except Exception:
                msg = 'Could not update the OpenStack definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = SECURITY.OPENSTACK_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.OPENSTACK
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an OpenStack definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_openstack_change_password_request'
        response_elem = 'zato_security_openstack_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(OpenStackSecurity, _auth, SECURITY.OPENSTACK_CHANGE_PASSWORD.value)

class Delete(AdminService):
    """ Deletes an OpenStack definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_openstack_delete_request'
        response_elem = 'zato_security_openstack_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(OpenStackSecurity).\
                    filter(OpenStackSecurity.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                msg = 'Could not delete the OpenStack definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.OPENSTACK_DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
