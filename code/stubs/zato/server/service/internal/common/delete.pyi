from typing import Any, TYPE_CHECKING

from contextlib import closing
from copy import deepcopy
from dataclasses import dataclass
from sqlalchemy import delete
from zato.common.odb.model.base import Base as BaseTable
from zato.common.odb.query.common import get_object_list_by_id_list, get_object_list_by_name_list, get_object_list_by_name_contains
from zato.common.typing_ import any_, anylist, callable_, intlistnone, intnone, strdict, strlistnone, strnone, type_
from zato.server.connection.http_soap import BadRequest
from zato.server.service import Model, Service
from bunch import Bunch
from sqlalchemy.orm import Session as SASession
from zato.common.typing_ import strlist
from zato.common.odb.model import HTTPSOAP
from zato.common.odb.model import SecurityBase
from zato.common.odb.model import SQLConnectionPool
from zato.common.odb.model import Job
from zato.common.odb.model import GenericConn, GenericConnDef, GenericObject
from zato.common.odb.model import CacheBuiltin, ChannelAMQP, IMAP, OutgoingAMQP, OutgoingFTP, OutgoingOdoo, OutgoingSAP, Service, SMTP


class BaseDeleteObjectsRequest(Model):
    id: intnone
    id_list: intlistnone
    name: strnone
    name_list: strlistnone
    pattern: strnone

class BaseDeleteObjectsResponse(Model):
    objects: anylist

class DeleteObjectsImplRequest(BaseDeleteObjectsRequest):
    table: BaseTable
    delete_class: type_[Service]

class DeleteObjectsImplResponse(BaseDeleteObjectsResponse):
    ...

class DeleteObjectsRequest(BaseDeleteObjectsRequest):
    object_type: str

class DeleteObjectsResponse(BaseDeleteObjectsResponse):
    ...

class DeleteObjectsImpl(Service):
    def _get_object_data(self: Any, query: any_, table: BaseTable, where: any_) -> anylist: ...
    def _delete_object_list(self: Any, table: BaseTable, object_id_list: anylist) -> anylist: ...
    def _get_object_id_list(self: Any, query: any_, table: BaseTable, where: any_) -> anylist: ...
    def handle(self: Any) -> None: ...

class DeleteObjects(Service):
    name: Any
    def handle(self: Any) -> None: ...

class DeleteMany(Service):
    name: Any
    input: Any
    def _delete(self: Any, session: SASession, tables: any_, pattern: strlist) -> None: ...
    def _delete_rest(self: Any, session: SASession, pattern: strlist) -> None: ...
    def _delete_security(self: Any, session: SASession, pattern: strlist) -> None: ...
    def _delete_sql(self: Any, session: SASession, pattern: strlist) -> None: ...
    def _delete_scheduler(self: Any, session: SASession, pattern: strlist) -> None: ...
    def _delete_generic(self: Any, session: SASession, pattern: strlist) -> None: ...
    def _delete_misc(self: Any, session: SASession, pattern: strlist) -> None: ...
    def handle(self: Any) -> None: ...
