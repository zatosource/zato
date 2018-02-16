# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from zato.server.service import List, Service

# ################################################################################################################################

class BaseSIO:
    """ A set of attributes common to all SSO services.
    """
    encrypt_secrets = False
    response_elem = None
    skip_empty_keys = True
    output_optional = ('status', List('sub_status'))

# ################################################################################################################################

class BaseService(Service):
    """ Base class for SSO sevices.
    """
    def before_handle(self):
        self.response.payload.sub_status = []


# ################################################################################################################################
