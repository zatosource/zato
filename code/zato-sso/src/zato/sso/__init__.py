# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime

# ################################################################################################################################

_utcnow = datetime.utcnow
not_given = object()

# ################################################################################################################################

class status_code:
    """ Reason codes pointing to specific API validation errors.
    """
    ok       = 'ok'
    error    = 'error'
    warning  = 'warning'

    class username:
        invalid        = 'E001001'
        exists         = 'E001002'
        too_long       = 'E001003'
        has_whitespace = 'E001004'

    class user_id:
        invalid        = 'E001100'

    class email:
        invalid        = 'E002001'
        exists         = 'E002002'
        too_long       = 'E002003'
        has_whitespace = 'E002004'
        missing        = 'E002005'

    class password:
        invalid   = 'E003001'
        too_short = 'E003002'
        too_long  = 'E003003'

        expired        = 'E003004'
        w_about_to_exp = 'W003005'
        e_about_to_exp = 'E003006'
        must_send_new  = 'E003007'

    class app_list:
        invalid   = 'E004001'
        no_signup = 'E004002'

    class auth:
        not_allowed           = 'E005001' # Generic 'You are not allowed to access this resource'
        locked                = 'E005002'
        invalid_signup_status = 'E005003'
        not_approved          = 'E005004'
        super_user_required   = 'E005005'
        no_such_sign_up_token = 'E005006'
        sign_up_confirmed     = 'E005007'

    class metadata:
        not_allowed = 'E006001'

    class session:
        no_such_session = 'E007001'
        expired         = 'E007002'

    class common:
        invalid_operation = 'E008001'
        invalid_input     = 'E008002'
        missing_input     = 'E008003'
        internal_error    = 'E008004'

    class attr:
        already_exists = 'E009001'
        no_such_attr   = 'E009002'

# ################################################################################################################################

class const:
    """ Constants used in SSO.
    """
    class signup_status:
        before_confirmation = 'before_confirmation'
        final               = 'final'

        def __iter__(self):
            return iter([self.before_confirmation, self.final])

    class approval_status:
        approved = 'approved'
        rejected = 'rejected'
        before_decision = 'before_decision'

        def __iter__(self):
            return iter([self.approved, self.rejected, self.before_decision])

    class search:
        and_ = 'and'
        or_ = 'or'
        page_size = 50

        def __iter__(self):
            return iter([self.and_, self.or_])

# ################################################################################################################################

class ValidationError(Exception):
    """ Raised if any input SSO data is invalid, subcode contains details of what was rejected.
    """
    def __init__(self, sub_status, return_status=False, status=status_code.error):
        super(ValidationError, self).__init__('{} {}'.format(status, sub_status))
        self.sub_status = sub_status if isinstance(sub_status, list) else [sub_status]
        self.return_status = return_status
        self.status = status

# ################################################################################################################################

class SearchCtx(object):
    """ A container for SSO user search parameters.
    """
    __slots__ = ('user_id', 'username', 'email', 'display_name', 'first_name', 'middle_name', 'last_name', 'sign_up_status',
        'approval_status', 'paginate', 'cur_page', 'page_size', 'name_op', 'is_name_exact')

    def __init__(self):

        # Query criteria
        self.user_id = not_given
        self.username = not_given
        self.email = not_given
        self.display_name = not_given
        self.first_name = not_given
        self.middle_name = not_given
        self.last_name = not_given
        self.sign_up_status = not_given
        self.approval_status = not_given

        # Query config
        self.paginate = True
        self.cur_page = 1
        self.page_size = None
        self.name_op = const.search.and_
        self.is_name_exact = True

# ################################################################################################################################

class SignupCtx(object):
    """ A container for SSO user signup parameters.
    """
    __slots__ = ('username', 'email', 'password', 'current_app', 'app_list', 'sign_up_status')

    def __init__(self):
        self.username = ''
        self.email = ''
        self.password = ''
        self.current_app = None
        self.app_list = None
        self.sign_up_status = const.signup_status.before_confirmation

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'current_app': self.current_app,
            'app_list': self.app_list,
            'sign_up_status': self.sign_up_status
        }

# ################################################################################################################################

class User(object):
    """ Represents a user managed by SSO.
    """
    __slots__ = ('approval_status', 'approval_status_mod_by', 'approval_status_mod_time','attr', 'creation_ctx', 'display_name',
        'email', 'first_name', 'is_active', 'is_approval_needed', 'is_internal', 'is_locked', 'is_super_user',
        'last_name', 'locked_by', 'locked_time', 'middle_name', 'password_expiry', 'password_is_set', 'password_last_set',
        'password_must_change', 'sign_up_status', 'sign_up_time', 'user_id', 'username')

    def __init__(self):
        self.approval_status = None
        self.approval_status_mod_by = None
        self.approval_status_mod_time = None
        self.attr = None
        self.creation_ctx = None
        self.display_name = None
        self.email = None
        self.first_name = None
        self.is_active = None
        self.is_approval_needed = None
        self.is_internal = None
        self.is_locked = None
        self.is_super_user = None
        self.last_name = None
        self.locked_by = None
        self.locked_time = None
        self.middle_name = None
        self.password_expiry = None
        self.password_is_set = None
        self.password_last_set = None
        self.password_must_change = None
        self.sign_up_status = None
        self.sign_up_time = None
        self.user_id = None
        self.username = None

    def to_dict(self):
        return dict((name, getattr(self, name)) for name in self.__slots__ if name != 'attr')

# ################################################################################################################################

class Session(object):
    """ Represents a session opened by a particular SSO user.
    """
    __slots__ = ('attr', 'creation_time', 'expiration_time', 'remote_addr', 'user_agent')

    def __init__(self):
        self.attr = None
        self.creation_time = None
        self.expiration_time = None
        self.remote_addr = None
        self.user_agent = None

    def to_dict(self):
        return dict((name, getattr(self, name)) for name in self.__slots__ if name != 'attr')

# ################################################################################################################################
