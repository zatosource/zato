# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, APIKeySecurity
from zato.common.odb.query import apikey_security_list
from zato.common.rate_limiting import DefinitionParser
from zato.common.util.sql import elems_with_opaque, parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.server.service import Boolean
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session as SASession
    from zato.common.typing_ import any_, anytuple

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of API keys available.
    """
    _filter_by = APIKeySecurity.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_apikey_get_list_request'
        response_elem = 'zato_security_apikey_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'username'
        output_optional:'anytuple' = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', \
            Boolean('rate_limit_check_parent_def'), 'header'

    def get_data(self, session:'SASession') -> 'any_':
        search_result = self._search(apikey_security_list, session, self.request.input.cluster_id, False)
        return elems_with_opaque(search_result) # type: ignore

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new API key.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_apikey_create_request'
        response_elem = 'zato_security_apikey_create_response'
        input_required = 'name', 'is_active'
        input_optional:'anytuple' = 'cluster_id', 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', \
            Boolean('rate_limit_check_parent_def'), 'header'
        output_required = 'id', 'name', 'header'

    def handle(self) -> 'None':

        # If we have a rate limiting definition, let's check it upfront
        DefinitionParser.check_definition_from_input(self.request.input)

        input = self.request.input
        input.username = 'Zato-Not-Used-' + uuid4().hex
        input.password = uuid4().hex
        input.password = self.server.encrypt(input.password)
        input.header = input.header or self.server.api_key_header
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(APIKeySecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(APIKeySecurity.name==input.name).first()

                if existing_one:
                    raise Exception('API key `{}` already exists in this cluster'.format(input.name))

                auth = APIKeySecurity(None, input.name, input.is_active, input.username, input.password, cluster)
                set_instance_opaque_attrs(auth, input)

                session.add(auth)
                session.commit()

            except Exception:
                self.logger.error('API key could not be created, e:`{}`', format_exc())
                session.rollback()

                raise
            else:
                input.id = auth.id
                input.action = SECURITY.APIKEY_CREATE.value
                input.sec_type = SEC_DEF_TYPE.APIKEY
                self.broker_client.publish(input)

                self.response.payload.id = auth.id
                self.response.payload.name = auth.name
                self.response.payload.header = input.header

        # Make sure the object has been created
        _:'any_' = self.server.worker_store.wait_for_apikey(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an API key.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_apikey_edit_request'
        response_elem = 'zato_security_apikey_edit_response'
        input_required = 'id', 'name', 'is_active'
        input_optional:'anytuple' = 'cluster_id', 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', \
            Boolean('rate_limit_check_parent_def'), 'header'
        output_required = 'id', 'name', 'header'

    def handle(self) -> 'None':

        input = self.request.input
        input.header = input.header or self.server.api_key_header
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        # If we have a rate limiting definition, let's check it upfront
        DefinitionParser.check_definition_from_input(input)

        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(APIKeySecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(APIKeySecurity.name==input.name).\
                    filter(APIKeySecurity.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('API key `{}` already exists in this cluster'.format(input.name))

                definition = session.query(APIKeySecurity).filter_by(id=input.id).one()

                opaque = parse_instance_opaque_attr(definition)
                set_instance_opaque_attrs(definition, input)

                old_name = definition.name

                definition.name = input.name
                definition.is_active = input.is_active

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('API key could not be updated, e:`{}`', format_exc())
                session.rollback()

                raise
            else:
                input.action = SECURITY.APIKEY_EDIT.value
                input.old_name = old_name
                input.username = definition.username
                input.sec_type = SEC_DEF_TYPE.APIKEY
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name
                self.response.payload.header = opaque.header

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an API key.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_apikey_change_password_request'
        response_elem = 'zato_security_apikey_change_password_response'

    def handle(self) -> 'None':

        def _auth(instance:'any_', password:'str') -> 'None':
            instance.password = password

        return self._handle(APIKeySecurity, _auth, SECURITY.APIKEY_CHANGE_PASSWORD.value)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an API key.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_apikey_delete_request'
        response_elem = 'zato_security_apikey_delete_response'
        input_required = 'id'

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(APIKeySecurity).\
                    filter(APIKeySecurity.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('API key could not be deleted, e:`{}`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.APIKEY_DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
