# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

def get_proxy_config(config):
    """ Returns HTTP/HTTPS proxy configuration from a given object's configuration data if any was configured.
    """
    # Proxy configuration, if any
    if config.http_proxy_list or config.https_proxy_list:
        proxy_config = {}

        # For now, all proxies we produce are not lists but a single one,
        # which can be revised if needed in the future.

        if config.http_proxy_list:
            proxy_config['http'] = config.http_proxy_list.strip()

        if config.https_proxy_list:
            proxy_config['https'] = config.https_proxy_list.strip()

        return proxy_config

# ################################################################################################################################
