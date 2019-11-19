# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from uuid import uuid4

# Base32 Crockford
from base32_crockford import encode as crockford_encode

# ipaddress
from ipaddress import ip_network

# SQLAlchemy
from sqlalchemy import update

# Python 2/3 compatibility
from past.builtins import unicode

# Zato
from zato.common.crypto import CryptoManager
from zato.common.odb.model import SSOUser as UserModel
from zato.sso import status_code, ValidationError

# ################################################################################################################################

_gen_secret = CryptoManager.generate_secret

# ################################################################################################################################

_utcnow = datetime.utcnow
UserModelTable = UserModel.__table__

# ################################################################################################################################

def _new_id(prefix, _uuid4=uuid4, _crockford_encode=crockford_encode):
    return '%s%s' % (prefix, _crockford_encode(_uuid4().int).lower())

# ################################################################################################################################

def new_confirm_token(_gen_secret=_gen_secret):
    return _gen_secret(192)

# ################################################################################################################################

def new_user_id(_new_id=_new_id):
    return _new_id('zusr')

# ################################################################################################################################

def new_user_session_token(_new_id=_new_id):
    return _new_id('zust')

# ################################################################################################################################

def validate_password(sso_conf, password):
    """ Raises ValidationError if password is invalid, e.g. it is too simple.
    """
    # Password may not be too short
    if len(password) < sso_conf.password.min_length:
        raise ValidationError(status_code.password.too_short, sso_conf.password.inform_if_invalid)

    # Password may not be too long
    if len(password) > sso_conf.password.max_length:
        raise ValidationError(status_code.password.too_long, sso_conf.password.inform_if_invalid)

    # Password's default complexity is checked case-insensitively
    password = password.lower()

    # Password may not contain most commonly used ones
    for elem in sso_conf.password.reject_list:
        if elem in password:
            raise ValidationError(status_code.password.invalid, sso_conf.password.inform_if_invalid)

# ################################################################################################################################

def make_data_secret(data, encrypt_func=None, hash_func=None):
    """ Turns data into a secret by hashing it (stretching) and then encrypting the result.
    """
    # E.g. PBKDF2-SHA512
    if hash_func:
        data = hash_func(data)

    data = data.encode('utf8') if isinstance(data, unicode) else data

    # E.g. Fernet (AES-128)
    if encrypt_func:
        data = encrypt_func(data)

    return data

# ################################################################################################################################

def make_password_secret(password, encrypt_password, encrypt_func=None, hash_func=None):
    """ Encrypts and hashes a user password.
    """
    return make_data_secret(password, encrypt_func if encrypt_password else None, hash_func)

# ################################################################################################################################

def normalize_password_reject_list(sso_conf):
    """ Turns a multi-line string with passwords to be rejected into a set.
    """
    reject = set()
    for line in sso_conf.password.get('reject_list', '').strip().splitlines():
        line = str(line.strip().lower())
        reject.add(line)
    sso_conf.password.reject_list = reject

# ################################################################################################################################

def set_password(odb_session_func, encrypt_func, hash_func, sso_conf, user_id, password, must_change=None, password_expiry=None,
        _utcnow=_utcnow):
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

def check_credentials(decrypt_func, verify_hash_func, stored_password, input_password):
    """ Checks that an incoming password is equal to the one that is stored in the database.
    """
    password_decrypted = decrypt_func(stored_password) # At this point it is decrypted but still hashed
    return verify_hash_func(input_password, password_decrypted)

# ################################################################################################################################

def normalize_sso_config(sso_conf):

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

def check_remote_app_exists(current_app, apps_all, logger):
    if current_app not in apps_all:
        logger.warn('Invalid current_app `%s`, not among `%s', current_app, apps_all)
        raise ValidationError(status_code.app_list.invalid)
    else:
        return True

# ################################################################################################################################
