# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################


template_simple_05 = """
security:

  - name: 'Test.Enmasse.Simple-05.Demo Security Definition.{test_suffix}'
    username: 'Demo Security Definition.{test_suffix}'
    type: basic_auth
    realm: 'Demo Security Definition'

pubsub_endpoint:

  - name: 'Test.Enmasse.Simple-05.Demo Endpoint'
    endpoint_type: rest
    security_name: 'Test.Enmasse.Simple-05.Demo Security Definition.{test_suffix}'
    topic_patterns: |-
      pub=/*
      sub=/*

outgoing_rest:

  - name: 'Test.Enmasse.Simple-05.Demo REST Connection.{test_suffix}'
    host: https://example.com
    url_path: /
    security_name: 'Test.Enmasse.Simple-05.Demo Security Definition.{test_suffix}'

pubsub_subscription:

  - name: Test.Enmasse.Simple-05.Subscription.000000001.{test_suffix}
    endpoint_name: 'Test.Enmasse.Simple-05.Demo Endpoint'
    endpoint_type: rest
    delivery_method: notify
    rest_connection: 'Test.Enmasse.Simple-05.Demo REST Connection.{test_suffix}'
    rest_method: POST
    topic_list:
      - /demo/enmasse/simple-05/topic-01.{test_suffix}
      - /demo/enmasse/simple-05/topic-02.{test_suffix}

pubsub_topic:

  - name: /demo/enmasse/simple-05/topic-01.{test_suffix}
  - name: /demo/enmasse/simple-05/topic-02.{test_suffix}
"""

# ################################################################################################################################
# ################################################################################################################################
