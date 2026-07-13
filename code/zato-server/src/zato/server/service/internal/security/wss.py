# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import query_parameters, SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, WSSecurity
from zato.common.odb.query import wss_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service import Boolean
from zato.server.service.internal import AdminService, ChangePasswordBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The mode-specific details every definition may carry - they all travel as opaque attributes.
_mode_fields = (

    # UsernameToken - whether the password goes out in digest form.
    Boolean('-use_digest'),

    # X.509 and SAML - what to do and the paths to the PEM files to do it with.
    Boolean('-sign'), Boolean('-encrypt'),
    '-signing_key', '-signing_certificate_chain', '-decryption_key', '-peer_certificate', '-trust_anchors',

    # SAML - the assertion fields.
    '-issuer', '-subject', '-audience',
)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of WS-Security definitions available.
    """
    _filter_by = WSSecurity.name,

    input = 'cluster_id', '-needs_password', *query_parameters
    output = 'id', 'name', 'is_active', 'username', '-mode', '-password', *_mode_fields

    def get_data(self, session): # type: ignore

        data = elems_with_opaque(self._search(wss_list, session, self.request.input.cluster_id, False))

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
    """ Creates a new WS-Security definition.
    """
    input = 'name', 'is_active', 'username', 'mode', '-cluster_id', *_mode_fields
    output = 'id', 'name'

    def handle(self):

        input = self.request.input
        input.password = uuid4().hex

        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(WSSecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(WSSecurity.name==input.name).first()

                if existing_one:
                    raise Exception('WS-Security definition `{}` already exists in this cluster'.format(input.name))

                auth = WSSecurity(None, input.name, input.is_active, input.username, input.password, cluster)
                set_instance_opaque_attrs(auth, input)

                session.add(auth)
                session.commit()

            except Exception:
                self.logger.error('Could not create a WS-Security definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.id = auth.id
                input.action = SECURITY.WSS_CREATE.value
                input.sec_type = SEC_DEF_TYPE.WSS

                # .. and publish it.
                self.config_dispatcher.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

        # Make sure the object has been created
        _:'any_' = self.server.config_manager.wait_for_wss(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a WS-Security definition.
    """
    input = 'name', 'is_active', 'username', 'mode', '-id', '-cluster_id', *_mode_fields
    output = 'id', 'name'

    def handle(self):

        # Local aliases
        input = self.request.input
        input_id = input.get('id')
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session: # type: ignore
            try:
                existing_one = session.query(WSSecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(WSSecurity.name==input.name)

                if input_id:
                    existing_one = existing_one.filter(WSSecurity.id!=input.id)
                    existing_one = existing_one.first()

                if existing_one:
                    raise Exception('WS-Security definition `{}` already exists on this cluster'.format(input.name))

                definition = session.query(WSSecurity)

                if input_id:
                    definition = definition.filter_by(id=input.id)
                else:
                    definition = definition.filter_by(name=input.name)
                definition = definition.one()

                old_name = definition.name

                set_instance_opaque_attrs(definition, input)

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not update the WS-Security definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.action = SECURITY.WSS_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.WSS

                # .. and publish it.
                self.config_dispatcher.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a WS-Security definition.
    """
    password_required = False

    def handle(self):
        def _auth(instance, password): # type: ignore
            instance.password = password

        return self._handle(WSSecurity, _auth, SECURITY.WSS_CHANGE_PASSWORD.value)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a WS-Security definition.
    """
    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(WSSecurity).\
                    filter(WSSecurity.id==self.request.input.id).\
                    one()

                # .. clean up all pub/sub state before the CASCADE delete ..
                self.server.config_manager.cleanup_security_pubsub(session, auth.id, auth.username)

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete the WS-Security definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                self.request.input.action = SECURITY.WSS_DELETE.value

                # Note that we need both name and sec_name.
                self.request.input.name = auth.name
                self.request.input.sec_name = auth.name

                self.request.input.username = auth.username

                self.config_dispatcher.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
