# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.cache.memcached import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import CACHE
from zato.common.odb.model import CacheBuiltin

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cache-memcached'
    template = 'zato/cache/memcached/index.html'
    service_name = 'zato.cache.memcached.get-list'
    output_class = CacheBuiltin
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'is_default', 'is_debug', 'servers', 'extra', 'cache_type')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'default_max_size': CACHE.DEFAULT.MAX_SIZE,
            'default_max_item_size': CACHE.DEFAULT.MAX_ITEM_SIZE,
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'is_default', 'is_debug', 'servers', 'extra', 'cache_type')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} cache `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'cache-memcached-create'
    service_name = 'zato.cache.memcached.create'

class Edit(_CreateEdit):
    url_name = 'cache-memcached-edit'
    form_prefix = 'edit-'
    service_name = 'zato.cache.memcached.edit'

class Delete(_Delete):
    url_name = 'cache-memcached-delete'
    error_message = 'Cache could not be deleted'
    service_name = 'zato.cache.memcached.delete'

class DetailsIndex(_Index):
    method_allowed = 'GET'
    url_name = 'cache-memcached-details'
