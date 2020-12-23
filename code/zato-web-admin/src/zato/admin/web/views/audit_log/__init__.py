# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.forms.cache.builtin import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, invoke_service_with_json_response, \
     method_allowed
from zato.common.api import CACHE
from zato.common.model import AuditLogEvent

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'audit-log'
    template = 'zato/audit/index.html'
    service_name = 'zato.audit-log.get-list'
    output_class = AuditLogEvent
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

@method_allowed('POST')
def clear(req):
    return invoke_service_with_json_response(
        req, 'zato.cache.builtin.clear',
        {
            'cluster_id':req.POST['cluster_id'],
            'cache_id':req.POST['cache_id']
        },
        'OK, audit log cleared.', 'Audit log could not be cleared, e:{e}')

# ################################################################################################################################

@method_allowed('GET')
def event_details(req):
    pass

# ################################################################################################################################

@method_allowed('GET')
def delete_event(req):
    pass

# ################################################################################################################################
