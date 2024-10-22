# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################


template_simple_06 = """
pubsub_endpoint:

  - name: 'Test.Enmasse.Simple-06.Demo Endpoint'
    endpoint_type: service
    service_name: 'pub.helpers.input-logger'
    topic_patterns: |-
      pub=/*
      sub=/*

pubsub_subscription:

  - name: Test.Enmasse.Simple-06.Subscription.000000001.{test_suffix}
    endpoint_name: 'Test.Enmasse.Simple-06.Demo Endpoint'
    endpoint_type: service
    delivery_method: notify
    topic_list:
      - /demo/enmasse/simple-06/topic-01.{test_suffix}
      - /demo/enmasse/simple-06/topic-02.{test_suffix}

pubsub_topic:

  - name: /demo/enmasse/simple-06/topic-01.{test_suffix}
  - name: /demo/enmasse/simple-06/topic-02.{test_suffix}

zato_generic_connection:

  - name: '{test_suffix}.Microsoft365'
    type_: cloud-microsoft-365
    tenant_id: {test_suffix} - My Teant ID
    client_id: {test_suffix} - My Client ID
    secret: "{test_suffix} - My Secret"
    scopes: https://graph.microsoft.com/.default
"""

# ################################################################################################################################
# ################################################################################################################################
