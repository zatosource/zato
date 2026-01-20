# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_rest_gateway = """

channel_rest:

  - name: enmasse.channel.rest.gateway.1
    service: demo.ping
    url_path: /enmasse.rest.gateway.1
    gateway_service_list:
      - demo.ping
      - api.my-service

  - name: enmasse.channel.rest.gateway.2
    service: demo.ping
    url_path: /enmasse.rest.gateway.2

"""

# ################################################################################################################################
# ################################################################################################################################
