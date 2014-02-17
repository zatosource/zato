# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.pubsub.topics import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import PUB_SUB
from zato.common.odb.model import PubSubTopic

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-producers'
    template = 'zato/pubsub/topics.html'
    service_name = 'zato.pubsub.topics.get-list'
    output_class = PubSubTopic

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'current_depth', 'max_depth', 'consumers_count', 'producers_count')
        output_repeated = True

    def handle(self):
        return {
            'default_max_depth': PUB_SUB.DEFAULT_MAX_DEPTH,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cluster_id', 'name', 'is_active', 'max_depth')
        output_required = ('id', 'name')

    def __call__(self, req, initial_input_dict={}, initial_return_data={}, *args, **kwargs):
        initial_return_data = {
            'current_depth': 123,
            'consumers_count': 1,
            'producers_count': 789,
            'last_pub_time': '2010-01-02T03:04:05.0607',
        }
        return super(_CreateEdit, self).__call__(
            req, initial_input_dict={}, initial_return_data=initial_return_data, *args, **kwargs)

    def success_message(self, item):
        return 'Successfully {0} the topic [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'pubsub-topics-create'
    service_name = 'zato.pubsub.topics.create'

class Edit(_CreateEdit):
    url_name = 'pubsub-topics-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.topics.edit'

class Delete(_Delete):
    url_name = 'pubsub-topics-delete'
    error_message = 'Could not delete the topic'
    service_name = 'zato.pubsub.topics.delete'
