# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_complex_02 = """


scheduler:

  - cron_definition: null,
    days: "7",
    extra: "",
    hours: null,
    id: 3,
    is_active: true,
    job_type: "interval_based",
    minutes: null,
    name: "test.complex-02.{test_suffix}",
    repeats: null,
    seconds: null,
    service: "pub.zato.ping",
    service_id: 684,
    service_name: "pub.zato.ping",
    start_date: "2023-02-05 03:00:00",
    weeks: null

channel_plain_http:

  - cache_expiry: 0,
    cache_id: null,
    cache_name: null,
    cache_type: null,
    connection: "channel",
    content_encoding: "",
    content_type: "",
    data_encoding: "utf-8",
    data_format: "json",
    has_rbac: false,
    hl7_version: "hl7-v2",
    host: "",
    http_accept: "",
    id: 98,
    is_active: true,
    is_audit_log_received_active: false,
    is_audit_log_sent_active: false,
    is_internal: false,
    is_rate_limit_active: false,
    json_path: "",
    match_slash: true,
    max_bytes_per_message_received: "",
    max_bytes_per_message_sent: "",
    max_len_messages_received: "",
    max_len_messages_sent: "",
    merge_url_params_req: "True",
    method: "",
    name: "/test/api/complex-01/from-json/001/{test_suffix}",
    params_pri: "channel-params-over-msg",
    ping_method: "HEAD",
    pool_size: 20,
    rate_limit_check_parent_def: false,
    rate_limit_def: "",
    rate_limit_type: "",
    sec_def: "zato-no-security",
    sec_tls_ca_cert_id: null,
    sec_type: null,
    sec_use_rbac: false,
    security_id: null,
    security_name: null,
    serialization_type: "string",
    service: "pub.zato.ping",
    "service_id: 707,
    service_name: "pub.zato.ping",
    service_whitelist: [
        ""
    ],
    should_parse_on_input: false,
    should_return_errors: false,
    should_validate: false,
    soap_action: "",
    soap_version: null,
    timeout: "10",
    transport: "plain_http",
    url_params_pri: "qs-over-path",
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

  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/api/complex-01/002/{test_suffix}
    params_pri: channel-params-over-msg
    sec_def: zato-no-security
    service: pub.zato.ping
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/api/complex-01/002/{test_suffix}

  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/api/complex-01/003/{test_suffix}
    params_pri: channel-params-over-msg
    sec_def: zato-no-security
    service: pub.zato.ping
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/api/complex-01/003/{test_suffix}

  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/api/complex-01/004/{test_suffix}
    params_pri: channel-params-over-msg
    sec_def: zato-no-security
    service: pub.zato.ping
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/api/complex-01/004/{test_suffix}

def_sec:

  - name: Test.Complex-01.DefSec.BasicAuth.001.{test_suffix}
    realm: Test.Complex-01.DefSec.BasicAuth.001.{test_suffix}
    username: Test.Complex-01.DefSec.BasicAuth.001.{test_suffix}
    is_active: true
    type: basic_auth
    password: "{test_suffix}"

  - name: ide_publisher
    realm: ide_publisher
    username: ide_publisher
    is_active: true
    type: basic_auth
    password: "{test_suffix}"


outconn_sql:

  - db_name: {test_suffix}?charset=utf8
    engine: mysql+pymysql
    engine_display_name: MySQL
    host: {test_suffix}
    is_active: true
    name: Test.Complex-01.SQL.001.{test_suffix}
    pool_size: 10
    port: 3306
    username: {test_suffix}
    password: "{test_suffix}"

pubsub_endpoint:

  - endpoint_type: wsx
    is_active: true
    is_internal: false
    name: Test.Complex-01.PubSub.Endpoint.001.{test_suffix}
    role: pub-sub
    sec_def: zato-no-security
    security_id:
    service_id:
    topic_patterns:
        pub=/*

        sub=/*
    ws_channel_name: Test.Complex-01.WSX.Channel.001.{test_suffix}

  - endpoint_type: wsx
    is_active: true
    is_internal: false
    name: Test.Complex-01.PubSub.Endpoint.002.{test_suffix}
    role: pub-sub
    sec_def: zato-no-security
    security_id:
    service_id:
    topic_patterns:
        pub=/test/{test_suffix}/*

        sub=/test/{test_suffix}/*
    ws_channel_name: Test.Complex-01.WSX.Channel.002.{test_suffix}

web_socket:

  - address: ws://0.0.0.0:33100/{test_suffix}
    data_format: json
    is_active: true
    is_internal: false
    is_out: false
    name: Test.Complex-01.WSX.Channel.001.{test_suffix}
    new_token_wait_time: 60
    ping_interval: 30
    pings_missed_threshold: 4
    service: pub.zato.ping
    service_name: pub.zato.ping
    token_ttl: 3600
    sec_def: zato-no-security

  - address: ws://0.0.0.0:33101/{test_suffix}
    data_format: json
    is_active: true
    is_internal: false
    is_out: false
    name: Test.Complex-01.WSX.Channel.002.{test_suffix}
    new_token_wait_time: 60
    ping_interval: 30
    pings_missed_threshold: 4
    service: pub.zato.ping
    service_name: pub.zato.ping
    token_ttl: 3600
    sec_type: basic_auth
    sec_def: 'Test.Complex-01.DefSec.BasicAuth.001.{test_suffix}'

zato_cache_builtin:

  - cache_type: builtin
    extend_expiry_on_get: true
    extend_expiry_on_set: true
    is_active: true
    is_default: true
    max_item_size: 1000
    max_size: 10000
    name: default
    persistent_storage: sql
    sync_method: in-background

email_smtp:

  - host: example.com
    is_active: true
    is_debug: false
    mode: starttls
    name: Test.Complex-01.E-mail.SMTP.001.{test_suffix}
    opaque1: {{}}
    ping_address: no-reply@example.com
    port: 587
    timeout: 300
    username: "{test_suffix}"
    password: "{test_suffix}"

email_smtp:

  - host: example.com
    is_active: true
    is_debug: false
    mode: starttls
    name: Test.Complex-01.E-mail.SMTP.002.{test_suffix}
    opaque1: {{}}
    ping_address: no-reply@example.com
    port: 587
    timeout: 300
    username: "{test_suffix}"

outconn_redis:

  - db: 0
    host: localhost
    is_active: true
    name: default
    port: 8712
    redis_sentinels: ""
    redis_sentinels_master: ""
    use_redis_sentinels: false
    password: {test_suffix}"

"""

# ################################################################################################################################
# ################################################################################################################################
