# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger
from uuid import uuid4

# Base32 Crockford
from base32_crockford import encode as crockford_encode

# ipaddress
from ipaddress import ip_network

# SQLAlchemy
from sqlalchemy import update

# zxcvbn
from zxcvbn import zxcvbn

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.odb.model import SSOUser as UserModel
from zato.sso import const, status_code, ValidationError
from zato.sso.common import LoginCtx

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.odb.model import SSOUser
    from zato.common.typing_ import any_, anylist, boolnone, callable_, callnone, intnone
    boolnone = boolnone
    callnone = callnone
    intnone = intnone

    SSOUser = SSOUser

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

_gen_secret = CryptoManager.generate_secret

# ################################################################################################################################

_utcnow = datetime.utcnow
UserModelTable = UserModel.__table__

# ################################################################################################################################

def _new_id(prefix:'str', _uuid4:'callable_'=uuid4, _crockford_encode:'callable_'=crockford_encode) -> 'str':
    return '%s%s' % (prefix, _crockford_encode(_uuid4().int).lower())

# ################################################################################################################################

def new_confirm_token(_gen_secret:'callable_'=_gen_secret) -> 'str':
    return _gen_secret(192)

# ################################################################################################################################

def new_user_id(_new_id:'callable_'=_new_id) -> 'str':
    return _new_id('zusr')

# ################################################################################################################################

def new_user_session_token(_new_id:'callable_'=_new_id) -> 'str':
    return _new_id('zust')

# ################################################################################################################################

def new_prt(_new_id:'callable_'=_new_id) -> 'str':

    # Note that these tokens are to be publicly visible and this is why we prefer
    # not to be conspicuous about the prefix.
    return _new_id('')

# ################################################################################################################################

def new_prt_reset_key(_new_id:'callable_'=_new_id) -> 'str':
    return _new_id('zprtrkey')

# ################################################################################################################################

def validate_password(sso_conf:'Bunch', password:'str') -> 'None':
    """ Raises ValidationError if password is invalid, e.g. it is too simple.
    """

    # This is optional
    min_complexity = int(sso_conf.password.get('min_complexity', 4))

    if min_complexity:
        result = zxcvbn(password)
        if result['score'] < min_complexity:
            raise ValidationError(status_code.password.not_complex_enough, sso_conf.password.inform_if_invalid)

    # Password may not be too short
    if len(password) < sso_conf.password.min_length:
        raise ValidationError(status_code.password.too_short, sso_conf.password.inform_if_invalid)

    # Password may not be too long
    if len(password) > sso_conf.password.max_length:
        raise ValidationError(status_code.password.too_long, sso_conf.password.inform_if_invalid)

    # Password's default complexity (i.e. the reject list) is checked case-insensitively
    password = password.lower()

    # Password may not contain most commonly used ones
    for elem in sso_conf.password.reject_list:
        if elem in password:
            logger.warning('Password rejected because it contains a disallowed pattern from sso.conf -> password.reject_list')
            raise ValidationError(status_code.password.invalid, sso_conf.password.inform_if_invalid)

# ################################################################################################################################

def make_data_secret(data:'str', encrypt_func:'callable_'=None, hash_func:'callable_'=None) -> 'bytes':
    """ Turns data into a secret by hashing it (stretching) and then encrypting the result.
    """
    # E.g. PBKDF2-SHA512
    if hash_func:
        data = hash_func(data)

    data = data.encode('utf8') if isinstance(data, str) else data

    # E.g. Fernet (AES-128)
    if encrypt_func:
        data = encrypt_func(data)

    return data

# ################################################################################################################################

def make_password_secret(
    password,          # type: str
    encrypt_password,  # type: callable_
    encrypt_func=None, # type: callnone
    hash_func=None     # type: callnone
) -> 'bytes':
    """ Encrypts and hashes a user password.
    """
    return make_data_secret(password, encrypt_func if encrypt_password else None, hash_func)

# ################################################################################################################################

def normalize_password_reject_list(sso_conf:'Bunch') -> 'None':
    """ Turns a multi-line string with passwords to be rejected into a set.
    """
    reject = set()
    for line in sso_conf.password.get('reject_list', '').strip().splitlines():
        line = str(line.strip().lower())
        reject.add(line)
    sso_conf.password.reject_list = reject

# ################################################################################################################################

def set_password(
    odb_session_func, # type: callable_
    encrypt_func,     # type: callable_
    hash_func,        # type: callable_
    sso_conf,         # type: Bunch
    user_id,          # type: str
    password,         # type: str
    must_change=None, # type: boolnone
    password_expiry=None, # type: intnone
    _utcnow=_utcnow   # type: callable_
) -> 'None':
    """ Sets a new password for user.
    """
    # Just to be doubly sure, validate the password before saving it to DB.
    # Will raise ValidationError if anything is wrong.
    validate_password(sso_conf, password)

    now = _utcnow()
    password = make_password_secret(password, sso_conf.main.encrypt_password, encrypt_func, hash_func)
    password_expiry = password_expiry or sso_conf.password.expiry

    new_values = {
        'password': password,
        'password_is_set': True,
        'password_last_set': now,
        'password_expiry': now + timedelta(days=password_expiry),
    }

    # Must be a boolean because the underlying SQL column is a bool
    if must_change is not None:
        if not isinstance(must_change, bool):
            raise ValueError('Expected for must_change to be a boolean instead of `{}`, `{}`'.format(
                type(must_change), repr(must_change)))
        else:
            new_values['password_must_change'] = must_change

    with closing(odb_session_func()) as session:
        session.execute(
            update(UserModelTable).\
            values(new_values).\
            where(UserModelTable.c.user_id==user_id)
        )
        session.commit()

# ################################################################################################################################

def check_credentials(
    decrypt_func,     # type: callable_
    verify_hash_func, # type: callable_
    stored_password,  # type: str
    input_password    # type: str
) -> 'bool':
    """ Checks that an incoming password is equal to the one that is stored in the database.
    """
    password_decrypted = decrypt_func(stored_password) # At this point it is decrypted but still hashed
    return verify_hash_func(input_password, password_decrypted)

# ################################################################################################################################

def normalize_sso_config(sso_conf:'Bunch') -> 'None':

    # Lower-case elements that must not be substrings in usernames ..
    reject_username = sso_conf.user_validation.get('reject_username', [])
    reject_username = [elem.strip().lower() for elem in reject_username]
    sso_conf.user_validation.reject_username = reject_username

    # .. and emails too.
    reject_email = sso_conf.user_validation.get('reject_email', [])
    reject_email = [elem.strip().lower() for elem in reject_email]
    sso_conf.user_validation.reject_email = reject_email

    # Construct a set of common passwords to reject out of a multi-line list
    normalize_password_reject_list(sso_conf)

    # Turn all app lists into sets to make lookups faster

    apps_all = sso_conf.apps.all
    apps_signup_allowed = sso_conf.apps.signup_allowed
    apps_login_allowed = sso_conf.apps.login_allowed

    apps_all = apps_all if isinstance(apps_all, list) else [apps_all]
    apps_signup_allowed = apps_signup_allowed if isinstance(apps_signup_allowed, list) else [apps_signup_allowed]
    apps_login_allowed = apps_login_allowed if isinstance(apps_login_allowed, list) else [apps_login_allowed]

    sso_conf.apps.all = set(apps_all)
    sso_conf.apps.signup_allowed = set(apps_signup_allowed)
    sso_conf.apps.login_allowed = set(apps_login_allowed)

    # There may be a single service in a relevant part of configuration
    # so for ease of use we always turn tjem into lists.
    usr_valid_srv = sso_conf.user_validation.service
    usr_valid_srv = usr_valid_srv if isinstance(usr_valid_srv, list) else [usr_valid_srv]
    sso_conf.user_validation.service = usr_valid_srv

    # Convert all white/black-listed IP addresses to sets of network objects
    # which will let serviced in run-time efficiently check for membership of an address in that network.

    user_address_list = sso_conf.user_address_list
    for username, ip_allowed in user_address_list.items():
        if ip_allowed:
            ip_allowed = user_address_list if isinstance(ip_allowed, list) else [ip_allowed]
            ip_allowed = [ip_network(elem.decode('utf8')) for elem in ip_allowed if elem != '*']
        else:
            ip_allowed = []
        user_address_list[username] = ip_allowed

    # Make sure signup service list is a list
    callback_service_list = sso_conf.signup.callback_service_list or []
    if callback_service_list:
        callback_service_list = callback_service_list if isinstance(callback_service_list, list) else [callback_service_list]
    sso_conf.signup.callback_service_list = callback_service_list

# ################################################################################################################################

def check_remote_app_exists(current_app:'str', apps_all:'anylist', logger) -> 'bool':
    if current_app not in apps_all:
        logger.warning('Invalid current_app `%s`, not among `%s', current_app, apps_all)
        raise ValidationError(status_code.app_list.invalid)
    else:
        return True

# ################################################################################################################################
# ################################################################################################################################

class UserChecker:
    """ Checks whether runtime information about the user making a request is valid.
    """
    def __init__(
        self,
        decrypt_func,     # type: callable_
        verify_hash_func, # type: callable_
        sso_conf          # type: Bunch
    ) -> 'None':
        self.decrypt_func = decrypt_func
        self.verify_hash_func = verify_hash_func
        self.sso_conf = sso_conf

# ################################################################################################################################

    def check_credentials(self, ctx:'LoginCtx', user_password:'str') -> 'bool':
        return check_credentials(self.decrypt_func, self.verify_hash_func, user_password, ctx.input['password'])

# ################################################################################################################################

    def check_remote_app_exists(self, ctx:'LoginCtx') -> 'bool':
        return check_remote_app_exists(ctx.input['current_app'], self.sso_conf.apps.all, logger)

# ################################################################################################################################

    def check_login_to_app_allowed(self, ctx:'LoginCtx') -> 'bool':
        if ctx.input['current_app'] not in self.sso_conf.apps.login_allowed:
            if self.sso_conf.apps.inform_if_app_invalid:
                raise ValidationError(status_code.app_list.invalid, True)
            else:
                raise ValidationError(status_code.auth.not_allowed, True)
        else:
            return True

# ################################################################################################################################

    def check_remote_ip_allowed(self, ctx:'LoginCtx', user:'SSOUser', _invalid:'any_'=object()) -> 'bool':

        ip_allowed = self.sso_conf.user_address_list.get(user.username, _invalid)

        # Shortcut in the simplest case
        if ip_allowed == '*':
            return True

        # Do not continue if user is not whitelisted but is required to
        if ip_allowed is _invalid:
            if self.sso_conf.login.reject_if_not_listed:
                return
            else:
                # We are not to reject users if they are not listed, in other words,
                # we are to accept them even if they are not so we return a success flag.
                return True

        # User was found in configuration so now we need to check IPs allowed ..
        else:

            # .. but if there are no IPs configured for user, it means the person may not log in
            # regardless of reject_if_not_whitelisted, which is why it is checked separately.
            if not ip_allowed:
                return

            # There is at least one address or pattern to check again ..
            else:
                # .. but if no remote address was sent, we cannot continue.
                if not ctx.remote_addr:
                    return False
                else:
                    for _remote_addr in ctx.remote_addr:
                        for _ip_allowed in ip_allowed:
                            if _remote_addr in _ip_allowed:
                                return True # OK, there was at least that one match so we report success

                    # If we get here, it means that none of remote addresses from input matched
                    # so we can return False to be explicit.
                    return False

# ################################################################################################################################

    def check_user_not_locked(self, user:'SSOUser') -> 'bool':

        if user.is_locked:
            if self.sso_conf.login.inform_if_locked:
                raise ValidationError(status_code.auth.locked, True)
        else:
            return True

# ################################################################################################################################

    def check_signup_status(self, user:'SSOUser') -> 'bool':

        if user.sign_up_status != const.signup_status.final:
            if self.sso_conf.login.inform_if_not_confirmed:
                raise ValidationError(status_code.auth.invalid_signup_status, True)
        else:
            return True

# ################################################################################################################################

    def check_is_approved(self, user:'SSOUser') -> 'bool':

        if not user.approval_status == const.approval_status.approved:
            if self.sso_conf.login.inform_if_not_approved:
                raise ValidationError(status_code.auth.invalid_signup_status, True)
        else:
            return True

# ################################################################################################################################

    def check_password_expired(self, user:'SSOUser', _now:'callable_'=datetime.utcnow) -> 'bool':

        if _now() > user.password_expiry:
            if self.sso_conf.password.inform_if_expired:
                raise ValidationError(status_code.password.expired, True)
        else:
            return True

# ################################################################################################################################

    def check_password_about_to_expire(
        self,
        user, # type: SSOUser
        _now=datetime.utcnow, # type: callable_
        _timedelta=timedelta  # type: timedelta
    ) -> 'bool':

        # Find time after which the password is considered to be about to expire
        threshold_time = user.password_expiry - _timedelta(days=self.sso_conf.password.about_to_expire_threshold)

        # .. check if current time is already past that threshold ..
        if _now() > threshold_time:

            # .. if it is, we may either return a warning and continue ..
            if self.sso_conf.password.inform_if_about_to_expire:
                return status_code.warning

            # .. or it can considered an error, which rejects the request.
            else:
                return status_code.error

        # No approaching expiry, we may continue
        else:
            return True

# ################################################################################################################################

    def check_must_send_new_password(self, ctx:'LoginCtx', user:'SSOUser') -> 'bool':

        if user.password_must_change and not ctx.input.get('new_password'):
            if self.sso_conf.password.inform_if_must_be_changed:
                raise ValidationError(status_code.password.must_send_new, True)
        else:
            return True

# ################################################################################################################################

    def check_login_metadata_allowed(self, ctx:'LoginCtx') -> 'bool':

        if ctx.has_remote_addr or ctx.has_user_agent:
            if ctx.input['current_app'] not in self.sso_conf.apps.login_metadata_allowed:
                raise ValidationError(status_code.metadata.not_allowed, False)

        return True

# ################################################################################################################################

    def check(self, ctx, user:'LoginCtx', check_if_password_expired:'bool'=True) -> 'None':
        """ Runs a series of checks for incoming request and user.
        """

        # Move checks to UserChecker in tools

        # Input application must have been previously defined
        if not self.check_remote_app_exists(ctx):
            raise ValidationError(status_code.auth.not_allowed, True)

        # If applicable, requests must originate in a white-listed IP address
        if not self.check_remote_ip_allowed(ctx, user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # User must not have been locked out of the auth system
        if not self.check_user_not_locked(user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # If applicable, user must be fully signed up, including account creation's confirmation
        if not self.check_signup_status(user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # If applicable, user must be approved by a super-user
        if not self.check_is_approved(user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # Password must not have expired, but only if input flag tells us to,
        # it may be possible that a user's password has already expired
        # and that person wants to change it in this very call, in which case
        # we cannot reject it on the basis that it is expired - no one would be able
        # to change expired passwords then.
        if check_if_password_expired:
            if not self.check_password_expired(user):
                raise ValidationError(status_code.auth.not_allowed, True)

        # Current application must be allowed to send login metadata
        if not self.check_login_metadata_allowed(ctx):
            raise ValidationError(status_code.auth.not_allowed, True)

# ################################################################################################################################
# ################################################################################################################################
