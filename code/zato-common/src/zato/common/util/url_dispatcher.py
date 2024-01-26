# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.common.api import HTTP_SOAP, MISC

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

accept_any_http = HTTP_SOAP.ACCEPT.ANY
accept_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

method_any_internal = HTTP_SOAP.METHOD.ANY_INTERNAL

# ################################################################################################################################

def get_match_target(config, sep=MISC.SEPARATOR, accept_any_http=accept_any_http, accept_any_internal=accept_any_internal,
    method_any_internal=method_any_internal, http_methods_allowed_re=None):

    http_method = config.get('method') or config.get('http_method')
    if not http_method:
        http_method = http_methods_allowed_re

    http_accept = config.get('http_accept') or accept_any_http
    http_accept = http_accept.replace('*', '{}'.format(accept_any_internal)).replace('/', 'HTTP_SEP')

    # Extract variables needed to build the pattern
    soap_action = config['soap_action']
    url_path = config['url_path']

    # Support parentheses in URL paths
    url_path = url_path.replace('(', r'\(')
    url_path = url_path.replace(')', r'\)')

    # Build the pattern ..
    pattern = f'{soap_action}{sep}{http_method}{sep}{http_accept}{sep}{url_path}'

    # .. and return it to our caller
    return pattern

# ################################################################################################################################
