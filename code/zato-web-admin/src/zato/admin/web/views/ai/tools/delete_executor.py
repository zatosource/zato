# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import CONNECTION, GENERIC, Groups, URL_TYPE

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_security_type_to_service = {
    'apikey': {
        'list': 'zato.security.apikey.get-list',
        'delete': 'zato.security.apikey.delete',
    },
    'basic_auth': {
        'list': 'zato.security.basic-auth.get-list',
        'delete': 'zato.security.basic-auth.delete',
    },
    'bearer_token': {
        'list': 'zato.security.oauth.get-list',
        'delete': 'zato.security.oauth.delete',
    },
    'ntlm': {
        'list': 'zato.security.ntlm.get-list',
        'delete': 'zato.security.ntlm.delete',
    },
}

# ################################################################################################################################

_delete_tool_config = {
    'delete_channel_rest': {
        'list_service': 'zato.http-soap.get-list',
        'delete_service': 'zato.http-soap.delete',
        'list_params': {
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
        'name_field': 'name',
    },
    'delete_outgoing_rest': {
        'list_service': 'zato.http-soap.get-list',
        'delete_service': 'zato.http-soap.delete',
        'list_params': {
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
        },
        'name_field': 'name',
    },
    'delete_outgoing_soap': {
        'list_service': 'zato.http-soap.get-list',
        'delete_service': 'zato.http-soap.delete',
        'list_params': {
            'connection': CONNECTION.OUTGOING,
            'transport': 'soap',
        },
        'name_field': 'name',
    },
    'delete_scheduler': {
        'list_service': 'zato.scheduler.job.get-list',
        'delete_service': 'zato.scheduler.job.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_sql': {
        'list_service': 'zato.outgoing.sql.get-list',
        'delete_service': 'zato.outgoing.sql.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_cache': {
        'list_service': 'zato.cache.builtin.get-list',
        'delete_service': 'zato.cache.builtin.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_groups': {
        'list_service': 'zato.groups.get-list',
        'delete_service': 'zato.groups.delete',
        'list_params': {
            'group_type': Groups.Type.API_Clients,
        },
        'name_field': 'name',
    },
    'delete_email_smtp': {
        'list_service': 'zato.email.smtp.get-list',
        'delete_service': 'zato.email.smtp.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_email_imap': {
        'list_service': 'zato.email.imap.get-list',
        'delete_service': 'zato.email.imap.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_odoo': {
        'list_service': 'zato.outgoing.odoo.get-list',
        'delete_service': 'zato.outgoing.odoo.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_elastic_search': {
        'list_service': 'zato.search.es.get-list',
        'delete_service': 'zato.search.es.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_confluence': {
        'list_service': 'zato.generic.connection.get-list',
        'delete_service': 'zato.generic.connection.delete',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
        },
        'name_field': 'name',
    },
    'delete_jira': {
        'list_service': 'zato.generic.connection.get-list',
        'delete_service': 'zato.generic.connection.delete',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_JIRA,
        },
        'name_field': 'name',
    },
    'delete_ldap': {
        'list_service': 'zato.generic.connection.get-list',
        'delete_service': 'zato.generic.connection.delete',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LDAP,
        },
        'name_field': 'name',
    },
    'delete_microsoft_365': {
        'list_service': 'zato.generic.connection.get-list',
        'delete_service': 'zato.generic.connection.delete',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365,
        },
        'name_field': 'name',
    },
    'delete_pubsub_topic': {
        'list_service': 'zato.pubsub.topic.get-list',
        'delete_service': 'zato.pubsub.topic.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_pubsub_subscription': {
        'list_service': 'zato.pubsub.subscription.get-list',
        'delete_service': 'zato.pubsub.subscription.delete',
        'list_params': {},
        'name_field': 'sub_key',
        'id_field': 'sub_key',
    },
    'delete_pubsub_permission': {
        'list_service': 'zato.pubsub.permission.get-list',
        'delete_service': 'zato.pubsub.permission.delete',
        'list_params': {},
        'name_field': 'name',
    },
    'delete_channel_openapi': {
        'list_service': 'zato.generic.connection.get-list',
        'delete_service': 'zato.generic.connection.delete',
        'list_params': {
            'type_': GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI,
        },
        'name_field': 'name',
    },
}

# ################################################################################################################################
# ################################################################################################################################

def _find_object_id_by_name(client, cluster_id, list_service, list_params, target_name, name_field='name'):
    """ Finds an object's ID by its name using the list service.
    """
    request = {'cluster_id': cluster_id}
    request.update(list_params)

    logger.info('Searching for object with %s=%s using service %s', name_field, target_name, list_service)

    response = client.invoke(list_service, request)

    if not response.ok:
        return None, f'Failed to list objects: {response.details}'

    data = response.data
    if isinstance(data, dict) and 'response' in data:
        data = data['response']

    for item in data:
        item_name = item.get(name_field) if isinstance(item, dict) else getattr(item, name_field, None)
        if item_name == target_name:
            item_id = item.get('id') if isinstance(item, dict) else getattr(item, 'id', None)
            logger.info('Found object %s with id=%s', target_name, item_id)
            return item_id, None

    return None, f'Object with {name_field}={target_name} not found'

# ################################################################################################################################

def _delete_object_by_id(client, cluster_id, delete_service, object_id, id_field='id'):
    """ Deletes an object by its ID.
    """
    request = {
        'cluster_id': cluster_id,
        id_field: object_id,
    }

    logger.info('Deleting object with %s=%s using service %s', id_field, object_id, delete_service)

    response = client.invoke(delete_service, request)

    if not response.ok:
        return False, f'Failed to delete object: {response.details}'

    return True, None

# ################################################################################################################################
# ################################################################################################################################

def execute_delete_security(client, cluster_id, arguments:'anydict') -> 'anydict':
    """ Deletes a security definition by name and type.
    """
    name = arguments.get('name')
    sec_type = arguments.get('type')

    if not name:
        return {'success': False, 'error': 'Name is required'}

    if not sec_type:
        return {'success': False, 'error': 'Security type is required'}

    if sec_type not in _security_type_to_service:
        return {'success': False, 'error': f'Unknown security type: {sec_type}'}

    config = _security_type_to_service[sec_type]
    list_service = config['list']
    delete_service = config['delete']

    try:
        object_id, error = _find_object_id_by_name(client, cluster_id, list_service, {}, name)

        if error:
            return {'success': False, 'error': error}

        success, error = _delete_object_by_id(client, cluster_id, delete_service, object_id)

        if error:
            return {'success': False, 'error': error}

        return {'success': True, 'message': f'Deleted {sec_type} security definition: {name}', 'id': object_id}

    except Exception:
        error_msg = format_exc()
        logger.warning('Delete security failed: %s', error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################

def execute_delete_tool(client, cluster_id, tool_name:'str', arguments:'anydict') -> 'anydict':
    """ Executes a delete tool by name.
    """
    if tool_name == 'delete_security':
        return execute_delete_security(client, cluster_id, arguments)

    if tool_name == 'delete_pubsub_subscription':
        sub_key = arguments.get('sub_key')
        if not sub_key:
            return {'success': False, 'error': 'Subscription key is required'}

        config = _delete_tool_config[tool_name]

        try:
            success, error = _delete_object_by_id(
                client, cluster_id, config['delete_service'], sub_key, id_field='sub_key'
            )

            if error:
                return {'success': False, 'error': error}

            return {'success': True, 'message': f'Deleted subscription: {sub_key}'}

        except Exception:
            error_msg = format_exc()
            logger.warning('Delete subscription failed: %s', error_msg)
            return {'success': False, 'error': error_msg}

    if tool_name not in _delete_tool_config:
        return {'success': False, 'error': f'Unknown delete tool: {tool_name}'}

    config = _delete_tool_config[tool_name]
    name_field = config.get('name_field', 'name')
    target_name = arguments.get('name')

    if not target_name:
        return {'success': False, 'error': f'{name_field} is required'}

    try:
        object_id, error = _find_object_id_by_name(
            client,
            cluster_id,
            config['list_service'],
            config['list_params'],
            target_name,
            name_field
        )

        if error:
            return {'success': False, 'error': error}

        id_field = config.get('id_field', 'id')
        success, error = _delete_object_by_id(client, cluster_id, config['delete_service'], object_id, id_field)

        if error:
            return {'success': False, 'error': error}

        object_type = tool_name.replace('delete_', '').replace('_', ' ')
        return {'success': True, 'message': f'Deleted {object_type}: {target_name}', 'id': object_id}

    except Exception:
        error_msg = format_exc()
        logger.warning('Delete tool %s failed: %s', tool_name, error_msg)
        return {'success': False, 'error': error_msg}

# ################################################################################################################################
# ################################################################################################################################
