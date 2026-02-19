from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from six import add_metaclass
from zato.common.broker_message import SEARCH
from zato.common.odb.model import ElasticSearch
from zato.common.odb.query import search_es_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

class GetList(AdminService):
    _filter_by: Any

class Create(AdminService):
    ...

class Edit(AdminService):
    ...

class Delete(AdminService):
    ...
