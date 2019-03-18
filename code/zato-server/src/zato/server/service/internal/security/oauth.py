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
from zato.common.odb.model import Cluster, OAuth
from zato.common.odb.query import oauth_list
from zato.server.service import Integer
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of OAuth definitions available.
    """
    _filter_by = OAuth.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_oauth_get_list_request'
        response_elem = 'zato_security_oauth_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username', 'proto_version',
            'sig_method', Integer('max_nonce_log'))

    def get_data(self, session):
        return self._search(oauth_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new OAuth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_oauth_create_request'
        response_elem = 'zato_security_oauth_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'username', 'proto_version',
            'sig_method', Integer('max_nonce_log'))
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(OAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(OAuth.name==input.name).first()

                if existing_one:
                    raise Exception('OAuth definition [{0}] already exists on this cluster'.format(input.name))

                auth = OAuth(None, input.name, input.is_active, input.username,
                    input.password, input.proto_version, input.sig_method,
                    input.max_nonce_log, cluster)

                session.add(auth)
                session.commit()

            except Exception:
                msg = 'Could not create an OAuth definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.id = auth.id
                input.action = SECURITY.OAUTH_CREATE.value
                input.sec_type = SEC_DEF_TYPE.OAUTH
                self.broker_client.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

class Edit(AdminService):
    """ Updates an OAuth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_oauth_edit_request'
        response_elem = 'zato_security_oauth_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'username',
            'proto_version', 'sig_method', Integer('max_nonce_log'))
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(OAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(OAuth.name==input.name).\
                    filter(OAuth.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('OAuth definition [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(OAuth).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username
                definition.proto_version = input.proto_version
                definition.sig_method = input.sig_method
                definition.max_nonce_log = input.max_nonce_log

                session.add(definition)
                session.commit()

            except Exception:
                msg = 'Could not update the OAuth definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = SECURITY.OAUTH_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.OAUTH
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an OAuth definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_oauth_change_password_request'
        response_elem = 'zato_security_oauth_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(OAuth, _auth, SECURITY.OAUTH_CHANGE_PASSWORD.value)

class Delete(AdminService):
    """ Deletes an OAuth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_oauth_delete_request'
        response_elem = 'zato_security_oauth_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(OAuth).\
                    filter(OAuth.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                msg = 'Could not delete the OAuth definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.OAUTH_DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
