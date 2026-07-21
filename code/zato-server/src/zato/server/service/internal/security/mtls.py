# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.api import query_parameters, SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, MTLSSecurity
from zato.common.odb.query import mtls_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The definition-specific details every definition may carry - they all travel as opaque attributes.
_mtls_fields = (

    # Outgoing connections - paths to the PEM files mounted into the container.
    '-cert_path', '-key_path', '-ca_certs_path',

    # Channels - the expected client certificate details, verified against what the TLS terminator reports.
    '-client_cert_fingerprint', '-client_cert_subject_dn',
)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of mTLS definitions available.
    """
    _filter_by = MTLSSecurity.name,

    input = 'cluster_id', *query_parameters
    output = 'id', 'name', 'is_active', *_mtls_fields

    def get_data(self, session): # type: ignore
        out = elems_with_opaque(self._search(mtls_list, session, self.request.input.cluster_id, False))
        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new mTLS definition.
    """
    input = 'name', 'is_active', '-cluster_id', *_mtls_fields
    output = 'id', 'name'

    def handle(self):

        input = self.request.input
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(MTLSSecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(MTLSSecurity.name==input.name).first()

                if existing_one:
                    raise Exception('mTLS definition `{}` already exists in this cluster'.format(input.name))

                auth = MTLSSecurity(None, input.name, input.is_active, input.name, cluster)
                set_instance_opaque_attrs(auth, input)

                session.add(auth)
                session.commit()

            except Exception:
                self.logger.error('Could not create an mTLS definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.id = auth.id
                input.action = SECURITY.MTLS_CREATE.value
                input.sec_type = SEC_DEF_TYPE.MTLS

                # .. and publish it.
                self.config_dispatcher.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

        # Make sure the object has been created
        _:'any_' = self.server.config_manager.wait_for_mtls(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an mTLS definition.
    """
    input = 'name', 'is_active', '-id', '-cluster_id', *_mtls_fields
    output = 'id', 'name'

    def handle(self):

        # Local aliases
        input = self.request.input
        input_id = input.get('id')
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session: # type: ignore
            try:
                existing_one = session.query(MTLSSecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(MTLSSecurity.name==input.name)

                if input_id:
                    existing_one = existing_one.filter(MTLSSecurity.id!=input.id)
                    existing_one = existing_one.first()

                if existing_one:
                    raise Exception('mTLS definition `{}` already exists on this cluster'.format(input.name))

                definition = session.query(MTLSSecurity)

                if input_id:
                    definition = definition.filter_by(id=input.id)
                else:
                    definition = definition.filter_by(name=input.name)
                definition = definition.one()

                old_name = definition.name

                set_instance_opaque_attrs(definition, input)

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.name

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not update the mTLS definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.action = SECURITY.MTLS_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.MTLS

                # .. and publish it.
                self.config_dispatcher.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an mTLS definition.
    """
    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(MTLSSecurity).\
                    filter(MTLSSecurity.id==self.request.input.id).\
                    one()

                # .. clean up all pub/sub state before the CASCADE delete ..
                self.server.config_manager.cleanup_security_pubsub(session, auth.id, auth.username)

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete the mTLS definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.MTLS_DELETE.value
                self.request.input.name = auth.name
                self.config_dispatcher.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
