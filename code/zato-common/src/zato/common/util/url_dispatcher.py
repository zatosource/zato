# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import MISC

# ################################################################################################################################

def get_match_target(config, sep=MISC.SEPARATOR, any_=MISC.HTTP_SOAP_ACCEPT_ANY):
    http_accept = config.get('http_accept') or any_
    if http_accept == any_:
        http_accept = 'any'
    return '%s%s%s%s%s' % (config['soap_action'], sep, http_accept, sep, config['url_path'])

# ################################################################################################################################
