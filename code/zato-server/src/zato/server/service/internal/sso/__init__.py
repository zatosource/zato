# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from http.client import FORBIDDEN
from traceback import format_exc

# Zato
from zato.common.api import NO_REMOTE_ADDRESS
from zato.server.service import List, Service
from zato.sso import status_code, ValidationError
from zato.sso.common import SSOCtx
from zato.sso.model import RequestCtx

# ################################################################################################################################

if 0:
    from zato.common.typing_ import type_
    from zato.common.crypto.totp_ import TOTPManager
    from zato.common.test.config import TestConfig

    type_ = type_
    TestConfig = TestConfig
    TOTPManager = TOTPManager

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
            if isinstance(sub_status, list):
                self.response.payload.sub_status.extend(sub_status)
            else:
                self.response.payload.sub_status.append(sub_status)

# ################################################################################################################################

    def before_handle(self):

        # Assume that all calls always fail unless explicitly set to status_code.ok
        self.response.payload.status = status_code.error
        self.response.payload.sub_status = []

        # Will be set to True if the default value of status_code.ok should not be returned
        self.environ['status_changed'] = False

# ################################################################################################################################

    def after_handle(self):

        # If status is an error set in before_handle or _handle_sso and there is no sub_status
        # set yet, return generic information that user is not allowed to access this resource.
        status     = self.response.payload.status
        sub_status = self.response.payload.sub_status

        if status != status_code.ok and (not sub_status):
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

        # OK, we can proceed to the actual call now
        sso_ctx = SSOCtx(
            self.cid,
            remote_addr,
            self.wsgi_environ.get('HTTP_USER_AGENT'),
            self.request.input,
            sso_conf
        )
        _ = self._call_sso_api(self._handle_sso, 'Could not call service', ctx=sso_ctx)

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
                self.logger.warning(log_msg)

            # Make sure we don't return specific status codes if we are not allowed to
            if e.return_status:
                self._set_response_error(e.sub_status, e.status)
            else:
                self._set_response_error()

        # All went fine, we can set status OK and return business data
        else:
            if not self.environ.get('status_changed'):
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
        except Exception as e:
            self.response.payload.status = status_code.error
            sub_status = e.sub_status if isinstance(e, ValidationError) else [status_code.auth.not_allowed]
            self.response.payload.sub_status = sub_status
            raise
        else:
            self.response.payload.status = status_code.ok
        finally:
            self.response.payload.cid = self.cid

# ################################################################################################################################

class SSOTestService(Service):

    def handle(self):

        # Zato
        from zato.common.crypto.totp_ import TOTPManager
        from zato.common.test.config import TestConfig

        # Run the test suite
        self._test_login(TestConfig, TOTPManager)
        self._test_get_user_attrs(TestConfig, TOTPManager)
        self._test_validate_totp_code(TestConfig, TOTPManager)

# ################################################################################################################################

    def _test_login(self, config, totp_manager):
        # type: (TestConfig, type_[TOTPManager]) -> None

        # We want to ensure that both str and bytes passwords can be used
        password1 = config.super_user_password
        password2 = config.super_user_password.encode('utf8')

        self.logger.info('SSO login with password1 (str)')

        # Check the str password
        _ = self.sso.user.login(
            self.cid, config.super_user_name, password1, config.current_app,
            '127.0.0.1', 'Zato', totp_code=totp_manager.get_current_totp_code(config.super_user_totp_key))

        self.logger.info('SSO login with password2 (bytes)')

        # Check the bytes password
        _ = self.sso.user.login(
            self.cid, config.super_user_name, password2, config.current_app,
            '127.0.0.1', 'Zato', totp_code=totp_manager.get_current_totp_code(config.super_user_totp_key))

# ################################################################################################################################

    def _test_get_user_attrs(self, config, totp_manager):
        # type: (TestConfig, type_[TOTPManager]) -> None

        # Zato
        from zato.common.test import rand_string
        from zato.sso.user import super_user_attrs

        all_attrs = deepcopy(super_user_attrs)
        all_attrs['totp_key'] = None

        remote_addr = '127.0.0.1'
        user_agent = 'My User Agent'

        username = 'test.attrs.{}'.format(rand_string())
        password = rand_string()
        display_name = 'My Display Name'
        totp_label   = 'My TOTP Label'

        # Attributes that can be None for this particular newly created user
        # even if return_all_attrs=True
        none_allowed = {'email', 'first_name', 'last_name', 'locked_by',
            'locked_time', 'middle_name', 'rate_limit_def', 'status'}

        data = {
          'username': username,
          'password': password,
          'display_name': display_name,
          'totp_label': totp_label
        }

        # Log in the super user first ..
        super_user_session = self.sso.user.login(
            self.cid, config.super_user_name, config.super_user_password, config.current_app,
            remote_addr, 'Zato', totp_code=totp_manager.get_current_totp_code(config.super_user_totp_key))

        # .. create the new user ..
        _ = self.sso.user.create_user(self.cid, data, ust=super_user_session.ust,
            current_app=config.current_app, auto_approve=True)

        # .. log the account in ..
        user_session = self.sso.user.login(self.cid, username, password, config.current_app, remote_addr, user_agent)

        # .. get the user back, but without requiring for all the attributes to be returned ..
        sso_user_regular_attrs = self.sso.user.get_current_user(self.cid, user_session.ust,
            config.current_app, remote_addr, return_all_attrs=False)

        # .. make sure that none of the super-user-only attributes were returned ..
        for name in all_attrs:
            value = getattr(sso_user_regular_attrs, name)
            if value:
                raise Exception('Value of {} should not be given'.format(name))

        # .. however, regular attrs should be still available

        if sso_user_regular_attrs.is_current_super_user is not False:
            raise Exception('Value of sso_user_regular_attrs.is_current_super_user should be False')

        if sso_user_regular_attrs.username != username:
            raise Exception('Value of sso_user_regular_attrs.username should be equal to `{}` instead of `{}`'.format(
                username, sso_user_regular_attrs.username))

        if sso_user_regular_attrs.display_name != display_name:
            raise Exception('Value of sso_user_regular_attrs.display_name should be equal to `{}` instead of `{}`'.format(
                display_name, sso_user_regular_attrs.display_name))

        if sso_user_regular_attrs.totp_label != totp_label:
            raise Exception('Value of sso_user_regular_attrs.totp_label should be equal to `{}` instead of `{}`'.format(
                totp_label, sso_user_regular_attrs.totp_label))

        # .. now, get the user back but without requiring for all the attributes to be returned ..
        sso_user_all_attrs = self.sso.user.get_current_user(self.cid, user_session.ust,
            config.current_app, remote_addr, return_all_attrs=True)

        # .. now, all of the super-user-only attributes should have been returned ..
        for name in all_attrs:
            value = getattr(sso_user_all_attrs, name)
            if value is None:
                if name not in none_allowed:
                    raise Exception('Value of {} should not be None'.format(name))

# ################################################################################################################################

    def _test_validate_totp_code(self, config, totp_manager):
        # type: (TestConfig, type_[TOTPManager]) -> None

        # Local aliases
        password = config.super_user_password

        req_ctx = RequestCtx()
        req_ctx.cid = self.cid
        req_ctx.current_app = config.current_app
        req_ctx.remote_addr = '127.0.0.1'

        self.logger.info('SSO is_totp_token_valid')

        # Logging the user in should work
        info = self.sso.user.login(
            self.cid, config.super_user_name, password, config.current_app,
            '127.0.0.1', 'Zato', totp_code=totp_manager.get_current_totp_code(config.super_user_totp_key))

        # Let's get the latest code
        code = totp_manager.get_current_totp_code(config.super_user_totp_key)

        # Validate the code via UST - it will raise an exception if the code is invalid
        self.sso.totp.validate_code(req_ctx, code=code, ust=info.ust)

        # Validate the code via username - it will also raise an exception if the code is invalid
        self.sso.totp.validate_code(req_ctx, code=code, username=config.super_user_name)

# ################################################################################################################################
