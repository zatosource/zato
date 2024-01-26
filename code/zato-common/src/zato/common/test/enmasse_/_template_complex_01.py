# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa

# ################################################################################################################################
# ################################################################################################################################

template_complex_01 = """

channel_plain_http:
  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/enmasse1/{test_suffix}
    params_pri: channel -params-over-msg
    sec_def: zato-no-security
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/enmasse1/{test_suffix}
  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/enmasse2/{test_suffix}
    params_pri: channel-params-over-msg
    sec_def: zato-no-security
    service: pub.zato.ping
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/enmasse2/{test_suffix}

zato_generic_connection:
    - address: ws://localhost:12345
      cache_expiry: 0
      has_auto_reconnect: true
      is_active: true
      is_channel: true
      is_internal: false
      is_outconn: false
      is_zato: true
      name: test.enmasse.{test_suffix}
      on_connect_service_name: pub.zato.ping
      on_message_service_name: pub.zato.ping
      pool_size: 1
      sec_use_rbac: false
      security_def: ZATO_NONE
      subscription_list:
      type_: outconn-wsx
      # These are taken from generic.connection.py -> extra_secret_keys
      oauth2_access_token: null
      consumer_key: null
      consumer_secret: null

def_sec:
  - name: "Test Basic Auth {test_suffix}"
    is_active: true
    type: basic_auth
    username: "MyUser {test_suffix}"
    password: "MyPassword"
    realm: "My Realm"

email_smtp:
  - name: test.email.smtp.complex-01.{smtp_config.name}.{test_suffix}
    host: {smtp_config.host}
    is_active: true
    is_debug: false
    mode: starttls
    port: 587
    timeout: 300
    username: {smtp_config.username}
    password: {smtp_config.password}
    ping_address: {smtp_config.ping_address}

web_socket:
    - address: "ws://0.0.0.0:10203/api/{test_suffix}"
      data_format: "json"
      id: 1
      is_active: true
      is_audit_log_received_active: false
      is_audit_log_sent_active: false
      is_internal: false
      max_bytes_per_message_received: null
      max_bytes_per_message_sent: null
      max_len_messages_received: null
      max_len_messages_sent: null
      name: "wsx.enmasse.{test_suffix}"
      new_token_wait_time: 5
      opaque1: '{{"max_bytes_per_message_sent":null,"max_bytes_per_message_received":null,"ping_interval":30,"extra_properties":null,"is_audit_log_received_active":false,"max_len_messages_received":null,"pings_missed_threshold":2,"max_len_messages_sent":null,"security":null,"is_audit_log_sent_active":false,"service_name":"pub.zato.ping"}}'
      ping_interval: 30
      pings_missed_threshold: 2
      sec_def: "zato-no-security"
      sec_type: null
      security_id: null
      service: "pub.zato.ping"
      service_name: "pub.zato.ping"
      token_ttl: 3600
"""

# ################################################################################################################################
# ################################################################################################################################
