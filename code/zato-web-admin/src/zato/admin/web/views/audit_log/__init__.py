# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.cache.builtin import CreateForm, EditForm
from zato.admin.web.views import Index as _Index, invoke_service_with_json_response, \
     method_allowed
from zato.common.api import CACHE
from zato.common.model.audit_log import AuditLogEvent

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'audit-log'
    template = 'zato/audit-log/index.html'
    service_name = 'zato.audit-log.event.get-list'
    output_class = AuditLogEvent
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_', 'object_id', 'object_name', 'object_type_label'
        output_required = 'server_name', 'server_pid', 'type_', 'object_id', 'conn_id', 'direction', 'data', 'timestamp', \
            'timestamp_utc', 'msg_id', 'in_reply_to', 'event_id'
        output_optional = 'data',
        output_repeated = True

    def on_before_append_item(self, item):
        # type: (AuditLogEvent)
        item.timestamp_utc = item.timestamp
        item.timestamp = from_utc_to_user(item.timestamp+'+00:00', self.req.zato.user_profile)
        return item

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'default_max_size': CACHE.DEFAULT.MAX_SIZE,
            'default_max_item_size': CACHE.DEFAULT.MAX_ITEM_SIZE,
            'cluster_id': self.input.cluster_id,
            'type_': self.input.type_,
            'object_id': self.input.object_id,
            'object_name': self.input.object_name,
            'object_type_label': self.input.object_type_label,
        }

# ################################################################################################################################

@method_allowed('POST')
def clear(req):
    return invoke_service_with_json_response(
        req, 'zato.audit-log.event.clear',
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
