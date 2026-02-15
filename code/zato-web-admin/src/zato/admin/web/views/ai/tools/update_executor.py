# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

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
        'edit_service': 'zato.security.apikey.edit',
    },
    'basic_auth': {
        'list_service': 'zato.security.basic-auth.get-list',
        'edit_service': 'zato.security.basic-auth.edit',
    },
    'ntlm': {
        'list_service': 'zato.security.ntlm.get-list',
        'edit_service': 'zato.security.ntlm.edit',
    },
}

_update_tool_config = {
    'update_channel_rest': {
        'list_service': 'zato.http-soap.get-list',
        'list_params': {
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
        'edit_service': 'zato.http-soap.edit',
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
        'edit_service': 'zato.http-soap.edit',
        'extra_params': {
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
    },
    'update_sql': {
        'list_service': 'zato.outgoing.sql.get-list',
        'list_params': {},
        'edit_service': 'zato.outgoing.sql.edit',
    },
    'update_cache': {
        'list_service': 'zato.cache.builtin.get-list',
        'list_params': {},
        'edit_service': 'zato.cache.builtin.edit',
    },
    'update_pubsub_topic': {
        'list_service': 'zato.pubsub.topic.get-list',
        'list_params': {},
        'edit_service': 'zato.pubsub.topic.edit',
    },
    'update_confluence': {
        'list_service': 'zato.generic.connection.get-list',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
        },
        'edit_service': 'zato.generic.connection.edit',
        'extra_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
        },
    },
    'update_jira': {
        'list_service': 'zato.generic.connection.get-list',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_JIRA,
        },
        'edit_service': 'zato.generic.connection.edit',
        'extra_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_JIRA,
        },
    },
}

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

def _build_edit_request(existing_object, updates, cluster_id, extra_params=None):
    """ Builds edit service request by merging existing object data with updates.
    """
    request = {'cluster_id': cluster_id}

    if isinstance(existing_object, dict):
        for key, value in existing_object.items():
            if value is not None:
                request[key] = value
    else:
        for key in dir(existing_object):
            if not key.startswith('_'):
                value = getattr(existing_object, key, None)
                if value is not None and not callable(value):
                    request[key] = value

    if 'new_name' in updates:
        request['name'] = updates['new_name']

    for key, value in updates.items():
        if key not in ('name', 'type', 'new_name'):
            request[key] = value

    if extra_params:
        request.update(extra_params)

    return request

# ################################################################################################################################
# ################################################################################################################################

def execute_update_security(client, cluster_id, arguments:'anydict') -> 'anydict':
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

        request = _build_edit_request(existing_object, arguments, cluster_id)

        response = client.invoke(config['edit_service'], request)

        if response.ok:
            new_name = arguments.get('new_name', name)
            return {'success': True, 'message': f'Updated {sec_type} security definition: {new_name}'}
        else:
            return {'success': False, 'error': f'Update failed: {response.details}'}

    except Exception:
        error_msg = format_exc()
        logger.warning('Update security failed: %s', error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################

def execute_update_tool(client, cluster_id, cluster, tool_name:'str', arguments:'anydict') -> 'anydict':
    """ Executes an update tool by name.
    """
    _ = cluster

    if tool_name == 'update_security':
        return execute_update_security(client, cluster_id, arguments)

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
        request = _build_edit_request(existing_object, arguments, cluster_id, extra_params)

        response = client.invoke(config['edit_service'], request)

        if response.ok:
            new_name = arguments.get('new_name', target_name)
            object_type = tool_name.replace('update_', '').replace('_', ' ')
            return {'success': True, 'message': f'Updated {object_type}: {new_name}'}
        else:
            return {'success': False, 'error': f'Update failed: {response.details}'}

    except Exception:
        error_msg = format_exc()
        logger.warning('Update tool %s failed: %s', tool_name, error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################
# ################################################################################################################################
