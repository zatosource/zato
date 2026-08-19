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
from zato.common.api import EnvVariable, HTTP_SOAP
from zato.common.util.api import asbool
from zato.common.util.sql import get_security_by_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.odb.model import HTTPSOAP
    from zato.common.typing_ import any_, anydict, strdict

    # Add dummy assignments to satisfy type checkers
    SASession = SASession
    EnmasseYAMLImporter = EnmasseYAMLImporter
    HTTPSOAP = HTTPSOAP
    anydict = anydict

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
    'redshift': 'redshift+redshift_connector',
    'snowflake': 'snowflake',
}

# How many connections an SQL pool holds unless its definition says otherwise.
SQL_Default_Pool_Size = 5

# The same mappings the other way around, for exports to turn engine names back into user-friendly types.
_engine_to_type_map = {}

for _type_name, _engine_name in SQL_TYPE_MAP.items():
    _engine_to_type_map[_engine_name] = _type_name

# ################################################################################################################################
# ################################################################################################################################

# What a top-level key that has been renamed is called now, keyed by the name it used to go by.
Renamed_Keys = {
    'channel_hl7_mllp': 'channel_mllp',
    'outgoing_hl7_mllp': 'outgoing_mllp',
}

# ################################################################################################################################
# ################################################################################################################################

def get_engine_from_type(database_type:'str') -> 'str':
    """ Converts a user-friendly database type to the internal engine name.
    """

    # An internal engine name on input is used directly ..
    if database_type in _engine_to_type_map:
        out = database_type

    # .. otherwise, the user-friendly name is mapped to its engine name.
    else:
        out = SQL_TYPE_MAP[database_type]

    return out

# ################################################################################################################################

def get_type_from_engine(engine:'str') -> 'str':
    """ Converts an internal engine name to a user-friendly database type.
    """

    # An engine without a user-friendly name is returned unchanged
    if engine in _engine_to_type_map:
        out = _engine_to_type_map[engine]
    else:
        out = engine

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_non_default_response_cache(stored:'anydict') -> 'anydict':
    """ Returns the response_cache fields whose values differ from the defaults, in the canonical
    field order - only these travel through enmasse files.
    """

    # Our response to produce
    out = {}

    defaults = HTTP_SOAP.ResponseCache.get_default_config()

    for field_name, default_value in defaults.items():
        if field_name in stored:
            value = stored[field_name]

            # The TTL unit always travels along with a non-default TTL - one is ambiguous without the other.
            if field_name == 'ttl_unit':
                is_ttl_unit_needed = 'ttl' in out
            else:
                is_ttl_unit_needed = False

            if value != default_value:
                out[field_name] = value
            elif is_ttl_unit_needed:
                out[field_name] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

def security_needs_update(yaml_item:'anydict', db_def:'anydict', importer:'EnmasseYAMLImporter') -> 'bool':

    yaml_security = yaml_item.get('security')
    db_security_id = db_def.get('security_id')

    logger.info('Checking security update: yaml_security=%s db_security_id=%s', yaml_security, db_security_id)
    logger.info('Available sec_defs: %s', list(importer.sec_defs.keys()))

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
        logger.info('Found sec_def: %s', sec_def)
        logger.info('Comparing sec_def id %s with db_security_id %s', sec_def['id'], db_security_id)
        if sec_def['id'] != db_security_id:
            logger.info('Security mismatch: YAML=%s (id=%s) DB_ID=%s', yaml_security, sec_def['id'], db_security_id)
            return True
        else:
            logger.info('Security matches: YAML=%s (id=%s) DB_ID=%s', yaml_security, sec_def['id'], db_security_id)

    return False

# ################################################################################################################################
# ################################################################################################################################

def get_value_from_environment(value:'any_') -> 'str':

    if not isinstance(value, str):
        return value

    # Handle ${VAR} syntax ..
    if value.startswith('${'):
        if value.endswith('}'):
            env_key = value[2:-1]
            logger.info('Resolving ${%s} from environment, present=%s', env_key, env_key in os.environ)
            default = f'{EnvVariable.Missing_Value_Prefix}{env_key}_{uuid.uuid4().hex[:12]}'
            value = os.environ.get(env_key, default)

            try:
                value = asbool(value)
            except Exception:
                pass

            return value

    # .. handle Zato_Enmasse_Env. prefix syntax.
    prefix = 'Zato_Enmasse_Env.'

    if not value.startswith(prefix):
        return value

    env_key = value.replace(prefix, '')
    default = f'{EnvVariable.Missing_Value_Prefix}{env_key}_{uuid.uuid4().hex[:12]}'

    value = os.environ.get(env_key, default)

    try:
        value = asbool(value)
    except Exception:
        pass

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
