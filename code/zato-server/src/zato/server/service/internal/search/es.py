# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Python 2/3 compatibility
from six import add_metaclass

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

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = ElasticSearch.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################
