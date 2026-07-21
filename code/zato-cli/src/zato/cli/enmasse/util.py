# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import uuid
from json import dumps as json_dumps, loads as json_loads

# Zato
from zato.common.api import HTTP_SOAP, SCHEDULER, SchedulerLink, URL_TYPE
from zato.common.odb.model import Job
from zato.common.util.api import asbool
from zato.common.util.imap_scheduler import interval_from_unit
from zato.common.util.sql import get_security_by_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.odb.model import HTTPSOAP
    from zato.common.typing_ import any_, anydict, bool_, strdict, strlist

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

# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_health_check = HTTP_SOAP.HealthCheck

# Row-based invocation fields are YAML lists of {key, value, mode} mappings in enmasse files
# and JSON strings in the database.
Invocation_Row_Fields = (
    _invocation.Field_Request_Query_String,
    _invocation.Field_Request_Path_Params,
    _invocation.Field_Request_Headers,
    _invocation.Field_Request_Message,
    _invocation.Field_Request_SOAP_Headers,
)

# The invocation and health check fields shared by outgoing REST and SOAP connections.
# Job IDs are environment-local so they never travel through enmasse - the importer
# recreates the linked jobs itself.
Invocation_Common_Fields = (
    _invocation.Field_Response_Map,
    _invocation.Field_Response_Map_Mode,
    _invocation.Field_Callback_Type,
    _invocation.Field_Callback_Name,
    _invocation.Field_Run_Every,
    _invocation.Field_Run_Unit,
    _invocation.Field_Start_Date,
    _health_check.Field_Run_Every,
    _health_check.Field_Run_Unit,
    _health_check.Field_Notify_On,
    _health_check.Field_Callback_Type,
    _health_check.Field_Callback_Name,
)

# Everything an outgoing REST connection carries
Invocation_Fields_REST = (
    _invocation.Field_Request_Method,
    _invocation.Field_Request_Query_String,
    _invocation.Field_Request_Path_Params,
    _invocation.Field_Request_Headers,
    _invocation.Field_Request_Data,
    _invocation.Field_Request_Data_Mode,
) + Invocation_Common_Fields

# Everything an outgoing SOAP connection carries
Invocation_Fields_SOAP = (
    _invocation.Field_Request_Operation,
    _invocation.Field_Request_Message,
    _invocation.Field_Request_Message_Map,
    _invocation.Field_Request_SOAP_Headers,
    _invocation.Field_WSA_Action,
    _invocation.Field_WSA_To,
    _invocation.Field_WSA_Reply_To,
) + Invocation_Common_Fields

# ################################################################################################################################

def _as_order_fields(field_names:'any_') -> 'any_':
    """ Turns a tuple of invocation field names into FileWriter order notation,
    marking row-based fields with the :list suffix so they render as YAML lists.
    """

    # Our response to produce
    out = []

    for field_name in field_names:
        if field_name in Invocation_Row_Fields:
            out.append(field_name + ':list')
        else:
            out.append(field_name)

    return tuple(out)

# The same field lists in the notation the file writer's order tuples use
Invocation_Order_Fields_REST = _as_order_fields(Invocation_Fields_REST)
Invocation_Order_Fields_SOAP = _as_order_fields(Invocation_Fields_SOAP)

# ################################################################################################################################

def as_row_list(value:'any_') -> 'any_':
    """ Normalizes a row-based invocation field to a list of rows - the Dashboard stores them
    in the database as JSON strings while YAML files carry them as lists of mappings.
    """

    # Our response to produce
    out = []

    if value:
        if isinstance(value, str):
            out = json_loads(value)
        else:
            out = value

    return out

# ################################################################################################################################

def export_invocation_fields(exported_conn:'anydict', opaque:'anydict', field_names:'any_') -> 'None':
    """ Copies the declarative invocation and health check fields from a connection's opaque
    attributes to its exported definition, turning row-based fields into YAML-friendly lists.
    """
    for field_name in field_names:
        value = opaque.get(field_name)
        if not value:
            continue

        # Row fields become lists so enmasse files stay human-editable
        if field_name in Invocation_Row_Fields:
            value = as_row_list(value)
            if not value:
                continue

        exported_conn[field_name] = value

# ################################################################################################################################

def serialize_invocation_rows(item:'anydict') -> 'None':
    """ Serializes the row-based invocation fields of a YAML definition back to the JSON strings
    the database keeps, ahead of the definition being stored.
    """
    for field_name in Invocation_Row_Fields:
        value = item.get(field_name)
        if value and not isinstance(value, str):
            item[field_name] = json_dumps(value)

# ################################################################################################################################

def _sync_one_invocation_job(
    importer,    # type: EnmasseYAMLImporter
    session,     # type: SASession
    conn_def,    # type: anydict
    conn,        # type: any_
    kind,        # type: str
    conn_type,   # type: str
    job_name,    # type: str
    job_service, # type: str
    run_every,   # type: any_
    run_unit,    # type: str
    start_date,  # type: any_
    extra,       # type: str
    ) -> 'any_':
    """ Creates or updates one scheduler job linked to a connection being imported.
    """

    # Build a regular scheduler job definition out of the connection's fields,
    # carrying the generic link attributes that point back to the connection.
    job_def = {
        'name': job_name,
        'service': job_service,
        'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
        'is_active': conn_def.get('is_active', True),
        'extra': extra,
        SchedulerLink.Conn_Type: conn_type,
        SchedulerLink.Conn_ID: conn.id,
        SchedulerLink.Kind: kind,
    }

    interval = interval_from_unit(int(run_every), run_unit)
    job_def.update(interval)

    if start_date:
        job_def['start_date'] = start_date

    # The job may already exist from a previous import, in which case it is updated in place
    existing_job = session.query(Job).filter_by(name=job_name, cluster_id=importer.cluster_id).first()

    if existing_job:
        job_def['id'] = existing_job.id
        out = importer.scheduler_importer.update_job_definition(job_def, session)
    else:
        out = importer.scheduler_importer.create_job_definition(job_def, session)

    return out

# ################################################################################################################################

def sync_invocation_jobs(
    importer,  # type: EnmasseYAMLImporter
    session,   # type: SASession
    conn_def,  # type: anydict
    conn,      # type: any_
    transport, # type: str
    ) -> 'None':
    """ Creates or updates the scheduled-invocation and health check jobs of an outgoing REST
    or SOAP connection being imported, storing the job IDs back in the definition so they land
    in the connection's opaque attributes. Job IDs never travel through enmasse files themselves.
    """
    if transport == URL_TYPE.SOAP:
        job_prefix = _invocation.Job_Prefix_SOAP
        conn_type = SchedulerLink.ConnType.SOAP_Outgoing
    else:
        job_prefix = _invocation.Job_Prefix_REST
        conn_type = SchedulerLink.ConnType.REST_Outgoing

    # The scheduled-invocation job runs the connection through the shared dispatch service ..
    if run_every := conn_def.get(_invocation.Field_Run_Every):

        run_unit = conn_def.get(_invocation.Field_Run_Unit)
        if not run_unit:
            run_unit = _invocation.Unit.Minutes
        conn_def[_invocation.Field_Run_Unit] = run_unit

        extra = json_dumps({
            _invocation.Extra_Conn_ID: conn.id,
            _invocation.Extra_Conn_Name: conn.name,
            _invocation.Extra_Transport: transport,
        })

        job = _sync_one_invocation_job(
            importer,
            session,
            conn_def,
            conn,
            kind=SchedulerLink.KindType.Scheduler,
            conn_type=conn_type,
            job_name=job_prefix + conn.name,
            job_service=_invocation.Dispatch_Service,
            run_every=run_every,
            run_unit=run_unit,
            start_date=conn_def.get(_invocation.Field_Start_Date),
            extra=extra,
        )
        conn_def[_invocation.Field_Job_ID] = job.id

    # .. and the health check job pings the connection, delivering each outcome to the callback.
    if health_check_run_every := conn_def.get(_health_check.Field_Run_Every):

        health_check_run_unit = conn_def.get(_health_check.Field_Run_Unit)
        if not health_check_run_unit:
            health_check_run_unit = _invocation.Unit.Minutes
        conn_def[_health_check.Field_Run_Unit] = health_check_run_unit

        notify_on = conn_def.get(_health_check.Field_Notify_On)
        if not notify_on:
            notify_on = _health_check.NotifyOn.Failures
        conn_def[_health_check.Field_Notify_On] = notify_on

        extra = json_dumps({
            _health_check.Extra_Conn_ID: conn.id,
            _health_check.Extra_Conn_Name: conn.name,
            _health_check.Extra_Conn_Type: conn_type,
            _health_check.Field_Callback_Type: conn_def.get(_health_check.Field_Callback_Type),
            _health_check.Field_Callback_Name: conn_def.get(_health_check.Field_Callback_Name),
            _health_check.Field_Notify_On: notify_on,
        })

        job = _sync_one_invocation_job(
            importer,
            session,
            conn_def,
            conn,
            kind=SchedulerLink.KindType.HealthCheck,
            conn_type=conn_type,
            job_name=_health_check.Job_Prefix + conn.name,
            job_service=_health_check.Dispatch_Service,
            run_every=health_check_run_every,
            run_unit=health_check_run_unit,
            start_date=None,
            extra=extra,
        )
        conn_def[_health_check.Field_Job_ID] = job.id

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

            # The TTL unit always travels along with a non-default TTL - one is ambiguous without the other
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
            default = f'Missing_{env_key}_{uuid.uuid4().hex[:12]}'
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
    default = f'Missing_{env_key}_{uuid.uuid4().hex[:12]}'

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
        'quota_tier',
        'security',
        'groups',
        'channel_rest',
        'channel_soap',
        'channel_as4',
        'outgoing_rest',
        'scheduler',
        'ldap',
        'llm',
        'odata',
        'sap',
        'sql',
        'outgoing_soap',
        'outgoing_as2',
        'outgoing_as4',
        'microsoft_cloud',
        'microsoft_fabric',
        'microsoft_power_automate',
        'confluence',
        'jira',
        'channel_ibm_mq',
        'outgoing_ibm_mq',
        'channel_kafka',
        'mcp_gateway',
        'outgoing_graphql',
        'outgoing_kafka',
        'channel_hl7_mllp',
        'outgoing_hl7_mllp',
        'email_imap',
        'email_smtp',
        'odoo',
        'elastic_search',
        'pubsub_topic',
        'pubsub_permission',
        'pubsub_subscription',
        'channel_openapi',
    ]

# ################################################################################################################################
# ################################################################################################################################

def get_object_order(object_type:'str') -> 'strlist':

    order = {}

    order['security'] = 'name', 'is_active', 'type', 'username', 'mode', 'use_digest', 'sign', 'encrypt', \
        'issuer', 'subject', 'audience', 'jwks_url', 'claims:list', 'signing_key', 'signing_certificate_chain', \
        'decryption_key', 'peer_certificate', 'trust_anchors', 'auth_endpoint', 'client_id_field', \
        'client_secret_field', 'grant_type', 'data_format', 'extra_fields:list', \
        'static_header', 'is_static_token', 'static_token', 'static_prefix', 'rate_limiting:list', 'quota_tier',

    order['quota_tier'] = 'name', 'description', 'rules:list',
    order['groups'] = 'name', 'is_active', 'quota_tier', 'members:list',
    order['channel_rest'] = 'name', 'is_active', 'service', 'url_path', 'security', 'data_format', 'groups:list', \
        'rate_limiting:list', 'response_cache:dict', 'is_deprecated', 'deprecation_sunset', 'deprecation_successor',
    order['channel_soap'] = 'name', 'is_active', 'service', 'url_path', 'security', 'soap_action', 'soap_version', 'use_mtom', \
        'groups:list', 'rate_limiting:list', 'response_cache:dict',
    order['outgoing_rest'] = ('name', 'is_active', 'host', 'url_path', 'security', 'data_format', 'timeout', 'ping_method', \
        'tls_verify') + Invocation_Order_Fields_REST
    order['scheduler'] = 'name', 'is_active', 'service', 'job_type', 'start_date', 'seconds', 'minutes', 'hours', 'days', 'extra:list',
    order['ldap'] = 'name', 'is_active', 'username', 'auth_type', 'server_list:list',
    order['llm'] = 'name', 'is_active', 'model', 'address', 'pool_size', 'timeout', 'max_tokens', \
        'max_history_turns', 'chat_expiry',
    order['odata'] = 'name', 'is_active', 'address', 'odata_version', 'auth_type', 'username', 'token_url', 'tenant_id', \
        'client_id', 'scopes', 'needs_csrf_token', 'page_size', 'timeout', 'pool_size',

    # SAP connections run on the OData implementation, so their fields are ordered the same way
    order['sap'] = order['odata']

    order['sql'] = 'name', 'is_active', 'type', 'host', 'port', 'db_name', 'username',
    order['outgoing_soap'] = ('name', 'is_active', 'host', 'port', 'url_path', 'security', 'soap_action', 'soap_version', \
        'timeout', 'tls_verify') + Invocation_Order_Fields_SOAP
    order['outgoing_as2'] = 'name', 'is_active', 'as2_from', 'as2_to', 'endpoint_url', 'isa_qualifier', 'isa_id', \
        'gs_id', 'unb_id', 'sign', 'sign_algorithm', 'encrypt', 'encryption_algorithm', 'compress', \
        'compress_before_signing', 'mdn_mode', 'mdn_signed', 'async_mdn_url', 'subject', 'content_type', \
        'as2_version', 'content_transfer_encoding', 'http_transfer_mode', 'http_timeout_seconds', \
        'chunked_threshold_bytes', 'ack_overdue_after', 'resend_max_retries', 'ship_notice_window_hours', \
        'alerting_opt_out', 'preserve_filename', \
        'warn_on_duplicate_filename', 'verify_tls', 'force_base64', 'prevent_canonicalization', \
        'inbound_topic', 'inbound_service', 'as2_partner_cert', 'as2_partner_next_cert', \
        'as2_partner_next_cert_from', 'as2_signing_cert_chain', 'as2_next_decryption_cert', \
        'as2_peer_signing_cert', 'as2_peer_encryption_cert', 'as2_trust_anchors',
    order['channel_as4'] = 'name', 'is_active', 'url_path', 'service', 'security', 'as4_profile', 'as4_from_party', \
        'as4_to_party', 'as4_service', 'as4_action', 'as4_agreement', 'as4_mpc', 'as4_original_sender', 'as4_final_recipient', \
        'as4_extra_pmodes', 'as4_serviced_participants', 'as4_inbound_topic', 'as4_signing_key', 'as4_signing_cert_chain', \
        'as4_decryption_key', 'as4_peer_signing_cert', 'as4_peer_encryption_cert', 'as4_trust_anchors',
    order['outgoing_as4'] = 'name', 'is_active', 'host', 'url_path', 'timeout', 'validate_tls', 'as4_profile', \
        'as4_from_party', 'as4_to_party', 'as4_service', 'as4_action', 'as4_agreement', 'as4_mpc', 'as4_original_sender', \
        'as4_final_recipient', 'as4_extra_pmodes', 'as4_use_discovery', 'as4_sml_domain', 'as4_signing_key', \
        'as4_signing_cert_chain', 'as4_decryption_key', 'as4_peer_signing_cert', 'as4_peer_encryption_cert', 'as4_trust_anchors',
    order['microsoft_cloud'] = 'name', 'is_active', 'client_id', 'tenant_id', 'scopes:list',
    order['microsoft_fabric'] = 'name', 'is_active', 'address', 'client_id', 'tenant_id',
    order['microsoft_power_automate'] = 'name', 'is_active', 'address', 'client_id', 'tenant_id', 'environment_id',
    order['confluence'] = 'name', 'is_active', 'address', 'username',
    order['jira'] = 'name', 'is_active', 'address', 'username',
    order['channel_ibm_mq'] = 'name', 'is_active', 'address', 'queue_manager', 'mq_channel_name', 'queue', 'service', \
        'username', 'remove_jms_headers', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
    order['outgoing_ibm_mq'] = 'name', 'is_active', 'address', 'queue_manager', 'mq_channel_name', 'queue', \
        'username', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
    order['channel_kafka'] = 'name', 'is_active', 'address', 'topic', 'group_id', 'service',
    order['mcp_gateway'] = 'name', 'is_active', 'url_path', 'services', 'security_groups:list',
    order['outgoing_graphql'] = 'name', 'is_active', 'address', 'security', 'default_query_timeout',
    order['outgoing_kafka'] = 'name', 'is_active', 'address', 'topic',
    order['channel_hl7_mllp'] = 'name', 'is_active', 'service', 'msh9_message_type', 'msh9_trigger_event', 'should_validate', \
        'normalize_line_endings', 'fix_off_by_one_field_index', 'dedup_ttl_value', 'dedup_ttl_unit', 'is_default',
    order['outgoing_hl7_mllp'] = 'name', 'is_active', 'address', 'start_seq', 'end_seq', 'recv_timeout', 'max_msg_size', \
        'read_buffer_size', 'max_wait_time', 'should_log_messages', 'logging_level', \
        'max_retries', 'backoff_base_seconds', 'backoff_cap_seconds', 'backoff_jitter_percent', \
        'circuit_breaker_threshold_percent', 'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds', \
        'tls_ca_path', 'tls_cert_path', 'tls_key_path',
    order['email_imap'] = 'name', 'is_active', 'type', 'host', 'port', 'username', 'tenant_id', 'client_id', \
        'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_service', \
        'scheduler_invoke_with', # TODO: Implement type vs. server_type
    order['email_smtp'] = 'name', 'is_active', 'host', 'port', 'username',
    order['odoo'] = 'name', 'is_active', 'host', 'port', 'database', 'user'
    order['elastic_search'] = 'name', 'is_active', 'address_list:list', 'username', 'timeout', \
        'is_tls_validation_enabled', 'tls_ca_certs_file', 'tls_cert_key_file'
    order['pubsub_topic'] = 'name', 'description'
    order['pubsub_permission'] = 'security', 'pub', 'sub'
    order['pubsub_subscription'] = 'security', 'delivery_type', 'push_rest_endpoint', 'push_service', 'max_retry_time', 'topic_list'
    order['channel_openapi'] = 'name', 'is_active', 'url_path', 'rest_channel_list:list'

    return order[object_type]

# ################################################################################################################################
# ################################################################################################################################

_yaml_unsafe_chars = frozenset(',:[]{}&*#?|->!%@`')

# Unquoted, these would be read back by a YAML parser as booleans or nulls instead of strings
_yaml_keyword_scalars = frozenset(('true', 'false', 'yes', 'no', 'on', 'off', 'null', '~'))

def _is_ambiguous_scalar(text:'str') -> 'bool':
    """ Returns True if unquoted text would be read back by a YAML parser
    as a number, boolean or null instead of a string.
    """
    text_lower = text.lower()

    if text_lower in _yaml_keyword_scalars:
        return True

    # Anything that parses as a number would lose its string type on a round trip
    try:
        _ = float(text)
    except ValueError:
        out = False
    else:
        out = True

    return out

def _yaml_quote(value:'any_') -> 'str':
    """ Wraps a scalar value in single quotes if it contains characters
    that would make the YAML parser misinterpret it.
    """
    text = str(value)

    needs_quoting = False

    if not text:
        needs_quoting = True
    elif text[0] in _yaml_unsafe_chars:
        needs_quoting = True
    else:
        for character in text:
            if character in _yaml_unsafe_chars:
                needs_quoting = True
                break

    # A string that reads back as a number or boolean must keep its string type
    if not needs_quoting:
        if isinstance(value, str):
            if _is_ambiguous_scalar(text):
                needs_quoting = True

    if needs_quoting:
        escaped = text.replace("'", "''")
        out = f"'{escaped}'"
        return out

    out = text
    return out

# ################################################################################################################################
# ################################################################################################################################

def _write_scalar_field(file_handle:'any_', line_prefix:'str', field_name:'str', value:'any_', block_indent:'int') -> 'None':
    """ Writes a single scalar field, using a YAML block scalar for multi-line values
    (e.g. PEM certificates and keys) so that newlines survive a round trip.
    """
    text = str(value)

    if isinstance(value, str) and '\n' in text:

        # A trailing newline needs the clip style, no trailing newline needs the strip style
        if text.endswith('\n'):
            indicator = '|'
            text = text[:-1]
        else:
            indicator = '|-'

        _ = file_handle.write(f'{line_prefix}{field_name}: {indicator}\n')

        pad = ' ' * block_indent
        for line in text.split('\n'):
            if line:
                _ = file_handle.write(f'{pad}{line}\n')
            else:
                _ = file_handle.write('\n')
    else:
        quoted = _yaml_quote(value)
        _ = file_handle.write(f'{line_prefix}{field_name}: {quoted}\n')

# ################################################################################################################################
# ################################################################################################################################

def _write_dict_list_item(file_handle:'any_', item:'anydict', indent:'int'=6) -> 'None':
    """ Writes a dict as a YAML list item with nested keys.
    """
    prefix = ' ' * indent
    is_first = True

    for key, value in item.items():

        # The first key gets the dash prefix ..
        if is_first:
            line_prefix = f'{prefix}- '
            is_first = False

        # .. subsequent keys are indented to align with the first.
        else:
            line_prefix = f'{prefix}  '

        # Nested lists (e.g. cidr_list, time_range) get their own sub-items
        if isinstance(value, list):
            _ = file_handle.write(f'{line_prefix}{key}:\n')
            for sub_item in value:
                if isinstance(sub_item, dict):
                    _write_dict_list_item(file_handle, sub_item, indent + 4)
                else:
                    quoted_sub_item = _yaml_quote(sub_item)
                    _ = file_handle.write(f'{prefix}    - {quoted_sub_item}\n')
        else:
            quoted_value = _yaml_quote(value)
            _ = file_handle.write(f'{line_prefix}{key}: {quoted_value}\n')

# ################################################################################################################################
# ################################################################################################################################

def _write_dict_field(file_handle:'any_', field_name:'str', value:'anydict', indent:'int'=4) -> 'None':
    """ Writes a dict-valued field as a nested YAML mapping, with list values inside it
    rendered as YAML lists (e.g. the response_cache block of a channel).
    """
    prefix = ' ' * indent
    _ = file_handle.write(f'{prefix}{field_name}:\n')

    for key, sub_value in value.items():

        if isinstance(sub_value, list):
            _ = file_handle.write(f'{prefix}  {key}:\n')
            for list_item in sub_value:
                quoted_item = _yaml_quote(list_item)
                _ = file_handle.write(f'{prefix}    - {quoted_item}\n')
        else:
            quoted_value = _yaml_quote(sub_value)
            _ = file_handle.write(f'{prefix}  {key}: {quoted_value}\n')

# ################################################################################################################################
# ################################################################################################################################

class FileWriter:

    def __init__(self, path:'str') -> 'None':
        self.path = path

# ################################################################################################################################

    def write(self, data_dict:'anydict') -> 'None':

        # Prefixes to remove from list items
        prefixes_to_remove = ['pub=', 'sub=']

        top_level = get_top_level_order()

        with open(self.path, 'w') as f:

            previous_had_data = False
            for element in top_level:

                # Check if this element exists on input
                if element in data_dict:

                    # Write the element header with newline before it
                    _ = f.write(f'\n{element}:\n')
                    previous_had_data = True

                    # Get the field order dictionary
                    fields = get_object_order(element)

                    # Process each item in the data
                    for item in data_dict[element]:

                        # Write the first field with dash ..
                        first_field = fields[0]

                        if first_field in item:
                            quoted_first = _yaml_quote(item[first_field])
                            _ = f.write(f'  - {first_field}: {quoted_first}\n')

                        # .. write remaining fields with indentation but no dash ..
                        for field in fields[1:]:

                            # Check if this is a dict field notation
                            if ':dict' in field:
                                actual_field = field.split(':')[0]

                                if actual_field in item:
                                    field_value = item[actual_field]

                                    if isinstance(field_value, dict):
                                        _write_dict_field(f, actual_field, field_value)
                                    else:
                                        _write_scalar_field(f, '    ', actual_field, field_value, 6)

                            # Check if this is a list field notation
                            elif ':list' in field:
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
                                            if isinstance(list_item, dict):
                                                _write_dict_list_item(f, list_item, indent=6)
                                            else:
                                                cleaned_item = str(list_item)
                                                if element == 'pubsub_permission' and actual_field in ['pub', 'sub']:
                                                    for prefix in prefixes_to_remove:
                                                        if cleaned_item.startswith(prefix):
                                                            cleaned_item = cleaned_item[len(prefix):]
                                                            break
                                                quoted_cleaned = _yaml_quote(cleaned_item)
                                                _ = f.write(f'      - {quoted_cleaned}\n')
                                    else:
                                        _write_scalar_field(f, '    ', actual_field, field_value, 6)

                            # For regular fields
                            elif field in item:
                                field_value = item[field]
                                if isinstance(field_value, list):
                                    _ = f.write(f'    {field}:\n')
                                    for list_item in field_value:
                                        cleaned_item = str(list_item)
                                        if element == 'pubsub_permission' and field in ['pub', 'sub']:
                                            for prefix in prefixes_to_remove:
                                                if cleaned_item.startswith(prefix):
                                                    cleaned_item = cleaned_item[len(prefix):]
                                                    break
                                        quoted_cleaned = _yaml_quote(cleaned_item)
                                        _ = f.write(f'      - {quoted_cleaned}\n')
                                else:
                                    _write_scalar_field(f, '    ', field, field_value, 6)

                else:
                    # Write the element header for empty sections
                    if previous_had_data:
                        _ = f.write(f'\n{element}:\n')
                    else:
                        _ = f.write(f'{element}:\n')
                    previous_had_data = False


# ################################################################################################################################
# ################################################################################################################################
