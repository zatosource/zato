# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from base64 import b64decode, b64encode

# Bunch
from bunch import Bunch

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import Delete as _Delete, Index as _Index

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CacheEntry:
    def __init__(self, cache_id=None, key=None, value=None, last_read=None, prev_read=None, prev_write=None, expiry_op=None,
            expires_at=None, hits=None, position=None, server=None):
        self.cache_id = cache_id
        self.key = key
        self._value = value
        self.last_read = last_read
        self.prev_read = prev_read
        self.prev_write = prev_write
        self.expiry_op = expiry_op
        self.expires_at = expires_at
        self.hits = hits
        self.position = position
        self.server = server

    @property
    def value(self):
        if isinstance(self._value, Bunch):
            return self._value.toDict()
        else:
            return self._value

    @value.setter
    def value(self, value):
        self._value = value

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

    def handle(self) -> 'strdict':
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

        if item.key is not None:
            item_key:'any_' = item.key
        else:
            item_key = ''

        item.key_escaped = item_key.encode('utf8') if isinstance(item_key, str) else item_key
        item.key_escaped = b64encode(item.key_escaped)
        item.key_escaped = item.key_escaped.decode('utf8')

        chars_omitted = getattr(item, 'chars_omitted', 0)
        item.chars_omitted = int(chars_omitted)

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
            'key': b64decode(self.req.POST['key']),
            'cluster_id': self.cluster_id
        }

# ################################################################################################################################
