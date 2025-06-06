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
    ]

# ################################################################################################################################
# ################################################################################################################################

def get_object_order(object_type:'str') -> 'strlist':

    order = {}

    order['security'] = 'name', 'type', 'username', 'auth_endpoint', 'client_id_field', 'client_secret_field', 'grant_type', \
        'data_format', 'extra_fields:list'

    order['groups'] = 'name',
    order['channel_rest'] = 'name',
    order['outgoing_rest'] = 'name',
    order['scheduler'] = 'name',
    order['ldap'] = 'name',
    order['sql'] = 'name',
    order['outgoing_soap'] = 'name',
    order['microsoft_365'] = 'name',
    order['cache'] = 'name',
    order['confluence'] = 'name',
    order['jira'] = 'name',
    order['email_imap'] = 'name',
    order['email_smtp'] = 'name',
    order['odoo'] = 'name',
    order['elastic_search'] = 'name',

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

                # Write the element header
                _ = f.write(f'{element}:\n\n')

                # Check if this element exists on input
                if element in data_dict:

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

                            # .. check if the optional field exists ..
                            if field in item:
                                _ = f.write(f'    {field}: {item[field]}\n')

                        # .. and add blank line after each item.
                        _ = f.write('\n')


# ################################################################################################################################
# ################################################################################################################################
