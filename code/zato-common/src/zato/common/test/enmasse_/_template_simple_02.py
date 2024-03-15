# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################


template_simple_02 = """
security:

  - name: 'Test.Unittest.Test Basic.{test_suffix}'
    username: 'Test.Unittest.Basic.{test_suffix}'
    type: basic_auth
    realm: 'My Realm'

  - name: Test.Unittest.APIKey.{test_suffix}
    username: Test.Unittest.APIKey.{test_suffix}
    type: apikey

  - name: Test.Unittest.NTLM.{test_suffix}
    username: domain\\Test.Unittest.NTLM.{test_suffix}
    type: ntlm

  - name: Test.Unittest.BearerToken.{test_suffix}
    username: Test.Unittest.BearerToken.{test_suffix}
    type: bearer_token
    auth_endpoint: https://example.com
    client_id_field: client_id
    client_secret_field: client_secret
    grant_type: client_credentials
    extra_fields:
      - audience=https://example.com

pubsub_endpoint:

  - name: 'Test.Unittest.My Endpoint.{test_suffix}'
    endpoint_type: rest
    security_name: 'Test.Unittest.Test Basic.{test_suffix}'
    topic_patterns: |-
      pub=/*
      sub=/*

pubsub_topic:

  - name: /topic/01.{test_suffix}
  - name: /topic/02.{test_suffix}
"""

# ################################################################################################################################
# ################################################################################################################################
