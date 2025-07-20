# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import uuid

# Zato
from zato.common.util.sql import get_security_by_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.odb.model import HTTPSOAP
    from zato.common.typing_ import any_, anydict, bool_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# SQL engine type mappings
SQL_TYPE_MAP = {
    'mssql': 'zato+mssql1',
    'mysql': 'mysql+pymysql',
    'oracle': 'oracle',
    'postgresql': 'postgresql+pg8000',
}

# ################################################################################################################################

def get_engine_from_type(raw_type:'str') -> 'str':
    """Converts a user-friendly database type to the internal type name.
    """

    # If raw_type is already an internal type name, use it directly ..
    if raw_type in SQL_TYPE_MAP.values():
        return raw_type

    # .. Otherwise, try to map it from user-friendly name to internal engine name
    else:
        return SQL_TYPE_MAP[raw_type]

# ################################################################################################################################

def get_type_from_engine(engine:'str') -> 'str':
    """Converts an internal engine name to a user-friendly database type.
    """
    engine_to_type_map = {value: key for key, value in SQL_TYPE_MAP.items()}

    # Return user-friendly type if found, otherwise return the engine name unchanged
    return engine_to_type_map.get(engine, engine)

# ################################################################################################################################

def security_needs_update(yaml_item:'anydict', db_def:'anydict', importer:'EnmasseYAMLImporter') -> 'bool_':

    yaml_security = yaml_item.get('security')
    db_security_id = db_def.get('security_id')

    # If security is not defined in YAML but exists in DB - update needed
    if yaml_security is None and db_security_id is not None:
        logger.info('Security removed in YAML but exists in DB')
        return True

    # If security is defined in YAML but not in DB - update needed
    elif yaml_security is not None and db_security_id is None:
        logger.info('Security defined in YAML but missing in DB')
        return True

    # If security is defined in both, check if they match
    elif yaml_security is not None and db_security_id is not None:
        if yaml_security not in importer.sec_defs:
            logger.warning('Security definition %s not found, skipping comparison', yaml_security)
            return False

        sec_def = importer.sec_defs[yaml_security]
        if sec_def['id'] != db_security_id:
            logger.info('Security mismatch: YAML=%s DB_ID=%s', yaml_security, db_security_id)
            return True

    return False

# ################################################################################################################################
# ################################################################################################################################

def get_value_from_environment(value:'any_') -> 'str':

    if not isinstance(value, str):
        return value

    prefix = 'Zato_Enmasse_Env.'

    if not value.startswith(prefix):
        return value

    env_key = value.replace(prefix, '')
    default = f'Missing_{env_key}_{uuid.uuid4().hex[:12]}'

    value = os.environ.get(env_key, default)
    return value

# ################################################################################################################################

def preprocess_item(item:'strdict') -> 'any_':

    for key, value in item.items():
        value = get_value_from_environment(value)
        item[key] = value

    return item

# ################################################################################################################################
# ################################################################################################################################

def assign_security(item:'HTTPSOAP', item_def:'anydict', importer:'EnmasseYAMLImporter', session:'SASession') -> 'None':

    if 'security' in item_def or 'security_name' in item_def:
        name = item_def['name']
        security_name = item_def.get('security') or item_def.get('security_name')

        if security_name not in importer.sec_defs:
            error_msg = f'Security definition "{security_name}" not found for "{name}"'
            logger.error(error_msg)
            return

        sec_def = importer.sec_defs[security_name]
        security_id = sec_def['id']
        item.security = get_security_by_id(session, security_id)

# ################################################################################################################################
# ################################################################################################################################

def reorder_fields(fields:'anydict') -> 'anydict':

    field_order = {}
    field_order['security'] = 'name', 'type', 'username', 'auth_endpoint', 'client_id_field', \
        'client_secret_field', 'grant_type', 'data_format', 'extra_fields'
    field_order['groups'] = 'name', 'members'
    field_order['channel_rest'] = 'name', 'service', 'url_path', 'security', 'groups', 'data_format'

# ################################################################################################################################
# ################################################################################################################################

def get_top_level_order() -> 'strlist':

    return [
        'security',
        'groups',
        'channel_rest',
        'outgoing_rest',
        'scheduler',
        'ldap',
        'sql',
        'outgoing_soap',
        'microsoft_365',
        'cache',
        'confluence',
        'jira',
        'email_imap',
        'email_smtp',
        'odoo',
        'elastic_search',
        'pubsub_topic',
        'pubsub_permission',
        'pubsub_subscription',
    ]

# ################################################################################################################################
# ################################################################################################################################

def get_object_order(object_type:'str') -> 'strlist':

    order = {}

    order['security'] = 'name', 'is_active', 'type', 'username', 'auth_endpoint', 'client_id_field', 'client_secret_field', 'grant_type', \
        'data_format', 'extra_fields:list',

    order['groups'] = 'name', 'is_active', 'members:list',
    order['channel_rest'] = 'name', 'is_active', 'service', 'url_path', 'security', 'data_format', 'groups:list',
    order['outgoing_rest'] = 'name', 'is_active', 'host', 'url_path', 'security', 'data_format', 'timeout', 'ping_method', 'tls_verify',
    order['scheduler'] = 'name', 'is_active', 'service', 'job_type', 'start_date', 'seconds', 'minutes', 'hours', 'days', 'extra:list',
    order['ldap'] = 'name', 'is_active', 'username', 'auth_type', 'server_list:list',
    order['sql'] = 'name', 'is_active', 'type', 'host', 'port', 'db_name', 'username',
    order['outgoing_soap'] = 'name', 'is_active', 'host', 'port', 'url_path', 'security', 'soap_action', 'soap_version', 'timeout', 'tls_verify',
    order['microsoft_365'] = 'name', 'is_active', 'client_id', 'tenant_id', 'scopes:list',
    order['cache'] = 'name', 'is_active', 'extend_expiry_on_get', 'extend_expiry_on_set',
    order['confluence'] = 'name', 'is_active', 'address', 'username',
    order['jira'] = 'name', 'is_active', 'address', 'username',
    order['email_imap'] = 'name', 'is_active', 'type', 'host', 'port', 'username', 'tenant_id', 'client_id', # TODO: Implement type vs. server_type
    order['email_smtp'] = 'name', 'is_active', 'host', 'port', 'username',
    order['odoo'] = 'name', 'is_active', 'host', 'port', 'database', 'user'
    order['elastic_search'] = 'name', 'is_active', 'hosts:list', 'timeout', 'body_as'
    order['pubsub_topic'] = 'name', 'description'
    order['pubsub_permission'] = 'security', 'pub', 'sub'
    order['pubsub_subscription'] = 'security', 'delivery_type', 'push_rest_endpoint', 'push_service', 'max_retry_time', 'topic_list'

    return order[object_type]

# ################################################################################################################################
# ################################################################################################################################

class FileWriter:

    def __init__(self, path:'str') -> 'None':
        self.path = path

# ################################################################################################################################

    def write(self, data_dict:'anydict') -> 'None':

        top_level = get_top_level_order()

        with open(self.path, 'w') as f:
            for element in top_level:

                # Check if this element exists on input
                if element in data_dict:

                    # Write the element header with newline before it
                    _ = f.write(f'\n{element}:\n')

                    # Get the field order dictionary
                    fields = get_object_order(element)

                    # Process each item in the data
                    for item in data_dict[element]:

                        # Write the first field with dash ..
                        first_field = fields[0]

                        if first_field in item:
                            _ = f.write(f'  - {first_field}: {item[first_field]}\n')

                        # .. write remaining fields with indentation but no dash ..
                        for field in fields[1:]:

                            # Check if this is a list field notation
                            if ':list' in field:
                                # Extract the actual field name without the suffix
                                actual_field = field.split(':')[0]

                                # Check if the actual field exists in the item
                                if actual_field in item:

                                    # Get the field value
                                    field_value = item[actual_field]

                                    # Check if it's actually a list
                                    if isinstance(field_value, list):
                                        # Write the field name as a list header
                                        _ = f.write(f'    {actual_field}:\n')

                                        # Write each list item with proper indentation
                                        for list_item in field_value:
                                            _ = f.write(f'      - {list_item}\n')
                                    else:
                                        # It's a string or other non-list value, treat as a regular field
                                        _ = f.write(f'    {actual_field}: {field_value}\n')

                            # For regular fields
                            elif field in item:
                                # Regular field
                                _ = f.write(f'    {field}: {item[field]}\n')

                        # .. and add blank line after each item.
                        _ = f.write('\n')
                else:
                    # Write the element header without newline for empty sections
                    _ = f.write(f'{element}:\n')


# ################################################################################################################################
# ################################################################################################################################
