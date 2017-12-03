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
from zato.common.exception import BadRequest
from zato.common.search_util import SearchResults
from zato.server.service import AsIs, Bool, Float, Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

time_keys = ('expires_at', 'last_read', 'prev_read', 'last_write', 'prev_write')

# ################################################################################################################################

class _Base(AdminService):
    """ Base class for services that access the contents of a given cache.
    """
    def _get_cache_by_input(self, needs_odb=False):
        odb_cache = self.server.odb.get_cache_builtin(self.server.cluster_id, self.request.input.cache_id)

        if needs_odb:
            return odb_cache
        else:
            return self.cache.get_cache(CACHE.TYPE.BUILTIN, odb_cache.name)

# ################################################################################################################################

class GetList(_Base):
    _filter_by = ('name',)

    class SimpleIO(GetListAdminSIO):
        input_required = (AsIs('cache_id'),)
        input_optional = GetListAdminSIO.input_optional + (Int('max_chars'),)
        output_required = (AsIs('cache_id'), 'key', 'position', 'hits', 'expiry_op', 'expiry_left', 'expires_at',
            'last_read', 'prev_read', 'last_write', 'prev_write', 'chars_omitted', 'server')
        output_optional = ('value',)
        output_repeated = True

# ################################################################################################################################

    def _get_data_from_sliceable(self, sliceable, query_ctx, _time_keys=time_keys):

        max_chars = self.request.input.get('max_chars') or 60
        out = []

        now = self.time.utcnow(needs_format=False)

        start = query_ctx.cur_page * query_ctx.page_size
        stop = start + query_ctx.page_size

        for idx, item in enumerate(sliceable[start:stop]):

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

            item['cache_id'] = self.request.input.cache_id
            item['server'] = '{} ({})'.format(self.server.name, self.server.pid)
            out.append(item)

        return SearchResults(None, out, None, len(sliceable))

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

        for key, entry in cache.iteritems():

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

    def _get_data(self, _ignored_session, _ignored_cluster_id, *args, **kwargs):

        # Get the cache object first
        cache = self._get_cache_by_input()

        query_ctx = bunchify(kwargs)
        query = query_ctx.get('query', None)

        # Without any query, simply return a slice of the underlying list from the cache object
        if not query:
            sliceable = cache
        else:
            sliceable = self._filter_cache(query, cache)

        return self._get_data_from_sliceable(sliceable, query_ctx)

# ################################################################################################################################

    def handle(self):
        self.response.payload[:] = self._search(self._get_data)

# ################################################################################################################################

class _CreateEdit(_Base):

    old_key_elem = '<invalid>'
    new_key_elem = 'key'

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'cache_id', 'key', 'value', Bool('replace_existing'))
        input_optional = ('key_data_type', 'value_data_type', Float('expiry'))

    def handle(self):

        key = self.request.input[self.new_key_elem]
        value = self.request.input.value or ''

        key = int(key) if self.request.input.get('key_data_type') == CACHE.BUILTIN_KV_DATA_TYPE.INT.id else key
        value = int(value) if self.request.input.get('value_data_type') == CACHE.BUILTIN_KV_DATA_TYPE.INT.id else value

        expiry = self.request.input.get('expiry', None) or 0

        # Double check expiry is actually an integer
        try:
            int(expiry)
        except ValueError:
            raise BadRequest(self.cid, 'Expiry {} must be an integer instead of {}'.format(repr(expiry)), type(expiry))

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
    old_key_elem = 'key'

# ################################################################################################################################

class Update(_CreateEdit):
    old_key_elem = 'old_key'

    class SimpleIO(_CreateEdit.SimpleIO):
        input_optional = _CreateEdit.SimpleIO.input_optional + ('old_key',)

    def handle(self):

        # Invoke common logic
        super(Update, self).handle()

        # Now, if new key and old key are different, we must delete the old one because it was a rename.
        if self.request.input.old_key != self.request.input.key:
            self._get_cache_by_input().delete(self.request.input.old_key)

# ################################################################################################################################

class Get(_Base):

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'cache_id', 'key')
        output_required = (Bool('key_found'),)
        output_optional = ('key', 'value', 'is_key_integer', 'is_value_integer', Float('expiry'))

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

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'cache_id', 'key')
        output_required = (Bool('key_found'),)

    def handle(self):

        try:
            self._get_cache_by_input().delete(self.request.input.key)
        except KeyError:
            key_found = False
        else:
            key_found = True

        self.response.payload.key_found = key_found

# ################################################################################################################################
