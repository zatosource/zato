# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_complex_01 = """

quota_tier:

  - name: enmasse.quota.tier.1
    description: Enmasse quota tier one
    rules:
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            limit: 1000
            limit_unit: month
            disabled: false
            disallowed: false

  - name: enmasse.quota.tier.2
    description: Enmasse quota tier two
    rules:
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            limit: 50
            limit_unit: day
            disabled: false
            disallowed: false

security:

  - name: enmasse.basic_auth.1
    type: basic_auth
    username: enmasse.1
    password: Zato_Enmasse_Env.BasicAuth1
    rate_limiting:
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            limit: 500
            limit_unit: month
            disabled: false
            disallowed: false

  - name: enmasse.basic_auth.2
    type: basic_auth
    username: enmasse.2
    password: Zato_Enmasse_Env.BasicAuth2

  - name: enmasse.basic_auth.3
    type: basic_auth
    username: enmasse.3
    password: Zato_Enmasse_Env.BasicAuth3

  - name: enmasse.bearer_token.1
    username: enmasse.1
    password: Zato_Enmasse_Env.EnmasseBearerToken1
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: username
    client_secret_field: password
    grant_type: password
    data_format: form

  - name: enmasse.bearer_token.2
    username: enmasse.2
    password: abcdef123456
    type: bearer_token
    auth_endpoint: example.com
    extra_fields:
      - audience=example.com

  - name: enmasse.ntlm.1
    username: enmasse\\user
    password: abcdef123456
    type: ntlm

  - name: enmasse.mtls.1
    type: mtls
    cert_path: /opt/hot-deploy/ssl/enmasse-client-cert.pem
    key_path: /opt/hot-deploy/ssl/enmasse-client-key.pem
    ca_certs_path: /opt/hot-deploy/ssl/enmasse-remote-ca.pem

  - name: enmasse.mtls.2
    type: mtls
    client_cert_fingerprint: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
    client_cert_subject_dn: CN=enmasse.client,O=Enmasse,C=US

  - name: enmasse.spnego.1
    type: spnego
    principal: enmasse@EXAMPLE.COM
    keytab_path: /opt/hot-deploy/krb5/enmasse.keytab
    target_spn: HTTP@api.example.com

  - name: enmasse.wss.1
    username: enmasse.1
    password: abcdef123456
    type: wss
    mode: username_token
    use_digest: true

  - name: enmasse.wss.2
    username: enmasse.2
    password: abcdef123456
    type: wss
    mode: x509
    sign: true
    encrypt: true
    signing_key: /opt/zato/pki/enmasse-wss-signing-key-2.pem
    signing_certificate_chain: /opt/zato/pki/enmasse-wss-signing-chain-2.pem
    decryption_key: /opt/zato/pki/enmasse-wss-decryption-key-2.pem
    peer_certificate: /opt/zato/pki/enmasse-wss-peer-certificate-2.pem
    trust_anchors: /opt/zato/pki/enmasse-wss-trust-anchors-2.pem

  - name: enmasse.wss.3
    username: enmasse.3
    password: abcdef123456
    type: wss
    mode: saml
    issuer: https://idp.example.com/enmasse
    subject: enmasse.subject.3
    audience: https://api.example.com/enmasse
    sign: true
    signing_key: /opt/zato/pki/enmasse-wss-signing-key-3.pem
    signing_certificate_chain: /opt/zato/pki/enmasse-wss-signing-chain-3.pem

  - name: enmasse.wss.4
    username: enmasse.4
    password: abcdef123456
    type: wss
    is_active: false
    mode: username_token
    use_digest: false

  - name: enmasse.apikey.1
    type: apikey
    username: enmasse.1
    password: Zato_Enmasse_Env.EnmasseApiKey1

  - name: enmasse.apikey.2
    type: apikey
    username: enmasse.2
    password: Zato_Enmasse_Env.EnmasseApiKey2

groups:
  - name: enmasse.group.1
    members:
      - enmasse.basic_auth.1
      - enmasse.basic_auth.2
      - enmasse.apikey.1

  - name: enmasse.group.2
    members:
      - enmasse.apikey.1
      - enmasse.apikey.2
      - enmasse.basic_auth.1

channel_rest:

  - name: enmasse.channel.rest.1
    service: demo.ping
    url_path: /enmasse.rest.1

  - name: enmasse.channel.rest.2
    service: demo.ping
    url_path: /enmasse.rest.2
    data_format: json
    is_audit_log_active: false
    should_include_in_openapi: false
    rate_limiting:
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            limit: 1000
            limit_unit: day
            disabled: false
            disallowed: false
    response_cache:
      is_enabled: true
      ttl: 10
      ttl_unit: seconds
      is_shared_across_callers: true
      vary_by_headers:
        - Accept-Language
      ignored_query_parameters:
        - utm_source
        - utm_medium

  - name: enmasse.channel.rest.3
    service: demo.ping
    url_path: /enmasse.rest.3
    security: enmasse.basic_auth.1
    data_format: json
    rate_limiting:
      - cidr_list:
          - 10.0.0.0/8
          - 192.168.0.0/16
        time_range:
          - is_all_day: false
            time_from: '08:00'
            time_to: '17:00'
            limit: 100
            limit_unit: minute
            disabled: false
            disallowed: false
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            limit: 50
            limit_unit: hour
            disabled: true
            disallowed: true

  - name: enmasse.channel.rest.4
    service: demo.ping
    url_path: /enmasse.rest.4
    data_format: json
    groups:
      - enmasse.group.1
      - enmasse.group.2

  - name: enmasse.channel.rest.5
    service: demo.ping
    url_path: /enmasse.rest.5
    data_format: json
    is_deprecated: true
    deprecation_sunset: '2030-06-30'
    deprecation_successor: /enmasse.rest.4

  - name: enmasse.channel.rest.6
    service: demo.ping
    url_path: /enmasse.rest.6
    security: enmasse.mtls.2
    data_format: json

channel_soap:

  - name: enmasse.channel.soap.1
    service: demo.ping
    url_path: /enmasse.soap.1
    soap_action: urn:enmasse:soap:1
    soap_version: "1.1"

  - name: enmasse.channel.soap.2
    service: demo.ping
    url_path: /enmasse.soap.2
    security: enmasse.basic_auth.1
    soap_action: urn:enmasse:soap:2
    soap_version: "1.2"
    use_mtom: true
    is_audit_log_active: false
    groups:
      - enmasse.group.1
      - enmasse.group.2
    rate_limiting:
      - cidr_list:
          - 0.0.0.0/0
        time_range:
          - is_all_day: true
            limit: 1000
            limit_unit: day
            disabled: false
            disallowed: false
    response_cache:
      is_enabled: true
      ttl: 2
      ttl_unit: minutes
      cache_on_second_request: false

channel_as4:

  - name: enmasse.channel.as4.1
    url_path: /enmasse.as4.1
    as4_profile: peppol
    as4_to_party: enmasse-ap
    as4_serviced_participants: |-
      0192:991825827
      0088:7315458756324
    as4_inbound_topic: enmasse.as4.inbound

  - name: enmasse.channel.as4.2
    url_path: /enmasse.as4.2
    service: demo.ping
    security: enmasse.basic_auth.1
    as4_profile: edelivery1
    as4_from_party: enmasse-peer
    as4_to_party: enmasse-ap
    as4_service: enmasse:service:1
    as4_action: enmasse:action:1
    as4_extra_pmodes: |-
      enmasse:service:2|enmasse:action:2

outgoing_rest:

  - name: enmasse.outgoing.rest.1
    host: https://example.com:443
    url_path: /sso/{{type}}/hello/{{endpoint}}
    data_format: json
    timeout: 60

  - name: enmasse.outgoing.rest.2
    host: https://api.businesscentral.dynamics.com
    url_path: /abc/2
    security: enmasse.bearer_token.1
    timeout: 20

  - name: enmasse.outgoing.rest.3
    host: https://example.azurewebsites.net
    url_path: /abc/3
    data_format: json # No default value

  - name: enmasse.outgoing.rest.6
    host: https://mtls.example.com
    url_path: /abc/6
    security: enmasse.mtls.1
    data_format: json
    timeout: 30

  - name: enmasse.outgoing.rest.7
    host: https://spnego.example.com
    url_path: /abc/7
    security: enmasse.spnego.1
    data_format: json
    timeout: 30

  - name: enmasse.outgoing.rest.4
    host: https://example.com
    url_path: /abc/4
    ping_method: GET # Set explicitly because it defaults to GET already

  - name: enmasse.outgoing.rest.5
    host: https://example.com
    url_path: /abc/5
    ping_method: GET
    tls_verify: false # Default is True
    is_audit_log_active: false # Default is True

scheduler:

  - name: enmasse.scheduler.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 2
    is_active: True

  - name: enmasse.scheduler.2
    service: demo.ping
    job_type: interval_based
    start_date: '2025-02-19 12:00:00'
    minutes: 51

  - name: enmasse.scheduler.3
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-03 15:00:00'
    hours: 3

  - name: enmasse.scheduler.4
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-21 23:19:47'
    days: 10

channel_kafka:

  - name: enmasse.kafka.channel.1
    is_active: true
    address: localhost:9092
    topic: enmasse-test-topic
    group_id: enmasse-test-group
    service: enmasse.kafka.test.service

  - name: enmasse.kafka.channel.2
    is_active: false
    address: broker1:9093
    topic: enmasse-test-topic-2
    group_id: enmasse-test-group-2
    service: enmasse.kafka.test.service.2
    ssl: true
    ssl_ca_file: /path/to/ca.pem
    ssl_cert_file: /path/to/cert.pem
    ssl_key_file: /path/to/key.pem

mcp_gateway:

  - name: enmasse.mcp.gateway.1
    is_active: true
    is_audit_log_active: true
    url_path: /mcp/enmasse-1
    services: crm.get-customer,crm.update-customer
    security_groups:
      - enmasse.group.1

  - name: enmasse.mcp.gateway.2
    is_active: true
    url_path: /mcp/enmasse-2
    services: billing.get-invoice

channel_hl7_mllp:

  - name: enmasse.hl7.mllp.1
    service: enmasse.hl7.test.service
    should_validate: true
    msh9_message_type: ORU

  - name: enmasse.hl7.mllp.2
    service: enmasse.hl7.test.service.2
    msh9_message_type: ADT
    msh9_trigger_event: A01
    fix_off_by_one_field_index: true
    dedup_ttl_value: 30
    dedup_ttl_unit: minutes

  - name: enmasse.hl7.mllp.3
    service: enmasse.hl7.test.service.3
    is_default: true
    normalize_obx2_value_type: false
    allow_short_encoding_characters: false

outgoing_kafka:

  - name: enmasse.kafka.outgoing.1
    is_active: true
    address: localhost:9092
    topic: enmasse-test-out-topic

  - name: enmasse.kafka.outgoing.2
    is_active: true
    address: broker2:9093
    topic: enmasse-test-out-topic-2
    ssl: true
    ssl_ca_file: /path/to/ca.pem

outgoing_graphql:

  - name: enmasse.graphql.outgoing.1
    is_active: true
    address: https://graph.microsoft.com/v1.0
    default_query_timeout: 30

  - name: enmasse.graphql.outgoing.2
    is_active: true
    address: https://api.github.com/graphql
    default_query_timeout: 60

outgoing_grpc:

  - name: enmasse.grpc.outgoing.1
    is_active: true
    address: billing.example.com:50051
    proto_path: /opt/zato/proto/billing.proto
    ping_timeout: 20

  - name: enmasse.grpc.outgoing.2
    is_active: true
    address: inventory.example.com:50051
    is_tls: false
    stub_module: inventory_pb2_grpc
    stub_class: InventoryServiceStub

ldap:

  - name: enmasse.ldap.1
    username: 'CN=enmasse,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.1:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password

llm:

  - name: enmasse.llm.1
    model: gpt-4o-mini
    address: https://api.openai.com/v1
    secret: Zato_Enmasse_Env.Enmasse_LLM_API_Key
    timeout: 30
    max_tokens: 2048
    max_history_turns: 10
    chat_expiry: 3600

  - name: enmasse.llm.2
    model: Sonnet 5
    address: https://api.anthropic.com

odata:

  - name: enmasse.odata.1
    address: https://example.com/sap/opu/odata/sap/API_SALES_ORDER_SRV/
    odata_version: '2.0'
    auth_type: basic
    username: enmasse.odata.user.1
    needs_csrf_token: true
    secret: Zato_Enmasse_Env.Enmasse_OData_Secret

  - name: enmasse.odata.2
    address: https://example.com/v2.0/test-tenant/sandbox/api/v2.0/
    odata_version: '4.0'
    auth_type: oauth2
    token_url: https://login.example.com/test-tenant/oauth2/v2.0/token
    tenant_id: test-tenant
    client_id: enmasse-odata-client-1
    scopes: https://api.businesscentral.dynamics.com/.default
    client_secret: Zato_Enmasse_Env.Enmasse_OData_Client_Secret

sap:

  - name: enmasse.sap.1
    address: https://example.com/sap/opu/odata/sap/API_BUSINESS_PARTNER/
    odata_version: '2.0'
    auth_type: basic
    username: enmasse.sap.user.1
    needs_csrf_token: true
    secret: Zato_Enmasse_Env.Enmasse_SAP_Secret

  - name: enmasse.sap.2
    address: https://api4.successfactors.com/odata/v2/
    odata_version: '2.0'
    auth_type: oauth2
    token_url: https://api4.successfactors.com/oauth/token
    tenant_id: test-company
    client_id: enmasse-sap-client-1
    client_secret: Zato_Enmasse_Env.Enmasse_SAP_Client_Secret

sql:

  - name: enmasse.sql.1
    type: mysql
    host: 127.0.0.1
    port: 3306
    db_name: MYDB_01
    username: enmasse.1
    password: Zato_Enmasse_Env.SQL_Password_1
    ssl: true
    ssl_ca_file: /path/to/enmasse-sql-ca.crt
    ssl_cert_file: /path/to/enmasse-sql-client.crt
    ssl_key_file: /path/to/enmasse-sql-client.key
    ssl_verify: true

  - name: enmasse.sql.2
    type: oracle
    host: 10.152.81.199
    port: 1521
    db_name: MYDB_01
    username: enmasse.2
    password: Zato_Enmasse_Env.SQL_Password_2
    extra: connect_timeout=10
    pool_size: 10

  - name: enmasse.sql.3
    type: snowflake
    host: myorg-myaccount
    port: 443
    db_name: MYDB_01
    username: enmasse.3
    password: Zato_Enmasse_Env.SQL_Password_3
    extra: warehouse=COMPUTE_WH;role=ANALYST;schema=PUBLIC

  - name: enmasse.sql.4
    type: redshift
    host: examplecluster.abc123xyz789.us-west-2.redshift.amazonaws.com
    port: 5439
    db_name: MYDB_01
    username: enmasse.4
    password: Zato_Enmasse_Env.SQL_Password_4
    extra: sslmode=verify-ca

outgoing_soap:

  - name: enmasse.outgoing.soap.1
    host: https://example.com
    url_path: /SOAP
    security: enmasse.ntlm.1
    soap_action: urn:microsoft-dynamics-schemas/page/example:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 20
    is_audit_log_active: false

  - name: enmasse.outgoing.soap.2
    host: https://registry.example.com
    url_path: /iisb/services
    security: enmasse.wss.1
    soap_action: urn:cdc:iisb:2014:submitSingleMessage
    soap_version: "1.2"
    timeout: 30
    use_ws_addressing: true
    use_mtom: true
    tls_client_cert: /opt/zato/certs/client-cert.pem
    tls_client_key: /opt/zato/certs/client-key.pem
    body_credentials:
      - name: username
      - name: password
        position: 2

outgoing_as2:

  - name: enmasse.outgoing.as2.1
    as2_from: EnmasseRetail
    as2_to: PartnerCorp
    endpoint_url: https://as2.partnercorp.example.com/as2
    isa_qualifier: ZZ
    isa_id: PARTNERCORP
    gs_id: PARTNERCORP
    sign_algorithm: sha-256
    encryption_algorithm: aes-128-cbc
    compress: true
    mdn_mode: sync
    subject: Enmasse AS2 message
    http_timeout_seconds: 30

  - name: enmasse.outgoing.as2.2
    as2_from: EnmasseRetail
    as2_to: LegacyPartner
    endpoint_url: http://legacy.example.com:8080/as2
    sign: false
    encrypt: false
    mdn_mode: none
    verify_tls: false
    content_type: application/edifact
    unb_id: LEGACYPARTNER
    is_audit_log_active: false

outgoing_as4:

  - name: enmasse.outgoing.as4.1
    host: https://ap.example.com
    url_path: /as4
    timeout: 20
    as4_profile: peppol
    as4_from_party: enmasse-ap
    as4_original_sender: 0192:991825827
    as4_use_discovery: true
    as4_sml_domain: acc.edelivery.tech.ec.europa.eu

  - name: enmasse.outgoing.as4.2
    host: https://customs.example.com
    url_path: /domibus/services/msh
    timeout: 30
    validate_tls: false
    as4_profile: ics2
    as4_from_party: enmasse-eori
    as4_to_party: sti-taxud
    as4_service: eu.customs.ics2
    as4_action: IE3F26
    as4_mpc: urn:fdc:ec.europa.eu:2019:mpc

microsoft_cloud:

  - name: enmasse.cloud.microsoft365.1
    is_active: true
    client_id: 12345678-1234-1234-1234-123456789abc
    secret_value: Zato_Enmasse_Env.Microsoft365SecretValue
    scopes: Mail.Read Mail.Send
    tenant_id: 87654321-4321-4321-4321-cba987654321

microsoft_fabric:

  - name: enmasse.cloud.microsoft-fabric.1
    is_active: true
    address: https://api.fabric.microsoft.com/v1
    client_id: 34567890-3456-3456-3456-34567890abcd
    client_secret: Zato_Enmasse_Env.MicrosoftFabricClientSecret
    tenant_id: 87654321-6543-6543-6543-edcba9876543

microsoft_power_automate:

  - name: enmasse.cloud.microsoft-power-automate.1
    is_active: true
    address: https://api.flow.microsoft.com
    client_id: 23456789-2345-2345-2345-23456789abcd
    client_secret: Zato_Enmasse_Env.MicrosoftPowerAutomateClientSecret
    tenant_id: 98765432-5432-5432-5432-dcba98765432
    environment_id: Default-98765432-5432-5432-5432-dcba98765432

confluence:

  - name: enmasse.confluence.1
    address: https://example.atlassian.net
    username: api_user@example.com
    password: Zato_Enmasse_Env.ConfluenceAPIToken

email_imap:

  - name: enmasse.email.imap.1
    host: imap.example.com
    port: 993
    username: enmasse@example.com
    password: Zato_Enmasse_Env.IMAPPassword

  - name: enmasse.email.imap.2
    host: imap2.example.com
    port: 143
    username: enmasse2@example.com
    password: Zato_Enmasse_Env.IMAPPassword
    is_audit_log_active: false
    scheduler_run_every: 5
    scheduler_run_unit: minutes
    scheduler_start_date: '2030-01-01T00:00:00'
    scheduler_service: demo.ping
    scheduler_invoke_with: each_attachment

email_smtp:

  - name: enmasse.email.smtp.1
    host: smtp.example.com
    port: 587
    username: enmasse@example.com
    password: Zato_Enmasse_Env.SMTPPassword

jira:

  - name: enmasse.jira.1
    address: https://example.atlassian.net
    username: enmasse@example.com
    password: Zato_Enmasse_Env.JiraAPIToken

odoo:

  - name: enmasse.odoo.1
    host: odoo.example.com
    port: 8069
    user: admin
    password: Zato_Enmasse_Env.OdooPassword
    database: enmasse_db

elastic_search:

  - name: enmasse.elastic.1
    is_active: true
    address_list:
      - http://elasticsearch:9200
    timeout: 60

pubsub_topic:

  - name: enmasse.topic.1
    description: Optional description for topic 1

  - name: enmasse.topic.2
    description: Optional description for topic 2
    is_audit_log_active: false

  - name: enmasse.topic.3
    description: Optional description for topic 3

pubsub_permission:

  - security: enmasse.basic_auth.1
    pub:
      - enmasse.topic.1
      - enmasse.topic.2
    sub:
      - enmasse.topic.2
      - enmasse.topic.3

  - security: enmasse.basic_auth.2
    pub:
      - enmasse.topic.*
    sub:
      - enmasse.#

  - security: enmasse.basic_auth.3
    sub:
      - enmasse.topic.3

pubsub_subscription:

  - security: enmasse.basic_auth.1
    delivery_type: pull
    max_retry_time: 365d
    topic_list:
      - enmasse.topic.1
      - enmasse.topic.2

  - security: enmasse.basic_auth.2
    delivery_type: push
    push_rest_endpoint: enmasse.outgoing.rest.1
    max_retry_time: 48h
    topic_list:
      - enmasse.topic.1

  - security: enmasse.basic_auth.3
    delivery_type: push
    push_service: demo.echo
    max_retry_time: 30m
    topic_list:
      - enmasse.topic.3

channel_openapi:

  - name: enmasse.channel.openapi.1
    is_active: true
    url_path: /openapi/enmasse-1
    rest_channel_list:
      - enmasse.channel.rest.1
      - enmasse.channel.rest.2

  - name: enmasse.channel.openapi.2
    is_active: true
    url_path: /openapi/enmasse-2

"""

# ################################################################################################################################
# ################################################################################################################################
