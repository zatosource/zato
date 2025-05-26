# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_simple_01 = """

security:
  - name: enmasse.basic_auth.1
    username: enmasse.basic_auth.1
    password: abcdef.123456
    type: basic_auth
    realm: enmasse

  - name: enmasse.basic_auth.2
    username: enmasse.basic_auth.2
    password: Zato_Enmasse_Env.My_Password
    type: basic_auth
    realm: enmasse

channel_rest:

  - name: enmasse.channel_rest.1
    service: demo.ping
    url_path: /enmasse.channel_rest.1

  - name: enmasse.channel_rest.2
    service: demo.ping
    url_path: /enmasse.channel_rest.2
    security: enmasse.basic_auth.2

outgoing_rest:

  - name: enmasse.outgoing_rest.1
    host: https://example.com
    url_path: /enmasse.outgoing_rest.1

  - name: enmasse.outgoing_rest.2
    host: https://example.com
    url_path: /enmasse.outgoing_rest.2
    data_format: json

  - name: enmasse.outgoing_rest.3
    host: https://example.com
    url_path: /enmasse.outgoing_rest.3
    data_format: form

  - name: enmasse.outgoing_rest.4
    host: https://example.com
    url_path: /enmasse.outgoing_rest.4
    data_format: json
    security: enmasse.basic_auth.1

outgoing_ldap:

  - name: enmasse.ldap.1
    server_list: 127.0.0.1:389
    username: 'CN=example.ldap,OU=example01,OU=Example,OU=Groups,DC=example,DC=corp'
    password: Zato_Enmasse_Env.LDAP_Password
    auth_type: NTLM
"""

# ################################################################################################################################
# ################################################################################################################################
