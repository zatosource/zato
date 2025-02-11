# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from base64 import b64decode

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode
from six import PY2

# Zato
from zato.common.api import AUTH_RESULT
from zato.common.crypto.api import is_string_equal
from zato.common.util.api import as_bool
from zato.server.connection.http_soap import Forbidden

logger = getLogger('zato')

def parse_basic_auth(auth, prefix='Basic '):
    """ Parses username/password out of incoming HTTP Basic Auth data.
    """
    if not auth:
        raise ValueError('No auth received in `{}` ({})'.format(auth, AUTH_RESULT.BASIC_AUTH.NO_AUTH))

    if not auth.startswith(prefix):
        raise ValueError('Invalid prefix in `{}` ({})'.format(auth, AUTH_RESULT.BASIC_AUTH.NO_AUTH))

    _, auth = auth.split(prefix)
    auth = b64decode(auth.strip())
    auth = auth if PY2 else auth.decode('utf8')

    return auth.split(':', 1)

# ################################################################################################################################
# ################################################################################################################################

# Code below comes from another project - will be moved elsewhere at one point thus the location of imports and definitions

# ################################################################################################################################
# ################################################################################################################################

# Python 2/3 compatibility
from zato.common.ext.future.moves.urllib.parse import quote_plus

# lxml
from lxml import etree

# PyYAML
from yaml import dump
try:
    from yaml import CDumper as Dumper
except ImportError:                      # pragma: no cover
    from yaml import Dumper              # pragma: no cover

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# ################################################################################################################################
# ################################################################################################################################

class AuthResult:
    """ Represents the result of validating a URL against the config. 'status' is the main boolean flag indicating
    whether the successful was successful or not. 'code' equal to '0' means success and any other value is a failure,
    note that 'code' may be a multi-character string including punctuation. 'description' is an optional attribute holding
    any additional textual information a callee might wish to pass to the calling layer. 'auth_info' is either
    an empty string or information regarding the authorization data presented by the calling application.

    Instances of this class are considered True or False in boolean comparisons
    according to the boolean value of self.status.
    """
    def __init__(self, status=False, code='-1', description=''):
        self.status = status
        self.code = code
        self.description = description
        self._auth_info = b''

    @property
    def auth_info(self):
        return self._auth_info

    @auth_info.setter
    def auth_info(self, value):
        self._auth_info = dump(value, Dumper=Dumper)

    def __repr__(self):
        return '<{0} at {1} status={2} code={3} description={4} auth_info={5}>'.format(
            self.__class__.__name__, hex(id(self)), self.status, self.code,
            self.description, self.auth_info)

    def __bool__(self):
        """ Returns the boolean value of self.status. Useful when an instance
        must be compared in a boolean context.
        """
        return bool(self.status)

    __nonzero__ = __bool__

# ################################################################################################################################
# ################################################################################################################################

class SecurityException(Exception):
    """ Indicates problems with validating incoming requests. The 'description'
    attribute holds textual information suitable for showing to human users.
    """
    def __init__(self, description):
        self.description = description

# ################################################################################################################################
# ################################################################################################################################

Auth_WSSE_No_Data = '0003.0001'
Auth_WSSE_Validation_Error = '0003.0002'

Auth_Basic_No_Auth = 'No_Auth_Provided'
Auth_Basic_Invalid_Prefix = 'Invalid_Auth_Prefix'
Auth_Basic_Username_Or_Password_Mismatch = 'Invalid_Username_Or_Password'

# ################################################################################################################################
# ################################################################################################################################

def on_wsse_pwd(wsse, url_config, data, needs_auth_info=True):
    """ Visit _RequestApp._on_wsse_pwd method's docstring.
    """
    if not data:
        return AuthResult(False, Auth_WSSE_No_Data)

    request = etree.fromstring(data)
    try:
        ok, wsse_username = wsse.validate(request, url_config)
    except SecurityException as e:
        return AuthResult(False, Auth_WSSE_Validation_Error, e.description)
    else:
        auth_result = AuthResult(True, '0')
        if needs_auth_info:
            auth_result.auth_info = {b'wsse-pwd-username': str(wsse_username)}

        return auth_result

# ################################################################################################################################
# ################################################################################################################################

def extract_basic_auth(cid:'str', auth:'str', *, raise_on_error:'bool'=False) -> 'str':

    if not auth:
        if raise_on_error:
            logger.warn(f'Basic Auth -> {Auth_Basic_No_Auth} -> {cid}')
            raise Forbidden(cid)
        else:
            return None, Auth_Basic_No_Auth

    prefix = 'Basic '
    if not auth.startswith(prefix):
        if raise_on_error:
            logger.warn(f'Basic Auth -> {Auth_Basic_Invalid_Prefix} -> {cid}')
            raise Forbidden(cid)
        else:
            return None, Auth_Basic_Invalid_Prefix

    _, auth = auth.split(prefix)
    auth = auth.strip()
    auth = b64decode(auth)
    auth = auth if isinstance(auth, unicode) else auth.decode('utf8')
    username, password = auth.split(':', 1)

    return username, password

# ################################################################################################################################
# ################################################################################################################################

def check_basic_auth(cid, auth, expected_username, expected_password, _needs_details=_needs_details):
    """ A low-level call for checking HTTP Basic Auth credentials.
    """
    result = extract_basic_auth(cid, auth, raise_on_error=False)

    if result[0]:
        username, password = result
    else:
        return result[1]

    if _needs_details:
        logger.info('*' * 60)

        logger.info('Username received: `%s`', username)
        logger.info('Username expected: `%s`', expected_username)

        logger.info('Password received: `%s`', password)
        logger.info('Password expected: `%s`', expected_password)

    if is_string_equal(username, expected_username) and is_string_equal(password, expected_password):
        return True
    else:
        return Auth_Basic_Username_Or_Password_Mismatch

# ################################################################################################################################
# ################################################################################################################################

def on_basic_auth(cid, env, url_config, needs_auth_info=True):
    """ Visit _RequestApp.check_basic_auth method's docstring.
    """
    username = url_config['basic-auth-username']
    result = check_basic_auth(cid, env.get('HTTP_AUTHORIZATION', ''), username, url_config['basic-auth-password'])
    is_success = result is True # Note that we need to compare with True

    auth_result = AuthResult(is_success)

    if is_success:
        if needs_auth_info:
            auth_result.auth_info = {b'basic-auth-username': quote_plus(username).encode('utf-8')}
    else:
        auth_result.code = result

    return auth_result

# ################################################################################################################################
# ################################################################################################################################

def enrich_with_sec_data(data_dict, sec_def, sec_def_type):
    data_dict['zato.sec_def'] = {}
    data_dict['zato.sec_def']['id'] = sec_def['id']
    data_dict['zato.sec_def']['name'] = sec_def['name']
    data_dict['zato.sec_def']['username'] = sec_def.get('username')
    data_dict['zato.sec_def']['impl'] = sec_def
    data_dict['zato.sec_def']['type'] = sec_def_type

# ################################################################################################################################
# ################################################################################################################################
