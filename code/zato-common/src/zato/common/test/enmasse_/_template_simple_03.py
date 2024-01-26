# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################


template_simple_03 = """
security:

  - name: 'Test.Enmasse.Simple-03.Demo Security Definition.{test_suffix}'
    username: 'Demo Security Definition.{test_suffix}'
    type: basic_auth
    realm: 'Demo Security Definition'

outgoing_rest:

  - name: 'Test.Enmasse.Simple-03.Demo REST Connection.{test_suffix}'
    host: https://example.com
    url_path: /
    security_name: 'Test.Enmasse.Simple-03.Demo Security Definition.{test_suffix}'

  - name: 'Test.Enmasse.Simple-03.Outgoing Rest Enmasse abc-123-{test_suffix}.2'
    host: https://example.com
    url_path: /enmasse/simple/abc-123-{test_suffix}.2
    data_format: "json"

  - name: 'Test.Enmasse.Simple-03.Outgoing Rest Enmasse abc-123-{test_suffix}.3'
    host: https://example.com
    url_path: /enmasse/simple/abc-123-{test_suffix}.3
    data_format: form

  - name: 'Test.Enmasse.Simple-03.Outgoing Rest Enmasse abc-123-{test_suffix}.4'
    host: https://example.com
    url_path: /enmasse/simple/abc-123-{test_suffix}.4
    data_format: ""

pubsub_endpoint:

  - name: 'Test.Enmasse.Simple-03.Demo Endpoint.{test_suffix}'
    endpoint_type: rest
    security_name: 'Test.Enmasse.Simple-03.Demo Security Definition.{test_suffix}'
    topic_patterns: |-
      pub=/*
      sub=/*

pubsub_subscription:

  - name: Test.Enmasse.Simple-03.Subscription.000000001.{test_suffix}
    endpoint_name: 'Test.Enmasse.Simple-03.Demo Endpoint.{test_suffix}'
    endpoint_type: rest
    delivery_method: notify
    rest_connection: 'Test.Enmasse.Simple-03.Demo REST Connection.{test_suffix}'
    rest_method: POST
    topic_list:
      - /demo/enmasse/simple-03/topic-01.{test_suffix}
      - /demo/enmasse/simple-03/topic-02.{test_suffix}

pubsub_topic:

  - name: /demo/enmasse/simple-03/topic-01.{test_suffix}
  - name: /demo/enmasse/simple-03/topic-02.{test_suffix}
"""

# ################################################################################################################################
# ################################################################################################################################
