# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

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
from zato.common.odb.model import Cluster, TechnicalAccount
from zato.common.odb.query import tech_acc_list
from zato.common.util import tech_account_password
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of technical accounts defined in the ODB. The items are
    sorted by the 'name' attribute.
    """
    _filter_by = TechnicalAccount.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_tech_account_get_list_request'
        response_elem = 'zato_security_tech_account_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active')

    def get_data(self, session):
        return self._search(tech_acc_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class GetByID(AdminService):
    """ Returns a technical account of a given ID.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_tech_account_get_by_id_request'
        response_elem = 'zato_security_tech_account_get_by_id_response'
        input_required = ('id',)
        output_required = ('id', 'name', 'is_active')

    def get_data(self, session):
        return session.query(TechnicalAccount.id,
            TechnicalAccount.name, TechnicalAccount.is_active).\
            filter(TechnicalAccount.id==self.request.input.id).\
            one()

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)

class Create(AdminService):
    """ Creates a new technical account.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_tech_account_create_request'
        response_elem = 'zato_security_tech_account_create_response'
        input_required = ('cluster_id', 'name', 'is_active')
        output_required = ('id', 'name')

    def handle(self):
        salt = uuid4().hex
        input = self.request.input
        input.password = tech_account_password(uuid4().hex, salt)
        input.salt = salt

        with closing(self.odb.session()) as session:
            cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

            # Let's see if we already have an account of that name before committing
            # any stuff into the database.
            existing_one = session.query(TechnicalAccount).\
                filter(Cluster.id==input.cluster_id).\
                filter(TechnicalAccount.name==input.name).first()

            if existing_one:
                raise Exception('Technical account [{0}] already exists on this cluster'.format(input.name))

            try:
                tech_account = TechnicalAccount(None, input.name, input.is_active, input.password, salt, cluster=cluster)
                session.add(tech_account)
                session.commit()

            except Exception, e:
                msg = 'Could not create a technical account, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.id = tech_account.id
                input.action = SECURITY.TECH_ACC_CREATE.value
                input.password = input.password
                input.sec_type = SEC_DEF_TYPE.TECH_ACCOUNT
                self.broker_client.publish(input)

                self.response.payload.id = tech_account.id
                self.response.payload.name = tech_account.name

class Edit(AdminService):
    """ Updates an existing technical account.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_tech_account_edit_request'
        response_elem = 'zato_security_tech_account_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(TechnicalAccount).\
                filter(Cluster.id==input.cluster_id).\
                filter(TechnicalAccount.name==input.name).\
                filter(TechnicalAccount.id!=input.id).\
                first()

            if existing_one:
                raise Exception('Technical account [{0}] already exists on this cluster'.format(input.name))

            tech_account = session.query(TechnicalAccount).\
                filter(TechnicalAccount.id==input.id).\
                one()
            old_name = tech_account.name

            tech_account.name = input.name
            tech_account.is_active = input.is_active

            try:
                session.add(tech_account)
                session.commit()

            except Exception, e:
                msg = "Could not update the technical account, e:[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = SECURITY.TECH_ACC_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.TECH_ACCOUNT
                self.broker_client.publish(input)

                self.response.payload.id = tech_account.id
                self.response.payload.name = tech_account.name

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a technical account.
    """
    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_tech_account_change_password_request'
        response_elem = 'zato_security_tech_account_change_password_response'

    def handle(self):
        salt = uuid4().hex

        def _auth(instance, password):
            instance.password = tech_account_password(password, salt)
            instance.salt = salt

        return self._handle(TechnicalAccount, _auth,
                            SECURITY.TECH_ACC_CHANGE_PASSWORD.value, salt=salt)

class Delete(AdminService):
    """ Deletes a technical account.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_tech_account_delete_request'
        response_elem = 'zato_security_tech_account_delete_response'
        input_required = ('id',)
        input_optional = ('current_tech_account_name',)

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            tech_account = session.query(TechnicalAccount).\
                filter(TechnicalAccount.id==input.id).\
                one()

            if tech_account.name == input.current_tech_account_name:
                msg = "Can't delete account [{0}], at least one client console uses it".\
                    format(input.current_tech_account_name)
                raise Exception(msg)

            try:
                session.delete(tech_account)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the account, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                input.action = SECURITY.TECH_ACC_DELETE.value
                input.name = tech_account.name
                self.broker_client.publish(input)
