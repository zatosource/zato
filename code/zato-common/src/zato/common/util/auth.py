# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from base64 import b64decode, b64encode

# Python 2/3 compatibility
from past.builtins import unicode
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

# stdlib
from hashlib import sha1
from datetime import datetime

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

class AuthResult(object):
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

soap_date_time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

soapenv_namespace = 'http://schemas.xmlsoap.org/soap/envelope/'

soap_body_path = '/soapenv:Envelope/soapenv:Body'
soap_body_xpath = etree.XPath(soap_body_path, namespaces={'soapenv':soapenv_namespace})

wsse_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
wsu_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'

wss_namespaces = {'soapenv':soapenv_namespace, 'wsse':wsse_namespace, 'wsu':wsu_namespace}

wsse_password_type_text = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
wsse_password_type_digest = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest'

supported_wsse_password_types = (wsse_password_type_text, wsse_password_type_digest)

wsse_username_token_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken'
wsse_username_token_xpath = etree.XPath(wsse_username_token_path, namespaces=wss_namespaces)

wsse_username_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username'
wsse_username_xpath = etree.XPath(wsse_username_path, namespaces=wss_namespaces)

wsse_password_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password'
wsse_password_xpath = etree.XPath(wsse_password_path, namespaces=wss_namespaces)

wsse_password_type_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password/@Type'
wsse_password_type_xpath = etree.XPath(wsse_password_type_path, namespaces=wss_namespaces)

wsse_nonce_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce'
wsse_nonce_xpath = etree.XPath(wsse_nonce_path, namespaces=wss_namespaces)

wsu_username_created_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created'
wsu_username_created_xpath = etree.XPath(wsu_username_created_path, namespaces=wss_namespaces)

class WSSE(object):
    """ Implements authentication using WS-Security.
    """

    def _replace_username_token_elem(self, soap, old_elem, attr_name):
        """ A utility function for replacing passwords and nonces with '***'
        for the purpose of logging the messages without worrying of disclosing
        any data known to be secret.
        """

        old_elem = old_elem[0]
        attr = old_elem.get(attr_name)

        username_token = wsse_username_token_xpath(soap)
        if not username_token:
            self.error(expected_element=wsse_username_token_path)

        username_token = username_token[0]

        elem_idx = username_token.index(old_elem)
        username_token.remove(old_elem)

        new_elem = etree.Element(old_elem.tag)
        new_elem.set(attr_name, attr)
        new_elem.text = '***'
        username_token.insert(elem_idx, new_elem)

        return old_elem.text, attr

    def _get_digest(self, password, nonce, created):
        """ Returns the password's expected digest.
        """
        nonce = b64decode(nonce)
        concat = nonce + created + password

        h = sha1()
        h.update(concat)

        return b64encode(h.digest()).rstrip('\n')

    def error(self, description='', expected_element='', soap=None):
        """ A utility function for exceptions in erronous situations. May be
        subclassed if error reporting needs to be customized. The 'soap'
        parameter is guaranteed to have WSSE password and token replaced
        with '***' characters. Note that default implementation doesn't use
        the 'soap' parameter however the subclasses are free to do so.
        """
        msg = description
        if expected_element:
            if description:
                msg += '. '
            msg += 'Element [{0}] doesn\'t exist'.format(expected_element)

        raise SecurityException(msg)

    def check_nonce(self, wsse_nonce, now, nonce_freshness_time):
        """ Checks whether the nonce has been already seen. Default implementation
        lets all nonces in. More sophisticated subclasses may wish to override
        this method and check the nonce against a cache of some sort.
        """
        return False

    def on_invalid_username(self, config, given, message):
        """ Invoked when the expected and given usernames don't match.
        """
        self.error('Invalid username or password')

    def on_invalid_password(self, config, given_username, given_password, message):
        """ Invoked when the expected and given passwords don't match.
        """
        self.error('Invalid username or password')

    def on_username_token_expired(self, config, elapsed, message):
        """ Invoked when the username token has been found to be expired.
        """
        self.error('UsernameToken has expired')

    def on_nonce_non_unique(self, config, nonce, now, message):
        """ Invoked when the nonce has been found not to be unique.
        """
        self.error('Nonce [{0}] is not unique'.format(nonce))

    def validate(self, soap, config):

        # Shadow the password and a nonce before any processing, getting
        # their values along the way.

        wsse_password = wsse_password_xpath(soap)
        if wsse_password:
            wsse_password, wsse_password_type = self._replace_username_token_elem(soap, wsse_password, 'Type')

        wsse_nonce = wsse_nonce_xpath(soap)
        if wsse_nonce:
            wsse_nonce, wsse_encoding_type = self._replace_username_token_elem(soap, wsse_nonce, 'EncodingType')

        wsse_username = wsse_username_xpath(soap)
        if not wsse_username:
            self.error('No username sent', wsse_username_path, soap)

        wsse_username = wsse_username[0].text

        if config['wsse-pwd-username'] != wsse_username:
            self.on_invalid_username(config, wsse_username, soap)

        if not wsse_password_type:
            self.error('No password type sent', wsse_password_type_path, soap)

        if not wsse_password_type in supported_wsse_password_types:
            msg = 'Unsupported password type=[{0}], not in [{1}]'.format(wsse_password_type, supported_wsse_password_types)
            self.error(msg, soap=soap)

        now = datetime.utcnow()

        if config['wsse-pwd-reject-empty-nonce-creation']:

            wsu_username_created = wsu_username_created_xpath(soap)
            if not all((wsse_nonce, wsu_username_created)):
                self.error('Both nonce and creation timestamp must be given', soap=soap)
            else:
                if wsu_username_created:
                    wsu_username_created = wsu_username_created[0].text

            # Check nonce freshness and report error if the UsernameToken is stale.
            token_created = datetime.strptime(wsu_username_created, soap_date_time_format)

            elapsed = (now - token_created)

            if config['wsse-pwd-reject-stale-tokens'] and elapsed.seconds > config['wsse-pwd-reject-expiry-limit']:
                self.on_username_token_expired(config, elapsed, soap)

        if config.get('wsse-pwd-password-digest'):
            expected_password = self._get_digest(config['wsse-pwd-password'], wsse_nonce, wsu_username_created)
        else:
            expected_password = config.get('wsse-pwd-password')

        if wsse_password != expected_password:
            self.on_invalid_password(config, wsse_username, wsse_password, soap)

        # Have we already seen such a nonce?
        if self.check_nonce(wsse_nonce, now, config.get('wsse-pwd-nonce-freshness-time')):
            self.on_nonce_non_unique(config, wsse_nonce, now, soap)

        # All good, we let the client in.
        return True, wsse_username

# ################################################################################################################################
# ################################################################################################################################
