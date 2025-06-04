# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import uuid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
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

def get_value_from_environment(value:'str') -> 'str':

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
