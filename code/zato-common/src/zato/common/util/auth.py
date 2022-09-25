# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from base64 import b64decode

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode
from six import PY2

# Zato
from zato.common.api import AUTH_RESULT

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
from future.moves.urllib.parse import quote_plus

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

AUTH_WSSE_NO_DATA = '0003.0001'
AUTH_WSSE_VALIDATION_ERROR = '0003.0002'

AUTH_BASIC_NO_AUTH = '0004.0001'
AUTH_BASIC_INVALID_PREFIX = '0004.0002'
AUTH_BASIC_USERNAME_OR_PASSWORD_MISMATCH = '0004.0003'

# ################################################################################################################################
# ################################################################################################################################

def on_wsse_pwd(wsse, url_config, data, needs_auth_info=True):
    """ Visit _RequestApp._on_wsse_pwd method's docstring.
    """
    if not data:
        return AuthResult(False, AUTH_WSSE_NO_DATA)

    request = etree.fromstring(data)
    try:
        ok, wsse_username = wsse.validate(request, url_config)
    except SecurityException as e:
        return AuthResult(False, AUTH_WSSE_VALIDATION_ERROR, e.description)
    else:
        auth_result = AuthResult(True, '0')
        if needs_auth_info:
            auth_result.auth_info = {b'wsse-pwd-username': str(wsse_username)}

        return auth_result

# ################################################################################################################################
# ################################################################################################################################

def _on_basic_auth(auth, expected_username, expected_password):
    """ A low-level call for checking the HTTP Basic Auth credentials.
    """
    if not auth:
        return AUTH_BASIC_NO_AUTH

    prefix = 'Basic '
    if not auth.startswith(prefix):
        return AUTH_BASIC_INVALID_PREFIX

    _, auth = auth.split(prefix)
    auth = auth.strip()
    auth = b64decode(auth)
    auth = auth if isinstance(auth, unicode) else auth.decode('utf8')
    username, password = auth.split(':', 1)

    if username == expected_username and password == expected_password:
        return True
    else:
        return AUTH_BASIC_USERNAME_OR_PASSWORD_MISMATCH
    # return True

# ################################################################################################################################
# ################################################################################################################################

def on_basic_auth(env, url_config, needs_auth_info=True):
    """ Visit _RequestApp._on_basic_auth method's docstring.
    """
    username = url_config['basic-auth-username']
    result = _on_basic_auth(env.get('HTTP_AUTHORIZATION', ''), username, url_config['basic-auth-password'])
    is_success = result is True # Yes, need to check for True

    auth_result = AuthResult(is_success)

    if is_success:
        if needs_auth_info:
            auth_result.auth_info = {b'basic-auth-username': quote_plus(username).encode('utf-8')}
    else:
        auth_result.code = result

    return auth_result

# ################################################################################################################################
# ################################################################################################################################
