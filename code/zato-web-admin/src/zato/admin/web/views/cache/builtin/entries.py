# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import Delete as _Delete, Index as _Index

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class CacheEntry(object):
    def __init__(self, cache_id=None, key=None, value=None, last_read=None, prev_read=None, prev_write=None, expiry_op=None,
            expires_at=None, hits=None, position=None, server=None):
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
        self.server = server

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cache-builtin-get-entries'
    template = 'zato/cache/builtin/entries.html'
    service_name = 'zato.cache.builtin.entry.get-list'
    output_class = CacheEntry
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'cache_id')
        output_required = ('cache_id', 'key', 'value', 'position', 'hits', 'expiry_op', 'expiry_left', 'expires_at',
            'last_read', 'prev_read', 'last_write', 'prev_write', 'chars_omitted', 'server')
        output_repeated = True

    def handle(self):
        return {
            'cluster_id': self.cluster_id,
            'cache_id': self.input.cache_id,
            'show_search_form': True,
            'cache_name': self.req.zato.client.invoke('zato.cache.builtin.get', {
                'cluster_id': self.cluster_id,
                'cache_id': self.input.cache_id
            }).data.response.name
        }

    def on_before_append_item(self, item, _to_user_dt=('expires_at', 'last_read', 'prev_read', 'last_write', 'prev_write')):
        item.key_escaped = item.key.encode('utf8').encode('hex') if isinstance(item.key, basestring) else item.key

        for name in _to_user_dt:
            value = getattr(item, name)
            if value:
                setattr(item, name, from_utc_to_user(value, self.req.zato.user_profile))

        return item

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cache-builtin-delete-entry'
    error_message = 'Could not delete key'
    service_name = 'zato.cache.builtin.entry.delete'

    def get_input_dict(self, *args, **kwargs):
        return {
            'cache_id': self.req.POST['cache_id'],
            'key': self.req.POST['key'].decode('hex'),
            'cluster_id': self.cluster_id
        }

# ################################################################################################################################
