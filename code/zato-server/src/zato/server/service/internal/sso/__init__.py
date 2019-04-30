# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import FORBIDDEN
from traceback import format_exc

# ipaddress
from ipaddress import ip_address

# Zato
from zato.common import NO_REMOTE_ADDRESS
from zato.server.service import List, Service
from zato.sso import status_code, ValidationError

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
    output_optional = ('cid', 'status', List('sub_status'))

# ################################################################################################################################

class BaseService(Service):
    """ Base class for SSO sevices.
    """
    class SimpleIO(BaseSIO):
        pass

# ################################################################################################################################

    def _set_response_ok(self):
        self.response.payload.status = status_code.ok

# ################################################################################################################################

    def _set_response_error(self, sub_status=status_code.auth.not_allowed, status=status_code.error):
        self.response.status_code = FORBIDDEN
        self.response.payload.status = status

        # BaseRESTService._handle_sso may have set it already so we need an if check
        if not self.response.payload.sub_status:
            self.response.payload.sub_status.append(sub_status)

# ################################################################################################################################

    def before_handle(self):

        # Assume that all calls always fail unless explicitly set to status_code.ok
        self.response.payload.status = status_code.error
        self.response.payload.sub_status = []

# ################################################################################################################################

    def after_handle(self):

        # If status is an error set in before_handle or _handle_sso and there is no sub_status
        # set yet, return generic information that user is not allowed to access this resource.
        if self.response.payload.status != status_code.ok and not self.response.payload.sub_status:
            self.response.payload.sub_status = status_code.auth.not_allowed

        # Always returned if any response is produced at all
        self.response.payload.cid = self.cid

# ################################################################################################################################

    def handle(self):
        sso_conf = self.server.sso_config

        # Basic checks, applicable to all requests
        if self.request.input.current_app not in sso_conf.apps.all:
            self.response.payload.status = status_code.error
            if sso_conf.apps.inform_if_app_invalid:
                self.response.payload.sub_status.append(status_code.app_list.invalid)
            return

        # Parse remote_addr into a series of IP address objects, possibly more than one,
        # depending on how many were sent in the request.
        remote_addr = self.wsgi_environ['zato.http.remote_addr']
        if remote_addr == NO_REMOTE_ADDRESS:
            remote_addr = None
        else:
            remote_addr = [elem.strip() for elem in remote_addr.strip().split(',')]
            remote_addr =  [ip_address(elem) for elem in remote_addr]

        # OK, we can proceed to the actual call now
        self._call_sso_api(self._handle_sso, 'Could not call service', ctx=SSOCtx(self.request.input, sso_conf, remote_addr))

# ################################################################################################################################

    def _call_sso_api(self, func, log_prefix, **kwargs):

        try:
            # Call the business functionality
            out = func(**kwargs)
        except ValidationError as e:

            # Log only if needed (likely WARN will be always enabled but still, it's better to check it first)
            if self.server.is_enabled_for_warn:
                kwargs['cid'] = self.cid
                log_msg = log_prefix.format(**kwargs)
                log_msg = log_msg + ', cid:`{}`, e:`{}`'.format(self.cid, format_exc())
                self.logger.warn(log_msg)

            # Make sure we don't return specific status codes if we are not allowed to
            if e.return_status:
                self._set_response_error(e.sub_status, e.status)
            else:
                self._set_response_error()

        # All went fine, we can set status OK and return business data
        else:
            self._set_response_ok()
            return out

# ################################################################################################################################

    def _handle_sso(self, ctx):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

class BaseRESTService(BaseService):
    """ Base class for services reacting to specific HTTP verbs.
    """
    def _handle_sso(self, ctx):
        http_verb = self.wsgi_environ['REQUEST_METHOD']

        try:
            getattr(self, '_handle_sso_{}'.format(http_verb))(ctx)
        except Exception:
            self.response.payload.status = status_code.error
            self.response.payload.sub_status = [status_code.auth.not_allowed]
            raise
        else:
            self.response.payload.status = status_code.ok
        finally:
            self.response.payload.cid = self.cid

# ################################################################################################################################
