# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from json import dumps
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub.endpoint import CreateForm, EditForm, EndpointQueueEditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, django_url_reverse, Index as _Index, method_allowed, slugify
from zato.admin.web.views.pubsub import get_client_html
from zato.common import ZATO_NONE
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubSubscription, PubSubTopic

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

def enrich_item(cluster_id, item):
    item.topic_patterns = item.topic_patterns or ''
    item.topic_patterns_html = '<br/>'.join(item.topic_patterns.splitlines())

    is_pub = 'pub' in item.role
    is_sub = 'sub' in item.role

    # Making a copy because it will be replaced with a concatenation of sec_type and security_id,
    # yet we still need it for the client string.
    security_id = item.security_id

    if item.security_id:
        item.security_id = '{}/{}'.format(item.sec_type, item.security_id)

    item.client_html = get_client_html(item, security_id, cluster_id)

    html_kwargs={'cluster_id':cluster_id, 'endpoint_id':item.id, 'name_slug':slugify(item.name)}

    if is_pub:
        endpoint_topics_path = django_url_reverse('pubsub-endpoint-topics', kwargs=html_kwargs)
        item.endpoint_topics_html = '<a href="{}">Topics</a>'.format(endpoint_topics_path)
    else:
        item.endpoint_topics_html = '<span class="form_hint">---</span>'

    if is_sub:
        endpoint_queues_path = django_url_reverse('pubsub-endpoint-queues', kwargs=html_kwargs)
        item.endpoint_queues_html = '<a href="{}">Queues</a>'.format(endpoint_queues_path)
    else:
        item.endpoint_queues_html = '<span class="form_hint">---</span>'

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
        output_required = ('id', 'name', 'endpoint_type', 'is_active', 'is_internal', 'role')
        output_optional = ('topic_patterns', 'security_id', 'ws_channel_id', 'ws_channel_name',
            'sec_type', 'sec_name', 'sub_key', 'service_id')
        output_repeated = True

    def on_before_append_item(self, item):
        return enrich_item(self.req.zato.cluster_id, item)

    def handle(self):

        data_list = Bunch()
        data_list.security_list = []
        data_list.ws_channel_list = []
        data_list.service_list = []

        in_use = Bunch()
        in_use.security_list = []
        in_use.ws_channel_list = []
        in_use.service_list = []

        if self.req.zato.cluster_id:

            # Security definitions
            data_list.security_list = self.get_sec_def_list('basic_auth').def_items

            # WebSockets channels
            data_list.ws_channel_list = self.req.zato.client.invoke(
                'zato.channel.web-socket.get-list', {'cluster_id': self.req.zato.cluster_id}).data

            # Services
            data_list.service_list = self.req.zato.client.invoke(
                'zato.service.get-list', {'cluster_id': self.req.zato.cluster_id}).data

            # Build a list of IDs that are already used to make fronted warn of this situation.
            # This is also enforced on SQL level by services.
            in_use.security_list = self.get_already_in_use(data_list.security_list, 'security_id')
            in_use.ws_channel_list = self.get_already_in_use(data_list.ws_channel_list, 'ws_channel_id')
            in_use.service_list = self.get_already_in_use(data_list.service_list, 'service_id')

        return {
            'create_form': CreateForm(self.req, data_list),
            'edit_form': EditForm(self.req, data_list, prefix='edit'),
            'in_use': dumps(in_use),
        }

    def get_already_in_use(self, data_list, id_attr):
        out = []
        id_list = [elem for elem in [getattr(elem, id_attr) for elem in self.items] if elem]

        if id_attr == 'security_id':
            for elem in data_list:
                elem_id = elem[0]
                if elem_id in id_list:
                    out.append(elem)
        else:
            for elem in data_list:
                if elem.id in id_list:
                    out.append(elem)

        return out

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_internal', 'role', 'is_active', 'endpoint_type')
        input_optional = ('is_internal', 'topic_patterns', 'security_id', 'service_id', 'ws_channel_id')
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
        return 'Successfully {} pub/sub endpoint `{}`'.format(self.verb, item.name)

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
    error_message = 'Could not delete pub/sub endpoint'
    service_name = 'zato.pubsub.endpoint.delete'

# ################################################################################################################################

class _EndpointObjects(_Index):
    method_allowed = 'GET'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'endpoint_id')
        output_repeated = True

    def handle(self):
        return {
            'endpoint_id': self.input.endpoint_id,
            'endpoint_name': self.req.zato.client.invoke(
                'zato.pubsub.endpoint.get', {
                    'cluster_id':self.req.zato.cluster_id,
                    'id':self.input.endpoint_id,
                }).data.response.name,
            'edit_form': EndpointQueueEditForm(),
        }

# ################################################################################################################################

class EndpointTopics(_EndpointObjects):
    url_name = 'pubsub-endpoint-topics'
    template = 'zato/pubsub/endpoint-topics.html'
    service_name = 'zato.pubsub.endpoint.get-topic-list'
    output_class = PubSubTopic

    class SimpleIO(_EndpointObjects.SimpleIO):
        output_required = ('topic_id', 'name', 'is_active', 'is_internal', 'max_depth_gd', 'max_depth_non_gd')
        output_optional = ('last_pub_time', 'last_msg_id', 'last_correl_id', 'last_in_reply_to', 'ext_client_id')

    def on_before_append_item(self, item):
        item.last_pub_time = from_utc_to_user(item.last_pub_time+'+00:00', self.req.zato.user_profile)
        return item

# ################################################################################################################################

class EndpointQueues(_EndpointObjects):
    url_name = 'pubsub-endpoint-queues'
    template = 'zato/pubsub/endpoint-queues.html'
    service_name = 'zato.pubsub.endpoint.get-endpoint-queue-list'
    output_class = PubSubSubscription

    class SimpleIO(_EndpointObjects.SimpleIO):
        output_required = ('sub_id', 'topic_id', 'topic_name', 'name', 'active_status', 'is_internal',
            'total_depth', 'current_depth', 'staging_depth')
        output_optional = ('creation_time', 'sub_key', 'has_gd', 'delivery_method', 'delivery_data_format', 'delivery_endpoint',
            'last_interaction_time', 'last_interaction_type', 'last_interaction_details', 'endpoint_name', 'is_staging_enabled',
            'ws_ext_client_id')

    def on_before_append_item(self, item):
        item.creation_time = from_utc_to_user(item.creation_time+'+00:00', self.req.zato.user_profile)
        item.name_slug = slugify(item.name)
        if item.last_interaction_time:
            item.last_interaction_time = from_utc_to_user(item.last_interaction_time+'+00:00', self.req.zato.user_profile)
        return item

# ################################################################################################################################

class EndpointQueueBrowser(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-endpoint-queue-browser'
    template = 'zato/pubsub/endpoint-queue-browser.html'
    service_name = 'zato.pubsub.endpoint.get-endpoint-queue-messages'
    output_class = PubSubEndpointEnqueuedMessage
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'sub_id', 'queue_type')
        output_required = ('msg_id', 'recv_time', 'data_prefix_short', 'has_gd', 'is_in_staging', 'delivery_count',
            'last_delivery_time', 'name', 'endpoint_id')
        output_repeated = True

    def handle(self):

        service_response = self.req.zato.client.invoke(
            'zato.pubsub.endpoint.get-endpoint-queue', {
                'cluster_id':self.req.zato.cluster_id,
                'id':self.input.sub_id,
            }).data.response

        return {
            'sub_id': self.input.sub_id,
            'name': service_response.name,
            'endpoint_id': service_response.endpoint_id,
            'ws_ext_client_id': service_response.ws_ext_client_id
        }

    def on_before_append_item(self, item):
        item.recv_time = from_utc_to_user(item.recv_time+'+00:00', self.req.zato.user_profile)
        return item

# ################################################################################################################################

@method_allowed('POST')
def endpoint_queue_edit(req):

    try:
        sub_id = req.POST['id']
        cluster_id = req.POST['cluster_id']

        request = {
            'id': sub_id,
            'cluster_id': cluster_id,
            'sub_key': req.POST['edit-sub_key'],
            'active_status': req.POST['edit-active_status'],
            'has_gd': req.POST.get('edit-has_gd'),
            'is_staging_enabled': req.POST.get('edit-is_staging_enabled'),
        }

        queue_name = req.zato.client.invoke('zato.pubsub.endpoint.update-endpoint-queue', request).data.name

    except Exception, e:
        return HttpResponseServerError(format_exc(e))
    else:
        service = 'zato.pubsub.endpoint.get-endpoint-queue'
        request = bunchify({
            'id': sub_id,
            'cluster_id': cluster_id,
        })
        response = deepcopy(request)
        response.message = 'Successfully updated sub queue for topic `{}`'.format(queue_name)
        response.queue_name_slug = slugify(queue_name)
        response.update(req.zato.client.invoke(service, request).data.response)

        response.creation_time = from_utc_to_user(response.creation_time+'+00:00', req.zato.user_profile)

        if response.last_interaction_time:
            response.last_interaction_time = from_utc_to_user(
                response.last_interaction_time+'+00:00', req.zato.user_profile)

        return HttpResponse(dumps(response), content_type='application/javascript')

# ################################################################################################################################

@method_allowed('GET')
def endpoint_queue_interactions(req):
    pass

# ################################################################################################################################

@method_allowed('POST')
def endpoint_queue_clear(req, cluster_id, sub_id):

    try:
        req.zato.client.invoke('zato.pubsub.endpoint.clear-endpoint-queue', {
            'id': sub_id,
            'cluster_id': cluster_id,
        })
    except Exception, e:
        return HttpResponseServerError(format_exc(e))
    else:
        queue_name = req.POST['queue_name']
        return HttpResponse('Cleared sub queue `{}`'.format(queue_name))

# ################################################################################################################################

@method_allowed('POST')
def endpoint_queue_delete(req, sub_id, sub_key, cluster_id):

    # Note that sub_id is always ignored, it's sent by JS but we don't use,
    # instead we are interested in sub_key.

    try:
        req.zato.client.invoke('zato.pubsub.endpoint.delete-endpoint-queue', {
            'sub_key': sub_key,
            'cluster_id': cluster_id,
        })
    except Exception, e:
        return HttpResponseServerError(format_exc(e))
    else:
        return HttpResponse() # 200 OK

# ################################################################################################################################
