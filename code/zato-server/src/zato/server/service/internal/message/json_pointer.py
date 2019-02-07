# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# jsonpointer
# Using 'as' below because Wing IDE confuses it with JSONPointer
from jsonpointer import JsonPointer as _JsonPointer

# Zato
from zato.common import MSG_PATTERN_TYPE
from zato.common.broker_message import MSG_JSON_POINTER
from zato.common.odb.model import Cluster, JSONPointer
from zato.common.odb.query import json_pointer_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ##############################################################################

class GetList(AdminService):
    """ Returns a list of JSON Pointers available.
    """
    _filter_by = JSONPointer.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_message_json_pointer_get_list_request'
        response_elem = 'zato_message_json_pointer_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value')

    def get_data(self, session):
        return self._search(json_pointer_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ##############################################################################

class _CreateEdit(AdminService):
    def check_json_pointer(self, value):
        """ Check whether the expression can be evaluated at all.
        """
        p = _JsonPointer(value)
        p.resolve({}, None)

class Create(_CreateEdit):
    """ Creates a new JSON Pointer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_json_pointer_create_request'
        response_elem = 'zato_message_json_pointer_create_response'
        input_required = ('cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        # Sanity check
        self.check_json_pointer(input.value)

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(JSONPointer).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(JSONPointer.name==input.name).first()

                if existing_one:
                    raise Exception('JSON Pointer `{}` already exists in this cluster'.format(input.name))

                definition = JSONPointer(None, input.name, input.value, cluster.id)

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not create a JSON Pointer, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = MSG_JSON_POINTER.CREATE.value
                self.broker_client.publish(input)

            self.response.payload.id = definition.id
            self.response.payload.name = definition.name

class Edit(_CreateEdit):
    """ Updates a JSON Pointer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_json_pointer_edit_request'
        response_elem = 'zato_message_json_pointer_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        # Sanity check
        self.check_json_pointer(input.value)

        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(JSONPointer).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(JSONPointer.name==input.name).\
                    filter(JSONPointer.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('JSON Pointer [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(JSONPointer).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.value = input.value

                session.add(definition)
                session.commit()

            except Exception:
                self.logger.error('Could not update the JSON Pointer, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                input.action = MSG_JSON_POINTER.EDIT.value
                input.old_name = old_name
                self.request.input.msg_pattern_type = MSG_PATTERN_TYPE.JSON_POINTER.id
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class Delete(AdminService):
    """ Deletes a JSON Pointer.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_json_pointer_delete_request'
        response_elem = 'zato_message_json_pointer_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(JSONPointer).\
                    filter(JSONPointer.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception:
                self.logger.error('Could not delete the JSON Pointer, e:`%s`', format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = MSG_JSON_POINTER.DELETE.value
                self.request.input.name = auth.name
                self.request.input.msg_pattern_type = MSG_PATTERN_TYPE.JSON_POINTER.id
                self.broker_client.publish(self.request.input)
