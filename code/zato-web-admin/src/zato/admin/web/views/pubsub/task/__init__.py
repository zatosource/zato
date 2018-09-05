# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.search.solr import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, id_only_service, Index as _Index, method_allowed
from zato.common.util import fs_safe_name

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class DeliveryTask(object):
    def __init__(self):
        self.id = None
        self.server_name = None
        self.server_pid = None
        self.task_id = None
        self.thread_id = None
        self.object_id = None
        self.sub_keys = None
        self.topics = None
        self.messages = None

        self.last_sync = None
        self.last_sync_utc = None

        self.last_delivery = None
        self.last_delivery_utc = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task'
    template = 'zato/pubsub/task/index.html'
    service_name = 'pubsub.task.get-list'
    output_class = DeliveryTask
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'server_name', 'server_pid', 'thread_id', 'object_id', 'sub_key', 'topic_id', 'topic_name',
            'messages', 'ext_client_id')
        output_optional = ('last_sync', 'last_sync_utc', 'last_delivery', 'last_delivery_utc')
        output_repeated = True

    def handle_return_data(self, return_data):

        for item in return_data['items']:

            item.id = fs_safe_name('{}-{}'.format(item.thread_id, item.object_id))

            if item.last_sync:
                item.last_sync_utc = item.last_sync
                item.last_sync = from_utc_to_user(item.last_sync_utc + '+00:00', self.req.zato.user_profile)

            if item.last_delivery:
                item.last_delivery_utc = item.last_delivery
                item.last_delivery = from_utc_to_user(item.last_delivery_utc + '+00:00', self.req.zato.user_profile)

        return return_data

    def handle(self):
        return {
            'server_name': self.req.zato.args.server_name,
            'server_pid': self.req.zato.args.server_pid
        }

# ################################################################################################################################

@method_allowed('POST')
def clear_messages(req, server_name, server_pid, task_id, cluster_id):
    return id_only_service(req, 'pubsub.task.clear-messages', id, 'Could not clear messages, e:`{}`')

# ################################################################################################################################

@method_allowed('POST')
def toggle_active(req, server_name, server_pid, task_id, cluster_id):
    return id_only_service(req, 'pubsub.task.toggle-active', id, 'Could not toggle server\'s active flag, e:`{}`')

# ################################################################################################################################
