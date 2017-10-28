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
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub.topic import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, django_url_reverse, Index as _Index, method_allowed, slugify
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

    def on_before_append_item(self, item):
        if item.last_pub_time:
            item.last_pub_time = from_utc_to_user(item.last_pub_time+'+00:00', self.req.zato.user_profile)
        return item

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

    def post_process_return_data(self, return_data):

        return_data['publishers_link'] = '<a href="{}">{}</a>'.format(
            django_url_reverse('pubsub-topic-publishers',
                kwargs={'cluster_id':self.req.zato.cluster_id,
                        'topic_id':return_data['id'], 'name_slug':slugify(return_data['name'])}),
            'Publishers')

        return_data['subscribers_link'] = '<a href="{}">{}</a>'.format(
            django_url_reverse('pubsub-topic-subscribers',
                kwargs={'cluster_id':self.req.zato.cluster_id,
                        'topic_id':return_data['id'], 'name_slug':slugify(return_data['name'])}),
            'Subscribers')

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

def topic_clear(req, cluster_id, topic_id):

    try:
        req.zato.client.invoke('zato.pubsub.topic.clear', {
            'cluster_id': cluster_id,
            'id': topic_id,
        })
    except Exception, e:
        return HttpResponseServerError(format_exc(e))
    else:
        msg = 'Cleared topic `{}`'.format(
            req.zato.client.invoke('zato.pubsub.topic.get', {
                'cluster_id': cluster_id,
                'id': topic_id,
            }).data.response.name)

    return HttpResponse(msg)

# ################################################################################################################################

def topic_subscribers(req, cluster_id, topic_id, name_slug):
    pass

# ################################################################################################################################

def topic_publishers(req, cluster_id, topic_id, name_slug):
    pass

# ################################################################################################################################
