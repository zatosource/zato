from typing import Any

from dataclasses import dataclass
from zato.common.api import CommonObject
from zato.common.exception import BadRequest
from zato.common.typing_ import any_, anylist, anylistnone, intlistnone, intnone, strdict, strlistnone, strnone
from zato.server.service import Model, Service
from zato.server.service.internal.security.basic_auth import Create as SecBasicAuthCreate

class DataItem(Model):
    name: str
    object_type: str
    initial_data: any_

class CreateObjectsRequest(Model):
    object_type: str
    id: intnone
    id_list: intlistnone
    name: strnone
    name_list: strlistnone
    object_list: anylistnone
    pattern: strnone
    initial_data: any_

class CreateObjectsResponse(Model):
    objects: anylist

class CreateObjects(Service):
    name: Any
    input: Any
    output: Any
    def _get_basic_security_basic_auth(self: Any, name: str, initial_data: strdict) -> strdict: ...
    def _extract_response_items(self: Any, response: strdict) -> strdict: ...
    def _turn_names_into_objects_list(self: Any, input: CreateObjectsRequest) -> CreateObjectsRequest: ...
    def handle(self: Any) -> None: ...
