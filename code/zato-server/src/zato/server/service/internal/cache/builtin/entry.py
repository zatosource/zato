# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Arrow
from arrow import get as arrow_get

# Bunch
from bunch import bunchify

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems
from zato.common.py23_.past.builtins import basestring, long

# Zato
from zato.common.api import CACHE
from zato.common.exception import BadRequest
from zato.server.service import AsIs, Bool, Float, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################

time_keys = ('expires_at', 'last_read', 'prev_read', 'last_write', 'prev_write')

# ################################################################################################################################

class _Base(AdminService):
    """ Base class for services that access the contents of a given cache.
    """
    def _get_cache_by_input(self, needs_config=False):
        cache_id = str(self.request.input.id)
        cache_list = self.server.config_store.get_list('cache_builtin')
        cache_item = None
        for item in cache_list:
            if item.get('id') == cache_id:
                cache_item = item
                break

        if not cache_item:
            raise BadRequest(self.cid, 'Could not find cache with id `{}`'.format(cache_id))

        if needs_config:
            return bunchify(cache_item)
        else:
            return self.cache.get_cache(CACHE.TYPE.BUILTIN, cache_item['name'])

# ################################################################################################################################

class GetList(_Base):
    """ Returns a list of entries from the cache given on input.
    """
    _filter_by = ('name',)

    input = AsIs('id'), Int('-cur_page'), Bool('-paginate'), '-query', Int('-max_chars')
    output = AsIs('id'), 'key', 'position', 'hits', 'expiry_op', 'expiry_left', 'expires_at', \
        'last_read', 'prev_read', 'last_write', 'prev_write', 'server', '-value', '-chars_omitted'

# ################################################################################################################################

    def _enrich_items(self, raw_items, _time_keys=time_keys) -> 'list':

        max_chars = self.request.input.get('max_chars') or 30
        now = self.time.utcnow(needs_format=False)
        out = []

        for item in raw_items:

            if isinstance(item, dict):
                pass
            elif hasattr(item, 'to_dict'):
                item = item.to_dict()
            else:
                continue

            for name in _time_keys:
                _value = item.get(name)
                if _value:
                    item[name] = arrow_get(_value)
                else:
                    item[name] = None

            expiry = item.pop('expiry', None)
            if expiry:
                item['expiry_op'] = int(expiry)
                item['expiry_left'] = int((item['expires_at'] - now).total_seconds())
            else:
                item['expiry_op'] = None
                item['expiry_left'] = None

            for name in _time_keys:
                if item[name]:
                    item[name] = item[name].isoformat()

            value = item.get('value', '')
            if isinstance(value, basestring):
                len_value = len(value)
                chars_omitted = len_value - max_chars
                chars_omitted = chars_omitted if chars_omitted > 0 else 0

                if chars_omitted:
                    value = value[:max_chars]

                item['value'] = value
                item['chars_omitted'] = chars_omitted

            item['id'] = self.request.input.id
            item['server'] = '{} ({})'.format(self.server.name, self.server.pid)
            out.append(item)

        return out

# ################################################################################################################################

    def _filter_cache(self, query, cache):

        out = []
        key_criteria = []
        value_criteria = []

        for item in query:

            if item.startswith('k:'):
                criterion = item.split('k:', 1)[1]
                key_criteria.append(criterion)

            elif item.startswith('v:'):
                criterion = item.split('v:', 1)[1]
                value_criteria.append(criterion)

            else:
                key_criteria.append(item)

        has_empty_key_criteria = len(key_criteria) == 0
        has_empty_value_criteria = len(value_criteria) == 0

        for key, entry in iteritems(cache):

            include_by_key = False
            include_by_value = False

            if key_criteria:
                if all(item in key for item in key_criteria):
                    include_by_key = True

            if value_criteria:
                if all(item in entry.value for item in value_criteria):
                    include_by_value = True

            if (include_by_key or has_empty_key_criteria) and (include_by_value or has_empty_value_criteria):
                out.append(entry.to_dict())

        return out

# ################################################################################################################################

    def handle(self):
        cache = self._get_cache_by_input()
        query = self.request.input.get('query')
        if query:
            raw_items = self._filter_cache(query, cache)
        else:
            raw_items = cache

        items = self._enrich_items(raw_items)
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################

class _CreateEdit(_Base):

    old_key_elem = '<invalid>'
    new_key_elem = 'key'

    input = 'cluster_id', 'id', 'key', 'value', Bool('replace_existing'), '-key_data_type', '-value_data_type', Float('-expiry')

    def handle(self):

        key = self.request.input[self.new_key_elem]
        value = self.request.input.value or ''

        key = int(key) if self.request.input.get('key_data_type') == CACHE.BUILTIN_KV_DATA_TYPE.INT.id else key
        value = int(value) if self.request.input.get('value_data_type') == CACHE.BUILTIN_KV_DATA_TYPE.INT.id else value

        expiry = self.request.input.get('expiry', None) or 0

        # Double check expiry is actually an integer
        try:
            expiry = int(expiry)
        except ValueError:
            raise BadRequest(self.cid, 'Expiry {} must be an integer instead of {}'.format(repr(expiry), type(expiry)))

        cache = self._get_cache_by_input()

        # Note that the try/except/else/set operation below is not atomic

        existing_value = cache.get(key)
        if existing_value:
            if not self.request.input.get('replace_existing'):
                raise BadRequest(self.cid, 'Key `{}` already exists with a value of `{}`'.format(key, existing_value))

        # If we get here it means the key doesn't exist or it's fine to overwrite it.
        cache.set(key, value, expiry)

# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new entry in the cache given on input.
    """
    old_key_elem = 'key'

# ################################################################################################################################

class Update(_CreateEdit):
    """ Updates an existing entry in the cache given on input.
    """
    old_key_elem = 'old_key'

    input = 'cluster_id', 'id', 'key', 'value', Bool('replace_existing'), '-key_data_type', '-value_data_type', \
        Float('-expiry'), '-old_key'

    def handle(self):

        # Invoke common logic
        super(Update, self).handle()

        # Now, if new key and old key are different, we must delete the old one because it was a rename.
        if self.request.input.old_key != self.request.input.key:
            self._get_cache_by_input().delete(self.request.input.old_key)

# ################################################################################################################################

class Get(_Base):
    """ Returns an individual entry from the cache given on input.
    """
    input = 'cluster_id', 'id', 'key'
    output = Bool('key_found'), '-key', '-value', '-is_key_integer', '-is_value_integer', Float('-expiry')

    def handle(self):

        key = self.request.input.key
        cache = self._get_cache_by_input()

        entry = cache.get(key, details=True)

        if entry:
            self.response.payload.key_found = True
            self.response.payload.key = key
            self.response.payload.is_key_integer = isinstance(key, (int, long))
            self.response.payload.value = entry.value
            self.response.payload.is_value_integer = isinstance(entry.value, (int, long))
            self.response.payload.expiry = entry.expiry
        else:
            self.response.payload.key_found = False

# ################################################################################################################################

class Delete(_Base):
    """ Deletes an entry from the cache given on input.
    """
    input = 'cluster_id', 'id', 'key'
    output = Bool('key_found'),

    def handle(self):

        try:
            self._get_cache_by_input().delete(self.request.input.key)
        except KeyError:
            key_found = False
        else:
            key_found = True

        self.response.payload.key_found = key_found

# ################################################################################################################################
