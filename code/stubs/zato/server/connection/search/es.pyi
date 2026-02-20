from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from elasticsearch.client import Elasticsearch
from zato.server.store import BaseAPI, BaseStore


class ElasticSearchAPI(BaseAPI):
    ...

class ElasticSearchConnStore(BaseStore):
    def create_impl(self: Any, config: Any, config_no_sensitive: Any) -> None: ...
