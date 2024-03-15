# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_complex_05 = """

zato_generic_connection:

  - address: null
    app_name: tagging
    auth_mechanism: SCRAM-SHA-256
    auth_source: admin
    cache_expiry: null
    cache_id: null
    client_id: null
    cluster_id: 1
    compressor_list:
    conn_def_id: null
    connect_timeout: 10
    consumer_key: null
    consumer_secret: null
    data_encoding: null
    data_format: null
    document_class:
    end_seq: null
    extra: null
    hb_frequency: 10
    hl7_version: null
    id: 1
    is_active: true
    is_audit_log_received_active: false
    is_audit_log_sent_active: false
    is_channel: false
    is_internal: false
    is_outconn: true
    is_rate_limit_active: false
    is_tls_enabled: false
    is_tls_match_hostname_enabled: true
    is_tz_aware: false
    is_write_fsync_enabled: true
    is_write_journal_enabled: false
    json_path: null
    logging_level: null
    max_bytes_per_message_received: null
    max_bytes_per_message_sent: null
    max_idle_time: 600
    max_len_messages_received: null
    max_len_messages_sent: null
    max_msg_size: null
    max_wait_time: null
    name: test.mongodb.complex-05.{test_suffix}
    oauth2_access_token: null
    oauth_def: null
    pool_size: 1
    pool_size_max: 10
    port: null
    rate_limit_check_parent_def: null
    rate_limit_def: null
    rate_limit_type: null
    read_buffer_size: null
    read_pref_max_stale: -1
    read_pref_tag_list:
    read_pref_type: primary
    recv_timeout: null
    replica_set:
    sec_tls_ca_cert_id: null
    sec_use_rbac: false
    secret: "{test_suffix}"
    secret_type: null
    security_id: null
    server_list: localhost
    server_select_timeout: 5
    should_log_messages: false
    should_retry_write: false
    socket_timeout: 30
    start_seq: null
    tenant_id: null
    timeout: null
    tls_ca_certs_file:
    tls_cert_file:
    tls_ciphers:
    tls_crl_file:
    tls_pem_passphrase: null
    tls_private_key_file:
    tls_validate: CERT_REQUIRED
    tls_version: SSLv23
    type_: outconn-mongodb
    username: {test_suffix}
    username_type: null
    version: null
    wait_queue_timeout: 10
    write_timeout: 5
    write_to_replica: true
    zlib_level: -1

  - address: ws://test.complex-05.{test_suffix}
    cache_expiry: 0
    cache_id: null
    client_id: null
    cluster_id: 1
    conn_def_id: null
    consumer_key: null
    consumer_secret: null
    data_encoding: null
    data_format: null
    end_seq: null
    extra: null
    has_auto_reconnect: true
    hl7_version: null
    id: 2
    is_active: true
    is_audit_log_received_active: false
    is_audit_log_sent_active: false
    is_channel: false
    is_internal: false
    is_outconn: true
    is_rate_limit_active: false
    is_zato: true
    json_path: null
    logging_level: null
    max_bytes_per_message_received: null
    max_bytes_per_message_sent: null
    max_len_messages_received: null
    max_len_messages_sent: null
    max_msg_size: null
    max_wait_time: null
    name: test.wsx.outconn.complex-05.{test_suffix}
    oauth2_access_token: null
    oauth_def: null
    on_close_service_name: helpers.pubsub.hook
    on_connect_service_name: helpers.pubsub.hook
    on_message_service_name: helpers.pubsub.hook
    pool_size: 1
    port: null
    rate_limit_check_parent_def: null
    rate_limit_def: null
    rate_limit_type: null
    read_buffer_size: null
    recv_timeout: null
    sec_tls_ca_cert_id: null
    sec_use_rbac: false
    secret: null
    secret_type: null
    security_def: ZATO_NONE
    security_id: null
    should_log_messages: false
    start_seq: null
    subscription_list:
    tenant_id: null
    timeout: null
    type_: outconn-wsx
    username: null
    username_type: null
    version: null
"""

# ################################################################################################################################
# ################################################################################################################################
