# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import SEARCH
from zato.common.odb.model import Solr
from zato.common.odb.query import search_solr_list
from zato.common.util import ping_solr
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta, PingMeta

elem = 'search_solr'
model = Solr
label = 'an Solr connection'
get_list_docs = 'Solr connections'
broker_message = SEARCH
broker_message_prefix = 'SOLR_'
list_func = search_solr_list

class GetList(AdminService):
    _filter_by = Solr.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class Ping(AdminService):
    """ Pings a Solr connection to check if it is alive.
    """
    __metaclass__ = PingMeta

    def ping(self, instance):
        ping_solr(instance)
