# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import HTTP_SOAP, MISC

any_http = HTTP_SOAP.ACCEPT.ANY
any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

# ################################################################################################################################

def get_match_target(config, sep=MISC.SEPARATOR, any_http=any_http, any_internal=any_internal):
    http_accept = config.get('http_accept') or any_http
    http_accept = http_accept.replace('*', '{unusued}').replace('/', 'HTTP_SEP')
    return '%s%s%s%s%s' % (config['soap_action'], sep, http_accept, sep, config['url_path'])

# ################################################################################################################################
