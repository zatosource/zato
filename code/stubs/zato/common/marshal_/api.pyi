from typing import Any

from dataclasses import asdict, _FIELDS, make_dataclass, MISSING, _PARAMS
from http.client import BAD_REQUEST
from inspect import isclass
from sys import exc_info
from traceback import extract_stack, extract_tb
from bson import ObjectId
from dateutil.parser import parse as dt_parse
from orjson import dumps
from sqlalchemy.sql.schema import Table
from typing_utils import issubtype
from zato.common.api import ZatoNotGiven
from zato.common.exception import BackendInvocationError
from zato.common.marshal_.model import BaseModel
from zato.common.typing_ import cast_, date_, datetime_, datetimez, extract_from_union, isotimestamp, is_union, type_
from typing import _GenericAlias as _ListBaseClass
from dataclasses import Field
from zato.common.typing_ import any_, anydict, anylist, boolnone, dictnone, intnone, optional, tuplist
from zato.server.base.parallel import ParallelServer
from zato.server.service import Service
from zato.simpleio import is_sio_bool, is_sio_int

def is_list(field_type: Field, is_class: bool) -> bool: ...

def extract_model_class(field_type: Field) -> Model | None: ...

class Model(BaseModel):
    __name__: str
    after_created: Any
    from_dict: Any
    def __getitem__(self: Any, name: Any, default: Any = ...) -> None: ...
    def __contains__(self: Any, name: Any) -> None: ...
    def get(self: Any, name: Any) -> None: ...
    @classmethod
    def zato_get_fields(class_: any_) -> anydict: ...
    @classmethod
    def _zato_from_dict(class_: Any, data: Any, extra: Any = ...) -> None: ...
    def to_dict(self: Any) -> None: ...
    def _json_default_serializer(self: Any, value: Any) -> None: ...
    def to_json(self: Any, default: Any = ..., impl_extra: Any = ...) -> None: ...
    def clone(self: Any) -> any_: ...
    @staticmethod
    def build_model_from_flat_input(server: Any, sio_server_config: Any, _CySimpleIO: Any, name: Any, input: Any) -> type_[BaseModel]: ...

class ModelCtx:
    service: Service
    data: anydict | Model
    DataClass: any_

class ModelValidationError(Exception):
    elem_path: Any
    reason: self.get_reason
    msg: self.get_reason
    status: Any
    needs_msg: Any
    def __init__(self: Any, elem_path: str) -> None: ...
    def get_reason(self: Any) -> None: ...

class ElementMissing(ModelValidationError):
    __str__: Any
    def __repr__(self: Any) -> None: ...
    def get_reason(self: Any) -> None: ...

class ElementIsNotAList(ElementMissing):
    def get_reason(self: Any) -> None: ...

class DictCtx:
    service: Any
    current_dict: Any
    extra: Any
    DataClass: Any
    list_idx: Any
    parent: Any
    has_init: Any
    fields: Any
    init_attrs: Any
    setattr_attrs: Any
    attrs_container: cast_
    def __init__(self: Any, service: Service, current_dict: anydict | Model, DataClass: any_, extra: dictnone, list_idx: intnone, parent: optional[FieldCtx] = ...) -> None: ...
    def init(self: Any) -> None: ...

class FieldCtx:
    dict_ctx: Any
    field: Any
    parent: Any
    name: Any
    field_type: Any
    model_class: Any
    value: Any
    is_class: Any
    is_list: Any
    is_required: Any
    is_model: Any
    contains_model: Any
    has_extra: Any
    def __init__(self: Any, dict_ctx: Any, field: Any, parent: Any) -> None: ...
    def init(self: Any) -> None: ...
    def get_name(self: Any) -> None: ...

class MarshalAPI:
    _field_cache: Any
    def __init__(self: Any) -> None: ...
    def get_validation_error(self: Any, field_ctx: Any, error_class: Any = ...) -> ModelValidationError: ...
    def _self_require_dict_or_model(self: Any, field_ctx: FieldCtx) -> None: ...
    def _visit_list(self: Any, field_ctx: FieldCtx) -> anylist: ...
    def from_field_ctx(self: Any, field_ctx: FieldCtx) -> any_: ...
    def _ensure_value_is_a_list(self: Any, field_ctx: FieldCtx, value: any_) -> None: ...
    def from_dict(self: Any, service: Service, current_dict: anydict | BaseModel, DataClass: any_, extra: dictnone = ..., list_idx: intnone = ..., parent: optional[FieldCtx] = ...) -> any_: ...
    def unmarshall(self: Any, data: dict, class_: any_) -> any_: ...
