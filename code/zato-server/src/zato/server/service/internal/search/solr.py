# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from urlparse import urlparse

# requests
from requests import get

# Zato
from zato.common.broker_message import SEARCH
from zato.common.odb.model import Solr
from zato.common.odb.query import search_solr_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta, PingMeta

elem = 'search_solr'
model = Solr
label = 'an Solr connection'
broker_message = SEARCH
broker_message_prefix = 'SOLR_'
list_func = search_solr_list

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class Ping(AdminService):
    __metaclass__ = PingMeta

    def ping(self, instance):
        result = urlparse(instance.address)
        get('{}://{}{}'.format(result.scheme, result.netloc, instance.ping_path))
