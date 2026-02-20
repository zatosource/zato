from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from arrow import get as arrow_get
from bunch import bunchify
from zato.common.ext.future.utils import iteritems
from zato.common.py23_.past.builtins import basestring, long
from zato.common.api import CACHE
from zato.common.exception import BadRequest
from zato.common.util.search import SearchResults
from zato.server.service import AsIs, Bool, Float, Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO


class _Base(AdminService):
    def _get_cache_by_input(self: Any, needs_odb: Any = ...) -> None: ...

class GetList(_Base):
    _filter_by: Any
    def _get_data_from_sliceable(self: Any, sliceable: Any, query_ctx: Any, _time_keys: Any = ...) -> None: ...
    def _filter_cache(self: Any, query: Any, cache: Any) -> None: ...
    def _get_data(self: Any, _ignored_session: Any, _ignored_cluster_id: Any, *args: Any, **kwargs: Any) -> None: ...
    def handle(self: Any) -> None: ...

class _CreateEdit(_Base):
    old_key_elem: Any
    new_key_elem: Any
    def handle(self: Any) -> None: ...

class Create(_CreateEdit):
    old_key_elem: Any

class Update(_CreateEdit):
    old_key_elem: Any
    def handle(self: Any) -> None: ...

class Get(_Base):
    def handle(self: Any) -> None: ...

class Delete(_Base):
    def handle(self: Any) -> None: ...
