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
from zato.common.odb.model import Cluster, SPNEGOSecurity
from zato.common.odb.query import spnego_list
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
_spnego_fields = (

    # The client principal and the path to the keytab file mounted into the container.
    'principal', 'keytab_path',

    # Optional negotiation details - the target SPN when it differs from HTTP/<hostname>
    # and whether to delegate credentials.
    '-target_spn', '-needs_delegation',
)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Kerberos (SPNEGO) definitions available.
    """
    _filter_by = SPNEGOSecurity.name,

    input = 'cluster_id', *query_parameters
    output = 'id', 'name', 'is_active', *_spnego_fields

    def get_data(self, session): # type: ignore
        out = elems_with_opaque(self._search(spnego_list, session, self.request.input.cluster_id, False))
        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Kerberos (SPNEGO) definition.
    """
    input = 'name', 'is_active', '-cluster_id', *_spnego_fields
    output = 'id', 'name'

    def handle(self):

        input = self.request.input
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(SPNEGOSecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(SPNEGOSecurity.name==input.name).first()

                if existing_one:
                    raise Exception('SPNEGO definition `{}` already exists in this cluster'.format(input.name))

                auth = SPNEGOSecurity(None, input.name, input.is_active, input.name, cluster)
                set_instance_opaque_attrs(auth, input)

                session.add(auth)
                session.commit()

            except Exception:
                self.logger.error('Could not create a SPNEGO definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.id = auth.id
                input.action = SECURITY.SPNEGO_CREATE.value
                input.sec_type = SEC_DEF_TYPE.SPNEGO

                # .. and publish it.
                self.config_dispatcher.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

        # Make sure the object has been created
        _:'any_' = self.server.config_manager.wait_for_spnego(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a Kerberos (SPNEGO) definition.
    """
    input = 'name', 'is_active', '-id', '-cluster_id', *_spnego_fields
    output = 'id', 'name'

    def handle(self):

        # Local aliases
        input = self.request.input
        input_id = input.get('id')
        cluster_id = input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session: # type: ignore
            try:
                existing_one = session.query(SPNEGOSecurity).\
                    filter(Cluster.id==cluster_id).\
                    filter(SPNEGOSecurity.name==input.name)

                if input_id:
                    existing_one = existing_one.filter(SPNEGOSecurity.id!=input.id)
                    existing_one = existing_one.first()

                if existing_one:
                    raise Exception('SPNEGO definition `{}` already exists on this cluster'.format(input.name))

                definition = session.query(SPNEGOSecurity)

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
                self.logger.error('Could not update the SPNEGO definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:

                # Enrich the message for the server ..
                input.action = SECURITY.SPNEGO_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.SPNEGO

                # .. and publish it.
                self.config_dispatcher.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a Kerberos (SPNEGO) definition.
    """
    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(SPNEGOSecurity).\
                    filter(SPNEGOSecurity.id==self.request.input.id).\
                    one()

                # .. clean up all pub/sub state before the CASCADE delete ..
                self.server.config_manager.cleanup_security_pubsub(session, auth.id, auth.username)

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete the SPNEGO definition, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.SPNEGO_DELETE.value
                self.request.input.name = auth.name
                self.config_dispatcher.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
