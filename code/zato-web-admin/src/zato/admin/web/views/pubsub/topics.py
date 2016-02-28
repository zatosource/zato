# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

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
from zato.admin.web.forms.pubsub.topics import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common import PUB_SUB
from zato.common.odb.model import PubSubTopic

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-topics'
    template = 'zato/pubsub/topics/index.html'
    service_name = 'zato.pubsub.topics.get-list'
    output_class = PubSubTopic

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'current_depth',
            'max_depth', 'consumers_count', 'producers_count', 'last_pub_time')
        output_repeated = True

    def handle(self):
        return {
            'default_max_depth': PUB_SUB.DEFAULT_MAX_DEPTH,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

    def _handle_item_list(self, item_list):
        super(Index, self)._handle_item_list(item_list)
        for item in self.items:
            if item.last_pub_time:
                item.last_pub_time = from_utc_to_user(item.last_pub_time + '+00:00', self.req.zato.user_profile)

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cluster_id', 'is_active', 'max_depth')
        input_optional = ('name',)
        output_required = ('id', 'name')

    def __call__(self, req, initial_input_dict={}, initial_return_data={}, *args, **kwargs):

        edit_name = req.POST.get('edit-name')
        name = req.POST.get('name', edit_name)

        initial_return_data = {
            'current_depth': 0,
            'consumers_count': 0,
            'producers_count': 0,
            'last_pub_time': None,
            'cluster_id': req.zato.cluster_id,
            'name': name,
        }

        if edit_name:
            response = req.zato.client.invoke('zato.pubsub.topics.get-info', {
                'cluster_id': req.zato.cluster_id,
                'name': edit_name
            })

            if response.ok:
                initial_return_data.update(response.data)
                if initial_return_data['last_pub_time']:
                    initial_return_data['last_pub_time'] = from_utc_to_user(
                        initial_return_data['last_pub_time'] + '+00:00', req.zato.user_profile)

        return super(_CreateEdit, self).__call__(
            req, initial_input_dict={}, initial_return_data=initial_return_data, *args, **kwargs)

    def success_message(self, item):
        return 'Successfully {0} the topic [{1}]'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-topics-create'
    service_name = 'zato.pubsub.topics.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-topics-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.topics.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-topics-delete'
    error_message = 'Could not delete the topic'
    service_name = 'zato.pubsub.topics.delete'

# ################################################################################################################################

@method_allowed('GET')
def publish(req, cluster_id, topic):

    return_data = {
        'cluster_id': cluster_id,
        'topic': topic,
        'default_mime_type': PUB_SUB.DEFAULT_MIME_TYPE,
        'default_priority': PUB_SUB.DEFAULT_PRIORITY,
        'default_expiration': int(PUB_SUB.DEFAULT_EXPIRATION),
    }

    return TemplateResponse(req, 'zato/pubsub/topics/publish.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def publish_action(req, cluster_id, topic):

    try:
        request = {'cluster_id': req.zato.cluster_id}
        request.update({k:v for k, v in req.POST.items() if k and v})
        response = req.zato.client.invoke('zato.pubsub.topics.publish', request)

        if response.ok:
            msg = 'Published message `{}` to topic `{}`'.format(response.data.msg_id, req.POST['name'])
            return HttpResponse(dumps({'msg': msg}), content_type='application/javascript')
        else:
            raise Exception(response.details)
    except Exception, e:
        msg = 'Caught an exception, e:`{}`'.format(format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
