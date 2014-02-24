# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common import ZatoException
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import LDAPConnectionPool
from zato.common.odb.query import out_ldap_list
from zato.server.service import Integer
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase

class _LDAPService(object):
    """ A common class for various LDAP-related services.
    """
    def notify_worker_threads(self, params, action=OUTGOING.LDAP_CREATE_EDIT):
        """ Notify worker threads of new or updated parameters.
        """
        params['action'] = action
        self.broker_client.publish(params)

    def validate_extra(self, cid, extra):
        if extra and not b'=' in extra:
            raise ZatoException(cid, 'extra should be a list of key=value parameters, possibly one-element long, instead of [{}]'.format(extra.decode('utf-8')))

class GetList(AdminService):
    """ Returns a list of outgoing LDAP connections.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ldap_get_list_request'
        response_elem = 'zato_outgoing_ldap_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'cluster_id', 'host', Integer('port'), 'bind_dn', Integer('pool_size'))
        output_optional = ('extra',)

    def get_data(self, session):
        return out_ldap_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService, _LDAPService):
    """ Creates a new outgoing LDAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ldap_create_request'
        response_elem = 'zato_outgoing_ldap_create_response'
        input_required = ('name', 'is_active', 'cluster_id', 'host', Integer('port'), 'bind_dn', Integer('pool_size'))
        input_optional = ('extra',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex
        input.extra = input.extra.encode('utf-8') if input.extra else b''

        self.validate_extra(self.cid, input.extra.decode('utf-8'))

        with closing(self.odb.session()) as session:
            existing_one = session.query(LDAPConnectionPool.id).\
                filter(LDAPConnectionPool.cluster_id==input.cluster_id).\
                filter(LDAPConnectionPool.name==input.name).\
                first()

            if existing_one:
                raise Exception('An outgoing LDAP connection [{0}] already exists on this cluster'.format(input.name))

            try:
                item = LDAPConnectionPool()
                item.name = input.name
                item.is_active = input.is_active
                item.cluster_id = input.cluster_id
                item.host = input.host
                item.port = input.port
                item.bind_dn = input.bind_dn
                item.password = input.password
                item.pool_size = input.pool_size
                item.extra = input.extra

                session.add(item)
                session.commit()

                self.notify_worker_threads(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not create an outgoing LDAP connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(AdminService, _LDAPService):
    """ Updates an outgoing LDAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ldap_edit_request'
        response_elem = 'zato_outgoing_ldap_edit_response'
        input_required = ('id', 'name', 'is_active', 'cluster_id', 'host', Integer('port'), 'bind_dn', Integer('pool_size'))
        input_optional = ('extra',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.extra = input.extra.encode('utf-8') if input.extra else ''

        self.validate_extra(self.cid, input.extra)

        with closing(self.odb.session()) as session:
            existing_one = session.query(LDAPConnectionPool.id).\
                filter(LDAPConnectionPool.cluster_id==input.cluster_id).\
                filter(LDAPConnectionPool.name==input.name).\
                filter(LDAPConnectionPool.id!=input.id).\
                first()

            if existing_one:
                raise Exception('An outgoing LDAP connection [{0}] already exists on this cluster'.format(input.name))

            try:
                item = session.query(LDAPConnectionPool).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.cluster_id = input.cluster_id
                item.host = input.host
                item.port = input.port
                item.bind_dn = input.bind_dn
                item.pool_size = input.pool_size
                item.extra = input.extra

                session.add(item)
                session.commit()

                input.password = item.password
                input.old_name = old_name
                self.notify_worker_threads(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not update the outgoing LDAP connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService, _LDAPService):
    """ Deletes an outgoing LDAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ldap_delete_request'
        response_elem = 'zato_outgoing_ldap_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(LDAPConnectionPool).\
                    filter(LDAPConnectionPool.id==self.request.input.id).\
                    one()
                old_name = item.name

                session.delete(item)
                session.commit()

                self.notify_worker_threads({'name':old_name}, OUTGOING.LDAP_DELETE)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing LDAP connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an outgoing LDAP connection. The underlying implementation
    will actually stop and recreate the connection using the new password.
    """
    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_outgoing_ldap_change_password_request'
        response_elem = 'zato_outgoing_ldap_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        self._handle(LDAPConnectionPool, _auth, OUTGOING.LDAP_CHANGE_PASSWORD)

class Ping(AdminService):
    """ Pings an LDAP database
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ldap_ping_request'
        response_elem = 'zato_outgoing_ldap_ping_response'
        input_required = ('id',)
        output_required = ('response_time',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(LDAPConnectionPool).\
                    filter(LDAPConnectionPool.id==self.request.input.id).\
                    one()

                self.response.payload.response_time = str(self.outgoing.ldap.get(item.name, False).ping())

            except Exception, e:
                session.rollback()
                msg = 'Could not ping the outgoing LDAP connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise
