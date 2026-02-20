from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime
from zato.common.ext.future.utils import iteritems
from zato.common.api import ZATO_NOT_GIVEN
from zato.common.exception import BadRequest, InternalServerError, NotFound
from zato.server.service import AsIs, Bool, Float, Service


class _BaseService(Service):
    def _get_cache(self: Any, input: Any) -> None: ...
    def _convert_item_dict(self: Any, item_dict: Any, _utcfromtimestamp: Any = ..., _dt_keys: Any = ...) -> None: ...

class SingleKeyService(_BaseService):
    def handle_GET(self: Any) -> None: ...
    def handle_POST(self: Any) -> None: ...
    def handle_DELETE(self: Any) -> None: ...

class _Multi(_BaseService):
    action: Any
    def handle(self: Any) -> None: ...
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class _GetMulti(_Multi):
    action: Any

class _SetMulti(_Multi):
    action: Any

class _DeleteMulti(_Multi):
    action: Any

class _ExpireMulti(_Multi):
    action: Any

class GetByPrefix(_GetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class GetBySuffix(_GetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class GetByRegex(_GetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class GetContains(_GetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class GetNotContains(_GetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class GetContainsAll(_GetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class GetContainsAny(_GetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class SetByPrefix(_SetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class SetBySuffix(_SetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class SetByRegex(_SetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class SetContains(_SetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class SetNotContains(_SetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class SetContainsAll(_SetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class SetContainsAny(_SetMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class DeleteByPrefix(_DeleteMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class DeleteBySuffix(_DeleteMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class DeleteByRegex(_DeleteMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class DeleteContains(_DeleteMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class DeleteNotContains(_DeleteMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class DeleteContainsAll(_DeleteMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class DeleteContainsAny(_DeleteMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class ExpireByPrefix(_ExpireMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class ExpireBySuffix(_ExpireMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class ExpireByRegex(_ExpireMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class ExpireContains(_ExpireMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class ExpireNotContains(_ExpireMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class ExpireContainsAll(_ExpireMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...

class ExpireContainsAny(_ExpireMulti):
    def _get_cache_func(self: Any, cache: Any) -> None: ...
