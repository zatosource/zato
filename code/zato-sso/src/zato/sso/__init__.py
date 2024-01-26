# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlistnone, strnone

# ################################################################################################################################
# ################################################################################################################################

not_given = object()

# ################################################################################################################################
# ################################################################################################################################

class Default:
    prt_valid_for = 1440 # In minutes = 1 day
    prt_password_change_session_duration=1800 # In seconds = 30 minutes
    prt_user_search_by = 'username'

    # User notifications are sent in this language by default
    prt_locale = 'en_GB'

# ################################################################################################################################
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

        not_complex_enough = 'E003008'

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
        totp_missing          = 'E005008'

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

    class password_reset:
        could_not_access = 'E010001'

# ################################################################################################################################
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

    class auth_type:
        basic_auth = 'basic_auth'
        default    = 'default'
        jwt        = 'jwt'

    class password_reset:
        token_type = 'prt'

# ################################################################################################################################
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
# ################################################################################################################################

class InvalidTOTPError(ValidationError):
    """ Raised if any input TOTP code is invalid for user.
    """

# ################################################################################################################################
# ################################################################################################################################

class SearchCtx:
    """ A container for SSO user search parameters.
    """

    # Query criteria
    user_id:         'str | object' = not_given
    username:        'str | object' = not_given
    email:           'str | object' = not_given
    display_name:    'str | object' = not_given
    first_name:      'str | object' = not_given
    middle_name:     'str | object' = not_given
    last_name:       'str | object' = not_given
    sign_up_status:  'str | object' = not_given
    approval_status: 'str | object' = not_given

    # Query config
    paginate:      'bool'    = True
    cur_page:      'int'     = 1
    page_size:     'strnone' = None
    name_op:       'str'     = const.search.and_
    is_name_exact: 'bool'    = True

# ################################################################################################################################
# ################################################################################################################################

class SignupCtx:
    """ A container for SSO user signup parameters.
    """

    username:       'str' = ''
    email:          'str' = ''
    password:       'str' = ''
    current_app:    'str' = None
    app_list:       'strlistnone' = None
    sign_up_status: 'str' = const.signup_status.before_confirmation

    def to_dict(self) -> 'stranydict':
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'current_app': self.current_app,
            'app_list': self.app_list,
            'sign_up_status': self.sign_up_status
        }

# ################################################################################################################################
# ################################################################################################################################

class User:
    """ Represents a user managed by SSO.
    """
    __slots__ = ('approval_status', 'approval_status_mod_by', 'approval_status_mod_time','attr', 'creation_ctx', 'display_name',
        'email', 'first_name', 'is_active', 'is_approval_needed', 'is_internal', 'is_locked', 'is_super_user',
        'last_name', 'locked_by', 'locked_time', 'middle_name', 'password_expiry', 'password_is_set', 'password_last_set',
        'password_must_change', 'sign_up_status', 'sign_up_time', 'user_id', 'username', 'is_rate_limit_active',
        'rate_limit_def', 'rate_limit_type', 'rate_limit_check_parent_def', 'is_totp_enabled', 'totp_key', 'totp_label',
        'status', 'is_current_super_user')

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
        self.is_rate_limit_active = None
        self.rate_limit_def = None
        self.rate_limit_type = None
        self.rate_limit_check_parent_def = None
        self.is_totp_enabled = None
        self.totp_key = None
        self.totp_label = None
        self.status = None

        # Set to True if the user whose session created this object is a super-user
        self.is_current_super_user = False

    def to_dict(self):
        return {name: getattr(self, name) for name in self.__slots__ if name != 'attr'}

# ################################################################################################################################
# ################################################################################################################################

class Session:
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
        return {name: getattr(self, name) for name in self.__slots__ if name != 'attr'}

# ################################################################################################################################
# ################################################################################################################################
