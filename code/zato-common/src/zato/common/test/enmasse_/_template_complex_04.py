# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_complex_04 = """

zato_cache_builtin:

  - cache_id: 1
    cache_type: "builtin"
    current_size: 11
    extend_expiry_on_get: true
    extend_expiry_on_set: true
    id: 1
    is_active: true
    is_default: true
    max_item_size: 10000
    max_size: 10000
    name: default
    opaque: null
    persistent_storage: "sql"
    sync_method: "in-background"

  - cache_id: 1
    cache_type: "builtin"
    current_size: 11
    extend_expiry_on_get: true
    extend_expiry_on_set: true
    id: 1
    is_active: true
    is_default: false
    max_item_size: 10000
    max_size: 10000
    name: "test.complex-01.from-json.002.{test_suffix}"
    opaque: "{{}}"
    persistent_storage: "no-persistent-storage"
    sync_method: "in-background"

channel_plain_http:

  - cache_expiry: 0
    cache_id: null
    cache_name: null
    cache_type: null
    connection: "channel"
    content_encoding: ""
    content_type: ""
    data_encoding: "utf-8"
    data_format: "json"
    has_rbac: false
    hl7_version: "hl7-v2"
    host: ""
    http_accept: ""
    id: 98
    is_active: true
    is_audit_log_received_active: false
    is_audit_log_sent_active: false
    is_internal: false
    is_rate_limit_active: false
    json_path: ""
    match_slash: true
    max_bytes_per_message_received: ""
    max_bytes_per_message_sent: ""
    max_len_messages_received: ""
    max_len_messages_sent: ""
    merge_url_params_req: "True"
    method: ""
    name: "/test/api/complex-01/from-json/001/{test_suffix}"
    params_pri: "channel-params-over-msg"
    ping_method: "HEAD"
    pool_size: 20
    rate_limit_check_parent_def: false
    rate_limit_def: ""
    rate_limit_type: ""
    sec_def: "zato-no-security"
    sec_tls_ca_cert_id: null
    sec_type: null
    sec_use_rbac: false
    security_id: null
    security_name: null
    serialization_type: "string"
    service: "pub.zato.ping"
    service_id: 707
    service_name: "pub.zato.ping"
    service_whitelist: [
        ""
    ]
    should_parse_on_input: false
    should_return_errors: false
    should_validate: false
    soap_action: ""
    soap_version: null
    timeout: "10"
    transport: "plain_http"
    url_params_pri: "qs-over-path"
    url_path: "/test/api/complex-01/from-json/001/{test_suffix}"

  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/api/complex-01/001/{test_suffix}
    params_pri: channel-params-over-msg
    sec_def: zato-no-security
    service: pub.zato.ping
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/api/complex-01/001/{test_suffix}


"""

# ################################################################################################################################
# ################################################################################################################################
