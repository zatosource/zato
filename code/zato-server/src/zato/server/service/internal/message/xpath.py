# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common import MSG_PATTERN_TYPE
from zato.common.broker_message import MSG_XPATH
from zato.common.odb.model import Cluster, XPath
from zato.common.odb.query import xpath_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ##############################################################################

class GetList(AdminService):
    """ Returns a list of XPaths available.
    """
    _filter_by = XPath.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_message_xpath_get_list_request'
        response_elem = 'zato_message_xpath_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value')

    def get_data(self, session):
        return self._search(xpath_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ##############################################################################

class _CreateEdit(AdminService):
    def check_xpath(self, value):
        """ Check whether the expression can be evaluated at all,
        making sure all the namespaces needed, if any, are already defined.
        """
        self.msg._xpath_store.compile(value, self.msg._ns_store.ns_map)

class Create(_CreateEdit):
    """ Creates a new XPath.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_xpath_create_request'
        response_elem = 'zato_message_xpath_create_response'
        input_required = ('cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        # Sanity check
        self.check_xpath(input.value)

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(XPath).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(XPath.name==input.name).first()

                if existing_one:
                    raise Exception('XPath [{0}] already exists on this cluster'.format(input.name))

                definition = XPath(None, input.name, input.value, cluster.id)

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not create an XPath, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = MSG_XPATH.CREATE.value
                self.broker_client.publish(input)

            self.response.payload.id = definition.id
            self.response.payload.name = definition.name

class Edit(_CreateEdit):
    """ Updates an XPath.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_xpath_edit_request'
        response_elem = 'zato_message_xpath_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        # Sanity check
        self.check_xpath(input.value)

        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(XPath).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(XPath.name==input.name).\
                    filter(XPath.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('XPath [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(XPath).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.value = input.value

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not update the XPath, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = MSG_XPATH.EDIT.value
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class Delete(AdminService):
    """ Deletes an XPath.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_xpath_delete_request'
        response_elem = 'zato_message_xpath_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(XPath).\
                    filter(XPath.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete the XPath, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = MSG_XPATH.DELETE.value
                self.request.input.name = auth.name
                self.request.input.msg_pattern_type = MSG_PATTERN_TYPE.XPATH.id
                self.broker_client.publish(self.request.input)
