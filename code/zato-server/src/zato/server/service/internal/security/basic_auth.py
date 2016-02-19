# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

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
from zato.common.odb.model import Cluster, HTTPBasicAuth
from zato.common.odb.query import basic_auth_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase

class GetList(AdminService):
    """ Returns a list of HTTP Basic Auth definitions available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_basic_auth_get_list_request'
        response_elem = 'zato_security_basic_auth_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username', 'realm')

    def get_data(self, session):
        return basic_auth_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new HTTP Basic Auth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_basic_auth_create_request'
        response_elem = 'zato_security_basic_auth_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'username', 'realm')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(HTTPBasicAuth.name==input.name).first()

                if existing_one:
                    raise Exception('HTTP Basic Auth definition [{0}] already exists on this cluster'.format(input.name))

                auth = HTTPBasicAuth(None, input.name, input.is_active, input.username,
                    input.realm or None, input.password, cluster)

                session.add(auth)
                session.commit()

            except Exception, e:
                msg = 'Could not create an HTTP Basic Auth definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = SECURITY.BASIC_AUTH_CREATE.value
                input.sec_type = SEC_DEF_TYPE.BASIC_AUTH
                input.id = auth.id
                self.broker_client.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

class Edit(AdminService):
    """ Updates an HTTP Basic Auth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_basic_auth_edit_request'
        response_elem = 'zato_security_basic_auth_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'username', 'realm')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(HTTPBasicAuth.name==input.name).\
                    filter(HTTPBasicAuth.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('HTTP Basic Auth definition [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(HTTPBasicAuth).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username
                definition.realm = input.realm or None

                session.add(definition)
                session.commit()

            except Exception, e:
                msg = 'Could not update the HTTP Basic Auth definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = SECURITY.BASIC_AUTH_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.BASIC_AUTH
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an HTTP Basic Auth definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_basic_auth_change_password_request'
        response_elem = 'zato_security_basic_auth_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(HTTPBasicAuth, _auth, SECURITY.BASIC_AUTH_CHANGE_PASSWORD.value)

class Delete(AdminService):
    """ Deletes an HTTP Basic Auth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_basic_auth_delete_request'
        response_elem = 'zato_security_basic_auth_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(HTTPBasicAuth).\
                    filter(HTTPBasicAuth.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the HTTP Basic Auth definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.BASIC_AUTH_DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
