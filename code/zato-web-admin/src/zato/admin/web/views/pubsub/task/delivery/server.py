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
from zato.admin.web.views import Index as _Index
from zato.common.util.file_system import fs_safe_name

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class DeliveryServer:
    def __init__(self):
        self.id = None
        self.name = None
        self.pid = None
        self.tasks = None
        self.tasks_running = None
        self.tasks_stopped = None
        self.sub_keys = None
        self.topics = None

        self.messages = None
        self.messages_gd = None
        self.messages_non_gd = None
        self.msg_handler_counter = 0

        self.last_gd_run = None
        self.last_gd_run_utc = None

        self.last_sync = None
        self.last_sync_utc = None

        self.last_task_run = None
        self.last_task_run_utc = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-delivery-server'
    template = 'zato/pubsub/task/delivery/server.html'
    service_name = 'zato.pubsub.task.delivery.server.get-list'
    output_class = DeliveryServer
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'pid', 'tasks', 'tasks_running', 'tasks_stopped', 'sub_keys', 'topics',
            'messages', 'messages_gd', 'messages_non_gd', 'msg_handler_counter')
        output_optional = ('last_gd_run', 'last_gd_run_utc', 'last_task_run', 'last_task_run_utc')
        output_repeated = True

    def handle_return_data(self, return_data):

        for item in return_data['items']:

            item.id = fs_safe_name('{}-{}'.format(item.name, item.pid))

            if item.last_gd_run:
                item.last_gd_run_utc = item.last_gd_run

                if item.last_gd_run_utc:
                    item.last_gd_run = from_utc_to_user(item.last_gd_run_utc + '+00:00', self.req.zato.user_profile)

            if item.last_task_run:
                item.last_task_run_utc = item.last_task_run
                item.last_task_run = from_utc_to_user(item.last_task_run_utc + '+00:00', self.req.zato.user_profile)

        return return_data

    def handle(self):
        return {}

# ################################################################################################################################
