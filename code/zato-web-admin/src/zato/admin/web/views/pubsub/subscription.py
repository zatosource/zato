# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.pubsub.subscription import CreateForm, EditForm
from zato.admin.web.util import get_pubsub_security_definitions, get_service_list as util_get_service_list
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, get_outconn_rest_list
from zato.common.odb.model import PubSubSubscription

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-subscription'
    template = 'zato/pubsub/subscription.html'
    service_name = 'zato.pubsub.subscription.get-list'
    output_class = PubSubSubscription
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_links', 'sec_base_id', 'sec_name', 'delivery_type', \
            'push_type', 'rest_push_endpoint_id', 'rest_push_endpoint_name', 'push_service_name', 'topic_names'
        output_repeated = True

    def on_before_append_item(self, item):
        topic_names = item.topic_names
        item.topic_names = dumps(topic_names)
        return item

    def handle(self):
        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)
        return {
            'create_form': create_form,
            'edit_form': edit_form,
            'show_search_form': True,
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):

    def post_process_return_data(self, return_data):
        topic_names = return_data['topic_names']
        return_data['topic_names'] = dumps(topic_names)
        return return_data

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-create'
    service_name = 'zato.pubsub.subscription.create'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'cluster_id', 'topic_id_list', 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
        output_required = 'id', 'sub_key', 'is_active', 'created', 'topic_links', 'sec_name', 'delivery_type', 'topic_names'

    def _get_input_dict(self):

        input_dict = {}

        # Map topic_id form field (which can be multiple) to topic_id_list service input
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('create-topic_id')
            if topic_ids:
                input_dict['topic_id_list'] = topic_ids

        return input_dict

    def pre_process_input_dict(self, input_dict):

        # Extract topic IDs from form POST data
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('topic_id')
            input_dict['topic_id_list'] = topic_ids

            # Map other form fields
            field_mapping = {
                'sec_base_id': 'sec_base_id',
                'delivery_type': 'delivery_type',
                'is_active': 'is_active',
                'rest_push_endpoint_id': 'rest_push_endpoint_id'
            }

            for form_field, service_field in field_mapping.items():
                value = self.req.POST.get(form_field)
                if value:
                    if service_field == 'is_active':
                        input_dict[service_field] = value == 'on'
                    else:
                        input_dict[service_field] = value

    def success_message(self, item):
        return 'Successfully created pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-edit'
    service_name = 'zato.pubsub.subscription.edit'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'sub_key', 'cluster_id', 'topic_id_list', 'sec_base_id', 'delivery_type'
        input_optional = 'is_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
        output_required = 'id', 'sub_key', 'topic_links', 'sec_name', 'delivery_type', 'is_active', 'topic_names'

    def _get_input_dict(self):

        input_dict = {}

        # Map topic_id form field (which can be multiple) to topic_id_list service input
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('edit-topic_id')
            if topic_ids:
                input_dict['topic_id_list'] = topic_ids

        return input_dict

    def pre_process_input_dict(self, input_dict):

        # Extract topic IDs from form POST data
        if self.req.method == 'POST':
            topic_ids = self.req.POST.getlist('edit-topic_id')
            input_dict['topic_id_list'] = topic_ids

            # Map other form fields
            field_mapping = {
                'edit-sub_key': 'sub_key',
                'edit-sec_base_id': 'sec_base_id',
                'edit-delivery_type': 'delivery_type',
                'edit-is_active': 'is_active',
                'edit-push_type': 'push_type',
                'edit-rest_push_endpoint_id': 'rest_push_endpoint_id',
                'edit-push_service_name': 'push_service_name',
            }

            for form_field, service_field in field_mapping.items():
                if form_field in self.req.POST and self.req.POST[form_field]:
                    value = self.req.POST[form_field]
                    if service_field == 'is_active':
                        input_dict[service_field] = value == 'on'
                    else:
                        input_dict[service_field] = value

    def success_message(self, item):
        return 'Successfully updated pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-subscription-delete'
    error_message = 'Could not delete pub/sub subscription'
    service_name = 'zato.pubsub.subscription.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_security_definitions(req):
    """ Retrieves a list of security definitions for pubsub subscriptions.
    """
    form_type = req.GET.get('form_type', 'create')

    try:
        security_definitions = get_pubsub_security_definitions(req, form_type, 'subscription')

        return HttpResponse(
            dumps({
                'msg': 'Security definitions retrieved successfully',
                'security_definitions': security_definitions
            }),
            content_type='application/json'
        )
    except Exception as e:
        return HttpResponse(
            dumps({
                'error': str(e) or 'Error retrieving security definitions'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_topics(req):
    """ Retrieves a list of topics for pubsub subscriptions.
    """
    cluster_id = req.GET.get('cluster_id')
    form_type = req.GET.get('form_type', 'create')

    logger.info('VIEW get_topics: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:
        # Call the service directly like in other views
        response = req.zato.client.invoke('zato.pubsub.topic.get-list', {
            'cluster_id': cluster_id
        })

        topics = []
        if response and hasattr(response, 'data'):
            for item in response.data:
                topics.append({
                    'id': item.id,
                    'name': item.name
                })

        logger.info('VIEW get_topics: returning %d topics', len(topics))

        return HttpResponse(
            dumps({
                'msg': 'Topics retrieved successfully',
                'topics': topics
            }),
            content_type='application/json'
        )
    except Exception as e:
        logger.error('VIEW get_topics: error=%s', e)
        return HttpResponse(
            dumps({
                'error': str(e) or 'Error retrieving topics'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################

def _get_subscriber_patterns_for_sec_def(req, sec_base_id, cluster_id):
    """ Get subscriber patterns for a given security definition.
    """
    logger = logging.getLogger(__name__)

    logger.info('Getting permissions for cluster_id=%s', cluster_id)
    permissions_response = req.zato.client.invoke('zato.pubsub.permission.get-list', {
        'cluster_id': cluster_id,
    })
    logger.info('Got %d permissions', len(permissions_response.data))

    subscriber_patterns = []
    for perm in permissions_response.data:
        if perm.sec_base_id == int(sec_base_id) and ('subscriber' in perm.access_type.lower()):
            logger.info('Found subscriber permission with pattern: %s', perm.pattern)
            patterns = [p.strip() for p in perm.pattern.splitlines() if p.strip()]
            subscriber_patterns.extend(patterns)

    logger.info('Found %d subscriber patterns: %s', len(subscriber_patterns), subscriber_patterns)
    return subscriber_patterns

# ################################################################################################################################

def _get_topics_for_patterns(req, subscriber_patterns, cluster_id):
    """ Get all topics matching the given patterns.
    """
    logger = logging.getLogger(__name__)

    all_topics = set()
    for pattern in subscriber_patterns:
        try:
            matches_response = req.zato.client.invoke('zato.pubsub.topic.get-matches', {
                'cluster_id': cluster_id,
                'pattern': pattern
            })
            logger.info('Got %d matches for pattern: %s', len(matches_response.data), pattern)
            for topic in matches_response.data:
                all_topics.add((topic.get('id', ''), topic.get('name', '')))
        except Exception as e:
            logger.error('Error getting matches for pattern: %s, error: %s', pattern, e)

    logger.info('Found %d topics', len(all_topics))
    return all_topics

# ################################################################################################################################

def _build_topic_checkbox_html(all_topics, cluster_id):
    """ Build HTML for topic checkboxes.
    """
    html_parts = []
    html_parts.append('<table id="multi-select-table" class="multi-select-table">')

    if all_topics:
        sorted_topics = sorted(all_topics, key=lambda x: x[1])
        for topic_id, topic_name in sorted_topics:
            checkbox_id = f'topic_checkbox_{topic_id}'
            html_parts.append(f'<tr>')
            html_parts.append(f'<td>')
            html_parts.append(f'<input type="checkbox" id="{checkbox_id}" name="name" value="{topic_name}" />')
            html_parts.append(f'</td>')
            html_parts.append(f'<td>')
            html_parts.append(f'<label for="{checkbox_id}">')
            html_parts.append(f'<a href="/zato/pubsub/topic/?cluster={cluster_id}&query={topic_name}" target="_blank">{topic_name}</a>')
            html_parts.append(f'</label>')
            html_parts.append(f'</td>')
            html_parts.append(f'</tr>')
    else:
        html_parts.append('<tr><td colspan="2"><em>No topics match the subscription patterns for this security definition</em></td></tr>')

    html_parts.append('</table>')
    return ''.join(html_parts)

# ################################################################################################################################

@method_allowed('POST')
def sec_def_topic_sub_list(req, sec_base_id, cluster_id):
    """ Returns HTML for topics to which a given security definition has access for subscription.
    """
    logger = logging.getLogger(__name__)
    logger.info('Starting with sec_base_id=%s, cluster_id=%s', sec_base_id, cluster_id)

    try:
        subscriber_patterns = _get_subscriber_patterns_for_sec_def(req, sec_base_id, cluster_id)

        if not subscriber_patterns:
            logger.warning('No subscription permissions found for sec_base_id=%s', sec_base_id)
            return HttpResponse('<table id="multi-select-table" class="multi-select-table"><tr><td colspan="2"><em>No subscription permissions defined for this security definition</em></td></tr></table>', content_type='text/html')

        all_topics = _get_topics_for_patterns(req, subscriber_patterns, cluster_id)
        html_content = _build_topic_checkbox_html(all_topics, cluster_id)

        return HttpResponse(html_content, content_type='text/html')

    except Exception as e:
        logger.error('Exception occurred: %s', format_exc())
        return HttpResponseServerError(format_exc())

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_rest_endpoints(req):
    """ Retrieves a list of REST outgoing connections for pubsub subscriptions.
    """
    cluster_id = req.GET.get('cluster_id')
    form_type = req.GET.get('form_type', 'create')

    logger.info('VIEW get_rest_endpoints: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:
        rest_endpoints = get_outconn_rest_list(req, name_to_id=False)
        endpoints_list = []

        for endpoint_id, endpoint_name in rest_endpoints.items():
            endpoints_list.append({
                'id': endpoint_id,
                'name': endpoint_name
            })

        logger.info('VIEW get_rest_endpoints: returning %d endpoints', len(endpoints_list))

        return HttpResponse(
            dumps({
                'msg': 'REST endpoints retrieved successfully',
                'rest_endpoints': endpoints_list
            }),
            content_type='application/json'
        )
    except Exception as e:
        logger.error('VIEW get_rest_endpoints: error=%s', e)
        return HttpResponse(
            dumps({
                'error': str(e) or 'Error retrieving REST endpoints'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_service_list(req):
    """ Retrieves a list of services for pubsub subscriptions.
    """
    cluster_id = req.GET.get('cluster_id')
    form_type = req.GET.get('form_type', 'create')

    logger.info('VIEW get_service_list: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:
        services = util_get_service_list(req)

        logger.info('VIEW get_service_list: returning %d services', len(services))

        return HttpResponse(
            dumps({
                'msg': 'Services retrieved successfully',
                'services': services
            }),
            content_type='application/json'
        )
    except Exception as e:
        logger.error('VIEW get_service_list: error=%s', e)
        return HttpResponse(
            dumps({
                'error': str(e) or 'Error retrieving services'
            }),
            content_type='application/json',
            status=500
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_topics_by_security(req):
    """ Retrieves a list of topics filtered by security definition's subscribe permissions.
    """
    cluster_id = req.GET.get('cluster_id')
    sec_base_id = req.GET.get('sec_base_id')

    logger.info('VIEW get_topics_by_security: cluster_id=%s, sec_base_id=%s', cluster_id, sec_base_id)

    if not sec_base_id:
        return HttpResponse(
            dumps({
                'error': 'Security definition ID is required'
            }),
            content_type='application/json',
            status=400
        )

    try:
        # Get subscribe permissions for this security definition
        permissions_response = req.zato.client.invoke('zato.pubsub.permission.get-list', {
            'cluster_id': cluster_id
        })

        # Filter permissions for this security definition and subscribe access
        subscribe_permissions = []
        if permissions_response and hasattr(permissions_response, 'data'):
            for perm in permissions_response.data:
                if (perm.sec_base_id == int(sec_base_id) and
                    (perm.access_type == 'subscriber' or perm.access_type == 'publisher-subscriber')):
                    subscribe_permissions.append(perm)

        logger.info('VIEW get_topics_by_security: found %d subscribe permissions', len(subscribe_permissions))

        if not subscribe_permissions:
            # No subscribe permissions found for this security definition
            logger.info('VIEW get_topics_by_security: no subscribe permissions found')
            return HttpResponse(
                dumps({
                    'msg': 'No topics available for this security definition',
                    'topics': []
                }),
                content_type='application/json'
            )

        # Collect all patterns from permissions (split newline-separated patterns)
        all_patterns = []
        for perm in subscribe_permissions:
            patterns = [p.strip() for p in perm.pattern.split('\n') if p.strip()]
            # Only include patterns that start with 'sub=' or have no prefix (assume subscribe)
            for pattern in patterns:
                if pattern.startswith('sub='):
                    all_patterns.append(pattern[4:])  # Remove 'sub=' prefix
                elif not pattern.startswith('pub='):
                    all_patterns.append(pattern)  # No prefix, assume subscribe

        logger.info('VIEW get_topics_by_security: collected %d patterns', len(all_patterns))

        if not all_patterns:
            # No valid subscribe patterns found
            logger.info('VIEW get_topics_by_security: no valid subscribe patterns found')
            return HttpResponse(
                dumps({
                    'msg': 'No topics available for this security definition',
                    'topics': []
                }),
                content_type='application/json'
            )

        # Get matching topics for each pattern using existing service
        matched_topics = set()  # Use set to avoid duplicates
        for pattern in all_patterns:
            try:
                matches_response = req.zato.client.invoke('zato.pubsub.topic.get-matches', {
                    'cluster_id': cluster_id,
                    'pattern': pattern
                })

                if matches_response and hasattr(matches_response, 'data'):
                    for topic in matches_response.data:
                        matched_topics.add((topic.id, topic.name))  # Use tuple to ensure uniqueness

            except Exception as e:
                logger.warning('VIEW get_topics_by_security: error matching pattern %s: %s', pattern, e)
                continue

        # Convert set back to list of dicts
        topics_list = []
        for topic_id, topic_name in matched_topics:
            topics_list.append({
                'id': topic_id,
                'name': topic_name
            })

        # Sort topics by name for consistent display
        topics_list.sort(key=lambda x: x['name'])

        logger.info('VIEW get_topics_by_security: returning %d topics', len(topics_list))

        return HttpResponse(
            dumps({
                'msg': 'Topics retrieved successfully',
                'topics': topics_list
            }),
            content_type='application/json'
        )

    except Exception as e:
        logger.error('VIEW get_topics_by_security: error=%s', e)
        return HttpResponse(
            dumps({
                'error': str(e) or 'Error retrieving topics for security definition'
            }),
            content_type='application/json',
            status=500
        )
