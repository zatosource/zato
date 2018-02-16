# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.sso import status_code
from zato.server.service import List, Service

# ################################################################################################################################

class SSOCtx(object):
    """ A set of attributes describing current SSO request.
    """
    __slots__ = ('input', 'sso_conf', 'remote_addr')

    def __init__(self, input, sso_conf, remote_addr):
        self.input = input
        self.sso_conf = sso_conf
        self.remote_addr = remote_addr

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

        # Assume that all calls always fail unless explicitly set to status_code.ok
        self.response.payload.status = status_code.error
        self.response.payload.sub_status = []

# ################################################################################################################################

    def after_handle(self):

        # If status is an error set in before_handle or _handle_sso and there is no sub_status
        # set yet, return generic information that user is not allowed to access this resource.
        if self.response.payload.status != status_code.ok and not self.response.payload.sub_status:
            self.response.payload.sub_status.append(status_code.auth.not_allowed)

# ################################################################################################################################

    def handle(self):
        sso_conf = self.server.sso_config

        # Basic checks, applicable to all requests
        if self.request.input.current_app not in sso_conf.apps.all:
            self.response.payload.status = status_code.error
            if sso_conf.main.inform_if_app_invalid:
                self.response.payload.sub_status.append(status_code.app_list.invalid)
            return

        # OK, we can proceed to the actual call now
        self._handle_sso(SSOCtx(self.request.input, sso_conf, self.wsgi_environ['zato.http.remote_addr']))

# ################################################################################################################################

    def _handle_sso(self, ctx):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################
