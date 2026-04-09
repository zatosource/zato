# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass

# gevent
from gevent import sleep

# Zato
from zato.common.typing_ import any_, anylist, callable_, intlistnone, intnone, strlistnone, strnone, type_
from zato.server.connection.http_soap import BadRequest
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
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

@dataclass(init=False)
class BaseDeleteObjectsResponse(Model):
    objects: anylist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteObjectsImplRequest(BaseDeleteObjectsRequest):
    delete_class: type_[Service]

@dataclass(init=False)
class DeleteObjectsImplResponse(BaseDeleteObjectsResponse):
    pass

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteObjectsRequest(BaseDeleteObjectsRequest):
    object_type: str

@dataclass(init=False)
class DeleteObjectsResponse(BaseDeleteObjectsResponse):
    pass

# ################################################################################################################################
# ################################################################################################################################

class DeleteObjectsImpl(Service):

    class SimpleIO:
        input = DeleteObjectsImplRequest
        output = DeleteObjectsImplResponse

    def _delete_object_list(self, object_id_list:'anylist') -> 'anylist':

        object_id_list = [int(elem) for elem in object_id_list]

        out:'anylist' = []

        for object_id in object_id_list:
            try:
                self.invoke(self.request.input.delete_class.get_name(), {
                    'id': object_id
                })
            except Exception as e:
                self.logger.warning('Exception while deleting object `%s` -> `%s`', object_id, e)
            else:
                out.append({'id': object_id})
                sleep(0.01)

        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        object_id_list:'anylist'

        input = self.request.input # type: DeleteObjectsImplRequest

        if input.id_list:
            object_id_list = input.id_list
        elif input.id:
            object_id_list = [input.id]
        else:
            raise BadRequest(self.cid, 'No deletion criteria were given on input')

        objects = self._delete_object_list(object_id_list)

        response = DeleteObjectsImplResponse()
        response.objects = objects

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class DeleteObjects(Service):

    name = 'zato.common.delete-objects'

    class SimpleIO:
        input = DeleteObjectsRequest
        output = DeleteObjectsResponse

    def handle(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class DeleteMany(Service):

    name = 'pub.zato.common.delete-many'
    input = '-name'

    def handle(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
