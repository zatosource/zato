from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import bool as stdlib_bool
from copy import deepcopy
from csv import DictWriter, reader as csv_reader
from datetime import date as stdlib_date, datetime as stdlib_datetime
from decimal import Decimal as decimal_Decimal
from io import StringIO
from json import JSONEncoder
from itertools import chain
from logging import getLogger
from traceback import format_exc
from uuid import UUID as uuid_UUID
import cython as cy
from dateutil.parser import parse as dt_parse
from lxml.etree import _Element as EtreeElementClass, SubElement, XPath
from sqlalchemy.engine.row import Row as SQLAlchemyRow
from zato.common.api import DATA_FORMAT, ZATO_NONE
from zato.common.marshal_.api import ElementMissing
from zato.common.odb.api import SQLRow
from zato.util_convert import to_bool
from zato.bunch import Bunch, bunchify
from zato.common.py23_.past.builtins import basestring, str as past_str
from zato.server.base.parallel import ParallelServer

def _not_implemented(func: Any) -> None: ...

class SIOJSONEncoder(JSONEncoder):
    bytes_to_str_encoding: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def default(self: Any, value: Any) -> None: ...

class _ForceEmptyKeyMarker:
    ...

class _NotGiven:
    def __str__(self: Any) -> None: ...
    def __bool__(self: Any) -> None: ...

class _InternalNotGiven(_NotGiven):
    def __str__(self: Any) -> None: ...

class ServiceInput(Bunch):
    def __getattr__(self: Any, name: Any) -> None: ...
    def deepcopy(self: Any) -> None: ...
    def require_any(self: Any, *elems: Any) -> None: ...

class SIODefault:
    input_value: Any
    output_value: Any
    input_value: Any
    output_value: Any
    def __init__(self: Any, input_value: Any, output_value: Any, default_value: Any) -> None: ...

class SIOSkipEmpty:
    empty_output_value: Any
    skip_input_set: Any
    skip_output_set: Any
    force_empty_input_set: Any
    force_empty_output_set: Any
    skip_all_empty_input: Any
    skip_all_empty_output: Any
    has_skip_input_set: Any
    empty_output_value: Any
    force_empty_input_set: set
    force_empty_output_set: set
    skip_input_set: Any
    skip_all_empty_input: Any
    skip_output_set: Any
    skip_all_empty_output: Any
    has_skip_input_set: bool
    def __init__(self: Any, input_def: Any, output_def: Any, force_empty_input_set: Any, force_empty_output_set: Any, empty_output_value: Any) -> None: ...

class ParsingError(Exception):
    ...

class SerialisationError(Exception):
    ...

class ElemType:
    as_is: int
    bool: int
    csv: int
    date: int
    date_time: int
    decimal: int
    dict_: int
    dict_list: int
    float_: int
    int_: int
    list_: int
    secret: int
    text: int
    utc: int
    uuid: int
    user_defined: int

class Elem:
    _type: Any
    _name: Any
    _xpath: Any
    user_default_value: Any
    default_value: Any
    is_required: Any
    parse_from: Any
    parse_to: Any
    get_default_value: Any
    __str__: Any
    from_json: Any
    to_json: Any
    from_xml: Any
    to_xml: Any
    from_csv: Any
    to_csv: Any
    from_dict: Any
    to_dict: Any
    name: self._get_unicode_name
    is_required: Any
    user_default_value: kwargs.get
    default_value: kwargs.get
    def __cinit__(self: Any) -> None: ...
    def __init__(self: Any, name: Any, **kwargs: Any) -> None: ...
    def __lt__(self: Any, other: Any) -> None: ...
    def __gt__(self: Any, other: Any) -> None: ...
    @property
    def name(self: Any) -> None: ...
    def name(self: Any, name: Any) -> None: ...
    def _get_unicode_name(self: Any, name: object) -> str: ...
    def set_default_value(self: Any, sio_default_value: Any) -> None: ...
    def __repr__(self: Any) -> None: ...
    def __cmp__(self: Any, other: Any) -> None: ...
    def __hash__(self: Any) -> None: ...
    @property
    def pretty(self: Any) -> None: ...
    @property
    def xpath(self: Any) -> None: ...
    def xpath(self: Any, value: Any) -> None: ...

class AsIs(Elem):
    to_dict: Any
    from_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    to_json: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class Bool(Elem):
    to_dict: Any
    from_dict: Any
    to_csv: Any
    to_xml: Any
    from_csv: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...
    @staticmethod
    def to_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def to_json(self: Any, value: Any) -> None: ...
    def get_default_value(self: Any) -> None: ...

class CSV(Elem):
    to_xml: Any
    from_xml: Any
    to_dict: Any
    from_dict: Any
    to_csv: Any
    from_csv: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...
    def to_json(self: Any, value: Any, *ignored: Any) -> None: ...

class Date(Elem):
    stdlib_type: Any
    from_dict: Any
    from_csv: Any
    from_xml: Any
    to_dict: Any
    to_csv: Any
    to_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...
    @staticmethod
    def to_json_static(value: Any, stdlib_type: Any, *args: Any, **kwargs: Any) -> None: ...
    def to_json(self: Any, value: Any) -> None: ...

class DateTime(Date):
    stdlib_type: Any
    def __cinit__(self: Any) -> None: ...

class Decimal(Elem):
    to_dict: Any
    to_csv: Any
    to_xml: Any
    from_dict: Any
    from_csv: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...
    @staticmethod
    def to_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def to_json(self: Any, value: Any) -> None: ...

class Dict(Elem):
    _keys_required: Any
    _keys_optional: Any
    skip_empty: Any
    from_dict: Any
    to_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    def __init__(self: Any, name: Any, *args: Any, **kwargs: Any) -> None: ...
    def set_default_value(self: Any, sio_default_value: Any) -> None: ...
    def set_skip_empty(self: Any, skip_empty: Any) -> None: ...
    @staticmethod
    def from_json_static(data: Any, keys_required: Any, keys_optional: Any, default_value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class DictList(Dict):
    from_dict: Any
    to_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, keys_required: Any, keys_optional: Any, default_value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class Float(Elem):
    to_dict: Any
    from_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class Int(Elem):
    to_dict: Any
    from_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class List(Elem):
    to_dict: Any
    from_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class Text(Elem):
    encoding: Any
    is_secret: Any
    to_dict: Any
    from_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    encoding: kwargs.get
    is_secret: Any
    def __cinit__(self: Any) -> None: ...
    def __init__(self: Any, name: Any, **kwargs: Any) -> None: ...
    @staticmethod
    def _from_value_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class Secret(Text):
    is_secret: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...

class UTC(Elem):
    to_dict: Any
    from_dict: Any
    to_csv: Any
    from_csv: Any
    to_xml: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...

class UUID(Elem):
    to_dict: Any
    to_csv: Any
    to_xml: Any
    from_dict: Any
    from_csv: Any
    from_xml: Any
    def __cinit__(self: Any) -> None: ...
    @staticmethod
    def from_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def from_json(self: Any, value: Any) -> None: ...
    @staticmethod
    def to_json_static(value: Any, *args: Any, **kwargs: Any) -> None: ...
    def to_json(self: Any, value: Any) -> None: ...

class SIO_TYPE_MAP:
    def __iter__(self: Any) -> None: ...

class ConfigItem:
    exact: Any
    prefixes: Any
    suffixes: Any
    def __str__(self: Any) -> None: ...

class BoolConfig(ConfigItem):
    ...

class IntConfig(ConfigItem):
    ...

class SecretConfig(ConfigItem):
    ...

class SIOServerConfig:
    bool_config: Any
    int_config: Any
    secret_config: Any
    json_encoder: Any
    input_required_name: Any
    input_optional_name: Any
    output_required_name: Any
    output_optional_name: Any
    default_value: Any
    default_input_value: Any
    default_output_value: Any
    response_elem: Any
    prefix_as_is: Any
    prefix_bool: Any
    prefix_csv: Any
    prefix_date: Any
    prefix_date_time: Any
    prefix_dict: Any
    prefix_dict_list: Any
    prefix_float: Any
    prefix_int: Any
    prefix_list: Any
    prefix_text: Any
    prefix_uuid: Any
    bytes_to_str_encoding: Any
    skip_empty_keys: Any
    skip_empty_request_keys: Any
    skip_empty_response_keys: Any
    def is_int(self: Any, name: Any) -> cy.bint: ...
    def is_bool(self: Any, name: Any) -> cy.bint: ...
    def is_secret(self: Any, name: Any) -> cy.bint: ...
    def __cinit__(self: Any) -> None: ...

class SIOList:
    elems: Any
    elems_by_name: Any
    def __cinit__(self: Any) -> None: ...
    def __iter__(self: Any) -> None: ...
    def __len__(self: Any) -> None: ...
    def set_elems(self: Any, elems: list) -> None: ...
    def get_elem_by_name(self: Any, name: object) -> Elem: ...
    def get_elem_names(self: Any, use_sorted: Any = ...) -> list: ...

class CSVConfig:
    dialect: Any
    common_config: Any
    writer_config: Any
    should_write_header: Any
    def __cinit__(self: Any) -> None: ...

class XMLConfig:
    namespace: Any
    encoding: Any
    declaration: Any
    pretty_print: Any
    def __cinit__(self: Any) -> None: ...

class SIODefinition:
    _input_required: Any
    _input_optional: Any
    _output_required: Any
    _output_optional: Any
    sio_default: Any
    skip_empty: Any
    _csv_config: Any
    _xml_config: Any
    output_repeated: Any
    has_input_required: Any
    has_input_optional: Any
    has_input_declared: Any
    has_output_required: Any
    has_output_optional: Any
    has_output_declared: Any
    all_input_elem_names: Any
    all_output_elem_names: Any
    all_input_elems: Any
    all_output_elems: Any
    _service_name: Any
    _response_elem: Any
    _has_response_elem: Any
    sio_default: Any
    skip_empty: Any
    def __cinit__(self: Any) -> None: ...
    def __init__(self: Any, sio_default: SIODefault, skip_empty: SIOSkipEmpty) -> None: ...
    def get_input_required(self: Any) -> SIOList: ...
    def get_input_optional(self: Any) -> SIOList: ...
    def get_output_required(self: Any) -> SIOList: ...
    def get_output_optional(self: Any) -> SIOList: ...
    def get_input_required_elem_names(self: Any) -> list: ...
    def get_input_optional_elem_names(self: Any) -> list: ...
    def get_output_required_elem_names(self: Any) -> list: ...
    def get_output_optional_elem_names(self: Any) -> list: ...
    def get_elems_pretty(self: Any, required_list: SIOList, optional_list: SIOList) -> str: ...
    def get_input_pretty(self: Any) -> str: ...
    def get_output_pretty(self: Any) -> str: ...
    def set_csv_config(self: Any, dialect: object, common_config: dict, writer_config: dict, should_write_header: cy.bint) -> None: ...
    def set_xml_config(self: Any, namespace: object, pretty_print: cy.bint, encoding: object, declaration: cy.bint) -> None: ...
    def __str__(self: Any) -> None: ...

class CySimpleIO:
    is_dataclass: Any
    server: Any
    server_config: Any
    definition: Any
    user_declaration: Any
    has_bool_force_empty_keys: Any
    service_class: Any
    def __cinit__(self: Any, server: object, server_config: SIOServerConfig, user_declaration: object) -> None: ...
    def _resolve_bool_force_empty_keys(self: Any) -> None: ...
    def _set_up_csv_config(self: Any) -> None: ...
    def _set_up_xml_config(self: Any) -> None: ...
    def build(self: Any, class_: object) -> None: ...
    def convert_to_elem_instance(self: Any, elem_name: Any, is_required: cy.bint) -> Elem: ...
    def _build_io_elems(self: Any, container: Any, class_: Any) -> None: ...
    @staticmethod
    def attach_sio(server: object, server_config: object, class_: object) -> None: ...
    def _should_skip_on_input(self: Any, definition: SIODefinition, sio_item: Elem, input_value: object) -> cy.bint: ...
    def _parse_input_elem(self: Any, elem: object, data_format: object, is_csv: cy.bint = ..., extra: dict = ...) -> object: ...
    def _parse_input_list(self: Any, data: object, data_format: object, is_csv: cy.bint) -> object: ...
    def parse_input(self: Any, data: object, data_format: object, service: object = ..., extra: dict = ...) -> object: ...
    def _yield_data_dicts(self: Any, data: object, data_format: str) -> None: ...
    def _get_output_csv(self: Any, data: object) -> str: ...
    def _convert_to_dicts(self: Any, data: object, data_format: object) -> object: ...
    def _get_output_json(self: Any, data: object, serialise: cy.bint) -> object: ...
    def _convert_dict_to_xml(self: Any, parent: object, namespace: object, dict_elem: dict) -> None: ...
    def get_output(self: Any, data: object, data_format: object, serialise: cy.int = ...) -> object: ...
    def serialise(self: Any, data: object, data_format: object) -> object: ...
    def eval_multi(self: Any, data: Any, encrypt_func: Any = ...) -> None: ...
    def eval_(self: Any, elem_name: Any, value: Any, encrypt_func: Any = ...) -> None: ...

def is_sio_bool(value: object) -> cy.int: ...

def is_sio_int(value: object) -> cy.int: ...
