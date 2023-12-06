# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from dataclasses import dataclass

# gevent
from gevent import sleep

# Zato
from zato.common.odb.model.base import Base as BaseTable
from zato.common.odb.query.common import get_object_list_by_id_list, get_object_list_by_name_list, \
    get_object_list_by_name_contains
from zato.common.typing_ import any_, anylist, callable_, intlistnone, intnone, strlistnone, strnone
from zato.server.connection.http_soap import BadRequest
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import anylist, strlist
    Bunch = Bunch
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BaseDeleteObjectsRequest(Model):
    id: intnone
    id_list: intlistnone
    name: strnone
    name_list: strlistnone
    pattern: strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteObjectsImplRequest(BaseDeleteObjectsRequest):
    delete_class_: Service
    object_class_: BaseTable

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteObjectsRequest(BaseDeleteObjectsRequest):
    object_type: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteObjectsImplResponse(Model):
    objects_deleted: anylist

# ################################################################################################################################
# ################################################################################################################################

class DeleteObjectsImpl(Service):

    class SimpleIO:
        input = DeleteObjectsImplRequest
        output = DeleteObjectsImplResponse

    def _get_object_data(self, query:'any_', where:'any_') -> 'anylist':

        with closing(self.odb.session()) as session:
            object_data = query(session, where)

        object_data = [dict(elem) for elem in object_data]
        return object_data

# ################################################################################################################################

    def _delete_object_list(self, object_id_list:'anylist') -> 'anylist':

        # Make sure we have a list of integers on input
        object_id_list = [int(elem) for elem in object_id_list]

        # We want to return a list of their IDs along with names so that the API users can easily understand what was deleted
        # which means that we need to construct the list upfront as otherwise, once we delete an object,
        # such information will be no longer available.
        object_data = self._get_object_data(get_object_list_by_id_list, object_id_list)

        # Our response to produce
        out:'anylist' = []

        # A list of object IDs that we were able to delete
        objects_deleted = []

        # Go through each of the input object IDs ..
        for object_id in object_id_list:

            # .. invoke the service that will delete the object ..
            try:
                self.invoke(self.request.input.delete_class_.get_name(), {
                    'id': object_id
                })
            except Exception as e:
                self.logger.warn('Exception while deleting object `%s` -> `%s`', object_id, e)
            else:
                # If we are here, it means that the object was deleted
                # in which case we add its ID for later use ..
                objects_deleted.append(object_id)

                # .. sleep for a while in case to make sure there is no sudden surge of deletions ..
                sleep(0.01)

        # Go through each of the IDs given on input and return it on output too
        # as long as we actually did delete such an object.
        for elem in object_data:
            if elem['id'] in objects_deleted:
                out.append(elem)

        # Return the response to our caller
        return out

# ################################################################################################################################

    def _get_object_id_list(self, query:'any_', where:'any_') -> 'anylist':
        object_data = self._get_object_data(query, where)
        out = [elem['id'] for elem in object_data]
        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        # Type checks
        object_id_list:'anylist'

        # Local aliases
        input = self.request.input # type: DeleteObjectsImplRequest

        # We can be given several types of input elements in the incoming request
        # and we always need to build a list of IDs out of them, unless we already
        # have a list of IDs on input.

        # This is a list - use it as-is
        if input.id_list:
            object_id_list = input.id_list

        # It is an individual object ID - we can turn it into a list as-is
        elif input.id:
            object_id_list = [input.id]

        # It is an individual object name - turn it into a list look it up in the database
        elif input.name:
            query:'callable_' = get_object_list_by_name_list
            where = [input.name]
            object_id_list = self._get_object_id_list(query, where)

        # It is a list of names - look up objects matching them now
        elif input.name_list:
            query:'callable_' = get_object_list_by_name_list
            where = input.name_list if isinstance(input.name_list, list) else [input.name_list] # type: ignore
            object_id_list = self._get_object_id_list(query, where)

        # This is a list of patterns but not necessarily full object names as above
        elif input.pattern:
            query:'callable_' = get_object_list_by_name_contains
            where = input.pattern
            object_id_list = self._get_object_id_list(query, where)

        else:
            raise BadRequest(self.cid, 'No deletion criteria were given on input')

        # No matter how we arrived at this result, we have a list of object IDs
        # and we can delete each of them now ..
        objects_deleted = self._delete_object_list(object_id_list)

        # .. now, we can produce a response for our caller ..
        response = DeleteObjectsImplResponse()
        response.objects_deleted = objects_deleted

        # .. and return it on output
        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################
# ################################################################################################################################
