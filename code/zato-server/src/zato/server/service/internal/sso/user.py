# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc
from uuid import uuid4

# dateutil
from dateutil.parser import parser as DateTimeParser

# Zato
from zato.common.util import asbool
from zato.server.service import AsIs, Bool, Int, List
from zato.server.service.internal.sso import BaseService, BaseRESTService, BaseSIO
from zato.sso import status_code, SearchCtx, SignupCtx, ValidationError
from zato.sso.user import update

# ################################################################################################################################

_create_user_attrs = ('username', 'password', 'password_must_change', 'display_name', 'first_name', 'middle_name', 'last_name', \
    'email', 'is_locked', 'sign_up_status')
_date_time_attrs = ('approv_rej_time', 'locked_time', 'password_expiry', 'password_last_set', 'sign_up_time',
    'approval_status_mod_time')

# ################################################################################################################################

# A marker that indicates a value that will never exist
_invalid = '_invalid.{}'.format(uuid4().hex)

# ################################################################################################################################

dt_parser = DateTimeParser()

# ################################################################################################################################

class Login(BaseService):
    """ Logs an SSO user in.
    """
    class SimpleIO(BaseSIO):
        input_required = ('username', 'password', 'current_app')
        input_optional = ('new_password', 'remote_addr', 'user_agent')
        output_required = ('status',)
        output_optional = BaseSIO.output_optional + ('ust',)

# ################################################################################################################################

    def _handle_sso(self, ctx):

        input = ctx.input
        has_remote_addr = input.get('remote_addr')
        has_user_agent = input.get('user_agent')

        input.has_remote_addr = has_remote_addr
        input.has_user_agent = has_user_agent

        input.remote_addr = input.remote_addr if has_remote_addr else self.wsgi_environ['zato.http.remote_addr'].decode('utf8')
        input.user_agent = input.user_agent if has_user_agent else self.wsgi_environ['HTTP_USER_AGENT']

        out = self._call_sso_api(self.sso.user.login, 'SSO user `{username}` cannot log in to `{current_app}`', **ctx.input)
        if out:
            self.response.payload.ust = out.ust

# ################################################################################################################################

class Logout(BaseService):
    """ Logs a user out of SSO.
    """
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app')
        output_required = ('status',)

    def _handle_sso(self, ctx):

        # Note that "ok" is always returned no matter the outcome - this is to thwart any attempts
        # to learn which USTs are/were valid or not.
        try:
            self.sso.user.logout(self.cid, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)
        except Exception:
            self.logger.warn('CID: `%s`, e:`%s`', self.cid, format_exc())
        finally:
            self.response.payload.status = status_code.ok

# ################################################################################################################################

class User(BaseRESTService):
    """ User manipulation through REST.
    """
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app')
        input_optional = (AsIs('user_id'), 'username', 'password', Bool('password_must_change'), 'password_expiry',
            'display_name', 'first_name', 'middle_name', 'last_name', 'email', 'is_locked', 'sign_up_status')

        output_optional = BaseSIO.output_optional + (AsIs('user_id'), 'username', 'email', 'display_name', 'first_name',
            'middle_name', 'last_name', 'is_active', 'is_internal', 'is_super_user', 'is_approval_needed',
            'approval_status', 'approval_status_mod_time', 'approval_status_mod_by', 'is_locked', 'locked_time',
            'creation_ctx', 'locked_by', 'approv_rej_time', 'approv_rej_by', 'password_expiry', 'password_is_set',
            'password_must_change', 'password_last_set', 'sign_up_status','sign_up_time')

        default_value = _invalid

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        """ Returns details of a particular user by UST or ID.
        """
        user_id = ctx.input.get('user_id')
        attrs = []

        if user_id:
            func = self.sso.user.get_user_by_id
            attrs.append(user_id)
        else:
            func = self.sso.user.get_user_by_ust

        # These will be always needed, no matter which function is used
        attrs += [ctx.input.ust, ctx.input.current_app, ctx.remote_addr]

        # Func will return a dictionary describing the required user, already taking permissions into account
        self.response.payload = func(self.cid, *attrs)

# ################################################################################################################################

    def _handle_sso_POST(self, ctx, _create_user_attrs=_create_user_attrs, _date_time_attrs=_date_time_attrs):
        """ Creates a new regular user (will not create super-users).
        """
        # Create input data explicitly, field-by-field, to make sure only well known parameters can be used
        # to create a new user.
        data = {}
        for name in _create_user_attrs:
            value = ctx.input.get(name)
            if value != _invalid:
                data[name] = value

        # This will update 'data' in place ..
        self.sso.user.create_user(self.cid, data, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

        # .. and we can now assign it to response..

        # .. first making sure that password is not returned
        data.pop('password', None)

        # .. then serializing all datetime objects to string ..
        for name in _date_time_attrs:
            value = data.get(name)
            if value:
                data[name] = value.isoformat()

        # .. and finally we can assign it.
        self.response.payload = data

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx):
        """ Deletes an existing user.
        """
        # Will take care of permissions / access rights and if everything is successful,
        # the user pointed to by user_id will be deleted.
        self.sso.user.delete_user_by_id(self.cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx):
        """ Updates an existing user.
        """
        current_ust = ctx.input.pop('ust')
        current_app = ctx.input.pop('current_app')

        # Explicitly provide only what we know is allowed
        data = {}
        for name in update.all_attrs:
            value = ctx.input.get(name)
            if value != _invalid:

                # Boolean values will never be None on input (SIO will convert them to a default value of an empty string)..
                if name in update.boolean_attrs:
                    if value is None:
                        continue
                    else:
                        value = asbool(value)

                # .. same goes for datetime ones.
                elif name in update.datetime_attrs:
                    if value is None:
                        continue
                    value = dt_parser.parse(value)

                data[name] = value

        user_id = data.pop('user_id', None)

        if user_id:
            self.sso.user.update_user_by_id(self.cid, user_id, data, current_ust, current_app, ctx.remote_addr)
        else:
            self.sso.user.update_current_user(self.cid, data, current_ust, current_app, ctx.remote_addr)

# ################################################################################################################################

class Password(BaseRESTService):
    """ User password management.
    """
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app', 'new_password')
        input_optional = (AsIs('user_id'), 'old_password', Int('password_expiry'), Bool('must_change'))

# ################################################################################################################################

    def _log_invalid_password_expiry(self, value):
        self.logger.warn('CID: `%s`, invalid password_expiry `%r`, forcing default of `%s`',
            self.cid, value, self.sso.password.expiry)

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx):
        """ Changes a user's password.
        """
        data = {
            'old_password': ctx.input.get('old_password') or uuid4().hex, # So it will never match anything
            'new_password': ctx.input['new_password'],
        }

        user_id = ctx.input.get('user_id')
        if user_id:
            data['user_id'] = user_id

        password_expiry = ctx.input.get('password_expiry')
        if password_expiry != '':
            if password_expiry < 0:
                self._log_invalid_password_expiry(password_expiry)
                password_expiry = self.sso.password.expiry
            data['password_expiry'] = password_expiry

        must_change = ctx.input.get('must_change')
        if must_change != '':
            must_change = asbool(must_change)
            data['must_change'] = must_change

        self.sso.user.change_password(self.cid, data, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

class _ChangeApprovalStatus(BaseRESTService):
    """ Base class for services changing a user's approval_status.
    """
    func_name = None

    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app', AsIs('user_id'))

    def _handle_sso_POST(self, ctx):
        func = getattr(self.sso.user, self.func_name)
        func(self.cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

class Approve(_ChangeApprovalStatus):
    """ Approves a user - changes his or her approval_status to 'approved'
    """
    func_name = 'approve_user'

# ################################################################################################################################

class Reject(_ChangeApprovalStatus):
    """ Rejects a user - changes his or her approval_status to 'rejected'
    """
    func_name = 'reject_user'

# ################################################################################################################################

class _CtxInputUsing(BaseService):
    """ Base class for services that create context objects based on their self.request.input
    which may possibly use _invalid default values.
    """
    class SimpleIO(BaseSIO):
        default_value = _invalid

    def _get_ctx_from_input(self, CtxClass, skip=None, _invalid=_invalid):

        ctx = CtxClass()
        skip = skip or []

        for key, value in sorted(self.request.input.items()):
            if key not in skip:
                if value != _invalid:
                    setattr(ctx, key, value)
        return ctx

# ################################################################################################################################

class Search(_CtxInputUsing):
    """ Looks up SSO users by input criteria.
    """
    class SimpleIO(_CtxInputUsing.SimpleIO):
        input_required = ('ust', 'current_app')
        input_optional = ('user_id', 'username', 'email', 'display_name', 'first_name', 'middle_name', 'last_name',
            'sign_up_status', 'approval_status', Bool('paginate'), Int('cur_page'), Int('page_size'), 'name_op',
            'is_name_exact')
        output_required = ('status',)
        output_optional = BaseSIO.output_optional + (Int('total'), Int('num_pages'), Int('page_size'), Int('cur_page'),
            'has_next_page', 'has_prev_page', Int('next_page'), Int('prev_page'), List('result'))
        default_value = _invalid

# ################################################################################################################################

    def _handle_sso(self, ctx, _skip_ctx=('ust', 'current_app')):

        # Search data built from all input parameters that were given on input
        search_ctx = self._get_ctx_from_input(SearchCtx, _skip_ctx)

        # Assign to response all the matching elements
        self.response.payload = self.sso.user.search(self.cid,
            search_ctx, ctx.input.ust, ctx.input.current_app, ctx.remote_addr, serialize_dt=True)

        # All went fine, return status code OK
        self.response.payload.status = status_code.ok

# ################################################################################################################################

class Signup(BaseRESTService, _CtxInputUsing):
    """ Lets users sign up with the system and confirm it afterwards.
    """
    class SimpleIO(_CtxInputUsing.SimpleIO):
        input_optional = ('confirm_token', 'email', 'username', 'password', 'current_app', List('app_list'))
        output_optional = _CtxInputUsing.SimpleIO.output_optional + ('confirm_token',)

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        self.response.payload.confirm_token = self.sso.user.signup(self.cid,
            self._get_ctx_from_input(SignupCtx), ctx.input.current_app, ctx.remote_addr)
        self.response.payload.status = status_code.ok

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx):
        try:
            self.sso.user.confirm_signup(self.cid, ctx.input.confirm_token, ctx.input.current_app, ctx.remote_addr)
        except ValidationError as e:
            self.logger.info(format_exc())
            self.response.payload.status = status_code.error
            if e.return_status:
                self.response.payload.sub_status = e.sub_status
            else:
                self.response.payload.sub_status = status_code.auth.not_allowed
        else:
            self.response.payload.status = status_code.ok

# ################################################################################################################################
