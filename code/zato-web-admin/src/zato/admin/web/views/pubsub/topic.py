# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from json import dumps
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.pubsub.topic import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import PubSubTopic

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-topic'
    template = 'zato/pubsub/topic.html'
    service_name = 'zato.pubsub.topic.get-list'
    output_class = PubSubTopic
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'max_depth', 'current_depth')
        output_optional = ('last_pub_time',)
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'max_depth')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the pub/sub topic `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-topic-create'
    service_name = 'zato.pubsub.topic.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-topic-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.topic.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-topic-delete'
    error_message = 'Could not delete the pub/sub topic'
    service_name = 'zato.pubsub.topic.delete'

# ################################################################################################################################

def topic_details(req, cluster_id, topic_id, name_slug):
    pass

# ################################################################################################################################

def topic_subscribers(req, cluster_id, topic_id, name_slug):
    pass

# ################################################################################################################################

def topic_publishers(req, cluster_id, topic_id, name_slug):
    pass

# ################################################################################################################################
