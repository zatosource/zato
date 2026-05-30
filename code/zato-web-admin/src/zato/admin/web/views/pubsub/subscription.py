# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http import HTTPStatus
from json import dumps, loads
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.pubsub.subscription import CreateForm, EditForm
from zato.admin.web.util import get_pubsub_security_definitions, get_service_list as util_get_service_list
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, get_outconn_rest_list
from zato.common.api import PubSub
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_No_Permissions_HTML = (
    '<table id="multi-select-table" class="multi-select-table">'
    '<tr><td colspan="2">'
    '<span class="multi-select-message">No matching subscription permissions.'
    '<a href="/zato/pubsub/permission/?cluster=1" style="color: #0936d5;" target="_new">Click to manage permissions</a></span>'
    '</td></tr>'
    '</table>'
)

_No_Topics_HTML = '<tr><td colspan="2"><em>No topics match the subscription patterns for this security definition</em></td></tr>'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    """ Lists pub/sub subscriptions.
    """
    method_allowed = 'GET'
    url_name = 'pubsub-subscription'
    template = 'zato/pubsub/subscription.html'
    service_name = 'zato.pubsub.subscription.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'sub_key', 'is_delivery_active', 'is_pub_active', 'created', 'sec_base_id', 'security', 'delivery_type', \
        'push_type', 'rest_push_endpoint_id', 'rest_push_endpoint_name', 'push_service_name', 'topic_name_list', \
        'topic_link_list', 'pending_depth'
    output_repeated = True

    def on_before_append_item(self, item:'any_') -> 'any_':

        topic_name_list = item.topic_name_list
        item.topic_name_list = dumps(topic_name_list)

        return item

    def handle(self) -> 'anydict':

        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)

        out = {
            'create_form': create_form,
            'edit_form': edit_form,
            'show_search_form': True,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    """ Base create/edit view for pub/sub subscriptions.
    """

    def post_process_return_data(self, return_data:'anydict') -> 'anydict':

        # Get the topic name list ..
        topic_name_list = return_data.get('topic_name_list', [])
        return_data['topic_name_list'] = dumps(topic_name_list)

        # .. and set the link list.
        topic_link_list = return_data.get('topic_link_list', [])
        return_data['topic_link_list'] = ', '.join(topic_link_list)

        return return_data

    def _get_input_dict_common(self, topic_field_name:'str') -> 'anydict':

        # Build the input dict based on POST data ..
        input_dict = {}

        if self.req.method == 'POST':
            topic_name_list = self.req.POST.getlist(topic_field_name)
            if topic_name_list:
                input_dict['topic_name_list'] = topic_name_list

        # .. and return the result.
        return input_dict

    def _pre_process_input_dict_common(self, input_dict:'anydict', field_prefix:'str') -> 'None':

        if self.req.method == 'POST':
            topic_data_list = self.req.POST.getlist('topic_data')
            topic_names = []

            for topic_data_json in topic_data_list:
                topic_data = loads(topic_data_json)
                topic_names.append({
                    'topic_name': topic_data['topic_name'],
                    'is_pub_enabled': topic_data['is_pub_enabled'],
                    'is_delivery_enabled': topic_data['is_delivery_enabled'],
                })

            input_dict['topic_name_list'] = topic_names

            field_mapping = self._get_field_mapping(field_prefix)

            for form_field, service_field in field_mapping.items():
                if form_field in self.req.POST and self.req.POST[form_field]:

                    value = self.req.POST[form_field]

                    if service_field in ('is_delivery_active', 'is_pub_active'):
                        input_dict[service_field] = value == 'on'
                    else:
                        input_dict[service_field] = value
                elif service_field in ('is_delivery_active', 'is_pub_active'):
                    input_dict[service_field] = False

    def _get_field_mapping(self, prefix:'str') -> 'anydict':
        raise NotImplementedError('Subclasses must implement _get_field_mapping')

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a pub/sub subscription.
    """
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-create'
    service_name = 'zato.pubsub.subscription.create'

    input_required = 'cluster_id', 'topic_name', 'sec_base_id', 'delivery_type'
    input_optional = 'is_delivery_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
    output_required = 'id', 'sub_key', 'is_delivery_active', 'created', 'security', 'delivery_type', \
        'topic_name_list', 'topic_link_list',

    def _get_input_dict(self) -> 'anydict':
        return self._get_input_dict_common('create-topic_name')

    def _get_field_mapping(self, prefix:'str') -> 'anydict':
        return {
            'sec_base_id': 'sec_base_id',
            'delivery_type': 'delivery_type',
            'is_delivery_active': 'is_delivery_active',
            'is_pub_active': 'is_pub_active',
            'rest_push_endpoint_id': 'rest_push_endpoint_id'
        }

    def pre_process_input_dict(self, input_dict:'anydict') -> 'None':
        self._pre_process_input_dict_common(input_dict, '')

    def success_message(self, item:'any_') -> 'str':
        return 'Successfully created pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    """ Edits a pub/sub subscription.
    """
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-edit'
    service_name = 'zato.pubsub.subscription.edit'

    input_required = 'sub_key', 'cluster_id', 'topic_id_list', 'sec_base_id', 'delivery_type'
    input_optional = 'is_delivery_active', 'is_pub_active', 'push_type', 'rest_push_endpoint_id', 'push_service_name'
    output_required = 'id', 'sub_key', 'security', 'delivery_type', 'is_delivery_active', 'topic_name_list', 'topic_link_list'

    def _get_input_dict(self) -> 'anydict':
        return self._get_input_dict_common('topic_name')

    def _get_field_mapping(self, prefix:'str') -> 'anydict':
        return {
            f'{prefix}sub_key': 'sub_key',
            f'{prefix}sec_base_id': 'sec_base_id',
            f'{prefix}delivery_type': 'delivery_type',
            f'{prefix}is_delivery_active': 'is_delivery_active',
            f'{prefix}is_pub_active': 'is_pub_active',
            f'{prefix}push_type': 'push_type',
            f'{prefix}rest_push_endpoint_id': 'rest_push_endpoint_id',
            f'{prefix}push_service_name': 'push_service_name',
        }

    def pre_process_input_dict(self, input_dict:'anydict') -> 'None':
        self._pre_process_input_dict_common(input_dict, 'edit-')

    def success_message(self, item:'any_') -> 'str':
        return 'Successfully updated pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    """ Deletes a pub/sub subscription.
    """
    url_name = 'pubsub-subscription-delete'
    error_message = 'Could not delete pub/sub subscription'
    service_name = 'zato.pubsub.subscription.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_security_definitions(request:'HttpRequest') -> 'HttpResponse':
    """ Retrieves a list of security definitions for pubsub subscriptions.
    """
    # Get the form type ..
    form_type = request.GET.get('form_type', 'create')

    try:

        # .. invoke the service ..
        security_definitions = get_pubsub_security_definitions(request, form_type, 'subscription')

        response_json = dumps({
            'msg': 'Security definitions retrieved successfully',
            'security_definitions': security_definitions
        })

        # .. and return the response.
        out = HttpResponse(response_json, content_type='application/json')
        return out

    except Exception as error:
        error_json = dumps({
            'error': str(error) or 'Error retrieving security definitions'
        })

        out = HttpResponse(error_json, content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_topics(request:'HttpRequest') -> 'HttpResponse':
    """ Retrieves a list of topics for pubsub subscriptions.
    """
    # Get the input parameters ..
    cluster_id = request.GET.get('cluster_id')
    form_type = request.GET.get('form_type', 'create')

    logger.info('VIEW get_topics: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:

        # .. invoke the service ..
        response = request.zato.client.invoke('zato.pubsub.topic.get-list', {
            'cluster_id': cluster_id
        })

        # .. build the topic list ..
        topics = []
        if response and hasattr(response, 'data'):
            for item in response.data:
                topics.append({
                    'id': item.id,
                    'name': item.name
                })

        logger.info('VIEW get_topics: returning %d topics', len(topics))

        response_json = dumps({
            'msg': 'Topics retrieved successfully',
            'topics': topics
        })

        # .. and return the response.
        out = HttpResponse(response_json, content_type='application/json')
        return out

    except Exception as error:
        logger.error('VIEW get_topics: error=%s', error)

        error_json = dumps({
            'error': str(error) or 'Error retrieving topics'
        })

        out = HttpResponse(error_json, content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_topic_name_from_tuple(topic_tuple:'tuple') -> 'str':
    """ Get topic name from tuple (id, name).
    """
    out = topic_tuple[1]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_topic_name_from_dict(topic_dict:'anydict') -> 'str':
    """ Get topic name from dictionary.
    """
    out = topic_dict['name']
    return out

# ################################################################################################################################
# ################################################################################################################################

def _sort_topics_by_name(topics:'any_') -> 'anylist':
    """ Sort topics by name.
    """
    out = sorted(topics, key=_get_topic_name_from_tuple)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _sort_topic_dicts_by_name(topic_dicts:'anylist') -> 'anylist':
    """ Sort topic dictionaries by name.
    """
    out = sorted(topic_dicts, key=_get_topic_name_from_dict)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_subscriber_access(access_type:'str') -> 'bool':
    """ Check if access type allows subscription.
    """
    out = access_type in (PubSub.API_Client.Subscriber, PubSub.API_Client.Publisher_Subscriber)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_subscriber_patterns_for_sec_def(request:'HttpRequest', sec_base_id:'str', cluster_id:'str') -> 'strlist':
    """ Get subscriber patterns for a given security definition.
    """

    # Get the permissions for this cluster ..
    logger.info('Getting permissions for cluster_id=%s', cluster_id)
    permissions_response = request.zato.client.invoke('zato.pubsub.permission.get-list', {
        'cluster_id': cluster_id,
    })
    logger.info('Got %d permissions', len(permissions_response.data))

    # .. and collect subscriber patterns.
    subscriber_patterns = []
    sec_base_id = int(sec_base_id)
    for permission in permissions_response.data:
        if permission.sec_base_id == sec_base_id and _is_subscriber_access(permission.access_type):
            logger.info('Found subscriber permission with pattern: %s', permission.pattern)

            patterns = []
            for line in permission.pattern.splitlines():
                stripped = line.strip()
                if stripped:
                    patterns.append(stripped)

            subscriber_patterns.extend(patterns)

    logger.info('Found %d subscriber patterns: %s', len(subscriber_patterns), subscriber_patterns)

    return subscriber_patterns

# ################################################################################################################################
# ################################################################################################################################

def _get_topics_for_patterns(request:'HttpRequest', subscriber_patterns:'strlist', cluster_id:'str') -> 'set':
    """ Get all topics matching the given patterns.
    """

    # Iterate over each pattern and collect matching topics.
    all_topics = set()
    for pattern in subscriber_patterns:
        try:
            matches_response = request.zato.client.invoke('zato.pubsub.topic.get-matches', {
                'cluster_id': cluster_id,
                'pattern': pattern
            })
            logger.info('Got %d matches for pattern: %s', len(matches_response.data), pattern)
            for topic in matches_response.data:
                all_topics.add((topic.get('id', ''), topic.get('name', '')))
        except Exception as error:
            logger.error('Error getting matches for pattern: %s, error: %s', pattern, error)

    logger.info('Found %d topics', len(all_topics))

    return all_topics

# ################################################################################################################################
# ################################################################################################################################

def _build_topic_checkbox_html(all_topics:'set', cluster_id:'str') -> 'str':
    """ Build HTML for topic checkboxes.
    """
    html_parts = []
    html_parts.append('<table id="multi-select-table" class="multi-select-table">')

    if all_topics:
        sorted_topics = _sort_topics_by_name(all_topics)
        for topic_id, topic_name in sorted_topics:
            checkbox_id = f'topic_checkbox_{topic_id}'
            html_parts.append('<tr>')
            html_parts.append('<td>')
            html_parts.append(f'<input type="checkbox" id="{checkbox_id}" name="topic_name" value="{topic_name}" />')
            html_parts.append('</td>')
            html_parts.append('<td>')
            html_parts.append(f'<label for="{checkbox_id}">')
            html_parts.append(f'<a href="/zato/pubsub/topic/?cluster={cluster_id}&query={topic_name}" target="_blank">{topic_name}</a>')
            html_parts.append('</label>')
            html_parts.append('</td>')
            html_parts.append('</tr>')
    else:
        html_parts.append(_No_Topics_HTML)

    html_parts.append('</table>')

    out = ''.join(html_parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def sec_def_topic_sub_list(request:'HttpRequest', sec_base_id:'str', cluster_id:'str') -> 'HttpResponse':
    """ Returns HTML for topics to which a given security definition has access for subscription.
    """

    logger.info('Starting with sec_base_id=%s, cluster_id=%s', sec_base_id, cluster_id)

    try:

        # Get the subscriber patterns ..
        subscriber_patterns = _get_subscriber_patterns_for_sec_def(request, sec_base_id, cluster_id)

        # .. check if any were found ..
        if not subscriber_patterns:
            logger.warning('No subscription permissions found for sec_base_id=%s', sec_base_id)
            out = HttpResponse(_No_Permissions_HTML, content_type='text/html')
            return out

        # .. get the matching topics ..
        all_topics = _get_topics_for_patterns(request, subscriber_patterns, cluster_id)

        # .. build the HTML ..
        html_content = _build_topic_checkbox_html(all_topics, cluster_id)

        # .. and return the response.
        out = HttpResponse(html_content, content_type='text/html')
        return out

    except Exception:
        logger.error('Exception occurred: %s', format_exc())

        error_text = format_exc()

        out = HttpResponseServerError(error_text)
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_rest_endpoints(request:'HttpRequest') -> 'HttpResponse':
    """ Retrieves a list of REST outgoing connections for pubsub subscriptions.
    """
    # Get the input parameters ..
    cluster_id = request.GET.get('cluster_id')
    form_type = request.GET.get('form_type', 'create')

    logger.info('VIEW get_rest_endpoints: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:

        # .. get the REST endpoints ..
        rest_endpoints = get_outconn_rest_list(request, name_to_id=False)

        # .. build the list ..
        endpoints_list = []

        for endpoint_id, endpoint_name in rest_endpoints.items():
            endpoints_list.append({
                'id': endpoint_id,
                'name': endpoint_name
            })

        logger.info('VIEW get_rest_endpoints: returning %d endpoints', len(endpoints_list))

        response_json = dumps({
            'msg': 'REST endpoints retrieved successfully',
            'rest_endpoints': endpoints_list
        })

        # .. and return the response.
        out = HttpResponse(response_json, content_type='application/json')
        return out

    except Exception as error:
        logger.error('VIEW get_rest_endpoints: error=%s', error)

        error_json = dumps({
            'error': str(error) or 'Error retrieving REST endpoints'
        })

        out = HttpResponse(error_json, content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_service_list(request:'HttpRequest') -> 'HttpResponse':
    """ Retrieves a list of services for pubsub subscriptions.
    """
    # Get the input parameters ..
    cluster_id = request.GET.get('cluster_id')
    form_type = request.GET.get('form_type', 'create')

    logger.info('VIEW get_service_list: received request with cluster_id=%s, form_type=%s', cluster_id, form_type)

    try:

        # .. invoke the service ..
        services = util_get_service_list(request)

        logger.info('VIEW get_service_list: returning %d services', len(services))

        response_json = dumps({
            'msg': 'Services retrieved successfully',
            'services': services
        })

        # .. and return the response.
        out = HttpResponse(response_json, content_type='application/json')
        return out

    except Exception as error:
        logger.error('VIEW get_service_list: error=%s', error)

        error_json = dumps({
            'error': str(error) or 'Error retrieving services'
        })

        out = HttpResponse(error_json, content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_topics_by_security(request:'HttpRequest') -> 'HttpResponse':
    """ Retrieves a list of topics filtered by security definition's subscribe permissions.
    """
    # Get the input parameters ..
    cluster_id = request.GET.get('cluster_id')
    sec_base_id = request.GET.get('sec_base_id')

    logger.info('VIEW get_topics_by_security: cluster_id=%s, sec_base_id=%s', cluster_id, sec_base_id)

    # .. validate the input ..
    if not sec_base_id:
        error_json = dumps({
            'error': 'Security definition ID is required'
        })

        out = HttpResponse(error_json, content_type='application/json', status=HTTPStatus.BAD_REQUEST)
        return out

    try:

        # .. get the permissions ..
        permissions_response = request.zato.client.invoke('zato.pubsub.permission.get-list', {
            'cluster_id': cluster_id
        })

        # .. filter for subscribe permissions ..
        subscribe_permissions = []
        if permissions_response and hasattr(permissions_response, 'data'):
            for permission in permissions_response.data:
                if (permission.sec_base_id == sec_base_id and
                    _is_subscriber_access(permission.access_type)):
                    subscribe_permissions.append(permission)

        logger.info('VIEW get_topics_by_security: found %d subscribe permissions', len(subscribe_permissions))

        if not subscribe_permissions:
            # No subscribe permissions found for this security definition
            logger.info('VIEW get_topics_by_security: no subscribe permissions found')

            response_json = dumps({
                'msg': 'No topics available for this security definition',
                'topics': []
            })

            out = HttpResponse(response_json, content_type='application/json')
            return out

        # Collect all patterns from permissions (split newline-separated patterns)
        all_patterns = []
        for permission in subscribe_permissions:

            patterns = []
            for line in permission.pattern.split('\n'):
                stripped = line.strip()
                if stripped:
                    patterns.append(stripped)

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

            response_json = dumps({
                'msg': 'No topics available for this security definition',
                'topics': []
            })

            out = HttpResponse(response_json, content_type='application/json')
            return out

        # .. get matching topics for each pattern ..
        matched_topics = set()
        for pattern in all_patterns:
            try:
                matches_response = request.zato.client.invoke('zato.pubsub.topic.get-matches', {
                    'cluster_id': cluster_id,
                    'pattern': pattern
                })

                if matches_response and hasattr(matches_response, 'data'):
                    for topic in matches_response.data:
                        matched_topics.add((topic.id, topic.name))  # Use tuple to ensure uniqueness

            except Exception as error:
                logger.warning('VIEW get_topics_by_security: error matching pattern %s: %s', pattern, error)
                continue

        # .. convert to list of dicts ..
        topics_list = []
        for topic_id, topic_name in matched_topics:
            topics_list.append({
                'id': topic_id,
                'name': topic_name
            })

        # .. sort by name ..
        topics_list = _sort_topic_dicts_by_name(topics_list)

        logger.info('VIEW get_topics_by_security: returning %d topics', len(topics_list))

        response_json = dumps({
            'msg': 'Topics retrieved successfully',
            'topics': topics_list
        })

        # .. and return the response.
        out = HttpResponse(response_json, content_type='application/json')
        return out

    except Exception as error:
        logger.error('VIEW get_topics_by_security: error=%s', error)

        error_json = dumps({
            'error': str(error) or 'Error retrieving topics for security definition'
        })

        out = HttpResponse(error_json, content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return out

# ################################################################################################################################
# ################################################################################################################################
