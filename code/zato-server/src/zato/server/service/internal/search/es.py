# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import SEARCH
from zato.common.odb.model import ElasticSearch
from zato.common.odb.query import search_es_list
from zato.server.service import Int
from zato.server.service.internal import AdminService
from zato.server.service.meta import GetListMeta

class CreateEditMeta(type):
    is_create = False
    output_required = ('id', 'name')

class BaseDelete(type):
    pass

class GetList(AdminService):
    __metaclass__ = GetListMeta
    elem = 'search_es'
    output_required = ElasticSearch
    get_data_func = search_es_list

class _CreateEdit(AdminService):
    elem = 'search_es'
    model = ElasticSearch
    input_required = ('name', 'is_active', 'hosts', Int('timeout'), 'body_as')
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'

class Create(_CreateEdit):
    is_create = True

class Edit(_CreateEdit):
    is_create = False

class Delete(object):
    model = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'
