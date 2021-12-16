# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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

    return '%s%s%s%s%s%s%s' % (config['soap_action'], sep, http_method, sep, http_accept, sep, config['url_path'])

# ################################################################################################################################
