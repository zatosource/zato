# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import SEARCH
from zato.common.odb.model import ElasticSearch
from zato.common.odb.query import search_es_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'search_es'
model = ElasticSearch
label = 'an ElasticSearch connection'
get_list_docs = 'ElasticSearch connections'
broker_message = SEARCH
broker_message_prefix = 'ES_'
list_func = search_es_list

class GetList(AdminService):
    _filter_by = ElasticSearch.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
