# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from http.client import BAD_REQUEST
from traceback import format_exc
from uuid import uuid4

# Cryptography
from cryptography.fernet import Fernet

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, JWT
from zato.common.odb.query import jwt_list
from zato.common.rate_limiting import DefinitionParser
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.connection.http_soap import Unauthorized
from zato.server.jwt_ import JWT as JWTBackend
from zato.server.service import Boolean, Integer, Service
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns the list of JWT definitions available.
    """
    _filter_by = JWT.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_jwt_get_list_request'
        response_elem = 'zato_security_jwt_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'username', Integer('ttl')
        output_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', Boolean('rate_limit_check_parent_def')

    def get_data(self, session):
        return elems_with_opaque(self._search(jwt_list, session, self.request.input.cluster_id, None, False))

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new JWT definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_jwt_create_request'
        response_elem = 'zato_security_jwt_create_response'
        input_required = 'cluster_id', 'name', 'is_active', 'username', Integer('ttl')
        input_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', Boolean('rate_limit_check_parent_def')
        output_required = 'id', 'name'

    def handle(self):

        # If we have a rate limiting definition, let's check it upfront
        DefinitionParser.check_definition_from_input(self.request.input)

        input = self.request.input
        input.password = uuid4().hex
        input.secret = Fernet.generate_key()

        with closing(self.odb.session()) as session:
            try:

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(JWT).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(JWT.name==input.name).first()

                if existing_one:
                    raise Exception('JWT definition `{}` already exists on this cluster'.format(input.name))

                item = self._new_zato_instance_with_cluster(JWT)
                item.name = input.name
                item.is_active = input.is_active
                item.username = input.username
                item.password = input.password
                item.secret = input.secret
                item.ttl = input.ttl
                item.cluster_id = input.cluster_id

                set_instance_opaque_attrs(item, input)

                session.add(item)
                session.commit()

            except Exception:
                self.logger.error('Could not create a JWT definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.id = item.id
                input.action = SECURITY.JWT_CREATE.value
                input.sec_type = SEC_DEF_TYPE.JWT
                self.broker_client.publish(input)

            self.response.payload.id = item.id
            self.response.payload.name = item.name

        # Make sure the object has been created
        _:'any_' = self.server.worker_store.wait_for_jwt(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a JWT definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_jwt_edit_request'
        response_elem = 'zato_security_jwt_edit_response'
        input_required = 'id', 'cluster_id', 'name', 'is_active', 'username', Integer('ttl')
        input_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', Boolean('rate_limit_check_parent_def')
        output_required = 'id', 'name'

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(JWT).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(JWT.name==input.name).\
                    filter(JWT.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('JWT definition `{}` already exists on this cluster'.format(input.name))

                item = session.query(JWT).filter_by(id=input.id).one()
                old_name = item.name

                item.name = input.name
                item.is_active = input.is_active
                item.username = input.username
                item.ttl = input.ttl
                item.cluster_id = input.cluster_id

                set_instance_opaque_attrs(item, input)

                session.add(item)
                session.commit()

            except Exception:
                self.logger.error('Could not update the JWT definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = SECURITY.JWT_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.JWT
                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a JWT definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_jwt_change_password_request'
        response_elem = 'zato_security_jwt_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(JWT, _auth, SECURITY.JWT_CHANGE_PASSWORD.value)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a JWT definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_jwt_delete_request'
        response_elem = 'zato_security_jwt_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(JWT).\
                    filter(JWT.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete the JWT definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.JWT_DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################

class LogIn(Service):
    """ Logs user into using JWT-backed credentials and returns a new token if credentials were correct.
    """
    class SimpleIO:
        input_required = 'username', 'password'
        input_optional = 'totp_code'
        output_optional = 'token',

# ################################################################################################################################

    def _raise_unathorized(self):
        raise Unauthorized(self.cid, 'Invalid credentials', 'jwt')

# ################################################################################################################################

    def handle(self, _sec_type=SEC_DEF_TYPE.JWT):

        try:
            auth_info = JWTBackend(self.odb, self.server.decrypt, self.server.jwt_secret).authenticate(
                self.request.input.username, self.server.decrypt(self.request.input.password))

            if auth_info:

                token = auth_info.token

                # Checks if there is an SSO user related to that JWT account
                # and logs that person in to SSO or resumes his or her session.
                self.server.sso_tool.on_external_auth(
                    _sec_type, auth_info.sec_def_id, auth_info.sec_def_username, self.cid, self.wsgi_environ,
                    token, self.request.input.totp_code)

                self.response.payload = {'token': auth_info.token}
                self.response.headers['Authorization'] = auth_info.token

            else:
                self._raise_unathorized()

        except Exception:
            self.logger.warning(format_exc())
            self._raise_unathorized()

# ################################################################################################################################
# ################################################################################################################################

class LogOut(Service):
    """ Logs a user out of an existing JWT token.
    """
    class SimpleIO(AdminSIO):
        response_elem = None
        output_optional = 'result',
        skip_empty_keys = True

    def handle(self):
        token = self.wsgi_environ.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if isinstance(token, unicode):
            token = token.encode('utf8')

        if not token:
            self.response.status_code = BAD_REQUEST
            self.response.payload.result = 'No JWT found'

        try:
            JWTBackend(self.odb, self.server.decrypt, self.server.jwt_secret).delete(token)
        except Exception:
            self.logger.warning(format_exc())
            self.response.status_code = BAD_REQUEST
            self.response.payload.result = 'Token could not be deleted'

# ################################################################################################################################
# ################################################################################################################################
