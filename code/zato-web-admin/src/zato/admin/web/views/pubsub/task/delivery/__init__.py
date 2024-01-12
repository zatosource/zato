# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import id_only_service, Index as _Index, method_allowed
from zato.common.util.file_system import fs_safe_name

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class DeliveryTask:
    def __init__(self):
        self.id = None
        self.is_active = None
        self.server_name = None
        self.server_pid = None
        self.task_id = None
        self.sub_keys = None
        self.topics = None

        self.len_messages = None
        self.len_history = None

        self.py_object = None
        self.python_id = None

        self.len_batches = None
        self.len_delivered = None

        self.endpoint_id = None
        self.endpoint_name = None

        self.last_sync = None
        self.last_sync_utc = None

        self.last_sync_sk = None
        self.last_sync_sk_utc = None

        self.last_iter_run = None
        self.last_iter_run_utc = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task'
    template = 'zato/pubsub/task/delivery/task/index.html'
    service_name = 'zato.pubsub.task.delivery.get-delivery-task-list'
    output_class = DeliveryTask
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'server_name', 'server_pid'
        output_required = ('id', 'server_name', 'server_pid', 'py_object', 'python_id',
            'endpoint_id', 'endpoint_name', 'sub_key', 'topic_id', 'topic_name',
            'len_messages', 'len_history', 'len_batches', 'len_delivered', 'ext_client_id', 'is_active')
        output_optional = 'last_sync', 'last_sync_utc', 'last_sync_sk', 'last_sync_sk_utc', 'last_iter_run', 'last_iter_run_utc'
        output_repeated = True

    def get_initial_input(self):
        return {
            'server_pid':self.input.server_pid,
        }

    def handle_return_data(self, return_data):

        for item in return_data['items']:

            item.id = fs_safe_name(item.py_object)

            if item.last_sync:
                item.last_sync_utc = item.last_sync
                item.last_sync = from_utc_to_user(item.last_sync_utc + '+00:00', self.req.zato.user_profile)

            if item.last_sync_sk:
                item.last_sync_sk_utc = item.last_sync_sk
                item.last_sync_sk = from_utc_to_user(item.last_sync_sk_utc + '+00:00', self.req.zato.user_profile)

            if item.last_iter_run:
                item.last_iter_run_utc = item.last_iter_run
                item.last_iter_run = from_utc_to_user(item.last_iter_run_utc + '+00:00', self.req.zato.user_profile)

        return return_data

    def handle(self):
        return {
            'server_name': self.req.zato.args.server_name,
            'server_pid': self.req.zato.args.server_pid,
        }

# ################################################################################################################################

@method_allowed('POST')
def clear_messages(req, server_name, server_pid, task_id, cluster_id):
    return id_only_service(req, 'pubsub.task.clear-messages', id, 'Could not clear messages, e:`{}`')

# ################################################################################################################################

@method_allowed('POST')
def toggle_active(req, server_name, server_pid, task_id, cluster_id):
    return id_only_service(req, 'pubsub.task.toggle-active', id, 'Task active flag could not be toggled, e:`{}`')

# ################################################################################################################################
