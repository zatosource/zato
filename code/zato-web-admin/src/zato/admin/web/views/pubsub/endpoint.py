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

# Arrow
from arrow import get as arrow_get

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub.endpoint import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, django_url_reverse, Index as _Index, method_allowed, slugify
from zato.common import ZATO_NONE
from zato.common.odb.model import PubSubEndpoint, PubSubTopic

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

def enrich_item(cluster_id, item):
    item.topic_patterns = item.topic_patterns or ''
    item.topic_patterns_html = '<br/>'.join(item.topic_patterns.splitlines())

    # Making a copy because it will be replaced with a concatenation of sec_type and security_id,
    # yet we still need it for the client string.
    security_id = item.security_id

    if item.security_id:
        item.security_id = '{}/{}'.format(item.sec_type, item.security_id)

    # Client is a string representation of a WebSockets channel or HTTP credentials
    client = ''

    if security_id or item.ws_channel_id:
        if security_id:
            path_name = 'security-basic-auth'
            id_value = security_id
            name = item.sec_name
            protocol = 'HTTP'

        elif item.ws_channel_id:
            path_name = 'channel-web-socket'
            id_value = item.ws_channel_id
            name = item.ws_channel_name
            protocol = 'WebSockets'

        path = django_url_reverse(path_name)
        client = '<span style="font-size:smaller">{}</span><br/><a href="{}?cluster={}&amp;highlight={}">{}</a>'.format(
            protocol, path, cluster_id, id_value, name)

    item.client_html = client

    html_kwargs={'cluster_id':cluster_id, 'endpoint_id':item.id, 'name_slug':slugify(item.name)}

    endpoint_topics_path = django_url_reverse('pubsub-endpoint-topics', kwargs=html_kwargs)
    item.endpoint_topics_html = '<a href="{}">Topics</a>'.format(endpoint_topics_path)

    endpoint_queues_path = django_url_reverse('pubsub-endpoint-queues', kwargs=html_kwargs)
    item.endpoint_queues_html = '<a href="{}">Queues</a>'.format(endpoint_queues_path)

    # This is also needed by the edit action so as not to construct it in JavaScript
    if item.is_internal:
        item.delete_html = '<span class="form_hint">Delete</span>'
    else:
        item.delete_html = """<a href="javascript:$.fn.zato.pubsub.endpoint.delete_('{}')">Delete</a>""".format(item.id)

    return item

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-endpoint'
    template = 'zato/pubsub/endpoint.html'
    service_name = 'zato.pubsub.endpoint.get-list'
    output_class = PubSubEndpoint
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'is_internal', 'role')
        output_optional = ('topic_patterns', 'security_id', 'ws_channel_id', 'ws_channel_name',
            'hook_service_id', 'hook_service_name', 'sec_type', 'sec_name')
        output_repeated = True

    def on_before_append_item(self, item):
        return enrich_item(self.req.zato.cluster_id, item)

    def handle(self):

        if self.req.zato.cluster_id:
            sec_list = self.get_sec_def_list('basic_auth').def_items
            ws_channel_list = result = self.req.zato.client.invoke(
                'zato.channel.web-socket.get-list', {'cluster_id': self.req.zato.cluster_id})
        else:
            sec_list = []
            ws_channel_list = []

        return {
            'create_form': CreateForm(sec_list, ws_channel_list, req=self.req),
            'edit_form': EditForm(sec_list, ws_channel_list, prefix='edit', req=self.req),
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_internal', 'role', 'is_active')
        input_optional = ('topic_patterns', 'security_id', 'ws_channel_id', 'hook_service_id')
        output_required = ('id', 'name')

    def on_after_set_input(self):
        if self.input.security_id and self.input.security_id != ZATO_NONE:
            self.input.security_id = int(self.input.security_id.split('/')[1])
        else:
            self.input.security_id = None

    def post_process_return_data(self, return_data):

        response = self.req.zato.client.invoke('zato.pubsub.endpoint.get', {
            'cluster_id': self.req.zato.cluster_id,
            'id': return_data['id'],
        }).data['response']

        return_data.update(enrich_item(self.req.zato.cluster_id, response))

    def success_message(self, item):
        return 'Successfully {} the pub/sub endpoint `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-endpoint-create'
    service_name = 'zato.pubsub.endpoint.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-endpoint-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.endpoint.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-endpoint-delete'
    error_message = 'Could not delete the pub/sub endpoint'
    service_name = 'zato.pubsub.endpoint.delete'

# ################################################################################################################################

class EndpointTopics(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-endpoint-topics'
    template = 'zato/pubsub/endpoint-topics.html'
    service_name = 'pubapi1.get-topic-list' #'zato.pubsub.endpoint.get-topic-list'
    output_class = PubSubTopic
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'endpoint_id')
        output_required = ('topic_id', 'name', 'is_active', 'is_internal', 'max_depth')
        output_optional = ('last_pub_time', 'last_msg_id', 'last_correl_id', 'last_in_reply_to')
        output_repeated = True

    def on_before_append_item(self, item):
        item.last_pub_time = from_utc_to_user(item.last_pub_time+'+00:00', self.req.zato.user_profile)
        return item

    def handle(self):

        from_utc_to_user
        return {
            'endpoint_id': self.input.endpoint_id,
            'endpoint_name': '333'
        }

# ################################################################################################################################

class EndpointQueues(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-endpoint-queues'
    template = 'zato/pubsub/endpoint-queues.html'
    service_name = 'pubapi1.get-queue-list' #'zato.pubsub.endpoint.get-queue-list'
    output_class = PubSubTopic
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'endpoint_id')
        output_required = ('msg_id', 'delivery_count', 'last_delivery_time', 'endpoint_id', 'topic_id', 'subscription_id')
        output_repeated = True

    def handle(self):
        pass

# ################################################################################################################################
