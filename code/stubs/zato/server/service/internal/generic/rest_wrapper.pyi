from typing import Any, TYPE_CHECKING

from contextlib import closing
from json import dumps
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.server.service import Service
from zato.common.typing_ import stranydict


def _replace_suffix_from_dict_name(data: stranydict, wrapper_type: str) -> str: ...

class GetList(Service):
    name: Any
    def handle(self: Any) -> None: ...

class _WrapperBase(Service):
    _wrapper_impl_suffix: Any
    _uses_name: Any
    output: Any
    def _handle(self: Any, initial: stranydict) -> None: ...
    def handle(self: Any) -> None: ...

class Create(_WrapperBase):
    name: Any
    response_elem: Any
    _wrapper_impl_suffix: Any
    _uses_name: Any

class Edit(_WrapperBase):
    name: Any
    response_elem: Any
    _wrapper_impl_suffix: Any
    _uses_name: Any

class Delete(_WrapperBase):
    name: Any
    _wrapper_impl_suffix: Any
    _uses_name: Any

class ChangePassword(_WrapperBase):
    name: Any
    _wrapper_impl_suffix: Any
    _uses_name: Any
    def handle(self: Any) -> None: ...

class Ping(_WrapperBase):
    name: Any
    _wrapper_impl_suffix: Any
    _uses_name: Any
