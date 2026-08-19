# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.util.invocation import Invocation_Order_Fields_REST, Invocation_Order_Fields_SOAP, Retry_Fields
from zato.common.hl7.fhir.fields import Outgoing_Enmasse_Names as Outgoing_FHIR_Enmasse_Names
from zato.common.hl7.mllp.fields import Channel_Enmasse_Names, Outgoing_Names

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist, strtuple

    # Add dummy assignments to satisfy type checkers
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The order the top-level sections are written to enmasse files in.
_top_level_order = [
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
    'mongodb',
    'outgoing_soap',
    'outgoing_as2',
    'outgoing_as4',
    'microsoft_cloud',
    'microsoft_fabric',
    'microsoft_power_automate',
    'microsoft_teams',
    'slack',
    'confluence',
    'jira',
    'channel_ibm_mq',
    'outgoing_ibm_mq',
    'channel_amqp',
    'outgoing_amqp',
    'channel_azure_service_bus',
    'outgoing_azure_service_bus',
    'channel_kafka',
    'mcp_gateway',
    'rule_engine_api',
    'outgoing_graphql',
    'outgoing_grpc',
    'outgoing_kafka',
    'channel_mllp',
    'outgoing_mllp',
    'outgoing_fhir',
    'email_imap',
    'email_smtp',
    'odoo',
    'elastic_search',
    'sftp',
    'smb',
    'pubsub_topic',
    'pubsub_permission',
    'pubsub_subscription',
    'channel_openapi',
    'alert_rules',
    'alert_notifications',
    'audit_retention',
    'audit_extraction',
]

# ################################################################################################################################
# ################################################################################################################################

# The order the fields of each section's items are written to enmasse files in.
_object_order:'anydict' = {}

_object_order['security'] = 'name', 'is_active', 'type', 'username', 'mode', 'use_digest', 'sign', 'encrypt', \
    'issuer', 'subject', 'audience', 'jwks_url', 'claims:list', 'signing_key', 'signing_certificate_chain', \
    'decryption_key', 'peer_certificate', 'trust_anchors', 'cert_path', 'key_path', 'ca_certs_path', \
    'client_cert_fingerprint', 'client_cert_subject_dn', 'principal', 'keytab_path', 'target_spn', \
    'needs_delegation', 'auth_endpoint', 'client_id_field', \
    'client_secret_field', 'grant_type', 'data_format', 'extra_fields:list', \
    'static_header', 'is_static_token', 'static_token', 'static_prefix', 'rate_limiting:list', 'quota_tier',

_object_order['quota_tier'] = 'name', 'description', 'rules:list',
_object_order['groups']     = 'name', 'quota_tier', 'members:list',

_object_order['channel_rest'] = 'name', 'is_active', 'service', 'url_path', 'security', 'data_format', 'method', \
    'content_type', 'timeout', 'is_audit_log_active', 'should_include_in_openapi', 'gateway_service_list:list', \
    'groups:list', \
    'rate_limiting:list', 'response_cache:dict', 'is_deprecated', 'deprecation_sunset', 'deprecation_successor',
_object_order['channel_soap'] = 'name', 'is_active', 'service', 'url_path', 'security', 'soap_action', 'soap_version', \
    'use_mtom', 'method', 'content_type', 'timeout', 'is_audit_log_active', \
    'groups:list', 'rate_limiting:list', 'response_cache:dict',

_object_order['outgoing_rest'] = ('name', 'is_active', 'host', 'url_path', 'security', 'data_format', 'content_type', \
    'timeout', 'ping_method', 'tls_verify', 'is_audit_log_active') + Retry_Fields + Invocation_Order_Fields_REST
_object_order['outgoing_soap'] = ('name', 'is_active', 'host', 'port', 'url_path', 'security', 'soap_action', 'soap_version', \
    'content_type', 'timeout', 'tls_verify', 'is_audit_log_active', 'use_ws_addressing', 'use_mtom', \
    'tls_client_cert', 'tls_client_key', 'body_credentials') + Retry_Fields + Invocation_Order_Fields_SOAP

_object_order['scheduler'] = 'name', 'is_active', 'service', 'job_type', 'start_date', 'seconds', 'minutes', 'hours', \
    'days', 'extra:list',
_object_order['ldap']  = 'name', 'is_active', 'username', 'auth_type', 'server_list:list',
_object_order['llm']   = 'name', 'is_active', 'model', 'address', 'pool_size', 'timeout', 'max_tokens', \
    'max_history_turns', 'chat_expiry',
_object_order['odata'] = 'name', 'is_active', 'address', 'odata_version', 'auth_type', 'username', 'token_url', \
    'tenant_id', 'client_id', 'scopes', 'needs_csrf_token', 'page_size', 'timeout', 'pool_size',

# SAP connections run on the OData implementation, so their fields are ordered the same way.
_object_order['sap'] = _object_order['odata']

_object_order['sql'] = 'name', 'is_active', 'type', 'host', 'port', 'db_name', 'username', 'extra:list', 'pool_size', \
    'timeout', 'audit_log', 'ssl', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file', 'ssl_verify',

_object_order['outgoing_as2'] = 'name', 'is_active', 'as2_from', 'as2_to', 'endpoint_url', 'isa_qualifier', 'isa_id', \
    'gs_id', 'unb_id', 'sign', 'sign_algorithm', 'encrypt', 'encryption_algorithm', 'compress', \
    'compress_before_signing', 'mdn_mode', 'mdn_signed', 'async_mdn_url', 'subject', 'content_type', \
    'as2_version', 'content_transfer_encoding', 'http_transfer_mode', 'http_timeout_seconds', \
    'chunked_threshold_bytes', 'ack_overdue_after', 'resend_max_retries', 'ship_notice_window_hours', \
    'alerting_opt_out', 'preserve_filename', \
    'warn_on_duplicate_filename', 'verify_tls', 'force_base64', 'prevent_canonicalization', \
    'inbound_topic', 'inbound_service', 'as2_partner_cert', 'as2_partner_next_cert', \
    'as2_partner_next_cert_from', 'as2_signing_cert_chain', 'as2_next_decryption_cert', \
    'as2_peer_signing_cert', 'as2_peer_encryption_cert', 'as2_trust_anchors',
_object_order['channel_as4'] = 'name', 'is_active', 'url_path', 'service', 'security', 'as4_profile', 'as4_from_party', \
    'as4_to_party', 'as4_service', 'as4_action', 'as4_agreement', 'as4_mpc', 'as4_original_sender', 'as4_final_recipient', \
    'as4_extra_pmodes', 'as4_serviced_participants', 'as4_inbound_topic', 'as4_token_type', 'as4_username', \
    'as4_password', 'as4_signing_key', 'as4_signing_cert_chain', 'as4_decryption_key', 'as4_saml_assertion', \
    'as4_peer_signing_cert', 'as4_peer_encryption_cert', 'as4_trust_anchors',
_object_order['outgoing_as4'] = 'name', 'is_active', 'host', 'url_path', 'timeout', 'validate_tls', 'as4_profile', \
    'as4_from_party', 'as4_to_party', 'as4_service', 'as4_action', 'as4_agreement', 'as4_mpc', 'as4_original_sender', \
    'as4_final_recipient', 'as4_extra_pmodes', 'as4_use_discovery', 'as4_sml_domain', 'as4_retry_max_attempts', \
    'as4_retry_interval', 'as4_missing_receipt_after', 'as4_token_type', 'as4_username', 'as4_password', \
    'as4_signing_key', 'as4_signing_cert_chain', 'as4_decryption_key', 'as4_saml_assertion', \
    'as4_peer_signing_cert', 'as4_peer_encryption_cert', 'as4_trust_anchors',

_object_order['microsoft_cloud']          = 'name', 'is_active', 'client_id', 'tenant_id', 'scopes:list',
_object_order['microsoft_fabric']         = 'name', 'is_active', 'address', 'client_id', 'tenant_id',
_object_order['microsoft_power_automate'] = 'name', 'is_active', 'address', 'client_id', 'tenant_id', 'environment_id',

# Microsoft Teams connections run on the Microsoft 365 implementation, so their fields are ordered the same way.
_object_order['microsoft_teams'] = _object_order['microsoft_cloud']

_object_order['slack']      = 'name', 'is_active',
_object_order['confluence'] = 'name', 'is_active', 'address', 'username',
_object_order['jira']       = 'name', 'is_active', 'address', 'username',

_object_order['channel_ibm_mq'] = 'name', 'is_active', 'address', 'queue_manager', 'mq_channel_name', 'queue', 'service', \
    'username', 'remove_jms_headers', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
_object_order['outgoing_ibm_mq'] = 'name', 'is_active', 'address', 'queue_manager', 'mq_channel_name', 'queue', \
    'username', 'ssl', 'cipher_spec', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
_object_order['channel_amqp'] = 'name', 'is_active', 'address', 'queue', 'service', 'username', 'consumer_tag_prefix', \
    'data_format', 'pool_size', 'prefetch_count', 'ack_mode',
_object_order['outgoing_amqp'] = 'name', 'is_active', 'address', 'username', 'content_type', 'content_encoding', \
    'expiration', 'user_id', 'app_id', 'delivery_mode', 'priority', 'pool_size',

# Azure Service Bus connections run on the AMQP implementation, so their fields are ordered the same way.
_object_order['channel_azure_service_bus']  = _object_order['channel_amqp']
_object_order['outgoing_azure_service_bus'] = _object_order['outgoing_amqp']

_object_order['channel_kafka'] = 'name', 'is_active', 'address', 'topic', 'group_id', 'service',
_object_order['mcp_gateway']   = 'name', 'is_active', 'url_path', 'services:list', 'security_groups:list', \
    'is_audit_log_active', 'skills:list', 'session_ttl', 'invoke_timeout', 'validate_input', 'allow_agent_filters', \
    'max_response_size', 'size_cap_mode', 'min_size_threshold', 'characters_per_token', \
    'safeguards_strip_nulls', 'safeguards_collapse_whitespace', 'safeguards_strip_base64', \
    'safeguards_pii_enabled', 'safeguards_pii_lands:list', 'safeguards_pii_detectors:list', \
    'safeguards_pii_exclude:list', 'safeguards_pii_validate', 'safeguards_pii_stable_replacements', \
    'safeguards_secrets_enabled', \
    'safeguards_normalize_unicode', 'safeguards_unicode_mode', 'safeguards_sanitize_markup', \
    'safeguards_markup_mode', 'safeguards_url_policy_enabled', 'safeguards_url_allow_list:list', \
    'safeguards_url_mode',
_object_order['rule_engine_api']  = 'name', 'is_active', 'url_path', 'rulesets:list', 'security_groups:list',
_object_order['outgoing_graphql'] = 'name', 'is_active', 'address', 'security', 'default_query_timeout',
_object_order['outgoing_grpc']    = 'name', 'is_active', 'address', 'security', 'is_tls', 'tls_ca_certs_file', \
    'proto_path', 'stub_module', 'stub_class', 'ping_timeout', 'max_send_message_size', 'max_recv_message_size',
_object_order['outgoing_kafka']   = 'name', 'is_active', 'address', 'topic',

_object_order['channel_mllp']  = ('name',) + Channel_Enmasse_Names
_object_order['outgoing_mllp'] = ('name', 'address') + Outgoing_Names
_object_order['outgoing_fhir'] = ('name', 'address') + Outgoing_FHIR_Enmasse_Names

_object_order['email_imap'] = 'name', 'is_active', 'type', 'host', 'port', 'username', 'tenant_id', 'client_id', \
    'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_service', 'scheduler_invoke_with',
_object_order['email_smtp'] = 'name', 'is_active', 'host', 'port', 'username',

_object_order['odoo']           = 'name', 'is_active', 'host', 'port', 'database', 'user'
_object_order['elastic_search'] = 'name', 'is_active', 'address_list:list', 'username', 'timeout', \
    'is_tls_validation_enabled', 'tls_ca_certs_file', 'tls_cert_key_file'
_object_order['mongodb']        = 'name', 'is_active', 'server_list', 'username', 'auth_source', 'replica_set', \
    'app_name', 'pool_size_max', 'connect_timeout', 'server_select_timeout', 'is_tls_enabled', 'tls_ca_certs_file', \
    'tls_cert_key_file', 'is_tls_validation_enabled',
_object_order['sftp']           = 'name', 'is_active', 'address', 'username', 'private_key', 'strict_host_key_checking', \
    'ignore_host_key_changes', 'should_store_content', 'schedules:list',
_object_order['smb']            = 'name', 'is_active', 'host', 'port', 'username', 'should_store_content', 'schedules:list',

_object_order['pubsub_topic']        = 'name', 'description'
_object_order['pubsub_permission']   = 'security', 'pub', 'sub'
_object_order['pubsub_subscription'] = 'security', 'delivery_type', 'push_rest_endpoint', 'push_service', \
    'max_retry_time', 'topic_list'

_object_order['channel_openapi'] = 'name', 'is_active', 'url_path', 'rest_channel_list:list'

_object_order['alert_rules'] = 'type', 'is_active', 'consecutive_failures', 'error_rate', 'alert_threshold', \
    'max_latency', 'max_query_time', 'warning_latency', 'critical_latency', 'max_tool_call_time', \
    'max_call_time', 'health_alerts', 'auth_failures', 'warning_failures', 'critical_failures', \
    'test_transfers', 'arrival_overdue', 'overdue_multiplier', 'start_delay', 'certificate_warning', \
    'outstanding_backlog', 'feed_silence', 'use_llm',
_object_order['alert_notifications'] = 'slack_webhook', 'teams_webhook', 'webhook_url', 'email_connection', \
    'email_to', 'email_from', 'dashboard_url',

_object_order['audit_retention']  = 'name', 'retention_days', 'content_retention_days', 'archive_dir',
_object_order['audit_extraction'] = 'name', 'source', 'rules:list',

# ################################################################################################################################
# ################################################################################################################################

def get_top_level_order() -> 'strlist':

    # A copy, because callers extend it with their own dynamic sections.
    out = list(_top_level_order)
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_custom_object_order(items:'anylist') -> 'strlist':
    """ Builds the field order for a custom connector section - the name and the active flag
    come first and the declared fields follow, sorted by name across all the section's items.
    """
    field_names = set()

    for item in items:
        field_names.update(item)

    _ = field_names.discard('name')
    _ = field_names.discard('is_active')

    out = ['name', 'is_active']
    out.extend(sorted(field_names))

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_object_order(object_type:'str') -> 'strtuple':

    out = _object_order[object_type]
    return out

# ################################################################################################################################
# ################################################################################################################################
