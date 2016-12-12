# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime
from hashlib import sha256
from json import dumps, loads
from operator import attrgetter
from threading import RLock
from traceback import format_exc

# oauth
from oauth.oauth import OAuthDataStore, OAuthConsumer, OAuthRequest, OAuthServer, OAuthSignatureMethod_HMAC_SHA1, \
     OAuthSignatureMethod_PLAINTEXT, OAuthToken

# regex
from regex import compile as re_compile

# sec-wall
from secwall.server import on_basic_auth, on_wsse_pwd
from secwall.wsse import WSSE

# SortedContainers
from sortedcontainers import SortedListWithKey

# Zato
from zato.bunch import Bunch
from zato.common import AUDIT_LOG, DATA_FORMAT, MISC, MSG_PATTERN_TYPE, SEC_DEF_TYPE, TRACE1, URL_TYPE, VAULT, ZATO_NONE
from zato.common.broker_message import code_to_name, CHANNEL, SECURITY, VAULT as VAULT_BROKER_MSG
from zato.common.dispatch import dispatcher
from zato.common.util import parse_tls_channel_security_definition
from zato.server.connection.http_soap import Forbidden, Unauthorized
from zato.server.jwt import JWT

logger = logging.getLogger(__name__)

_internal_url_path_indicator = '{}/zato/'.format(MISC.SEPARATOR)

class Matcher(object):
    """ Matches incoming URL paths in requests received against the pattern it's configured to react to.
    For instance, '/permission/user/{user_id}/group/{group_id}' gets translated and compiled to the regex
    of '/permission/user/(?P<user_id>\\w+)/group/(?P<group_id>\\w+)$' which in runtime is used for matching.
    """
    def __init__(self, pattern):
        self.group_names = []
        self.pattern = pattern
        self.matcher = None
        self.is_static = True
        self._brace_pattern = re_compile('\{[a-zA-Z0-9 _\$.\-|=~^]+\}')
        self._elem_re_template = r'(?P<{}>[a-zA-Z0-9 _\$.\-|=~^]+)'
        self._set_up_matcher(self.pattern)

    def __str__(self):
        return '<{} at {} {} {}>'.format(self.__class__.__name__, hex(id(self)), self.pattern, self.matcher)

    __repr__ = __str__

    def _set_up_matcher(self, pattern):
        orig_groups = self._brace_pattern.findall(pattern)
        groups = [elem.replace('{', '').replace('}', '') for elem in orig_groups]
        groups = [[elem, self._elem_re_template.format(elem)] for elem in groups]

        for idx, (group, re) in enumerate(groups):
            pattern = pattern.replace(orig_groups[idx], re)

        self.group_names.extend([elem[0] for elem in groups])
        self.matcher = re_compile(pattern + '$')

        # No groups = URL is static and has no dynamic variables in the pattern
        self.is_static = not bool(self.group_names)

        # URL path contains /zato = this is a path to an internal service
        self.is_internal = _internal_url_path_indicator in self.pattern

    def match(self, value):
        m = self.matcher.match(value)
        if m:
            return dict(zip(self.group_names, m.groups()))

class OAuthStore(object):
    def __init__(self, oauth_config):
        self.oauth_config = oauth_config

class URLData(OAuthDataStore):
    """ Performs URL matching and security checks.
    """
    def __init__(self, worker, channel_data=None, url_sec=None, basic_auth_config=None, jwt_config=None, ntlm_config=None, \
                 oauth_config=None, tech_acc_config=None, wss_config=None, apikey_config=None, aws_config=None, \
                 openstack_config=None, xpath_sec_config=None, tls_channel_sec_config=None, tls_key_cert_config=None, \
                 vault_conn_sec_config=None, kvdb=None, broker_client=None, odb=None, json_pointer_store=None, xpath_store=None,
                 jwt_secret=None, vault_conn_api=None):
        self.worker = worker
        self.channel_data = SortedListWithKey(channel_data, key=attrgetter('name'))
        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.jwt_config = jwt_config
        self.ntlm_config = ntlm_config
        self.oauth_config = oauth_config
        self.tech_acc_config = tech_acc_config
        self.wss_config = wss_config
        self.apikey_config = apikey_config
        self.aws_config = aws_config
        self.openstack_config = openstack_config
        self.xpath_sec_config = xpath_sec_config
        self.tls_channel_sec_config = tls_channel_sec_config
        self.tls_key_cert_config = tls_key_cert_config
        self.vault_conn_sec_config = vault_conn_sec_config
        self.kvdb = kvdb
        self.broker_client = broker_client
        self.odb = odb
        self.jwt_secret = jwt_secret
        self.vault_conn_api = vault_conn_api

        self.sec_config_getter = Bunch()
        self.sec_config_getter[SEC_DEF_TYPE.BASIC_AUTH] = self.basic_auth_get
        self.sec_config_getter[SEC_DEF_TYPE.APIKEY] = self.apikey_get
        self.sec_config_getter[SEC_DEF_TYPE.JWT] = self.jwt_get

        self.json_pointer_store = json_pointer_store
        self.xpath_store = xpath_store

        self.url_sec_lock = RLock()
        self.update_lock = RLock()
        self._wss = WSSE()
        self._target_separator = MISC.SEPARATOR

        self._oauth_server = OAuthServer(self)
        self._oauth_server.add_signature_method(OAuthSignatureMethod_HMAC_SHA1())
        self._oauth_server.add_signature_method(OAuthSignatureMethod_PLAINTEXT())

        self

        self.url_path_cache = {}

        dispatcher.listen_for_updates(SECURITY, self.dispatcher_callback)
        dispatcher.listen_for_updates(VAULT_BROKER_MSG, self.dispatcher_callback)

# ################################################################################################################################

    def dispatcher_callback(self, event, ctx, **opaque):
        getattr(self, 'on_broker_msg_{}'.format(code_to_name[event]))(ctx)

# ################################################################################################################################

    # OAuth data store API

    def _lookup_oauth(self, username, class_):
        # usernames are unique so we know the first match is ours
        for sec_config in self.oauth_config.values():
            if sec_config.config.username == username:
                return class_(sec_config.config.username, sec_config.config.password)

    def lookup_consumer(self, key):
        return self._lookup_oauth(key, OAuthConsumer)

    def lookup_token(self, token_type, token_field):
        return self._lookup_oauth(token_field, OAuthToken)

    def lookup_nonce(self, oauth_consumer, oauth_token, nonce):
        for sec_config in self.oauth_config.values():
            if sec_config.config.username == oauth_consumer.key:

                # The nonce was reused
                existing_nonce = self.kvdb.has_oauth_nonce(oauth_consumer.key, nonce)
                if existing_nonce:
                    return nonce
                else:
                    # No such nonce so we add it to the store
                    self.kvdb.add_oauth_nonce(
                        oauth_consumer.key, nonce, sec_config.config.max_nonce_log)

    def fetch_request_token(self, oauth_consumer, oauth_callback):
        """-> OAuthToken."""
        raise NotImplementedError

    def fetch_access_token(self, oauth_consumer, oauth_token, oauth_verifier):
        """-> OAuthToken."""
        raise NotImplementedError

    def authorize_request_token(self, oauth_token, user):
        """-> OAuthToken."""
        raise NotImplementedError

# ################################################################################################################################

    def enrich_with_sec_data(self, data_dict, sec_def, sec_def_type):
        data_dict['zato.sec_def'] = {}
        data_dict['zato.sec_def']['id'] = sec_def['id']
        data_dict['zato.sec_def']['name'] = sec_def['name']
        data_dict['zato.sec_def']['username'] = sec_def.get('username')
        data_dict['zato.sec_def']['impl'] = sec_def
        data_dict['zato.sec_def']['type'] = sec_def_type

# ################################################################################################################################

    def authenticate_web_socket(self, cid, sec_def_type, auth, sec_name, _basic_auth=SEC_DEF_TYPE.BASIC_AUTH,
        _jwt=SEC_DEF_TYPE.JWT, _vault_ws=VAULT.WEB_SOCKET):
        """ Authenticates a WebSocket-based connection using HTTP Basic Auth credentials.
        """
        if sec_def_type == _basic_auth:
            auth_func = self._handle_security_basic_auth
            get_func = self.basic_auth_get
            headers = {'HTTP_AUTHORIZATION': 'Basic {}'.format('{}:{}'.format(auth['username'], auth['secret']).encode('base64'))}
        elif sec_def_type == _jwt:
            auth_func = self._handle_security_jwt
            get_func = self.jwt_get
            headers = {'HTTP_AUTHORIZATION': 'Bearer {}'.format(auth['secret'])}
        else:
            auth_func = self._handle_security_vault_conn_sec
            get_func = self.vault_conn_sec_get

            # The defauly header is a dummy one
            headers = {'zato.http.response.headers':{}}
            for key, header in _vault_ws[sec_def_type].iteritems():
                headers[header] = auth[key]

        return auth_func(cid, get_func(sec_name)['config'], None, None, headers, enforce_auth=False)

# ################################################################################################################################

    def _handle_security_apikey(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None, enforce_auth=True):
        """ Performs the authentication against an API key in a specified HTTP header.
        """
        # Find out if the header was provided at all
        if sec_def['username'] not in wsgi_environ:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:`{}`, cid:`{}`'.format(path_info, cid)
                logger.error(msg + ' (No header)')
                raise Unauthorized(cid, msg, 'zato-apikey')
            else:
                return False

        expected_key = sec_def.get('password', '')

        # Passwords are not required
        if expected_key and wsgi_environ[sec_def['username']] != expected_key:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:`{}`, cid:`{}`'.format(path_info, cid)
                logger.error(msg + ' (Invalid key)')
                raise Unauthorized(cid, msg, 'zato-apikey')
            else:
                return False

        return True

# ################################################################################################################################

    def _handle_security_basic_auth(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None,
        enforce_auth=True):
        """ Performs the authentication using HTTP Basic Auth.
        """
        env = {'HTTP_AUTHORIZATION':wsgi_environ.get('HTTP_AUTHORIZATION')}
        url_config = {'basic-auth-username':sec_def.username, 'basic-auth-password':sec_def.password}

        result = on_basic_auth(env, url_config, False)

        if not result:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:[{}], cid:[{}], sec-wall code:[{}], description:[{}]\n'.format(
                    path_info, cid, result.code, result.description)
                logger.error(msg)
                raise Unauthorized(cid, msg, 'Basic realm="{}"'.format(sec_def.realm))
            else:
                return False

        return True

# ################################################################################################################################

    def _handle_security_jwt(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None, enforce_auth=True):
        """ Performs the authentication using a JavaScript Web Token (JWT).
        """
        authorization = wsgi_environ.get('HTTP_AUTHORIZATION')
        if not authorization:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:`{}`, cid:`{}`'.format(path_info, cid)
                logger.error(msg)
                raise Unauthorized(cid, msg, 'JWT')
            else:
                return False

        if not authorization.startswith('Bearer '):
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:`{}`, cid:`{}`'.format(path_info, cid)
                logger.error(msg)
                raise Unauthorized(cid, msg, 'JWT')
            else:
                return False

        token = authorization.split('Bearer ', 1)[1]
        result = JWT(self.kvdb, self.odb, self.jwt_secret).validate(token.encode('utf8'))

        if not result.valid:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:`{}`, cid:`{}`'.format(path_info, cid)
                logger.error(msg)
                raise Unauthorized(cid, msg, 'JWT')
            else:
                return False

        return True

# ################################################################################################################################

    def _handle_security_wss(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None, enforce_auth=True):
        """ Performs the authentication using WS-Security.
        """
        if not body:
            if enforce_auth:
                raise Unauthorized(cid, 'No message body found in [{}]'.format(body), 'zato-wss')
            else:
                return False

        url_config = {}

        url_config['wsse-pwd-password'] = sec_def['password']
        url_config['wsse-pwd-username'] = sec_def['username']
        url_config['wsse-pwd-reject-empty-nonce-creation'] = sec_def['reject_empty_nonce_creat']
        url_config['wsse-pwd-reject-stale-tokens'] = sec_def['reject_stale_tokens']
        url_config['wsse-pwd-reject-expiry-limit'] = sec_def['reject_expiry_limit']
        url_config['wsse-pwd-nonce-freshness-time'] = sec_def['nonce_freshness_time']

        try:
            result = on_wsse_pwd(self._wss, url_config, body, False)
        except Exception, e:
            if enforce_auth:
                msg = 'Could not parse the WS-Security data, body:[{}], e:[{}]'.format(body, format_exc(e))
                raise Unauthorized(cid, msg, 'zato-wss')
            else:
                return False

        if not result:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:[{}], cid:[{}], sec-wall code:[{}], description:[{}]\n'.format(
                    path_info, cid, result.code, result.description)
                logger.error(msg)
                raise Unauthorized(cid, msg, 'zato-wss')
            else:
                return False

        return True

# ################################################################################################################################

    def _handle_security_oauth(self, cid, sec_def, path_info, body, wsgi_environ, post_data, enforce_auth=True):
        """ Performs the authentication using OAuth.
        """
        http_url = '{}://{}{}'.format(wsgi_environ['wsgi.url_scheme'],
            wsgi_environ['HTTP_HOST'], wsgi_environ['RAW_URI'])

        # The underlying library needs Authorization instead of HTTP_AUTHORIZATION
        http_auth_header = wsgi_environ.get('HTTP_AUTHORIZATION')

        if not http_auth_header:
            if enforce_auth:
                msg = 'No Authorization header in wsgi_environ:[%r]'
                logger.error(msg, wsgi_environ)
                raise Unauthorized(cid, 'No Authorization header found', 'OAuth')
            else:
                return False

        wsgi_environ['Authorization'] = http_auth_header

        oauth_request = OAuthRequest.from_request(
            wsgi_environ['REQUEST_METHOD'], http_url, wsgi_environ, post_data.copy(),
            wsgi_environ['QUERY_STRING'])

        if oauth_request is None:
            msg = 'No sig could be built using wsgi_environ:[%r], post_data:[%r]'
            logger.error(msg, wsgi_environ, post_data)

            if enforce_auth:
                raise Unauthorized(cid, 'No parameters to build signature found', 'OAuth')
            else:
                return False

        try:
            self._oauth_server.verify_request(oauth_request)
        except Exception, e:
            if enforce_auth:
                msg = 'Signature verification failed, wsgi_environ:[%r], e:[%s], e.message:[%s]'
                logger.error(msg, wsgi_environ, format_exc(e), e.message)
                raise Unauthorized(cid, 'Signature verification failed', 'OAuth')
            else:
                return False

        else:
            # Store for later use, custom channels may want to inspect it later on
            wsgi_environ['zato.oauth.request'] = oauth_request

        return True

# ################################################################################################################################

    def _handle_security_tech_acc(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None,
        enforce_auth=True):
        """ Performs the authentication using technical accounts.
        """
        zato_headers = ('HTTP_X_ZATO_USER', 'HTTP_X_ZATO_PASSWORD')

        for header in zato_headers:
            if not wsgi_environ.get(header, None):
                if enforce_auth:
                    error_msg = ("[{}] The header [{}] doesn't exist or is empty, URI:[{}, wsgi_environ:[{}]]").\
                        format(cid, header, path_info, wsgi_environ)
                    logger.error(error_msg)
                    raise Unauthorized(cid, error_msg, 'zato-tech-acc')
                else:
                    return False

        # Note that logs get a specific information what went wrong whereas the
        # user gets a generic 'username or password' message
        msg_template = '[{}] The {} is incorrect, URI:[{}], X_ZATO_USER:[{}]'

        if wsgi_environ['HTTP_X_ZATO_USER'] != sec_def.name:
            if enforce_auth:
                error_msg = msg_template.format(cid, 'username', path_info, wsgi_environ['HTTP_X_ZATO_USER'])
                user_msg = msg_template.format(cid, 'username or password', path_info, wsgi_environ['HTTP_X_ZATO_USER'])
                logger.error(error_msg)
                raise Unauthorized(cid, user_msg, 'zato-tech-acc')
            else:
                return False

        incoming_password = sha256(wsgi_environ['HTTP_X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()

        if incoming_password != sec_def.password:
            if enforce_auth:
                error_msg = msg_template.format(cid, 'password', path_info, wsgi_environ['HTTP_X_ZATO_USER'])
                user_msg = msg_template.format(cid, 'username or password', path_info, wsgi_environ['HTTP_X_ZATO_USER'])
                logger.error(error_msg)
                raise Unauthorized(cid, user_msg, 'zato-tech-acc')
            else:
                return False

        return wsgi_environ['HTTP_X_ZATO_USER']

# ################################################################################################################################

    def _handle_security_xpath_sec(self, cid, sec_def, ignored_path_info, ignored_body, wsgi_environ, ignored_post_data=None,
        enforce_auth=True):

        payload = wsgi_environ['zato.request.payload']
        user_msg = 'Invalid username or password'

        username = payload.xpath(sec_def.username_expr)
        if not username:
            if enforce_auth:
                logger.error('%s `%s` expr:`%s`, value:`%r`', user_msg, '(no username)', sec_def.username_expr, username)
                raise Unauthorized(cid, user_msg, 'zato-xpath')
            else:
                return False

        username = username[0]

        if username != sec_def.username:
            if enforce_auth:
                logger.error('%s `%s` expr:`%s`, value:`%r`', user_msg, '(username)', sec_def.username_expr, username)
                raise Unauthorized(cid, user_msg, 'zato-xpath')
            else:
                return False

        if sec_def.get('password_expr'):

            password = payload.xpath(sec_def.password_expr)
            if not password:
                if enforce_auth:
                    logger.error('%s `%s` expr:`%s`', user_msg, '(no password)', sec_def.password_expr)
                    raise Unauthorized(cid, user_msg, 'zato-xpath')
                else:
                    return False

            password = password[0]

            if password != sec_def.password:
                if enforce_auth:
                    logger.error('%s `%s` expr:`%s`', user_msg, '(password)', sec_def.password_expr)
                    raise Unauthorized(cid, user_msg, 'zato-xpath')
                else:
                    return False

        return True

# ################################################################################################################################

    def _handle_security_tls_channel_sec(self, cid, sec_def, ignored_path_info, ignored_body, wsgi_environ,
        ignored_post_data=None, enforce_auth=True):
        user_msg = 'Failed to satisfy TLS conditions'

        for header, expected_value in sec_def.value.items():
            given_value = wsgi_environ.get(header)

            if expected_value != given_value:
                if enforce_auth:
                    logger.error(
                        '%s, header:`%s`, expected:`%s`, given:`%s` (%s)', user_msg, header, expected_value, given_value, cid)
                    raise Unauthorized(cid, user_msg, 'zato-tls-channel-sec')
                else:
                    return False

        return True

# ################################################################################################################################

    def _vault_conn_check_headers(self, client, wsgi_environ, sec_def_config, _auth_method=VAULT.AUTH_METHOD,
        _headers=VAULT.HEADERS):
        """ Authenticate with Vault with credentials extracted from WSGI environment. Authentication is attempted
        in the order of: API keys, username/password, GitHub.
        """

        # API key
        if _headers.TOKEN_VAULT in wsgi_environ:
            return client.authenticate(_auth_method.TOKEN, wsgi_environ[_headers.TOKEN_VAULT])

        # Username/password
        elif _headers.USERNAME in wsgi_environ:
            return client.authenticate(
                _auth_method.USERNAME_PASSWORD, wsgi_environ[_headers.USERNAME], wsgi_environ.get(_headers.PASSWORD))

        # GitHub
        elif _headers.TOKEN_GH in wsgi_environ:
            return client.authenticate(_auth_method.GITHUB, wsgi_environ[_headers.TOKEN_GH])

# ################################################################################################################################

    def _vault_conn_by_method(self, client, method, headers):
        auth_attrs = []
        auth_headers = VAULT.METHOD_HEADER[method]
        auth_headers = [auth_headers] if isinstance(auth_headers, basestring) else auth_headers

        for header in auth_headers:
            auth_attrs.append(headers[header])

        return client.authenticate(method, *auth_attrs)

# ################################################################################################################################

    def _enforce_vault_sec(self, cid, name):
        logger.error('Could not authenticate with Vault `%s`, cid:`%s`', name, cid)
        raise Unauthorized(cid, 'Failed to authenticate', 'zato-vault')

# ################################################################################################################################

    def _handle_security_vault_conn_sec(self, cid, sec_def, path_info, body, wsgi_environ, post_data=None, enforce_auth=True):
        """ Authenticates users with Vault.
        """
        # 1. Has service that will drive us and give us credentials out of incoming data
        # 2. No service but has default authentication method - need to extract those headers that pertain to this method
        # 3. No service and no default authentication method - need to extract all headers that may contain credentials

        sec_def_config = self.vault_conn_sec_config[sec_def.name]['config']
        client = self.worker.vault_conn_api.get_client(sec_def.name)

        try:

            #
            # 1.
            #
            if sec_def_config['service_name']:
                response = self.worker.invoke(sec_def_config['service_name'], {
                    'sec_def': sec_def,
                    'body': body,
                    'environ': wsgi_environ
                }, data_format=DATA_FORMAT.DICT, serialize=False)['response']

                vault_response = self._vault_conn_by_method(client, response['method'], response['headers'])

            else:

                #
                # 2.
                #
                if sec_def_config['default_auth_method']:
                    vault_response = self._vault_conn_by_method(client, sec_def_config['default_auth_method'], wsgi_environ)

                #
                # 3.
                #
                else:
                    vault_response = self._vault_conn_check_headers(client, wsgi_environ, sec_def_config)

        except Exception, e:
            logger.warn(format_exc(e))
            if enforce_auth:
                self._enforce_vault_sec(cid, sec_def.name)
            else:
                return False
        else:
            if vault_response:
                wsgi_environ['zato.http.response.headers'][VAULT.HEADERS.TOKEN_RESPONSE] = vault_response.client_token
                wsgi_environ['zato.http.response.headers'][VAULT.HEADERS.TOKEN_RESPONSE_LEASE] = str(
                    vault_response.lease_duration)
                return vault_response
            else:
                self._enforce_vault_sec(cid, sec_def.name)

# ################################################################################################################################

    def match(self, url_path, soap_action, has_trace1=logger.isEnabledFor(TRACE1)):
        """ Attemps to match the combination of SOAP Action and URL path against
        the list of HTTP channel targets.
        """
        target = '{}{}{}'.format(soap_action, self._target_separator, url_path)

        # Return from cache if already seen
        try:
            return {}, self.url_path_cache[target]
        except KeyError:
            needs_user = not url_path.startswith('/zato')

            for item in self.channel_data:
                if needs_user and item.match_target_compiled.is_internal:
                    continue

                match = item.match_target_compiled.match(target)
                if match is not None:
                    if has_trace1:
                        logger.log(TRACE1, 'Matched target:`%s` with:`%r` and `%r`', target, match, item)

                    # Cache that URL if it's a static one, i.e. does not contain dynamically computed variables
                    if item.match_target_compiled.is_static:
                        self.url_path_cache[target] = item

                    return match, item

            return None, None

# ################################################################################################################################

    def check_rbac_delegated_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store,
            sep=MISC.SEPARATOR, plain_http=URL_TYPE.PLAIN_HTTP):

        is_allowed = False

        http_method = wsgi_environ.get('REQUEST_METHOD')
        http_method_permission_id = worker_store.rbac.http_permissions.get(http_method)

        if not http_method_permission_id:
            logger.error('Invalid HTTP method `%s`, cid:`%s`', http_method, cid)
            raise Forbidden(cid, 'You are not allowed to access this URL\n')

        for role_id, perm_id, resource_id in worker_store.rbac.registry._allowed.iterkeys():

            if is_allowed:
                break

            if perm_id == http_method_permission_id and resource_id == channel_item['service_id']:
                for client_def in worker_store.rbac.role_id_to_client_def[role_id]:
                    _, sec_type, sec_name = client_def.split(sep)

                    sec = Bunch()
                    sec.is_active = True
                    sec.transport = plain_http
                    sec.sec_use_rbac = False
                    sec.sec_def = self.sec_config_getter[sec_type](sec_name)['config']

                    is_allowed = self.check_security(
                        sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store, False)

                    if is_allowed:
                        self.enrich_with_sec_data(wsgi_environ, sec.sec_def, sec_type)
                        break

        if not is_allowed:
            logger.error('Cound not find a matching RBAC definition, cid:`%s`', cid)
            raise Unauthorized(cid, 'You are not allowed to access this resource', 'zato')

# ################################################################################################################################

    def check_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store,
        enforce_auth=True):
        """ Authenticates and authorizes a given request. Returns None on success
        or raises an exception otherwise.
        """
        if sec.sec_use_rbac:
            return self.check_rbac_delegated_security(
                sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store)

        sec_def, sec_def_type = sec.sec_def, sec.sec_def['sec_type']
        handler_name = '_handle_security_%s' % sec_def_type.replace('-', '_')

        if not getattr(self, handler_name)(cid, sec_def, path_info, payload, wsgi_environ, post_data, enforce_auth):
            return False

        # Ok, we now know that the credentials are valid so we can check RBAC permissions if need be.
        if channel_item.get('has_rbac'):
            is_allowed = worker_store.rbac.is_http_client_allowed(
                'sec_def:::{}:::{}'.format(sec.sec_def['sec_type'], sec.sec_def['name']), wsgi_environ['REQUEST_METHOD'],
                channel_item.service_id)

            if not is_allowed:
                raise Forbidden(cid, 'You are not allowed to access this URL\n')

        self.enrich_with_sec_data(wsgi_environ, sec_def, sec_def_type)

        return True

# ################################################################################################################################

    def _update_url_sec(self, msg, sec_def_type, delete=False):
        """ Updates URL security definitions that use the security configuration
        of the name and type given in 'msg' so that existing definitions use
        the new configuration or, optionally, deletes the URL security definition
        altogether if 'delete' is True.
        """
        for target_match, url_info in self.url_sec.items():
            sec_def = url_info.sec_def
            if sec_def != ZATO_NONE and sec_def.sec_type == sec_def_type:
                name = msg.get('old_name') if msg.get('old_name') else msg.get('name')
                if sec_def.name == name:
                    if delete:
                        del self.url_sec[target_match]
                    else:
                        for key, new_value in msg.items():
                            if key in sec_def:
                                sec_def[key] = msg[key]

# ################################################################################################################################

    def _delete_channel_data(self, sec_type, sec_name):
        match_idx = ZATO_NONE
        for item in self.channel_data:
            if item.get('sec_type') == sec_type and item.security_name == sec_name:
                match_idx = self.channel_data.index(item)

        # No error, let's delete channel info
        if match_idx != ZATO_NONE:
            self.channel_data.pop(match_idx)

# ################################################################################################################################

    def _update_apikey(self, name, config):
        config.username = 'HTTP_{}'.format(config.get('username', '').replace('-', '_'))
        self.apikey_config[name] = Bunch()
        self.apikey_config[name].config = config

    def apikey_get(self, name):
        """ Returns the configuration of the API key of the given name.
        """
        with self.url_sec_lock:
            return self.apikey_config.get(name)

    def on_broker_msg_SECURITY_APIKEY_CREATE(self, msg, *args):
        """ Creates a new API key security definition.
        """
        with self.url_sec_lock:
            self._update_apikey(msg.name, msg)

    def on_broker_msg_SECURITY_APIKEY_EDIT(self, msg, *args):
        """ Updates an existing API key security definition.
        """
        with self.url_sec_lock:
            del self.apikey_config[msg.old_name]
            self._update_apikey(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.APIKEY)

    def on_broker_msg_SECURITY_APIKEY_DELETE(self, msg, *args):
        """ Deletes an API key security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('apikey', msg.name)
            del self.apikey_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.APIKEY, True)

    def on_broker_msg_SECURITY_APIKEY_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an API key security definition.
        """
        with self.url_sec_lock:
            self.apikey_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.APIKEY)

# ################################################################################################################################

    def _update_aws(self, name, config):
        self.aws_config[name] = Bunch()
        self.aws_config[name].config = config

    def aws_get(self, name):
        """ Returns the configuration of the AWS security definition of the given name.
        """
        with self.url_sec_lock:
            return self.aws_config.get(name)

    def on_broker_msg_SECURITY_AWS_CREATE(self, msg, *args):
        """ Creates a new AWS security definition.
        """
        with self.url_sec_lock:
            self._update_aws(msg.name, msg)

    def on_broker_msg_SECURITY_AWS_EDIT(self, msg, *args):
        """ Updates an existing AWS security definition.
        """
        with self.url_sec_lock:
            del self.aws_config[msg.old_name]
            self._update_aws(msg.name, msg)

    def on_broker_msg_SECURITY_AWS_DELETE(self, msg, *args):
        """ Deletes an AWS security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('aws', msg.name)
            del self.aws_config[msg.name]

    def on_broker_msg_SECURITY_AWS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an AWS security definition.
        """
        with self.url_sec_lock:
            self.aws_config[msg.name]['config']['password'] = msg.password

# ################################################################################################################################

    def _update_openstack(self, name, config):
        self.openstack_config[name] = Bunch()
        self.openstack_config[name].config = config

    def openstack_get(self, name):
        """ Returns the configuration of the OpenStack security definition of the given name.
        """
        with self.url_sec_lock:
            return self.openstack_config.get(name)

    def on_broker_msg_SECURITY_OPENSTACK_CREATE(self, msg, *args):
        """ Creates a new OpenStack security definition.
        """
        with self.url_sec_lock:
            self._update_openstack(msg.name, msg)

    def on_broker_msg_SECURITY_OPENSTACK_EDIT(self, msg, *args):
        """ Updates an existing OpenStack security definition.
        """
        with self.url_sec_lock:
            del self.openstack_config[msg.old_name]
            self._update_openstack(msg.name, msg)

    def on_broker_msg_SECURITY_OPENSTACK_DELETE(self, msg, *args):
        """ Deletes an OpenStack security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('openstack', msg.name)
            del self.openstack_config[msg.name]

    def on_broker_msg_SECURITY_OPENSTACK_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an OpenStack security definition.
        """
        with self.url_sec_lock:
            self.openstack_config[msg.name]['config']['password'] = msg.password

# ################################################################################################################################

    def _update_basic_auth(self, name, config):
        self.basic_auth_config[name] = Bunch()
        self.basic_auth_config[name].config = config

    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition
        of the given name.
        """
        with self.url_sec_lock:
            return self.basic_auth_config.get(name)

    def on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self._update_basic_auth(msg.name, msg)

    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            del self.basic_auth_config[msg.old_name]
            self._update_basic_auth(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH)

    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('basic_auth', msg.name)
            del self.basic_auth_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH, True)

    def on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self.basic_auth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH)

# ################################################################################################################################

    def _update_vault_conn_sec(self, name, config):
        self.vault_conn_sec_config[name] = Bunch()
        self.vault_conn_sec_config[name].config = config

    def vault_conn_sec_get(self, name):
        """ Returns configuration of a Vault connection of the given name.
        """
        with self.url_sec_lock:
            return self.vault_conn_sec_config.get(name)

    def on_broker_msg_VAULT_CONNECTION_CREATE(self, msg, *args):
        """ Creates a new Vault security definition.
        """
        with self.url_sec_lock:
            self._update_vault_conn_sec(msg.name, msg)

    def on_broker_msg_VAULT_CONNECTION_EDIT(self, msg, *args):
        """ Updates an existing Vault security definition.
        """
        with self.url_sec_lock:
            del self.vault_conn_sec_config[msg.old_name]
            self._update_vault_conn_sec(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.VAULT)

    def on_broker_msg_VAULT_CONNECTION_DELETE(self, msg, *args):
        """ Deletes an Vault security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('vault_conn_sec', msg.name)
            del self.vault_conn_sec_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.VAULT, True)

# ################################################################################################################################

    def _update_jwt(self, name, config):
        self.jwt_config[name] = Bunch()
        self.jwt_config[name].config = config

    def jwt_get(self, name):
        """ Returns configuration of a JWT security definition of the given name.
        """
        with self.url_sec_lock:
            return self.jwt_config.get(name)

    def on_broker_msg_SECURITY_JWT_CREATE(self, msg, *args):
        """ Creates a new JWT security definition.
        """
        with self.url_sec_lock:
            self._update_jwt(msg.name, msg)

    def on_broker_msg_SECURITY_JWT_EDIT(self, msg, *args):
        """ Updates an existing JWT security definition.
        """
        with self.url_sec_lock:
            del self.jwt_config[msg.old_name]
            self._update_jwt(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.JWT)

    def on_broker_msg_SECURITY_JWT_DELETE(self, msg, *args):
        """ Deletes a JWT security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('jwt', msg.name)
            del self.jwt_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.JWT, True)

    def on_broker_msg_SECURITY_JWT_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of a JWT security definition.
        """
        with self.url_sec_lock:
            self.jwt_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.JWT)

# ################################################################################################################################

    def _update_ntlm(self, name, config):
        self.ntlm_config[name] = Bunch()
        self.ntlm_config[name].config = config

    def ntlm_get(self, name):
        """ Returns the configuration of the NTLM security definition of the given name.
        """
        with self.url_sec_lock:
            return self.ntlm_config.get(name)

    def on_broker_msg_SECURITY_NTLM_CREATE(self, msg, *args):
        """ Creates a new NTLM security definition.
        """
        with self.url_sec_lock:
            self._update_ntlm(msg.name, msg)

    def on_broker_msg_SECURITY_NTLM_EDIT(self, msg, *args):
        """ Updates an existing NTLM security definition.
        """
        with self.url_sec_lock:
            del self.ntlm_config[msg.old_name]
            self._update_ntlm(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.NTLM)

    def on_broker_msg_SECURITY_NTLM_DELETE(self, msg, *args):
        """ Deletes an NTLM security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('ntlm', msg.name)
            del self.ntlm_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.NTLM, True)

    def on_broker_msg_SECURITY_NTLM_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an NTLM security definition.
        """
        with self.url_sec_lock:
            self.ntlm_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.NTLM)

# ################################################################################################################################

    def _update_oauth(self, name, config):
        self.oauth_config[name] = Bunch()
        self.oauth_config[name].config = config

    def oauth_get(self, name):
        """ Returns the configuration of the OAuth account of the given name.
        """
        with self.url_sec_lock:
            return self.oauth_config.get(name)

    def on_broker_msg_SECURITY_OAUTH_CREATE(self, msg, *args):
        """ Creates a new OAuth account.
        """
        with self.url_sec_lock:
            self._update_oauth(msg.name, msg)

    def on_broker_msg_SECURITY_OAUTH_EDIT(self, msg, *args):
        """ Updates an existing OAuth account.
        """
        with self.url_sec_lock:
            del self.oauth_config[msg.old_name]
            self._update_oauth(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH)

    def on_broker_msg_SECURITY_OAUTH_DELETE(self, msg, *args):
        """ Deletes an OAuth account.
        """
        with self.url_sec_lock:
            self._delete_channel_data('oauth', msg.name)
            del self.oauth_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH, True)

    def on_broker_msg_SECURITY_OAUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an OAuth account.
        """
        with self.url_sec_lock:
            self.oauth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH)

# ################################################################################################################################

    def _update_tech_acc(self, name, config):
        self.tech_acc_config[name] = Bunch()
        self.tech_acc_config[name].config = config

    def tech_acc_get(self, name):
        """ Returns the configuration of the technical account of the given name.
        """
        with self.url_sec_lock:
            return self.tech_acc_config.get(name)

    def on_broker_msg_SECURITY_TECH_ACC_CREATE(self, msg, *args):
        """ Creates a new technical account.
        """
        with self.url_sec_lock:
            self._update_tech_acc(msg.name, msg)

    def on_broker_msg_SECURITY_TECH_ACC_EDIT(self, msg, *args):
        """ Updates an existing technical account.
        """
        with self.url_sec_lock:
            del self.tech_acc_config[msg.old_name]
            self._update_tech_acc(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.TECH_ACCOUNT)

    def on_broker_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        with self.url_sec_lock:
            self._delete_channel_data('tech_acc', msg.name)
            del self.tech_acc_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.TECH_ACCOUNT, True)

    def on_broker_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        with self.url_sec_lock:
            # The message's 'password' attribute already takes the salt
            # into account (pun intended ;-))
            self.tech_acc_config[msg.name]['config']['password'] = msg.password
            self.tech_acc_config[msg.name]['config']['salt'] = msg.salt
            self._update_url_sec(msg, SEC_DEF_TYPE.TECH_ACCOUNT)

# ################################################################################################################################

    def _update_wss(self, name, config):
        if name in self.wss_config:
            self.wss_config[name].clear()

        self.wss_config[name] = Bunch()
        self.wss_config[name].config = config

    def wss_get(self, name):
        """ Returns the configuration of the WSS definition of the given name.
        """
        with self.url_sec_lock:
            return self.wss_config.get(name)

    def on_broker_msg_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        with self.url_sec_lock:
            self._update_wss(msg.name, msg)

    def on_broker_msg_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        with self.url_sec_lock:
            del self.wss_config[msg.old_name]
            self._update_wss(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.WSS)

    def on_broker_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('wss', msg.name)
            del self.wss_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.WSS, True)

    def on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        with self.url_sec_lock:
            # The message's 'password' attribute already takes the salt
            # into account.
            self.wss_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.WSS)

# ################################################################################################################################

    def _update_xpath_sec(self, name, config):
        self.xpath_sec_config[name] = Bunch()
        self.xpath_sec_config[name].config = config

    def xpath_sec_get(self, name):
        """ Returns the configuration of the XPath security definition
        of the given name.
        """
        with self.url_sec_lock:
            return self.xpath_sec_config.get(name)

    def on_broker_msg_SECURITY_XPATH_SEC_CREATE(self, msg, *args):
        """ Creates a new XPath security definition.
        """
        with self.url_sec_lock:
            self._update_xpath_sec(msg.name, msg)

    def on_broker_msg_SECURITY_XPATH_SEC_EDIT(self, msg, *args):
        """ Updates an existing XPath security definition.
        """
        with self.url_sec_lock:
            del self.xpath_sec_config[msg.old_name]
            self._update_xpath_sec(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.XPATH_SEC)

    def on_broker_msg_SECURITY_XPATH_SEC_DELETE(self, msg, *args):
        """ Deletes an XPath security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('xpath_sec', msg.name)
            del self.xpath_sec_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.XPATH_SEC, True)

    def on_broker_msg_SECURITY_XPATH_SEC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an XPath security definition.
        """
        with self.url_sec_lock:
            self.xpath_sec_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.XPATH_SEC)

# ################################################################################################################################

    def _update_tls_channel_sec(self, name, config):
        self.tls_channel_sec_config[name] = Bunch()
        self.tls_channel_sec_config[name].config = config
        self.tls_channel_sec_config[name].config.value = dict(parse_tls_channel_security_definition(config.value))

    def tls_channel_security_get(self, name):
        with self.url_sec_lock:
            return self.tls_channel_sec_config.get(name)

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_CREATE(self, msg, *args):
        """ Creates a new security definition based on TLS certificates.
        """
        with self.url_sec_lock:
            self._update_tls_channel_sec(msg.name, msg)

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_EDIT(self, msg, *args):
        """ Updates an existing security definition based on TLS certificates.
        """
        with self.url_sec_lock:
            del self.tls_channel_sec_config[msg.old_name]
            self._update_tls_channel_sec(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.TLS_CHANNEL_SEC)

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_DELETE(self, msg, *args):
        """ Deletes a security definition based on TLS certificates.
        """
        with self.url_sec_lock:
            del self.tls_channel_sec_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.TLS_CHANNEL_SEC, True)

# ################################################################################################################################

    def _update_tls_key_cert(self, name, config):
        self.tls_key_cert_config[name] = Bunch()
        self.tls_key_cert_config[name].config = config

    def tls_key_cert_get(self, name):
        with self.url_sec_lock:
            return self.tls_key_cert_config.get(name)

    def on_broker_msg_SECURITY_TLS_KEY_CERT_CREATE(self, msg, *args):
        """ Creates a new TLS key/cert security definition.
        """
        with self.url_sec_lock:
            self._update_tls_key_cert(msg.name, msg)

    def on_broker_msg_SECURITY_TLS_KEY_CERT_EDIT(self, msg, *args):
        """ Updates an existing TLS key/cert security definition.
        """
        with self.url_sec_lock:
            del self.tls_key_cert_config[msg.old_name]
            self._update_tls_key_cert(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.TLS_KEY_CERT)

    def on_broker_msg_SECURITY_TLS_KEY_CERT_DELETE(self, msg, *args):
        """ Deletes an TLS key/cert security definition.
        """
        with self.url_sec_lock:
            del self.tls_key_cert_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.TLS_KEY_CERT, True)

# ################################################################################################################################

    def _channel_item_from_msg(self, msg, match_target, old_data={}):
        """ Creates a channel info bunch out of an incoming CREATE_EDIT message.
        """
        channel_item = Bunch()
        for name in('connection', 'content_type', 'data_format', 'host', 'id', 'has_rbac', 'impl_name', 'is_active',
            'is_internal', 'merge_url_params_req', 'method', 'name', 'params_pri', 'ping_method', 'pool_size', 'service_id',
            'service_name', 'soap_action', 'soap_version', 'transport', 'url_params_pri', 'url_path', 'sec_use_rbac'):

            channel_item[name] = msg[name]

        if msg.get('security_id'):
            channel_item['sec_type'] = msg['sec_type']
            channel_item['security_id'] = msg['security_id']
            channel_item['security_name'] = msg['security_name']

        channel_item.audit_enabled = old_data.get('audit_enabled', False)
        channel_item.audit_max_payload = old_data.get('audit_max_payload', 0)
        channel_item.audit_repl_patt_type = old_data.get('audit_repl_patt_type', None)
        channel_item.replace_patterns_json_pointer = old_data.get('replace_patterns_json_pointer', [])
        channel_item.replace_patterns_xpath = old_data.get('replace_patterns_xpath', [])

        channel_item.service_impl_name = msg.impl_name
        channel_item.match_target = match_target
        channel_item.match_target_compiled = Matcher(channel_item.match_target)

        return channel_item

    def _sec_info_from_msg(self, msg):
        """ Creates a security info bunch out of an incoming CREATE_EDIT message.
        """
        sec_info = Bunch()
        sec_info.id = msg.id
        sec_info.is_active = msg.is_active
        sec_info.data_format = msg.data_format
        sec_info.transport = msg.transport
        sec_info.sec_use_rbac = msg.sec_use_rbac

        if msg.get('security_name'):
            sec_info.sec_def = Bunch()
            sec_config = getattr(self, '{}_config'.format(msg['sec_type']))
            config_item = sec_config[msg['security_name']]

            for k, v in config_item['config'].items():
                sec_info.sec_def[k] = config_item['config'][k]
        else:
            sec_info.sec_def = ZATO_NONE

        return sec_info

    def _create_channel(self, msg, old_data):
        """ Creates a new channel, both its core data and the related security definition.
        Clears out URL cache for that entry, if it existed at all.
        """
        match_target = '{}{}{}'.format(msg.soap_action, MISC.SEPARATOR, msg.url_path)
        self.channel_data.add(self._channel_item_from_msg(msg, match_target, old_data))
        self.url_sec[match_target] = self._sec_info_from_msg(msg)
        self.url_path_cache.pop(match_target, None)

    def _delete_channel(self, msg):
        """ Deletes a channel, both its core data and the related security definition. Clears relevant
        entry in URL cache. Returns the deleted data.
        """
        old_match_target = '{}{}{}'.format(
            msg.get('old_soap_action'), MISC.SEPARATOR, msg.get('old_url_path'))

        # In case of an internal error, we won't have the match all
        match_idx = ZATO_NONE
        for item in self.channel_data:
            if item.match_target == old_match_target:
                match_idx = self.channel_data.index(item)

        # No error, let's delete channel info
        if match_idx != ZATO_NONE:
            old_data = self.channel_data.pop(match_idx)
        else:
            old_data = {}

        # Channel's security now
        del self.url_sec[old_match_target]

        # Delete from URL cache
        self.url_path_cache.pop(old_match_target, None)

        return old_data

    def on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        with self.url_sec_lock:
            # Only edits have 'old_name', creates don't. So for edits we delete
            # the channel and later recreate it while creates, obviously,
            # get to creation only.
            if msg.get('old_name'):
                old_data = self._delete_channel(msg)
            else:
                old_data = {}

            self._create_channel(msg, old_data)

    def on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        with self.url_sec_lock:
            self._delete_channel(msg)

# ################################################################################################################################

    def replace_payload(self, pattern_name, payload, pattern_type):
        """ Replaces elements in a given payload using either JSON Pointer or XPath
        """
        store = self.json_pointer_store if pattern_type == MSG_PATTERN_TYPE.JSON_POINTER.id else self.xpath_store

        logger.debug('Replacing pattern:`%r` in`%r` , store:`%r`', pattern_name, payload, store)

        return store.set(pattern_name, payload, AUDIT_LOG.REPLACE_WITH, True)

# ################################################################################################################################

    def _dump_wsgi_environ(self, wsgi_environ):
        """ A convenience method to dump WSGI environment with all the element repr'ed.
        """
        # TODO: There should be another copy of WSGI environ added with password masked out
        env = wsgi_environ.items()
        for elem in env:
            if elem[0] == 'zato.http.channel_item':
                elem[1]['password'] = AUDIT_LOG.REPLACE_WITH

        return dumps({key: repr(value) for key, value in env})

    def audit_set_request(self, cid, channel_item, payload, wsgi_environ):
        """ Stores initial audit information, right after receiving a request.
        """
        if channel_item['audit_repl_patt_type'] == MSG_PATTERN_TYPE.JSON_POINTER.id:
            payload = loads(payload) if payload else ''
            pattern_list = channel_item['replace_patterns_json_pointer']
        else:
            pattern_list = channel_item['replace_patterns_xpath']

        if payload:
            for name in pattern_list:
                logger.debug('Before `%r`:`%r`', name, payload)
                payload = self.replace_payload(name, payload, channel_item.audit_repl_patt_type)
                logger.debug('After `%r`:`%r`', name, payload)

        if channel_item['audit_repl_patt_type'] == MSG_PATTERN_TYPE.JSON_POINTER.id:
            payload = dumps(payload)

        if channel_item['audit_max_payload']:
            payload = payload[:channel_item['audit_max_payload']]

        remote_addr = wsgi_environ.get('HTTP_X_FORWARDED_FOR')
        if not remote_addr:
            remote_addr = wsgi_environ.get('REMOTE_ADDR', '(None)')

        self.odb.audit_set_request_http_soap(channel_item['id'], channel_item['name'], cid,
            channel_item['transport'], channel_item['connection'], datetime.utcnow(),
            channel_item.get('username'), remote_addr, self._dump_wsgi_environ(wsgi_environ), payload)

    def audit_set_response(self, cid, response, wsgi_environ):
        """ Stores audit info regarding a response to a previous request.
        """
        payload = dumps({
            'cid': cid,
            'invoke_ok': wsgi_environ['zato.http.response.status'][0] not in ('4', '5'),
            'auth_ok': wsgi_environ['zato.http.response.status'][0] != '4',
            'resp_time': datetime.utcnow().isoformat(),
            'resp_headers': self._dump_wsgi_environ(wsgi_environ),
            'resp_payload': response,
        })

        self.broker_client.publish({
            'cid': cid,
            'data_format':DATA_FORMAT.JSON,
            'action': CHANNEL.HTTP_SOAP_AUDIT_RESPONSE.value,
            'payload': payload,
            'service': 'zato.http-soap.set-audit-response-data'
        })

    def on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_CONFIG(self, msg):
        for item in self.channel_data:
            if item.id == msg.id:
                item.audit_max_payload = msg.audit_max_payload

    def on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_STATE(self, msg):
        for item in self.channel_data:
            if item.id == msg.id:
                item.audit_enabled = msg.audit_enabled
                break

    def on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_PATTERNS(self, msg):
        for item in self.channel_data:
            if item.id == msg.id:
                item.audit_repl_patt_type = msg.audit_repl_patt_type

                if item.audit_repl_patt_type == MSG_PATTERN_TYPE.JSON_POINTER.id:
                    item.replace_patterns_json_pointer = msg.pattern_list
                else:
                    item.replace_patterns_xpath = msg.pattern_list

                break

    def _yield_pattern_list(self, msg):
        for item in self.channel_data:
            if msg.msg_pattern_type == MSG_PATTERN_TYPE.JSON_POINTER.id:
                pattern_list = item.replace_patterns_json_pointer
            else:
                pattern_list = item.replace_patterns_xpath

            if pattern_list:
                yield item, pattern_list

    def on_broker_msg_MSG_JSON_POINTER_EDIT(self, msg):
        with self.update_lock:
            for _, pattern_list in self._yield_pattern_list(msg):
                if msg.old_name in pattern_list:
                    pattern_list.remove(msg.old_name)
                    pattern_list.append(msg.name)

    def on_broker_msg_MSG_JSON_POINTER_DELETE(self, msg):
        with self.update_lock:
            for item, pattern_list in self._yield_pattern_list(msg):

                try:
                    pattern_list.remove(msg.name)
                except ValueError:
                    # It's OK, this item wasn't using that particular JSON Pointer
                    pass

                yield item.id, pattern_list

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_CA_CERT_CREATE(self, msg):
        # Ignored, does nothing.
        pass

    on_broker_msg_SECURITY_TLS_CA_CERT_DELETE = on_broker_msg_SECURITY_TLS_CA_CERT_EDIT = on_broker_msg_SECURITY_TLS_CA_CERT_CREATE
