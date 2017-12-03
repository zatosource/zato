# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.forms.cache.builtin import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, invoke_service_with_json_response, \
     method_allowed
from zato.common import CACHE
from zato.common.odb.model import CacheBuiltin

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cache-builtin'
    template = 'zato/cache/builtin/index.html'
    service_name = 'zato.cache.builtin.get-list'
    output_class = CacheBuiltin
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('cache_id', 'name', 'is_active', 'is_default', 'max_size', 'max_item_size', 'extend_expiry_on_get',
            'extend_expiry_on_set', 'sync_method', 'persistent_storage', 'cache_type', 'current_size')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'default_max_size': CACHE.DEFAULT.MAX_SIZE,
            'default_max_item_size': CACHE.DEFAULT.MAX_ITEM_SIZE,
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cache_id', 'name', 'is_active', 'is_default', 'max_size', 'max_item_size', 'extend_expiry_on_get',
            'extend_expiry_on_set', 'sync_method', 'persistent_storage', 'cache_type', 'current_size')
        output_required = ('cache_id', 'name')

    def success_message(self, item):
        return 'Successfully {} cache `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'cache-builtin-create'
    service_name = 'zato.cache.builtin.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'cache-builtin-edit'
    form_prefix = 'edit-'
    service_name = 'zato.cache.builtin.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cache-builtin-delete'
    error_message = 'Cache could not be deleted'
    service_name = 'zato.cache.builtin.delete'

# ################################################################################################################################

@method_allowed('POST')
def clear(req):
    return invoke_service_with_json_response(
        req, 'zato.cache.builtin.clear', {'cluster_id':req.POST['cluster_id'], 'cache_id':req.POST['cache_id']},
        'OK, cache cleared.', 'Cache could not be cleared, e:{e}')

# ################################################################################################################################
