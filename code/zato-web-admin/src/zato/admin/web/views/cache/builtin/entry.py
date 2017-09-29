# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib

# Django
from django.http.response import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import invoke_service_with_json_response, method_allowed
from zato.admin.web.forms.cache.builtin.entry import CreateForm, EditForm

# ################################################################################################################################

@method_allowed('GET')
def create(req, cache_id, cluster_id):

    out = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'form': CreateForm(''),
        'action': 'create',
        'cache_id': cache_id,
        'cache': req.zato.client.invoke('zato.cache.builtin.get', {
                'cluster_id': req.zato.cluster_id,
                'id': cache_id,
            }).data.response
    }
    return TemplateResponse(req, 'zato/cache/builtin/entry.html', out)

# ################################################################################################################################

@method_allowed('POST')
def create_action(req, cache_id, cluster_id):
    #return invoke_service_with_json_response(req, '
    pass

# ################################################################################################################################

@method_allowed('GET')
def edit(req, cache_id, cluster_id):
    zzz

# ################################################################################################################################

@method_allowed('POST')
def edit_action(req, cache_id, cluster_id):
    eee

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
from zato.common.exception import BadRequest
from zato.common.search_util import SearchResults
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

time_keys = ('expires_at', 'last_read', 'prev_read', 'prev_write')

# ################################################################################################################################

class GetItems(AdminService):
    name = 'cache3.get-entries'
    _filter_by = ('name',)

    class SimpleIO(GetListAdminSIO):
        input_required = (AsIs('id'),)
        input_optional = GetListAdminSIO.input_optional + (Int('max_chars'),)
        output_required = (AsIs('cache_id'), 'key', 'value', 'position', 'hits', 'expiry_op', 'expiry_left', 'expires_at',
            'last_read', 'prev_read', 'prev_write', 'chars_omitted')
        output_repeated = True

# ################################################################################################################################

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

# ################################################################################################################################

    def handle(self):
        self.response.payload[:] = self._search(self._get_data)

# ################################################################################################################################

class _CacheModifyingService(AdminService):
    """ Base class for services that modify the contents of a given cache.
    """
    def _get_cache_by_input(self):
        odb_cache = self.server.odb.get_cache_builtin(self.server.cluster_id, self.request.input.cache_id)
        return self.cache.get_cache(CACHE.TYPE.BUILTIN, odb_cache.name)

# ################################################################################################################################

class Create(_CacheModifyingService):
    name = 'cache3.create-entry'

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'cache_id', 'key', 'value', Bool('ignore_existing'))
        input_optional = ('key_data_type', 'value_data_type', 'expiry')

    def handle(self):

        key = self.request.input.key
        value = self.request.input.value

        key = int(key) if self.request.input.get('key_data_type') == CACHE.BUILTIN_KV_DATA_TYPE.INT.id else key
        value = int(value) if self.request.input.get('value_data_type') == CACHE.BUILTIN_KV_DATA_TYPE.INT.id else value

        expiry = self.request.input.get('expiry', None) or 0

        # Double check expiry is actually an integer
        try:
            int(expiry)
        except ValueError:
            raise BadRequest(self.cid, 'Expiry {} must be an integer instead of {}'.format(repr(expiry)), type(expiry))

        # Note that the check operation below is not atomic
        cache = self._get_cache_by_input()

        existing = cache.get(key)
        if existing and (not self.request.input.ignore_existing):
            raise BadRequest('Key `{}` already exists with value of `{}`'.format(key, existing))

# ################################################################################################################################

class Delete(AdminService):
    name = 'cache3.delete-entry'

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

'''
