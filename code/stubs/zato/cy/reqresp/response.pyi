from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from http.client import OK
from logging import getLogger
import cython as cy
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement
from sqlalchemy.engine.result import Row as KeyedTuple
from zato.common.api import DATA_FORMAT, RESTAdapterResponse, simple_types, ZATO_OK
from zato.common.marshal_.api import Model
from zato.cy.reqresp.payload import SimpleIOPayload
from zato.common.py23_.past.builtins import unicode as past_unicode
from zato.common.typing_ import any_
from zato.simpleio import CySimpleIO


class Response:
    result: Any
    result_details: Any
    _payload: Any
    content_encoding: Any
    cid: Any
    data_format: Any
    headers: Any
    status_code: Any
    status_message: Any
    sio: Any
    _content_type: Any
    _has_sio_output: Any
    content_type_changed: Any
    content_type: Any
    payload: Any
    def __cinit__(self: Any) -> None: ...
    def __len__(self: Any) -> None: ...
    def init(self: Any, cid: Any, sio: object, data_format: Any) -> None: ...
    def _get_content_type(self: Any) -> None: ...
    def _set_content_type(self: Any, value: Any) -> None: ...
    def _get_payload(self: Any) -> None: ...
    def _set_payload(self: Any, value: Any, _json: Any = ...) -> None: ...
