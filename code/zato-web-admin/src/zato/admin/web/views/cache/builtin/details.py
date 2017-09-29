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
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import BaseCallView, Index as _Index

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class CacheEntry(object):
    def __init__(self, cache_id=None, key=None, value=None, last_read=None, prev_read=None, prev_write=None, expiry_op=None,
            expires_at=None, hits=None, position=None):
        self.cache_id = cache_id
        self.key = key
        self.value = value
        self.last_read = last_read
        self.prev_read = prev_read
        self.prev_write = prev_write
        self.expiry_op = expiry_op
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
        output_required = ('cache_id', 'key', 'value', 'position', 'hits', 'expiry_op', 'expiry_left', 'expires_at',
            'last_read', 'prev_read', 'prev_write', 'chars_omitted')
        output_repeated = True

    def handle(self):
        return {
            'show_search_form': True
        }

    def on_before_append_item(self, item, _to_user_dt=('expires_at', 'last_read', 'prev_read', 'prev_write')):
        item.cache_id_escaped = urllib_quote(item.cache_id.encode('utf-8'))
        item.key_escaped = urllib_quote(item.key.encode('utf-8'))

        for name in _to_user_dt:
            value = getattr(item, name)
            if value:
                setattr(item, name, from_utc_to_user(value, self.req.zato.user_profile))

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

# Arrow
from arrow import get as arrow_get

# Bunch
from bunch import bunchify

# Zato
from zato.common import CACHE
from zato.common.search_util import SearchResults
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, GetListAdminSIO

time_keys = ('expires_at', 'last_read', 'prev_read', 'prev_write')

class GetItems(AdminService):
    name = 'cache3.get-items'
    _filter_by = ('name',)

    class SimpleIO(GetListAdminSIO):
        input_required = (AsIs('id'),)
        input_optional = GetListAdminSIO.input_optional + (Int('max_chars'),)
        output_required = (AsIs('cache_id'), 'key', 'value', 'position', 'hits', 'expiry_op', 'expiry_left', 'expires_at',
            'last_read', 'prev_read', 'prev_write', 'chars_omitted')
        output_repeated = True

    def _get_data(self, _ignored_session, _ignored_cluster_id, _time_keys=time_keys, *args, **kwargs):

        # Get the cache object first
        odb_cache = self.server.odb.get_cache_builtin(self.server.cluster_id, self.request.input.id)
        cache = self.cache.get_cache(CACHE.TYPE.BUILTIN, odb_cache.name)

        query_ctx = bunchify(kwargs)
        query = query_ctx.get('query', None)

        max_chars = self.request.input.get('max_chars') or 30
        out = []

        now = self.time.utc_now(needs_format=False)

        # Without any query, simply return a slice of the underlying list from the cache object
        if not query:
            start = query_ctx.cur_page * query_ctx.page_size
            stop = start + query_ctx.page_size

            for idx, item in enumerate(cache[start:stop]):

                # Internally, time is kept as doubles so we need to convert it to a datetime object or null it out.
                for name in _time_keys:
                    _value = item[name]
                    if _value:
                        item[name] = arrow_get(_value)
                    else:
                        item[name] = None

                del _value

                # Compute expiry since the last operation + the time left to expiry
                expiry = item.pop('expiry')
                if expiry:
                    item['expiry_op'] = int(expiry)
                    item['expiry_left'] = int((item['expires_at'] - now).total_seconds())
                else:
                    item['expiry_op'] = None
                    item['expiry_left'] = None

                # Now that we have worked with all the time keys needed, we can serialize them to the ISO-8601 format.
                for name in _time_keys:
                    if item[name]:
                        item[name] = item[name].isoformat()

                # Shorten the value if it's possible, if it's not something else than a string/unicode
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
