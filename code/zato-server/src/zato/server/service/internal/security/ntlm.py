# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, NTLM
from zato.common.odb.query import ntlm_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of NTLM definitions available.
    """
    _filter_by = NTLM.name,

    input = 'cluster_id',
    output = 'id', 'name', 'is_active', 'username'

    def get_data(self, session):
        return self._search(ntlm_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new NTLM definition.
    """
    input = 'cluster_id', 'name', 'is_active', 'username'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(NTLM).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(NTLM.name==input.name).first()

                if existing_one:
                    raise Exception('NTLM definition [{0}] already exists on this cluster'.format(input.name))

                auth = NTLM(None, input.name, input.is_active, input.username, input.password, cluster)

                session.add(auth)
                session.commit()

            except Exception:
                msg = 'Could not create an NTLM definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.id = auth.id
                input.action = SECURITY.NTLM_CREATE.value
                input.sec_type = SEC_DEF_TYPE.NTLM
                self.config_dispatcher.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

        # Make sure the object has been created
        _:'any_' = self.server.config_manager.wait_for_ntlm(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an NTLM definition.
    """
    input = 'id', 'cluster_id', 'name', 'is_active', 'username'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(NTLM).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(NTLM.name==input.name).\
                    filter(NTLM.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('NTLM definition [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(NTLM).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username

                session.add(definition)
                session.commit()

            except Exception:
                msg = 'Could not update the NTLM definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = SECURITY.NTLM_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.NTLM
                self.config_dispatcher.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an NTLM definition.
    """
    password_required = False

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(NTLM, _auth, SECURITY.NTLM_CHANGE_PASSWORD.value)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an NTLM definition.
    """
    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(NTLM).\
                    filter(NTLM.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                msg = 'Could not delete the NTLM definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.NTLM_DELETE.value
                self.request.input.name = auth.name
                self.config_dispatcher.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################
