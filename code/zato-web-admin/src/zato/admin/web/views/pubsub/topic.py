# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from http.client import INTERNAL_SERVER_ERROR
from traceback import format_exc

# Django
from django.http import HttpResponse, JsonResponse

# Zato
from zato.admin.web.forms.pubsub.topic import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.admin.web.views.http_soap import _build_invoke_response

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-topic'
    template = 'zato/pubsub/topic.html'
    service_name = 'zato.pubsub.topic.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active'
    output_optional = 'description', 'publisher_count', 'subscriber_count',
    output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'show_search_form': True,
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):

    method_allowed = 'POST'

    input_required = 'name', 'is_active'
    input_optional = 'description',
    output_required = 'id', 'name'

    def success_message(self, item):
        return 'Successfully {} Pub/Sub topic `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-topic-create'
    service_name = 'zato.pubsub.topic.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-topic-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.topic.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-topic-delete'
    error_message = 'Could not delete the Pub/Sub topic'
    service_name = 'zato.pubsub.topic.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_matches(req):
    """ Retrieves a list of topics matching a pattern.
    """
    cluster_id = req.POST.get('cluster_id')
    pattern = req.POST.get('pattern')

    logger.info('VIEW get_matches: received request with cluster_id=%s, pattern=%s', cluster_id, pattern)

    service_response = req.zato.client.invoke('zato.pubsub.topic.get-matches', {
        'cluster_id': cluster_id,
        'pattern': pattern,
    })

    logger.info('VIEW get_matches: service_response.ok=%s, data=%r',
                service_response.ok, service_response.data if service_response.ok else service_response.details)

    if service_response.ok:
        return HttpResponse(
            json.dumps({
                'msg': 'Topics retrieved successfully',
                'matches': service_response.data
            }),
            content_type='application/json'
        )
    else:
        return HttpResponse(
            json.dumps({
                'error': service_response.details or 'Error retrieving matching topics'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def publish_message(request:'any_', id:'str') -> 'JsonResponse':
    """ Publishes a message to a pub/sub topic from the dashboard.
    """
    try:
        # Get the topic name and message data from the form ..
        topic_name = request.POST['topic_name']
        data = request.POST['data-request']

        # .. and invoke the publish service.
        service_response = request.zato.client.invoke('zato.pubsub.topic.publish', {
            'topic_name': topic_name,
            'data': data,
        })

        out = _build_invoke_response(service_response)
        return out

    except Exception:
        traceback = format_exc()
        logger.error('publish_message error: %s', traceback)

        out = JsonResponse({
            'data': traceback,
            'response_time_human': '',
            'content_type': 'text/plain',
        }, status=INTERNAL_SERVER_ERROR)

        return out

# ################################################################################################################################
# ################################################################################################################################
