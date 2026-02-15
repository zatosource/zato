# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import Bunch

# Django
from django.http import QueryDict

# Zato
from zato.common.api import CONNECTION, GENERIC, URL_TYPE

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_security_type_to_config = {
    'apikey': {
        'list_service': 'zato.security.apikey.get-list',
        'edit_view_module': 'zato.admin.web.views.security.apikey',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
    'basic_auth': {
        'list_service': 'zato.security.basic-auth.get-list',
        'edit_view_module': 'zato.admin.web.views.security.basic_auth',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
    'bearer_token': {
        'list_service': 'zato.security.oauth.get-list',
        'edit_view_module': 'zato.admin.web.views.security.oauth.outconn_client_credentials',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
    'ntlm': {
        'list_service': 'zato.security.ntlm.get-list',
        'edit_view_module': 'zato.admin.web.views.security.ntlm',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
}

_update_tool_config = {
    'update_channel_rest': {
        'list_service': 'zato.http-soap.get-list',
        'list_params': {
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
        'edit_view_module': 'zato.admin.web.views.http_soap',
        'edit_view_func': 'edit',
        'form_prefix': 'edit-',
        'extra_params': {
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
    },
    'update_outgoing_rest': {
        'list_service': 'zato.http-soap.get-list',
        'list_params': {
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
        'edit_view_module': 'zato.admin.web.views.http_soap',
        'edit_view_func': 'edit',
        'form_prefix': 'edit-',
        'extra_params': {
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
    },
    'update_scheduler': {
        'list_service': 'zato.scheduler.job.get-list',
        'list_params': {},
        'edit_view_module': 'zato.admin.web.views.scheduler',
        'edit_view_func': 'edit',
        'form_prefix': 'edit-',
    },
    'update_sql': {
        'list_service': 'zato.outgoing.sql.get-list',
        'list_params': {},
        'edit_view_module': 'zato.admin.web.views.outgoing.sql',
        'edit_view_func': 'edit',
        'form_prefix': 'edit-',
    },
    'update_cache': {
        'list_service': 'zato.cache.builtin.get-list',
        'list_params': {},
        'edit_view_module': 'zato.admin.web.views.cache.builtin',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
    'update_pubsub_topic': {
        'list_service': 'zato.pubsub.topic.get-list',
        'list_params': {},
        'edit_view_module': 'zato.admin.web.views.pubsub.topic',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
    'update_confluence': {
        'list_service': 'zato.generic.connection.get-list',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
        },
        'edit_view_module': 'zato.admin.web.views.cloud.confluence',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
    'update_jira': {
        'list_service': 'zato.generic.connection.get-list',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_JIRA,
        },
        'edit_view_module': 'zato.admin.web.views.cloud.jira',
        'edit_view_class': 'Edit',
        'form_prefix': 'edit-',
    },
}

# ################################################################################################################################
# ################################################################################################################################

class MockRequest:
    """ A mock request object that can be passed to Django views.
    """
    def __init__(self, zato_client:'any_', cluster_id:'int', cluster:'any_', post_data:'anydict'):
        self.method = 'POST'
        self.POST = QueryDict(mutable=True)
        self.POST.update(post_data)
        self.GET = QueryDict()
        self.META = {}
        self.zato = Bunch()
        self.zato.client = zato_client
        self.zato.cluster_id = cluster_id
        self.zato.cluster = cluster
        self.zato.args = Bunch()
        self.zato.id = post_data.get('id')

# ################################################################################################################################
# ################################################################################################################################

def _find_object_by_name(client, cluster_id, list_service, list_params, target_name):
    """ Finds an object by its name using the list service and returns all its details.
    """
    request = {'cluster_id': cluster_id}
    request.update(list_params)

    logger.info('Searching for object with name=%s using service %s', target_name, list_service)

    response = client.invoke(list_service, request)

    if not response.ok:
        return None, f'Failed to list objects: {response.details}'

    data = response.data
    if isinstance(data, dict) and 'response' in data:
        data = data['response']

    for item in data:
        item_name = item.get('name') if isinstance(item, dict) else getattr(item, 'name', None)
        if item_name == target_name:
            logger.info('Found object %s', target_name)
            return item, None

    return None, f'Object with name={target_name} not found'

# ################################################################################################################################

def _build_post_data(existing_object, updates, form_prefix, extra_params=None):
    """ Builds POST data for the edit view by merging existing object data with updates.
    """
    post_data = {}

    if isinstance(existing_object, dict):
        for key, value in existing_object.items():
            if value is not None:
                post_data[form_prefix + key] = value
    else:
        for key in dir(existing_object):
            if not key.startswith('_'):
                value = getattr(existing_object, key, None)
                if value is not None and not callable(value):
                    post_data[form_prefix + key] = value

    obj_id = existing_object.get('id') if isinstance(existing_object, dict) else getattr(existing_object, 'id', None)
    if obj_id:
        post_data['id'] = obj_id

    security_id = existing_object.get('security_id') if isinstance(existing_object, dict) else getattr(existing_object, 'security_id', None)
    sec_type = existing_object.get('sec_type') if isinstance(existing_object, dict) else getattr(existing_object, 'sec_type', None)
    if security_id and sec_type:
        post_data[form_prefix + 'security'] = f'{sec_type}/{security_id}'
    elif security_id:
        post_data[form_prefix + 'security'] = f'/{security_id}'
    else:
        post_data[form_prefix + 'security'] = 'ZATO_NONE'

    if 'new_name' in updates:
        post_data[form_prefix + 'name'] = updates['new_name']
        del updates['new_name']

    for key, value in updates.items():
        if key not in ('name', 'type'):
            post_data[form_prefix + key] = value

    if extra_params:
        post_data.update(extra_params)

    return post_data

# ################################################################################################################################

def _invoke_class_view(view_module, view_class, mock_request):
    """ Invokes a class-based view.
    """
    import importlib
    module = importlib.import_module(view_module)
    view_cls = getattr(module, view_class)
    view_instance = view_cls()
    response = view_instance(mock_request)
    return response

# ################################################################################################################################

def _invoke_func_view(view_module, view_func, mock_request):
    """ Invokes a function-based view.
    """
    import importlib
    module = importlib.import_module(view_module)
    view_fn = getattr(module, view_func)
    response = view_fn(mock_request)
    return response

# ################################################################################################################################
# ################################################################################################################################

def execute_update_security(client, cluster_id, cluster, arguments:'anydict') -> 'anydict':
    """ Updates a security definition by name.
    """
    name = arguments.get('name')
    sec_type = arguments.get('type')

    if not name:
        return {'success': False, 'error': 'Name is required'}

    if not sec_type:
        return {'success': False, 'error': 'Security type is required'}

    if sec_type not in _security_type_to_config:
        return {'success': False, 'error': f'Unknown security type: {sec_type}'}

    config = _security_type_to_config[sec_type]

    try:
        existing_object, error = _find_object_by_name(
            client, cluster_id, config['list_service'], {}, name
        )

        if error:
            return {'success': False, 'error': error}

        post_data = _build_post_data(existing_object, arguments, config['form_prefix'])
        post_data['cluster_id'] = cluster_id

        mock_request = MockRequest(client, cluster_id, cluster, post_data)

        response = _invoke_class_view(
            config['edit_view_module'],
            config['edit_view_class'],
            mock_request
        )

        if response.status_code == 200:
            new_name = arguments.get('new_name', name)
            return {'success': True, 'message': f'Updated {sec_type} security definition: {new_name}'}
        else:
            return {'success': False, 'error': f'Update failed with status {response.status_code}: {response.content}'}

    except Exception:
        error_msg = format_exc()
        logger.warning('Update security failed: %s', error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################

def execute_update_tool(client, cluster_id, cluster, tool_name:'str', arguments:'anydict') -> 'anydict':
    """ Executes an update tool by name.
    """
    if tool_name == 'update_security':
        return execute_update_security(client, cluster_id, cluster, arguments)

    if tool_name not in _update_tool_config:
        return {'success': False, 'error': f'Unknown update tool: {tool_name}'}

    config = _update_tool_config[tool_name]
    target_name = arguments.get('name')

    if not target_name:
        return {'success': False, 'error': 'Name is required'}

    try:
        existing_object, error = _find_object_by_name(
            client,
            cluster_id,
            config['list_service'],
            config.get('list_params', {}),
            target_name
        )

        if error:
            return {'success': False, 'error': error}

        extra_params = config.get('extra_params', {})
        post_data = _build_post_data(existing_object, arguments, config['form_prefix'], extra_params)
        post_data['cluster_id'] = cluster_id

        mock_request = MockRequest(client, cluster_id, cluster, post_data)

        if 'edit_view_class' in config:
            response = _invoke_class_view(
                config['edit_view_module'],
                config['edit_view_class'],
                mock_request
            )
        else:
            response = _invoke_func_view(
                config['edit_view_module'],
                config['edit_view_func'],
                mock_request
            )

        if response.status_code == 200:
            new_name = arguments.get('new_name', target_name)
            object_type = tool_name.replace('update_', '').replace('_', ' ')
            return {'success': True, 'message': f'Updated {object_type}: {new_name}'}
        else:
            content = getattr(response, 'content', str(response))
            return {'success': False, 'error': f'Update failed with status {response.status_code}: {content}'}

    except Exception:
        error_msg = format_exc()
        logger.warning('Update tool %s failed: %s', tool_name, error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################
# ################################################################################################################################
