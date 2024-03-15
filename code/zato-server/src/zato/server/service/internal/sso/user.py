# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc
from uuid import uuid4

# dateutil
from dateutil.parser import parser as DateTimeParser

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# Zato
from zato.common import NotGiven
from zato.common.broker_message import SSO as BROKER_MSG_SSO
from zato.common.simpleio_ import drop_sio_elems
from zato.common.util import asbool
from zato.server.service import AsIs, Bool, Int, List, Opaque, SIOElem
from zato.server.service.internal.sso import BaseService, BaseRESTService, BaseSIO
from zato.sso import status_code, SearchCtx, SignupCtx, ValidationError
from zato.sso.user import super_user_attrs, update

# ################################################################################################################################

if 0:
    from zato.sso import User as UserEntity

    UserEntity = UserEntity

# ################################################################################################################################

_create_user_attrs = sorted(('username', 'password', Bool('password_must_change'), 'display_name', 'first_name', 'middle_name',
    'last_name', 'email', 'is_locked', 'sign_up_status', 'is_rate_limit_active', 'rate_limit_def', 'is_totp_enabled',
    'totp_label', 'totp_key'))
_date_time_attrs = sorted(('approv_rej_time', 'locked_time', 'password_expiry', 'password_last_set', 'sign_up_time',
    'approval_status_mod_time'))

# ################################################################################################################################

# A marker that indicates a value that will never exist
_invalid = '_invalid.{}'.format(uuid4().hex)

# ################################################################################################################################

dt_parser = DateTimeParser()

# ################################################################################################################################
# ################################################################################################################################

class Login(BaseService):
    """ Logs an SSO user in.
    """
    class SimpleIO(BaseSIO):
        input_required = ('username', 'password', 'current_app')
        input_optional = ('totp_code', 'new_password', 'remote_addr', 'user_agent')
        output_required = ('status',)
        output_optional = tuple(drop_sio_elems(BaseSIO.output_optional, 'status')) + ('ust',)

# ################################################################################################################################

    def _handle_sso(self, ctx):

        input = ctx.input
        input.cid = self.cid

        has_remote_addr = bool(input.get('remote_addr'))

        user_provided_user_agent = input.get('user_agent')
        has_user_agent = bool(user_provided_user_agent)

        user_agent = user_provided_user_agent if has_user_agent else ctx.user_agent

        input.has_remote_addr = has_remote_addr
        input.has_user_agent = has_user_agent

        if not has_remote_addr:
            wsgi_remote_addr = self.wsgi_environ['zato.http.remote_addr']
            wsgi_remote_addr = wsgi_remote_addr.decode('utf8') if not isinstance(wsgi_remote_addr, unicode) else wsgi_remote_addr
            input.remote_addr = wsgi_remote_addr

        out = self.sso.user.login(input.cid, input.username, input.password, input.current_app, input.remote_addr,
            user_agent, has_remote_addr, has_user_agent, input.new_password, input.totp_code)

        if out:
            self.response.payload.ust = out.ust
            if out.has_w_about_to_exp:
                self.environ['status_changed'] = True
                self.response.payload.status = status_code.warning
                self.response.payload.sub_status = [status_code.password.w_about_to_exp]

# ################################################################################################################################
# ################################################################################################################################

class Logout(BaseService):
    """ Logs a user out of SSO.
    """
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app')
        output_required = ('status',)
        output_optional = tuple(drop_sio_elems(BaseSIO.output_optional, 'status'))

    def _handle_sso(self, ctx):

        # Note that "ok" is always returned no matter the outcome - this is to thwart any attempts
        # to learn which USTs are/were valid or not.
        try:
            self.sso.user.logout(self.cid, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)
        except Exception:
            self.logger.warning('CID: `%s`, e:`%s`', self.cid, format_exc())
        finally:
            self.response.payload.status = status_code.ok

# ################################################################################################################################
# ################################################################################################################################

class User(BaseRESTService):
    """ User manipulation through REST.
    """
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app')
        input_optional = (AsIs('user_id'), 'username', 'password', Bool('password_must_change'), 'password_expiry',
            'display_name', 'first_name', 'middle_name', 'last_name', 'email', 'is_locked', 'sign_up_status',
            'approval_status', 'is_rate_limit_active', 'rate_limit_def', 'is_totp_enabled', 'totp_key', 'totp_label',
            Bool('auto_approve'))

        output_optional = BaseSIO.output_optional + (AsIs('user_id'), 'username', 'email', 'display_name', 'first_name',
            'middle_name', 'last_name', 'is_active', 'is_internal', 'is_super_user', 'is_approval_needed',
            'approval_status', 'approval_status_mod_time', 'approval_status_mod_by', 'is_locked', 'locked_time',
            'creation_ctx', 'locked_by', 'approv_rej_time', 'approv_rej_by', 'password_expiry', Bool('password_is_set'),
            Bool('password_must_change'), 'password_last_set', 'sign_up_status','sign_up_time', 'is_totp_enabled',
            'totp_label')

        default_value = _invalid

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        """ Returns details of a particular user by UST or ID.
        """
        user_id = ctx.input.get('user_id')
        attrs = []

        if user_id != self.SimpleIO.default_value:
            func = self.sso.user.get_user_by_id
            attrs.append(user_id)
        else:
            func = self.sso.user.get_current_user

        # These will be always needed, no matter which function is used
        attrs += [ctx.input.ust, ctx.input.current_app, ctx.remote_addr]

        # Get the dict describing this user
        user_entity = func(self.cid, *attrs) # type: UserEntity
        out = user_entity.to_dict()

        # Make sure regular users do not receive super-user specific details
        if not user_entity.is_current_super_user:
            for name in super_user_attrs:
                out.pop(name, None)

        # Func will return a dictionary describing the required user, already taking permissions into account
        self.response.payload = out

# ################################################################################################################################

    def _handle_sso_POST(self, ctx, _create_user_attrs=_create_user_attrs, _date_time_attrs=_date_time_attrs):
        """ Creates a new regular user (will not create super-users).
        """
        # Create input data explicitly, field-by-field, to make sure only well known parameters can be used
        # to create a new user.
        data = {}
        for name in _create_user_attrs:
            name = name.name if isinstance(name, SIOElem) else name
            value = ctx.input.get(name)
            if value != self.SimpleIO.default_value:

                if name == 'password':
                    value = self.server.decrypt(value)

                data[name] = value

        auto_approve = self.request.input.auto_approve
        if auto_approve == self.SimpleIO.default_value:
            auto_approve = False

        # This will update 'data' in place ..
        user_id = self.sso.user.create_user(
            self.cid, data, ctx.input.ust, ctx.input.current_app, ctx.remote_addr, auto_approve=auto_approve)

        # .. and we can now assign it to response..

        # .. first making sure that password is not returned
        data.pop('password', None)

        # .. then serializing all datetime objects to string ..
        for name in _date_time_attrs:
            value = data.get(name)
            if value:
                data[name] = value.isoformat()

        # .. if rate-limiting is active, let all servers know about it ..
        if ctx.input.is_rate_limit_active:
            self.broker_client.publish({
                'action': BROKER_MSG_SSO.USER_CREATE.value,
                'user_id': user_id,
                'is_rate_limit_active': True,
                'rate_limit_def': ctx.input.rate_limit_def if ctx.input.rate_limit_def != _invalid else None
            })

        # .. and finally we can create the response.
        self.response.payload = data

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx):
        """ Deletes an existing user.
        """
        # Will take care of permissions / access rights and if everything is successful,
        # the user pointed to by user_id will be deleted.
        self.sso.user.delete_user_by_id(self.cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx, _not_given=NotGiven):
        """ Updates an existing user.
        """
        current_ust = ctx.input.pop('ust')
        current_app = ctx.input.pop('current_app')

        # Explicitly provide only what we know is allowed
        data = {}
        for name in sorted(update.all_attrs):

            # No such key on input, we can ignore it
            if name not in self.request.payload:
                continue

            value = ctx.input.get(name, _not_given)

            # Just to be doubly sure, check the value too
            if value is _not_given:
                continue

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
            user = self.sso.user.get_user_by_id(self.cid, user_id, current_ust, current_app, ctx.remote_addr)
        else:
            self.sso.user.update_current_user(self.cid, data, current_ust, current_app, ctx.remote_addr)
            user = self.sso.user.get_current_user(self.cid, current_ust, current_app, ctx.remote_addr)
            user_id = user.user_id

        # Always notify all servers about this event in case we need to disable rate limiting
        self.broker_client.publish({
            'action': BROKER_MSG_SSO.USER_EDIT.value,
            'user_id': user_id,
            'is_rate_limit_active': ctx.input.is_rate_limit_active,
            'rate_limit_def': ctx.input.rate_limit_def if ctx.input.rate_limit_def != _invalid else None,
        })

# ################################################################################################################################
# ################################################################################################################################

class TOTP(BaseRESTService):
    """ TOTP key management.
    """
    name = 'zato.server.service.internal.sso.user.totp'

    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app', 'totp_key', 'totp_label')
        input_optional = AsIs('user_id'),
        output_optional = BaseSIO.output_optional + ('totp_key',)

    def _handle_sso_PATCH(self, ctx):
        """ Resets a user's TOTP key.
        """
        self.response.payload.totp_key = self.sso.user.reset_totp_key(
            self.cid, ctx.input.ust, ctx.input.user_id,
            ctx.input.totp_key,
            ctx.input.totp_label,
            ctx.input.current_app,
            ctx.remote_addr)

# ################################################################################################################################
# ################################################################################################################################

class Lock(BaseRESTService):
    """ Locks or unlocks a user account.
    """
    name = 'zato.server.service.internal.sso.user.lock'

    class SimpleIO(BaseSIO):
        input_required = 'ust', 'current_app', AsIs('user_id')

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        """ Locks a user account.
        """
        self.sso.user.lock_user(self.cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx):
        """ Unlocks a user account.
        """
        self.sso.user.unlock_user(self.cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################
# ################################################################################################################################

class Password(BaseRESTService):
    """ User password management.
    """
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app', 'new_password')
        input_optional = (AsIs('user_id'), 'old_password', Int('password_expiry'), Bool('must_change'))

# ################################################################################################################################

    def _log_invalid_password_expiry(self, value):
        self.logger.warning('CID: `%s`, invalid password_expiry `%r`, forcing default of `%s`',
            self.cid, value, self.sso.password_expiry)

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
                password_expiry = self.sso.password_expiry
            data['password_expiry'] = password_expiry

        if 'must_change' in self.request.payload:
            must_change = ctx.input.get('must_change')
            must_change = asbool(must_change)
            data['must_change'] = must_change

        self.sso.user.change_password(self.cid, data, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################
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
# ################################################################################################################################

class Approve(_ChangeApprovalStatus):
    """ Approves a user - changes his or her approval_status to 'approved'
    """
    func_name = 'approve_user'

# ################################################################################################################################
# ################################################################################################################################

class Reject(_ChangeApprovalStatus):
    """ Rejects a user - changes his or her approval_status to 'rejected'
    """
    func_name = 'reject_user'

# ################################################################################################################################
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
# ################################################################################################################################

class Search(_CtxInputUsing):
    """ Looks up SSO users by input criteria.
    """
    class SimpleIO(_CtxInputUsing.SimpleIO):
        input_required = ('ust', 'current_app')
        input_optional = (AsIs('user_id'), 'username', 'email', 'display_name', 'first_name', 'middle_name', 'last_name',
            'sign_up_status', 'approval_status', Bool('paginate'), Int('cur_page'), Int('page_size'), 'name_op',
            'is_name_exact')
        output_required = ('status',)
        output_optional = tuple(drop_sio_elems(BaseSIO.output_optional, 'status')) + (Int('total'), Int('num_pages'),
            Int('page_size'), Int('cur_page'), 'has_next_page', 'has_prev_page', Int('next_page'), Int('prev_page'),
            List('result'))
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
# ################################################################################################################################

class LinkedAuth(BaseRESTService):
    class SimpleIO(BaseSIO):
        input_required = 'current_app', 'ust'
        input_optional = Opaque('user_id'), 'auth_type', 'auth_username', 'is_active',
        output_optional = BaseSIO.output_optional + ('result',)
        default_value = _invalid
        skip_empty_keys = True

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        user_id = ctx.input.user_id
        user_id = user_id if user_id != _invalid else None

        out = []
        result = self.sso.user.get_linked_auth_list(self.cid, ctx.input.ust, ctx.input.current_app, ctx.remote_addr, user_id)

        for item in result:
            item['creation_time'] = item['creation_time'].isoformat()
            for name in 'auth_principal', 'auth_source':
                if item[name] == 'reserved':
                    del item[name]

            item.pop('is_internal', None)
            item.pop('auth_id', None)
            item.pop('user_id', None)
            item.pop('auth_principal', None)
            item.pop('has_ext_principal', None)

            out.append(item)

        self.response.payload.result = out

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):

        user_id, auth_id = self.sso.user.create_linked_auth(self.cid, ctx.input.ust, ctx.input.user_id, ctx.input.auth_type,
            ctx.input.auth_username, ctx.input.is_active, ctx.input.current_app, ctx.remote_addr)

        # With data saved to SQL, we can now notify all the servers about the new link
        msg = {}
        msg['action'] = BROKER_MSG_SSO.LINK_AUTH_CREATE.value
        msg['auth_type'] = ctx.input.auth_type
        msg['user_id'] = user_id
        msg['auth_id'] = auth_id
        self.broker_client.publish(msg)

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx):

        auth_id = self.sso.user.delete_linked_auth(self.cid, ctx.input.ust, ctx.input.user_id, ctx.input.auth_type,
            ctx.input.auth_username, ctx.input.current_app, ctx.remote_addr)

        # With data saved to SQL, we can now notify all the servers about the new link
        msg = {}
        msg['action'] = BROKER_MSG_SSO.LINK_AUTH_DELETE.value
        msg['auth_type'] = ctx.input.auth_type
        msg['auth_username'] = ctx.input.auth_username
        msg['user_id'] = ctx.input.user_id
        msg['auth_id'] = auth_id
        self.broker_client.publish(msg)

# ################################################################################################################################
# ################################################################################################################################
