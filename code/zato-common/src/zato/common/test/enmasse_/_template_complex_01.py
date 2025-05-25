# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_complex_01 = """

security:

  - name: enmasse.basic_auth.1
    username: pubapi
    password: abcdef123456
    type: basic_auth
    realm: 'enmasse'

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
    username: enmasse\user
    password: abcdef123456
    type: ntlm

  - name: enmasse.apikey.1
    type: apikey
    username: enmasse
    password: Zato_Enmasse_Env.EnmasseApiKey1

channel_rest:

  - name: enmasse.channel.rest.1
    service: demo.ping
    url_path: /enmasse.rest.1

  - name: enmasse.channel.rest.2
    service: demo.ping
    url_path: /enmasse.rest.2
    data_format: json

  - name: enmasse.channel.rest.3
    service: demo.ping
    security_name: enmasse.basic_auth.1
    data_format: json

outgoing_rest:

  - name: enmasse.outgoing.rest.1
    host: https://example.com:443
    url_path: /sso/{type}/hello/{endpoint}
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

  - name: enmasse.outgoing.rest.4
    host: https://example.com
    url_path: /abc/4
    ping_method: GET # Set explicitly because it defaults to GET already

  - name: enmasse.outgoing.rest.5
    host: https://example.com
    url_path: /abc/5
    ping_method: GET
    tls_verify: false # Default is True

scheduler:

  - name: enmasse.scheduler.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-11 11:23:52'
    seconds: 2
    is_active: Zato_Enmasse_Env.Enmasse_Scheduler_Is_Active

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

ldap:

  - name: enmasse.ldap.1
    username: 'CN=enmasse,OU=testing,OU=Servers,DC=enmasse'
    auth_type: NTLM
    server_list: 127.0.0.1:389
    password: Zato_Enmasse_Env.Enmasse_LDAP_Password

sql:

  - name: enmasse.sql.1
    type: mysql
    host: 127.0.0.1
    port: 3306
    db_name: MYDB_01
    username: enmasse.1
    password: Zato_Enmasse_Env.SQL_Password_1

  - name: enmasse.sql.2
    type: oracle
    host: 10.152.81.199
    port: 1521
    db_name: MYDB_01
    username: enmasse.2
    password: Zato_Enmasse_Env.SQL_Password_2
    extra: connect_timeout=10
    pool_size: 10

outgoing_soap:

  - name: enmasse.outgoing.soap.1
    host: https://example.com
    url_path: /SOAP
    security: enmasse.ntlm.1
    soap_action: urn:microsoft-dynamics-schemas/page/example:Create
    soap_version: "1.1"
    tls_verify: false
    timeout: 20
"""

# ################################################################################################################################
# ################################################################################################################################
