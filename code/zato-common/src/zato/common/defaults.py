# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A place for storing all the defaults values.

web_admin_host = '0.0.0.0'
web_admin_port = 8182

http_plain_server_port = 17010

default_cluster_id = 1

# Fields whose values must be masked in logs and query strings
secret_fields_exact = {'auth_data', 'auth_token', 'password', 'secret_key', 'tls_pem_passphrase', 'token', 'api_key', 'apiKey', 'xApiKey'}
secret_fields_prefix:'set[str]' = set()
secret_fields_suffix:'set[str]' = set()
