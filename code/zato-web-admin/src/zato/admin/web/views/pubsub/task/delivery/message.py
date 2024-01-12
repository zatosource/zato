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
from zato.admin.web.views import Index as _Index, method_allowed

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Message:
    def __init__(self):
        self.id = None
        self.msg_id = None
        self.published_by_id = None
        self.published_by_name = None
        self.delivery_count = None
        self.recv_time = None
        self.ext_client_id = None
        self.data_prefix_short = None

# ################################################################################################################################
# ################################################################################################################################

class MessageBrowserInFlight(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-message-browser'
    template = 'zato/pubsub/task/message/browser.html'
    service_name = 'pubsub.task.message.get-list2'
    output_class = Message
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'server_name', 'server_pid', 'python_id'
        output_required = 'msg_id', 'published_by_id', 'published_by_name', 'delivery_count', 'recv_time'
        output_optional = 'ext_client_id', 'data_prefix_short'
        output_repeated = True

    def get_initial_input(self):

        return {
            'server_pid':self.input.server_pid,
            'python_id':self.input.python_id,
        }

    def handle_return_data(self, return_data):

        # Get task metadata from a relevant service
        response = self.req.zato.client.invoke('zato.pubsub.task.delivery.get-delivery-task', {
            'server_name':self.input.server_name,
            'server_pid':self.input.server_pid,
            'python_id':self.input.python_id,
        })
        return_data['task'] = response.data

        # Handle the list of results now
        for item in return_data['items']:

            item.id = item.msg_id

            if item.recv_time:
                item.recv_time_utc = item.recv_time
                item.recv_time = from_utc_to_user(item.recv_time_utc + '+00:00', self.req.zato.user_profile)

        return return_data

    def handle(self):
        return {
            'server_name': self.req.zato.args.server_name,
            'server_pid': self.req.zato.args.server_pid,
            'python_id': self.req.zato.args.python_id,
        }

# ################################################################################################################################
# ################################################################################################################################

class MessageBrowserHistory:
    url_name = 'zzz'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get(req, cluster_id, object_id, msg_id):
    pass

# ################################################################################################################################
# ################################################################################################################################
