# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, XPathSecurity
from zato.common.odb.query import xpath_sec_list
from zato.common.util.api import validate_xpath
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of XPath-based security definitions available.
    """
    _filter_by = XPathSecurity.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_xpath_get_list_request'
        response_elem = 'zato_security_xpath_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username', 'username_expr')
        output_optional = ('password_expr',)

    def get_data(self, session):
        return self._search(xpath_sec_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class _CreateEdit(AdminService):
    """ A common class for both Create and Edit.
    """
    def validate_input(self):
        validate_xpath(self.request.input.username_expr)
        validate_xpath(self.request.input.get('password_expr') or '/')

class Create(_CreateEdit):
    """ Creates a new XPath-based security definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_xpath_create_request'
        response_elem = 'zato_security_xpath_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'username', 'username_expr')
        input_optional = ('password_expr',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(XPathSecurity).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(XPathSecurity.name==input.name).first()

                if existing_one:
                    raise Exception('XPath security definition [{0}] already exists on this cluster'.format(input.name))

                auth = self._new_zato_instance_with_cluster(XPathSecurity)
                auth.name = input.name
                auth.is_active = input.is_active
                auth.username = input.username
                auth.password = input.password
                auth.username_expr = input.username_expr
                auth.password_expr = input.get('password_expr')
                auth.cluster_id = cluster.id

                session.add(auth)
                session.commit()

            except Exception:
                self.logger.error('XPath security definition could not be created, e:`{}', format_exc())
                session.rollback()

                raise
            else:
                input.id = auth.id
                input.action = SECURITY.XPATH_SEC_CREATE.value
                input.sec_type = SEC_DEF_TYPE.XPATH_SEC
                self.broker_client.publish(input)

            self.response.payload.id = auth.id
            self.response.payload.name = auth.name

class Edit(_CreateEdit):
    """ Updates an XPath-based security definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_xpath_edit_request'
        response_elem = 'zato_security_xpath_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'username', 'username_expr')
        input_optional = ('password_expr',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(XPathSecurity).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(XPathSecurity.name==input.name).\
                    filter(XPathSecurity.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('XPath security definition [{0}] already exists on this cluster'.format(input.name))

                auth = session.query(XPathSecurity).filter_by(id=input.id).one()
                old_name = auth.name

                auth.name = input.name
                auth.is_active = input.is_active
                auth.username = input.username
                auth.username_expr = input.username_expr
                auth.password_expr = input.get('password_expr')

                session.add(auth)
                session.commit()

            except Exception:
                self.logger.error('XPath security definition could not be updated, e:`{}', format_exc())
                session.rollback()

                raise
            else:
                input.action = SECURITY.XPATH_SEC_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.XPATH_SEC
                self.broker_client.publish(input)

                self.response.payload.id = auth.id
                self.response.payload.name = auth.name

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an XPath-based security definition.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_security_xpath_change_password_request'
        response_elem = 'zato_security_xpath_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(XPathSecurity, _auth, SECURITY.XPATH_SEC_CHANGE_PASSWORD.value)

class Delete(AdminService):
    """ Deletes an XPath-based security definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_xpath_delete_request'
        response_elem = 'zato_security_xpath_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(XPathSecurity).\
                    filter(XPathSecurity.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                msg = 'Could not delete the XPath security definition, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.XPATH_SEC_DELETE.value
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
