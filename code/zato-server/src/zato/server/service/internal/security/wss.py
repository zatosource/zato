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
from zato.common.odb.model import Cluster, WSSDefinition
from zato.common.odb.query import wss_list
from zato.server.service import Boolean, Integer
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of WS-Security definitions available.
    """
    _filter_by = WSSDefinition.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_wss_get_list_request'
        response_elem = 'zato_security_wss_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'password_type', 'username',
            Boolean('reject_empty_nonce_creat'), Boolean('reject_stale_tokens'), Integer('reject_expiry_limit'),
            Integer('nonce_freshness_time'))

    def get_data(self, session):
        return self._search(wss_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new WS-Security definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_wss_create_request'
        response_elem = 'zato_security_wss_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'username',
            'password_type', Boolean('reject_empty_nonce_creat'), Boolean('reject_stale_tokens'),
            Integer('reject_expiry_limit'), Integer('nonce_freshness_time'))
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = session.query(WSSDefinition).\
                filter(Cluster.id==input.cluster_id).\
                filter(WSSDefinition.name==input.name).first()

            if existing_one:
                raise Exception('WS-Security definition [{0}] already exists on this cluster'.format(input.name))

            password = uuid4().hex

            try:
                wss = WSSDefinition(
                    None, input.name, input.is_active, input.username,
                    password, input.password_type, input.reject_empty_nonce_creat,
                    input.reject_stale_tokens, input.reject_expiry_limit, input.nonce_freshness_time,
                    cluster)

                session.add(wss)
                session.commit()

            except Exception:
                self.logger.error('WSS definition could created, e:`{}`', format_exc())
                session.rollback()

                raise
            else:
                input.id = wss.id
                input.action = SECURITY.WSS_CREATE.value
                input.password = password
                input.sec_type = SEC_DEF_TYPE.WSS
                self.broker_client.publish(self.request.input)

            self.response.payload.id = wss.id
            self.response.payload.name = input.name

class Edit(AdminService):
    """ Updates a WS-Security definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_wss_edit_request'
        response_elem = 'zato_security_wss_edit_response'
        input_required = (
            'id', 'cluster_id', 'name', 'is_active', 'username',
            'password_type', Boolean('reject_empty_nonce_creat'), Boolean('reject_stale_tokens'),
            Integer('reject_expiry_limit'), Integer('nonce_freshness_time'))
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(WSSDefinition).\
                filter(Cluster.id==input.cluster_id).\
                filter(WSSDefinition.name==input.name).\
                filter(WSSDefinition.id!=input.id).\
                first()

            if existing_one:
                raise Exception('WS-Security definition [{0}] already exists on this cluster'.format(input.name))

            try:
                wss = session.query(WSSDefinition).filter_by(id=input.id).one()
                old_name = wss.name

                wss.name = input.name
                wss.is_active = input.is_active
                wss.username = input.username
                wss.password_type = input.password_type
                wss.reject_empty_nonce_creat = input.reject_empty_nonce_creat
                wss.reject_stale_tokens = input.reject_stale_tokens
                wss.reject_expiry_limit = input.reject_expiry_limit
                wss.nonce_freshness_time = input.nonce_freshness_time

                session.add(wss)
                session.commit()

            except Exception:
                self.logger.error('WSS definition could updated, e:`{}`', format_exc())
                session.rollback()

                raise
            else:
                input.action = SECURITY.WSS_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.WSS
                self.broker_client.publish(self.request.input)

            self.response.payload.id = input.id
            self.response.payload.name = input.name

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a WS-Security definition.
    """
    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_wss_change_password_request'
        response_elem = 'zato_security_wss_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(WSSDefinition, _auth, SECURITY.WSS_CHANGE_PASSWORD.value)

class Delete(AdminService):
    """ Deletes a WS-Security definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_wss_delete_request'
        response_elem = 'zato_security_wss_delete_response'
        input_required = ('id',)

    def handle(self):

        with closing(self.odb.session()) as session:
            try:
                wss = session.query(WSSDefinition).\
                    filter(WSSDefinition.id==self.request.input.id).\
                    one()

                session.delete(wss)
                session.commit()
            except Exception:
                self.logger.error('WSS definition could deleted, e:`{}`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.WSS_DELETE.value
                self.request.input.name = wss.name
                self.broker_client.publish(self.request.input)
