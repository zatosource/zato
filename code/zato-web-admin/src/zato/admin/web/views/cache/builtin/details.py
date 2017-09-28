# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from urllib import quote_plus as urllib_quote

# Zato
from zato.admin.web.views import BaseCallView, Index as _Index

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class CacheEntry(object):
    def __init__(self, cache_id=None, key=None, value=None, last_read=None, prev_read=None, prev_write=None, expiry=None,
            expires_at=None, hits=None, position=None):
        self.cache_id = cache_id
        self.key = key
        self.value = value
        self.last_read = last_read
        self.prev_read = prev_read
        self.prev_write = prev_write
        self.expiry = expiry
        self.expires_at = expires_at
        self.hits = hits
        self.position = position

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cache-builtin-get-items'
    template = 'zato/cache/builtin/items.html'
    service_name = 'cache3.get-items' #'zato.cache.builtin.details.get-list'
    output_class = CacheEntry
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'id')
        output_required = ('cache_id', 'key', 'value', 'position', 'hits', 'expiry', 'expires_at', 'last_read', 'prev_read',
            'prev_write', 'chars_omitted')
        output_repeated = True

    def handle(self):
        return {
            'show_search_form': True
        }

    def on_before_append_item(self, item):
        item.cache_id_escaped = urllib_quote(item.cache_id.encode('utf-8'))
        item.key_escaped = urllib_quote(item.key.encode('utf-8'))
        return item

# ################################################################################################################################

class GetItem(BaseCallView):
    method_allowed = 'GET'
    url_name = 'cache-builtin-get-item'
    template = 'zato/cache/builtin/item.html'
    service_name = 'cache3.get-item' #'zato.cache.builtin.details.get-entry'

    class SimpleIO(BaseCallView.SimpleIO):
        input_required = ('cluster_id', 'id', 'key')
        output_required = ('value',)

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.search_util import SearchResults
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, GetListAdminSIO

class GetItems(AdminService):
    name = 'cache3.get-items'
    _filter_by = ('name',)

    class SimpleIO(GetListAdminSIO):
        input_required = (AsIs('id'),)
        output_required = (AsIs('cache_id'), 'key', 'value', 'position', 'hits', 'expiry', 'expires_at', 'last_read',
            'prev_read', 'prev_write')
        output_repeated = True

    def _get_data(self, _ignored_session, _ignored_cluster_id, *args, **kwargs):
        data = [{
            'cache_id':'GEZ · ARX ',
            'key': 'GEZ · ARX ',
            'value': 'zzz',
            'position': 'zzz',
            'hits': 'zzz',
            'expiry': 'zzz',
            'expires_at': 'zzz',
            'last_read': 'zzz',
            'prev_read': 'zzz',
            'prev_write': 'zzz'
        }]
        return SearchResults(None, data, None, 123)

    def handle(self):
        self.response.payload[:] = self._search(self._get_data)
        '''
