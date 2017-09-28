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

# Bunch
from bunch import bunchify

# Zato
from zato.common import CACHE
from zato.common.search_util import SearchResults
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, GetListAdminSIO

null_out = ('expiry', 'expires_at', 'last_read', 'prev_read', 'prev_write')

class GetItems(AdminService):
    name = 'cache3.get-items'
    _filter_by = ('name',)

    class SimpleIO(GetListAdminSIO):
        input_required = (AsIs('id'),)
        input_optional = GetListAdminSIO.input_optional + (Int('max_chars'),)
        output_required = (AsIs('cache_id'), 'key', 'value', 'position', 'hits', 'expiry', 'expires_at', 'last_read',
            'prev_read', 'prev_write', 'chars_omitted')
        output_repeated = True

    def _get_data(self, _ignored_session, _ignored_cluster_id, _null_out=null_out, *args, **kwargs):

        # Get the cache object first
        odb_cache = self.server.odb.get_cache_builtin(self.server.cluster_id, self.request.input.id)
        cache = self.cache.get_cache(CACHE.TYPE.BUILTIN, odb_cache.name)

        query_ctx = bunchify(kwargs)
        query = query_ctx.get('query', None)

        max_chars = self.request.input.get('max_chars') or 50
        out = []

        # Without any query, simply return a slice of the underlying list from the cache object
        if not query:
            start = query_ctx.cur_page * query_ctx.page_size
            stop = start + query_ctx.page_size

            for idx, item in enumerate(cache[start:stop]):

                for name in _null_out:
                    _value = item[name]
                    _value = _value or None
                    item[name] = _value

                del _value

                value = item['value']

                if isinstance(value, basestring):
                    len_value = len(value)
                    chars_omitted = len_value - max_chars
                    chars_omitted = chars_omitted if chars_omitted > 0 else 0

                    if chars_omitted:
                        value = value[:max_chars]

                    item['value'] = value
                    item['chars_omitted'] = chars_omitted


                item['cache_id'] = self.request.input.id
                out.append(item)

            return SearchResults(None, out, None, len(cache))

        else:
            return SearchResults(None, [], None, 0)

    def handle(self):
        self.response.payload[:] = self._search(self._get_data)
'''
