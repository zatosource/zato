# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.views import django_url_reverse

# ################################################################################################################################

def get_client_html(item, security_id, cluster_id):
    """ Client is a string representation of a WebSockets channel, HTTP credentials or a service.
    """
    client = ''
    path_name = ''

    if security_id:
        path_name = 'security-basic-auth'
        id_value = security_id
        name = item.sec_name
        protocol = 'HTTP'

    elif item.ws_channel_id:
        path_name = 'channel-web-socket'
        id_value = item.ws_channel_id
        name = item.ws_channel_name
        protocol = 'WebSockets'

    elif getattr(item, 'service_id', None):
        path_name = 'service'
        id_value = item.service_id
        name = item.service_name
        protocol = 'Service'

    if path_name:
        path = django_url_reverse(path_name)
        client = '<span style="font-size:smaller">{}</span><br/><a href="{}?cluster={}&amp;highlight={}">{}</a>'.format(
            protocol, path, cluster_id, id_value, name)

    return client

# ################################################################################################################################

def get_endpoint_html(item, cluster_id, endpoint_id_attr='endpoint_id', endpoint_name_attr='endpoint_name'):
    id_value = getattr(item, endpoint_id_attr, None) or item[endpoint_id_attr]
    name = getattr(item, endpoint_name_attr, None) or item[endpoint_name_attr]

    path = django_url_reverse('pubsub-endpoint')
    endpoint = '<span style="font-size:smaller"><a href="{}?cluster={}&amp;highlight={}">{}</a>'.format(
        path, cluster_id, id_value, name)

    return endpoint

# ################################################################################################################################
