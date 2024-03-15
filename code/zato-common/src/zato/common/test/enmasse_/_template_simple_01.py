# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_simple_01 = """

security:
  - name: Test Basic Auth Simple
    username: "MyUser {test_suffix}"
    password: "MyPassword"
    type: basic_auth
    realm: "My Realm"

  - name: Test Basic Auth Simple.2
    username: "MyUser {test_suffix}.2"
    type: basic_auth
    realm: "My Realm"

channel_rest:

  - name: /test/enmasse1/simple/{test_suffix}
    service: pub.zato.ping
    url_path: /test/enmasse1/simple/{test_suffix}

outgoing_rest:

  - name: Outgoing Rest Enmasse {test_suffix}
    host: https://example.com
    url_path: /enmasse/simple/{test_suffix}

  - name: Outgoing Rest Enmasse {test_suffix}.2
    host: https://example.com
    url_path: /enmasse/simple/{test_suffix}.2
    data_format: form

outgoing_ldap:

  - name: Enmasse LDAP {test_suffix}
    username: 'CN=example.ldap,OU=example01,OU=Example,OU=Groups,DC=example,DC=corp'
    auth_type: NTLM
    server_list: 127.0.0.1:389
    password: {test_suffix}
"""

# ################################################################################################################################
# ################################################################################################################################
