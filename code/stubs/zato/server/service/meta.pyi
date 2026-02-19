from typing import Any

from contextlib import closing
from inspect import getmodule, isclass
from itertools import chain
from json import dumps
from logging import getLogger
from time import time
from traceback import format_exc
from bunch import bunchify
from sqlalchemy import Boolean, Integer
from sqlalchemy.exc import IntegrityError
from zato.common.api import ZATO_NOT_GIVEN
from zato.common.odb.model import Base, Cluster
from zato.common.util.api import parse_literal_dict
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.connection.http_soap import BadRequest
from zato.server.service import AsIs, Bool as BoolSIO, Int as IntSIO
from zato.server.service.internal import AdminSIO, GetListAdminSIO
from zato.server.service import Service

def _is_column_required(column: Any) -> None: ...

def get_columns_to_visit(columns: Any, is_required: Any) -> None: ...

def get_io(attrs: Any, elems_name: Any, is_edit: Any, is_required: Any, is_output: Any, is_get_list: Any, has_cluster_id: Any) -> None: ...

def update_attrs(cls: Any, name: Any, attrs: Any) -> None: ...

class AdminServiceMeta(type):
    @staticmethod
    def get_sio() -> None: ...

class GetListMeta(AdminServiceMeta):
    def __init__(cls: Any, name: Any, bases: Any, attrs: Any) -> None: ...
    @staticmethod
    def get_data(get_data_func: Any) -> None: ...
    @staticmethod
    def handle(attrs: Any) -> None: ...

class CreateEditMeta(AdminServiceMeta):
    is_create: Any
    output_required: Any
    def __init__(cls: Any, name: Any, bases: Any, attrs: Any) -> None: ...
    @staticmethod
    def handle(attrs: Any) -> None: ...

class DeleteMeta(AdminServiceMeta):
    def __init__(cls: Any, name: Any, bases: Any, attrs: Any) -> None: ...
    @staticmethod
    def handle(attrs: Any) -> None: ...

class PingMeta(AdminServiceMeta):
    def __init__(cls: Any, name: Any, bases: Any, attrs: Any) -> None: ...
    @staticmethod
    def handle(attrs: Any) -> None: ...
