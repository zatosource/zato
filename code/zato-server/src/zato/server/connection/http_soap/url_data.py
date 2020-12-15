# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from base64 import b64encode
from operator import itemgetter
from threading import RLock
from traceback import format_exc

# Python 2/3 compatibility
from future.utils import iteritems, iterkeys, itervalues
from past.builtins import basestring, unicode
from six import PY2

# Zato
from zato.bunch import Bunch
from zato.common.api import CONNECTION, DATA_FORMAT, MISC, RATE_LIMIT, SEC_DEF_TYPE, URL_TYPE, ZATO_NONE
from zato.common.vault_ import VAULT
from zato.common.broker_message import code_to_name, SECURITY, VAULT as VAULT_BROKER_MSG
from zato.common.dispatch import dispatcher
from zato.common.util.api import parse_tls_channel_security_definition, update_apikey_username_to_channel
from zato.common.util.auth import on_basic_auth, on_wsse_pwd, WSSE
from zato.common.util.url_dispatcher import get_match_target
from zato.server.connection.http_soap import Forbidden, Unauthorized
from zato.server.jwt import JWT
from zato.url_dispatcher import CyURLData, Matcher

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:
    from zato.server.base.worker import WorkerStore

    # For pyflakes
    WorkerStore = WorkerStore

# ################################################################################################################################

if PY2:
    from oauth.oauth import OAuthDataStore, OAuthConsumer, OAuthRequest, OAuthServer, OAuthSignatureMethod_HMAC_SHA1, \
         OAuthSignatureMethod_PLAINTEXT, OAuthToken
else:
    class _Placeholder(object):
        def __init__(self, *ignored_args, **ignored_kwargs):
            pass

        def _placeholder(self, *ignored_args, **ignored_kwargs):
            pass

        add_signature_method = _placeholder

    OAuthDataStore = OAuthConsumer = OAuthRequest = OAuthServer = OAuthSignatureMethod_HMAC_SHA1 = \
        OAuthSignatureMethod_PLAINTEXT = OAuthToken = _Placeholder

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_internal_url_path_indicator = '{}/zato/'.format(MISC.SEPARATOR)

# ################################################################################################################################
# ################################################################################################################################

class OAuthStore(object):
    def __init__(self, oauth_config):
        self.oauth_config = oauth_config

# ################################################################################################################################
# ################################################################################################################################

class URLData(CyURLData, OAuthDataStore):
    """ Performs URL matching and security checks.
    """
    def __init__(self, worker, channel_data=None, url_sec=None, basic_auth_config=None, jwt_config=None, ntlm_config=None, \
                 oauth_config=None, wss_config=None, apikey_config=None, aws_config=None, \
                 openstack_config=None, xpath_sec_config=None, tls_channel_sec_config=None, tls_key_cert_config=None, \
                 vault_conn_sec_config=None, kvdb=None, broker_client=None, odb=None, json_pointer_store=None, xpath_store=None,
                 jwt_secret=None, vault_conn_api=None):
        super(URLData, self).__init__(channel_data)
        self.worker = worker # type: WorkerStore
        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config # type: dict
        self.jwt_config = jwt_config # type: dict
        self.ntlm_config = ntlm_config # type: dict
        self.oauth_config = oauth_config # type: dict
        self.wss_config = wss_config # type: dict
        self.apikey_config = apikey_config # type: dict
        self.aws_config = aws_config # type: dict
        self.openstack_config = openstack_config # type: dict
        self.xpath_sec_config = xpath_sec_config # type: dict
        self.tls_channel_sec_config = tls_channel_sec_config # type: dict
        self.tls_key_cert_config = tls_key_cert_config # type: dict
        self.vault_conn_sec_config = vault_conn_sec_config # type: dict
        self.kvdb = kvdb
        self.broker_client = broker_client
        self.odb = odb
        self.jwt_secret = jwt_secret
        self.vault_conn_api = vault_conn_api
        self.rbac_auth_type_hooks = self.worker.server.fs_server_config.rbac.auth_type_hook

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

        dispatcher.listen_for_updates(SECURITY, self.dispatcher_callback)
        dispatcher.listen_for_updates(VAULT_BROKER_MSG, self.dispatcher_callback)

        # Needs always to be sorted by name in case of conflicts in paths resolution
        self.sort_channel_data()

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

    def authenticate_web_socket(self, cid, sec_def_type, auth, sec_name, vault_conn_default_auth_method,
        initial_http_wsgi_environ, initial_headers=None, _basic_auth=SEC_DEF_TYPE.BASIC_AUTH, _jwt=SEC_DEF_TYPE.JWT,
        _vault_sec_def_type=SEC_DEF_TYPE.VAULT,
        _vault_ws=VAULT.WEB_SOCKET):
        """ Authenticates a WebSocket-based connection using HTTP Basic Auth credentials.
        """
        headers = initial_headers if initial_headers is not None else {}
        headers['zato.ws.initial_http_wsgi_environ'] = initial_http_wsgi_environ

        if sec_def_type == _basic_auth:
            auth_func = self._handle_security_basic_auth
            get_func = self.basic_auth_get

            username = auth['username']
            secret = auth['secret']

            username = username if isinstance(username, unicode) else username.decode('utf8')
            secret = secret if isinstance(secret, unicode) else secret.decode('utf8')

            auth_info = '{}:{}'.format(username, secret)
            auth_info = auth_info.encode('utf8')

            auth = b64encode(auth_info)
            headers['HTTP_AUTHORIZATION'] = 'Basic {}'.format(auth.decode('utf8'))

        elif sec_def_type == _jwt:
            auth_func = self._handle_security_jwt
            get_func = self.jwt_get
            headers['HTTP_AUTHORIZATION'] ='Bearer {}'.format(auth['secret'])

        elif sec_def_type == _vault_sec_def_type:
            auth_func = self._handle_security_vault_conn_sec
            get_func = self.vault_conn_sec_get

            headers['zato.http.response.headers'] = {}
            for header_info in itervalues(_vault_ws):
                for key, header in iteritems(header_info):
                    headers[header] = auth[key]

        else:
            raise ValueError('Unrecognized sec_def_type:`{}`'.format(sec_def_type))

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
                msg_log = 'Unauthorized; path_info:`{}`, cid:`{}`, sec-wall code:`{}`, description:`{}`\n'.format(
                    path_info, cid, result.code, result.description)
                msg_exc = 'Unauthorized; cid={}'.format(cid)
                logger.error(msg_log)
                raise Unauthorized(cid, msg_exc, 'Basic realm="{}"'.format(sec_def.realm))
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
        result = JWT(self.kvdb, self.odb, self.worker.server.decrypt, self.jwt_secret).validate(
            sec_def.username, token.encode('utf8'))

        if not result.valid:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:`{}`, cid:`{}`'.format(path_info, cid)
                logger.error(msg)
                raise Unauthorized(cid, msg, 'JWT')
            else:
                return False

        return result

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
        except Exception:
            if enforce_auth:
                msg = 'Could not parse the WS-Security data, body:`{}`, e:`{}`'.format(body, format_exc())
                raise Unauthorized(cid, msg, 'zato-wss')
            else:
                return False

        if not result:
            if enforce_auth:
                msg = 'UNAUTHORIZED path_info:`{}`, cid:`{}`, sec-wall code:`{}`, description:`{}`\n'.format(
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
        except Exception as e:
            if enforce_auth:
                msg = 'Signature verification failed, wsgi_environ:`%r`, e:`%s`, e.message:`%s`'
                logger.error(msg, wsgi_environ, format_exc(e), e.message)
                raise Unauthorized(cid, 'Signature verification failed', 'OAuth')
            else:
                return False

        else:
            # Store for later use, custom channels may want to inspect it later on
            wsgi_environ['zato.oauth.request'] = oauth_request

        return True

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
            return client.authenticate(_auth_method.TOKEN.id, wsgi_environ[_headers.TOKEN_VAULT])

        # Username/password
        elif _headers.USERNAME in wsgi_environ:
            return client.authenticate(
                _auth_method.USERNAME_PASSWORD.id, wsgi_environ[_headers.USERNAME], wsgi_environ.get(_headers.PASSWORD))

        # GitHub
        elif _headers.TOKEN_GH in wsgi_environ:
            return client.authenticate(_auth_method.GITHUB.id, wsgi_environ[_headers.TOKEN_GH])

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
            if sec_def_config.get('service_name'):
                response = self.worker.invoke(sec_def_config['service_name'], {
                    'sec_def': sec_def,
                    'body': body,
                    'environ': wsgi_environ
                }, data_format=DATA_FORMAT.DICT, serialize=False)

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

        except Exception:
            logger.warn(format_exc())
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

    def check_rbac_delegated_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store,
            sep=MISC.SEPARATOR, plain_http=URL_TYPE.PLAIN_HTTP, _empty_client_def=tuple()):

        auth_result = False

        http_method = wsgi_environ.get('REQUEST_METHOD')
        http_method_permission_id = worker_store.rbac.http_permissions.get(http_method)

        if not http_method_permission_id:
            logger.error('Invalid HTTP method `%s`, cid:`%s`', http_method, cid)
            raise Forbidden(cid, 'You are not allowed to access this URL\n')

        for role_id, perm_id, resource_id in iterkeys(worker_store.rbac.registry._allowed):

            if auth_result:
                return auth_result

            if perm_id == http_method_permission_id and resource_id == channel_item['service_id']:
                for client_def in worker_store.rbac.role_id_to_client_def.get(role_id, _empty_client_def):

                    _, sec_type, sec_name = client_def.split(sep)

                    _sec = Bunch()
                    _sec.is_active = True
                    _sec.transport = plain_http
                    _sec.sec_use_rbac = False
                    _sec.sec_def = self.sec_config_getter[sec_type](sec_name)['config']

                    auth_result = self.check_security(
                        _sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store, False)

                    if auth_result:

                        # If input sec object is a dict/Bunch-like one, it means that we have just confirmed
                        # credentials of the underlying security definition behind an RBAC one,
                        # in which case we need to overwrite the sec object's sec_def attribute and make it
                        # point to the one that we have just found. Otherwise, it would still point to ZATO_NONE.
                        if hasattr(sec, 'keys'):
                            sec.sec_def = _sec['sec_def']

                        self.enrich_with_sec_data(wsgi_environ, _sec.sec_def, sec_type)
                        break

        if auth_result:
            return auth_result
        else:
            logger.warn('None of RBAC definitions allowed request in, cid:`%s`', cid)

            # We need to return 401 Unauthorized but we need to send a challenge, i.e. authentication type
            # that this channel can be accessed through so we as the last resort, we invoke a hook
            # service which decides what it should be. If there is no hook, we default to 'zato'.
            if channel_item['url_path'] in self.rbac_auth_type_hooks:
                service_name = self.rbac_auth_type_hooks[channel_item['url_path']]
                response = self.worker.invoke(service_name, {'channel_item':channel_item}, serialize=False)
                response = response.getvalue(serialize=False)
                auth_type = response['response']['auth_type']
            else:
                auth_type = 'zato'

            raise Unauthorized(cid, 'You are not allowed to access this resource', auth_type)

# ################################################################################################################################

    def check_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store,
        enforce_auth=True, _object_type=RATE_LIMIT.OBJECT_TYPE.SEC_DEF):
        """ Authenticates and authorizes a given request. Returns None on success
        """
        if sec.sec_use_rbac:
            return self.check_rbac_delegated_security(
                sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store)

        sec_def, sec_def_type = sec.sec_def, sec.sec_def['sec_type']
        handler_name = '_handle_security_%s' % sec_def_type.replace('-', '_')

        auth_result = getattr(self, handler_name)(cid, sec_def, path_info, payload, wsgi_environ, post_data, enforce_auth)
        if not auth_result:
            return False

        # Ok, we now know that the credentials are valid so we can check RBAC permissions if need be.
        if channel_item.get('has_rbac'):
            is_allowed = worker_store.rbac.is_http_client_allowed(
                'sec_def:::{}:::{}'.format(sec.sec_def['sec_type'], sec.sec_def['name']), wsgi_environ['REQUEST_METHOD'],
                channel_item.service_id)

            if not is_allowed:
                raise Forbidden(cid, 'You are not allowed to access this URL\n')

        if sec_def.get('is_rate_limit_active'):
            self.worker.server.rate_limiting.check_limit(cid, _object_type, sec_def.name, wsgi_environ['zato.http.remote_addr'])

        self.enrich_with_sec_data(wsgi_environ, sec_def, sec_def_type)

        return auth_result

# ################################################################################################################################

    def _update_url_sec(self, msg, sec_def_type, delete=False):
        """ Updates URL security definitions that use the security configuration
        of the name and type given in 'msg' so that existing definitions use
        the new configuration or, optionally, deletes the URL security definition
        altogether if 'delete' is True.
        """
        items = list(iteritems(self.url_sec))
        for target_match, url_info in items:
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
            if item.get('sec_type') == sec_type and item['security_name'] == sec_name:
                match_idx = self.channel_data.index(item)

        # No error, let's delete channel info
        if match_idx != ZATO_NONE:
            self.channel_data.pop(match_idx)

# ################################################################################################################################

    def _update_apikey(self, name, config):
        config.orig_username = config.username
        update_apikey_username_to_channel(config)
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

    def _get_sec_def_by_id(self, def_type, def_id):
        with self.url_sec_lock:
            for item in def_type.values():
                if item.config['id'] == def_id:
                    return item.config

# ################################################################################################################################

    def _update_basic_auth(self, name, config):
        self.basic_auth_config[name] = Bunch()
        self.basic_auth_config[name].config = config

    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition of the given name.
        """
        with self.url_sec_lock:
            return self.basic_auth_config.get(name)

    def basic_auth_get_by_id(self, def_id):
        """ Same as basic_auth_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(self.basic_auth_config, def_id)

    def on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self._update_basic_auth(msg.name, msg)

    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            current_config = self.basic_auth_config[msg.old_name]
            msg.password = current_config.config.password
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

            # This will delete a link from this account an SSO user,
            # assuming that SSO is enabled (in which case it is not None).
            if self.worker.server.sso_api:
                self.worker.server.sso_api.user.on_broker_msg_SSO_LINK_AUTH_DELETE(SEC_DEF_TYPE.BASIC_AUTH, msg.id)

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

    def jwt_get_by_id(self, def_id):
        """ Same as jwt_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(self.jwt_config, def_id)

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

            # This will delete a link from this account an SSO user,
            # assuming that SSO is enabled (in which case it is not None).
            if self.worker.server.sso_api:
                self.worker.server.sso_api.user.on_broker_msg_SSO_LINK_AUTH_DELETE(SEC_DEF_TYPE.JWT, msg.id)

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

# ################################################################################################################################

    def tls_key_cert_get(self, name):
        with self.url_sec_lock:
            return self.tls_key_cert_config.get(name)

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_KEY_CERT_CREATE(self, msg, *args):
        """ Creates a new TLS key/cert security definition.
        """
        with self.url_sec_lock:
            self._update_tls_key_cert(msg.name, msg)

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_KEY_CERT_EDIT(self, msg, *args):
        """ Updates an existing TLS key/cert security definition.
        """
        with self.url_sec_lock:
            del self.tls_key_cert_config[msg.old_name]
            self._update_tls_key_cert(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.TLS_KEY_CERT)

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_KEY_CERT_DELETE(self, msg, *args):
        """ Deletes an TLS key/cert security definition.
        """
        with self.url_sec_lock:
            del self.tls_key_cert_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.TLS_KEY_CERT, True)

# ################################################################################################################################

    def get_channel_by_name(self, name, _channel=CONNECTION.CHANNEL):
        # type: (unicode, unicode) -> dict
        for item in self.channel_data:
            if item['connection'] == _channel:
                if item['name'] == name:
                    return item

# ################################################################################################################################

    def sort_channel_data(self):
        """ Sorts channel items by name and then re-arranges the result so that user-facing services are closer to the begining
        of the list which makes it faster to look them up - searches in the list are O(n).
        """
        channel_data = []
        user_services = []
        internal_services = []

        for item in self.channel_data:
            if item['is_internal']:
                internal_services.append(item)
            else:
                user_services.append(item)

        user_services.sort(key=itemgetter('name'))
        internal_services.sort(key=itemgetter('name')) # Internal services will never conflict in names but let's do it anyway

        channel_data.extend(user_services)
        channel_data.extend(internal_services)

        self.channel_data[:] = channel_data

# ################################################################################################################################

    def _channel_item_from_msg(self, msg, match_target, old_data={}):
        """ Creates a channel info bunch out of an incoming CREATE_EDIT message.
        """
        channel_item = {}
        for name in('connection', 'content_type', 'data_format', 'host', 'id', 'has_rbac', 'impl_name', 'is_active',
            'is_internal', 'merge_url_params_req', 'method', 'name', 'params_pri', 'ping_method', 'pool_size', 'service_id',
            'service_name', 'soap_action', 'soap_version', 'transport', 'url_params_pri', 'url_path', 'sec_use_rbac',
            'cache_type', 'cache_id', 'cache_name', 'cache_expiry', 'content_encoding', 'match_slash', 'hl7_version',
            'json_path', 'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding'):

            channel_item[name] = msg.get(name)

        if msg.get('security_id'):
            channel_item['sec_type'] = msg['sec_type']
            channel_item['security_id'] = msg['security_id']
            channel_item['security_name'] = msg['security_name']

        # For JSON-RPC
        channel_item['service_whitelist'] = msg.get('service_whitelist', [])

        channel_item['service_impl_name'] = msg['impl_name']
        channel_item['match_target'] = match_target
        channel_item['match_target_compiled'] = Matcher(channel_item['match_target'], channel_item['match_slash'])

        # For rate limiting
        for name in('is_rate_limit_active', 'rate_limit_def', 'rate_limit_type', 'rate_limit_check_parent_def'):
            channel_item[name] = msg.get(name)

        return channel_item

# ################################################################################################################################

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

            for k, v in iteritems(config_item['config']):
                sec_info.sec_def[k] = config_item['config'][k]
        else:
            sec_info.sec_def = ZATO_NONE

        return sec_info

# ################################################################################################################################

    def _create_channel(self, msg, old_data):
        """ Creates a new channel, both its core data and the related security definition.
        Clears out URL cache for that entry, if it existed at all.
        """
        match_target = get_match_target(msg, http_methods_allowed_re=self.worker.server.http_methods_allowed_re)
        channel_item = self._channel_item_from_msg(msg, match_target, old_data)
        self.channel_data.append(channel_item)
        self.url_sec[match_target] = self._sec_info_from_msg(msg)

        self._remove_from_cache(match_target)
        self.sort_channel_data()

        # Set up rate limiting
        self.worker.server.set_up_object_rate_limiting(
            RATE_LIMIT.OBJECT_TYPE.HTTP_SOAP, channel_item['name'], config=channel_item)

# ################################################################################################################################

    def _delete_channel(self, msg):
        """ Deletes a channel, both its core data and the related security definition. Clears relevant
        entry in URL cache. Returns the deleted data.
        """
        old_match_target = get_match_target({
            'http_method': msg.get('old_http_method'),
            'http_accept': msg.get('old_http_accept'),
            'soap_action': msg.get('old_soap_action'),
            'url_path': msg.get('old_url_path'),
        }, http_methods_allowed_re=self.worker.server.http_methods_allowed_re)

        # Delete from URL cache
        self._remove_from_cache(old_match_target)

        # In case of an internal error, we won't have the match all
        match_idx = ZATO_NONE
        for item in self.channel_data:
            if item['match_target'] == old_match_target:
                match_idx = self.channel_data.index(item)

        # No error, let's delete channel info
        if match_idx != ZATO_NONE:
            old_data = self.channel_data.pop(match_idx)
        else:
            old_data = {}

        # Channel's security now
        del self.url_sec[old_match_target]

        # Re-sort all elements to match against
        self.sort_channel_data()

        # Delete rate limiting configuration
        self.worker.server.delete_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.HTTP_SOAP, msg.name)

        return old_data

# ################################################################################################################################

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

    def on_broker_msg_MSG_JSON_POINTER_EDIT(self, msg):
        pass

    def on_broker_msg_MSG_JSON_POINTER_DELETE(self, msg):
        pass

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_CA_CERT_CREATE(self, msg):
        # Ignored, does nothing.
        pass

    on_broker_msg_SECURITY_TLS_CA_CERT_DELETE = on_broker_msg_SECURITY_TLS_CA_CERT_EDIT = on_broker_msg_SECURITY_TLS_CA_CERT_CREATE

# ################################################################################################################################
# ################################################################################################################################
