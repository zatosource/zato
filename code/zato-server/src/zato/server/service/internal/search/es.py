# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.common.broker_message import SEARCH
from zato.common.odb.model import ElasticSearch
from zato.common.odb.query import search_es_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, GetListMeta

logger = getLogger(__name__)

class DeleteMeta(type):
    def __init__(cls, name, bases, attrs):
        logger.warn('111111 %r %r %r %r', cls, name, bases, attrs)

class GetList(AdminService):
    __metaclass__ = GetListMeta
    elem = 'search_es'
    output_required = ElasticSearch
    get_data_func = search_es_list

class Create(AdminService):
    __metaclass__ = CreateEditMeta
    is_create_edit = True
    is_edit = False
    elem = 'search_es'
    model = ElasticSearch
    input_required = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'

class Edit(AdminService):
    __metaclass__ = CreateEditMeta
    is_create_edit = True
    is_edit = True
    elem = 'search_es'
    model = ElasticSearch
    input_required = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'

class Delete(AdminService):
    __metaclass__ = DeleteMeta
    model = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'
