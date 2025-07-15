# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, HTTPBasicAuth
from zato.common.odb.query import basic_auth_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of HTTP Basic Auth definitions available.
    """
    _filter_by = HTTPBasicAuth.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_basic_auth_get_list_request'
        response_elem = 'zato_security_basic_auth_get_list_response'
        input_required = 'cluster_id',
        input_optional = 'needs_password',
        output_required = 'id', 'name', 'is_active', 'username', 'realm',
        output_optional = 'password',

    def get_data(self, session): # type: ignore

        data = elems_with_opaque(self._search(basic_auth_list, session, self.request.input.cluster_id, None, False))

        if self.request.input.needs_password:
            for item in data:
                password = item['password']
                password = self.crypto.decrypt(password)
                item['password'] = password

        return data

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new HTTP Basic Auth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_basic_auth_create_request'
        response_elem = 'zato_security_basic_auth_create_response'
        input_required = 'name', 'is_active', 'username', 'realm'
        input_optional = 'cluster_id'
        output_required = 'id', 'name'

    def handle(self):

        input = self.request.input
        input.password = uuid4().hex

        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==cluster_id).\
                    filter(HTTPBasicAuth.name==input.name).first()

                if existing_one:
                    raise Exception('HTTP Basic Auth definition `{}` already exists in this cluster'.format(input.name))

                auth = HTTPBasicAuth(None, input.name, input.is_active, input.username,
                    input.realm or None, input.password, cluster)
                set_instance_opaque_attrs(auth, input)

                session.add(auth)
                session.commit()

            except Exception:
                self.logger.error('Could not create an HTTP Basic Auth definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.id = auth.id
                input.action = SECURITY.BASIC_AUTH_CREATE.value
                input.sec_type = SEC_DEF_TYPE.BASIC_AUTH

                # .. build a message for pub/sub too ..
                pubsub_msg = Bunch()
                pubsub_msg.cid = self.cid
                pubsub_msg.action = SECURITY.BASIC_AUTH_CREATE.value
                pubsub_msg.username = input.username
                pubsub_msg.password = input.password

                # .. and publish both ..
                self.broker_client.publish(input)
                self.broker_client.publish(pubsub_msg, routing_key='pubsub')

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

        # Make sure the object has been created
        _:'any_' = self.server.worker_store.wait_for_basic_auth(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an HTTP Basic Auth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_basic_auth_edit_request'
        response_elem = 'zato_security_basic_auth_edit_response'
        input_required = 'name', 'is_active', 'username', 'realm'
        input_optional = 'id', 'cluster_id'
        output_required = 'id', 'name'

    def handle(self):

        # Local aliases
        input = self.request.input
        input_id = input.get('id')
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session: # type: ignore
            try:
                existing_one = session.query(HTTPBasicAuth).\
                    filter(Cluster.id==cluster_id).\
                    filter(HTTPBasicAuth.name==input.name)

                if input_id:
                    existing_one = existing_one.filter(HTTPBasicAuth.id!=input.id)
                    existing_one = existing_one.first()

                if existing_one:
                    raise Exception('HTTP Basic Auth definition `{}` already exists on this cluster'.format(input.name))

                definition = session.query(HTTPBasicAuth)

                if input_id:
                    definition = definition.filter_by(id=input.id)
                else:
                    definition = definition.filter_by(name=input.name)
                definition = definition.one()

                old_name = definition.name
                old_username = definition.username

                set_instance_opaque_attrs(definition, input)

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username
                definition.realm = input.realm or None

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not update HTTP Basic Auth definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.action = SECURITY.BASIC_AUTH_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.BASIC_AUTH

                # .. publish it ..
                self.broker_client.publish(input)

                # .. build a message for pub/sub only if something has actually changed ..
                has_name_changed = input.name != old_name
                has_username_changed = input.username != old_username

                if has_name_changed or has_username_changed:

                    pubsub_msg = Bunch()

                    pubsub_msg.cid = self.cid
                    pubsub_msg.action = SECURITY.BASIC_AUTH_EDIT.value

                    pubsub_msg.has_name_changed = has_name_changed
                    pubsub_msg.has_username_changed = has_username_changed

                    pubsub_msg.old_sec_name = old_name
                    pubsub_msg.new_sec_name = input.name

                    pubsub_msg.old_username = old_username
                    pubsub_msg.new_username = input.username

                    self.broker_client.publish(pubsub_msg, routing_key='pubsub')

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an HTTP Basic Auth definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_basic_auth_change_password_request'
        response_elem = 'zato_security_basic_auth_change_password_response'

    def handle(self):
        def _auth(instance, password): # type: ignore
            instance.password = password

        return self._handle(HTTPBasicAuth, _auth, SECURITY.BASIC_AUTH_CHANGE_PASSWORD.value)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an HTTP Basic Auth definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_basic_auth_delete_request'
        response_elem = 'zato_security_basic_auth_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(HTTPBasicAuth).\
                    filter(HTTPBasicAuth.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete HTTP Basic Auth definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.BASIC_AUTH_DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
