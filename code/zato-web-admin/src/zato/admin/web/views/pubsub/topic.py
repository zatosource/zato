# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.pubsub.topic import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, invoke_service_with_json_response, method_allowed
from zato.common.odb.model import PubSubTopic

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
    output_class = PubSubTopic
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active'
        output_optional = 'description', 'publisher_count', 'subscriber_count',
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):

    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
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
    """Retrieves a list of topics matching a pattern."""
    import logging
    logger = logging.getLogger('zato')

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
