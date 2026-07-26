# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from operator import itemgetter
from threading import RLock
from traceback import format_exc

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.api import AS2, AS4, CONNECTION, MISC, SEC_DEF_TYPE, URL_TYPE, ZATO_NONE
from zato.common.bearer_token_verifier import BearerTokenVerifier, build_verify_config, extract_bearer_token
from zato.common.broker_message import code_to_name, SECURITY
from zato.common.crypto.api import is_string_equal
from zato.common.dispatch import dispatcher
from zato.common.soap.common import SOAPSecurityException
from zato.common.soap.envelope import parse_envelope
from zato.common.soap.security.wss import enforce_wss, invalidate_keystores
from zato.common.util.api import update_apikey_username_to_channel, wait_for_dict_key
from zato.common.util.auth import enrich_with_sec_data, on_basic_auth
from zato.common.util.url_dispatcher import get_match_target
from zato.server.connection.http_soap import Unauthorized
from zato.server.connection.http_soap.url_dispatcher import Matcher, PyURLData, resolve_match_slash

# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    from zato.server.base.config_manager import ConfigManager

    anydict = anydict
    ConfigManager = ConfigManager

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields that inbound bearer token verification reads from a definition's opaque attributes
_oauth_inbound_keys = ('is_static_token', 'static_token', 'issuer', 'jwks_url', 'audience', 'claims')

# Fields that inbound mTLS verification reads from a definition's opaque attributes
_mtls_inbound_keys = ('client_cert_fingerprint', 'client_cert_subject_dn')

# Headers injected by the TLS-terminating proxy once it has verified the client certificate -
# they arrive in their WSGI form, i.e. upper-cased, with dashes turned into underscores.
_mtls_header_verify      = 'HTTP_X_ZATO_SSL_CLIENT_VERIFY'
_mtls_header_fingerprint = 'HTTP_X_ZATO_SSL_CLIENT_SHA256'
_mtls_header_subject_dn  = 'HTTP_X_ZATO_SSL_CLIENT_SUBJECT_DN'

# The value the TLS-terminating proxy reports for a successfully verified client certificate.
_mtls_verify_success = 'SUCCESS'

# Every definition type kept in an id-keyed index.
_indexed_sec_types = (
    SEC_DEF_TYPE.APIKEY,
    SEC_DEF_TYPE.BASIC_AUTH,
    SEC_DEF_TYPE.MTLS,
    SEC_DEF_TYPE.NTLM,
    SEC_DEF_TYPE.OAUTH,
    SEC_DEF_TYPE.SPNEGO,
    SEC_DEF_TYPE.WSS,
)

# Definition types a channel can authenticate against - each one has a _handle_security_* method here.
_channel_sec_types = (
    SEC_DEF_TYPE.APIKEY,
    SEC_DEF_TYPE.BASIC_AUTH,
    SEC_DEF_TYPE.MTLS,
    SEC_DEF_TYPE.OAUTH,
    SEC_DEF_TYPE.WSS,
)

# ################################################################################################################################
# ################################################################################################################################

class URLData(PyURLData):
    """ Performs URL matching and security checks.
    """
    def __init__(self, config_manager, channel_data=None, url_sec=None, basic_auth_config=None, mtls_config=None, \
                 ntlm_config=None, oauth_config=None, spnego_config=None, apikey_config=None, wss_config=None, \
                 config_dispatcher=None, odb=None):
        super(URLData, self).__init__(channel_data)

        self.config_manager = config_manager
        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.mtls_config = mtls_config
        self.ntlm_config = ntlm_config
        self.oauth_config = oauth_config
        self.spnego_config = spnego_config
        self.apikey_config = apikey_config
        self.wss_config = wss_config
        self.config_dispatcher = config_dispatcher
        self.odb = odb

        self.url_sec_lock = RLock()
        self.update_lock = RLock()
        self._target_separator = MISC.SEPARATOR

        # Definitions by id, per definition type - group-authenticated requests look definitions up
        # by id, so a scan would cost more the more definitions there are.
        self._sec_def_by_id = {sec_type:{} for sec_type in _indexed_sec_types}
        self._rebuild_sec_def_index()

        # Built on first use because the cache it needs may not exist yet when we are created
        self._bearer_token_verifier = None

        dispatcher.listen_for_updates(SECURITY, self.dispatcher_callback)

        # Needs always to be sorted by name in case of conflicts in paths resolution
        self.sort_channel_data()

# ################################################################################################################################

    def set_security_objects(self, *, url_sec, basic_auth_config, mtls_config, ntlm_config, oauth_config, spnego_config,
        apikey_config, wss_config):

        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.mtls_config = mtls_config
        self.ntlm_config = ntlm_config
        self.oauth_config = oauth_config
        self.spnego_config = spnego_config
        self.apikey_config = apikey_config
        self.wss_config = wss_config

        with self.url_sec_lock:
            self._rebuild_sec_def_index()

# ################################################################################################################################

    def _get_sec_config_dicts(self) -> 'anydict':
        """ Returns each definition type's configuration dict, keyed by that type.
        """
        out = {
            SEC_DEF_TYPE.APIKEY: self.apikey_config,
            SEC_DEF_TYPE.BASIC_AUTH: self.basic_auth_config,
            SEC_DEF_TYPE.MTLS: self.mtls_config,
            SEC_DEF_TYPE.NTLM: self.ntlm_config,
            SEC_DEF_TYPE.OAUTH: self.oauth_config,
            SEC_DEF_TYPE.SPNEGO: self.spnego_config,
            SEC_DEF_TYPE.WSS: self.wss_config,
        }

        return out

# ################################################################################################################################

    def _rebuild_sec_def_index(self) -> 'None':
        """ Builds the id-keyed index from scratch, which is what a full configuration load needs.
        """
        for sec_type, config_dict in self._get_sec_config_dicts().items():

            index = {}

            # A definition type whose configuration has not been handed over yet has nothing to index
            if config_dict is None:
                self._sec_def_by_id[sec_type] = index
                continue

            for item_name in list(config_dict.keys()):
                item = config_dict[item_name]

                # An entry that is still being populated has no configuration to index yet
                if not hasattr(item, 'config'):
                    continue
                if 'id' not in item.config:
                    continue

                index[int(item.config['id'])] = item.config

            self._sec_def_by_id[sec_type] = index

# ################################################################################################################################

    def _index_sec_def(self, sec_type:'str', config:'anydict') -> 'None':
        self._sec_def_by_id[sec_type][int(config['id'])] = config

    def _unindex_sec_def(self, sec_type:'str', name:'str') -> 'None':
        config = self._get_sec_config_dicts()[sec_type][name].config
        del self._sec_def_by_id[sec_type][int(config['id'])]

# ################################################################################################################################

    def dispatcher_callback(self, event, ctx, **opaque):
        handler_name = 'on_config_event_{}'.format(code_to_name[event])
        getattr(self, handler_name)(ctx)

# ################################################################################################################################

    def _handle_security_apikey(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None, enforce_auth=True):
        """ Performs the authentication against an API key in a specified HTTP header.
        """
        # Find out if the header was provided at all
        if sec_def['header'] not in wsgi_environ:
            if enforce_auth:
                msg = '401 Unauthorized path_info:`{}`, cid:`{}`'.format(path_info, cid)
                error_msg = '401 Unauthorized'
                logger.error(msg + ' (No header)')
                raise Unauthorized(cid, error_msg, None)
            else:
                return False

        expected_key = sec_def.get('password')

        if not expected_key:
            if enforce_auth:
                logger.error(
                    '401 Unauthorized path_info:`%s`, cid:`%s` (API key definition `%s` has no key configured)',
                    path_info, cid, sec_def['name'])
                raise Unauthorized(cid, '401 Unauthorized', None)
            else:
                return False

        if not is_string_equal(wsgi_environ[sec_def['header']], expected_key):
            if enforce_auth:
                msg = '401 Unauthorized path_info:`{}`, cid:`{}`'.format(path_info, cid)
                error_msg = '401 Unauthorized'
                logger.error(msg + ' (Password)')
                raise Unauthorized(cid, error_msg, None)
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
        result = on_basic_auth(cid, env, url_config, False)

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

    def _handle_security_mtls(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None, enforce_auth=True):
        """ Performs the authentication against the client certificate details that the TLS-terminating proxy
        reports in its injected headers after it has verified the certificate against the client CA.
        """
        # Local aliases
        verify_result = wsgi_environ.get(_mtls_header_verify)

        # Assume the request will not be let through until proven otherwise.
        is_valid = False
        reason = 'No client certificate'

        # The proxy must have seen and verified a client certificate at all ..
        if verify_result == _mtls_verify_success:

            expected_fingerprint = sec_def.get('client_cert_fingerprint')
            expected_subject_dn = sec_def.get('client_cert_subject_dn')

            # .. a configured fingerprint must match what the proxy reports - fingerprints are hex strings
            # .. that may arrive with colon separators and in either case, so both sides are normalized first ..
            if expected_fingerprint:
                given_fingerprint = wsgi_environ.get(_mtls_header_fingerprint) or ''
                expected_fingerprint = expected_fingerprint.replace(':', '').lower()
                given_fingerprint = given_fingerprint.replace(':', '').lower()

                if is_string_equal(expected_fingerprint, given_fingerprint):
                    is_valid = True
                else:
                    reason = 'Fingerprint mismatch'

            # .. otherwise, a configured subject DN must match the one from the certificate ..
            elif expected_subject_dn:
                given_subject_dn = wsgi_environ.get(_mtls_header_subject_dn) or ''

                if is_string_equal(expected_subject_dn, given_subject_dn):
                    is_valid = True
                else:
                    reason = 'Subject DN mismatch'

            # .. with no match criteria configured, a certificate verified by the proxy is enough.
            else:
                is_valid = True

        # If we are here with a negative result, the request is rejected.
        if not is_valid:
            if enforce_auth:
                msg = '401 Unauthorized path_info:`{}`, cid:`{}`'.format(path_info, cid)
                error_msg = '401 Unauthorized'
                logger.error(msg + ' ({})'.format(reason))
                raise Unauthorized(cid, error_msg, None)
            else:
                return False

        return True

# ################################################################################################################################

    def get_bearer_token_verifier(self):
        """ Returns the bearer token verifier, building it on first use.
        """
        if not self._bearer_token_verifier:
            self._bearer_token_verifier = BearerTokenVerifier(self.config_manager.cache_api)

        return self._bearer_token_verifier

# ################################################################################################################################

    def _handle_security_oauth(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None, enforce_auth=True):
        """ Performs the authentication against an inbound bearer token, either a static one or a JWT.
        """
        # Extract the token from the Authorization header ..
        auth_header = wsgi_environ.get('HTTP_AUTHORIZATION') or ''
        token = extract_bearer_token(auth_header)

        # .. and verify it against the one definition attached to this channel.
        if token:
            verifier = self.get_bearer_token_verifier()
            verify_config = build_verify_config(sec_def)
            claims = verifier.verify(cid, path_info, token, verify_config)

            if claims is not None:
                return True

        if enforce_auth:
            msg = '401 Unauthorized path_info:`{}`, cid:`{}`'.format(path_info, cid)
            error_msg = '401 Unauthorized'
            logger.error(msg + ' (Bearer token)')
            raise Unauthorized(cid, error_msg, 'Bearer')
        else:
            return False

# ################################################################################################################################

    def _handle_security_wss(self, cid, sec_def, path_info, body, wsgi_environ, ignored_post_data=None, enforce_auth=True):
        """ Enforces the channel's WS-Security definition on the incoming SOAP envelope.
        """
        soap_context = wsgi_environ.get('zato.request.soap')

        try:
            # A SOAP channel has already parsed the envelope, so enforcement runs against
            # that shared element - what it decrypts in place is what the service reads.
            if soap_context:
                envelope = soap_context.element
            else:
                envelope = parse_envelope(body)

            verified = enforce_wss(envelope, sec_def)

        # Only a security failure is a credential failure. Catching everything here turned a bug
        # anywhere in the verification path into a 401, which hid it and told the caller its
        # credentials were wrong when they were not.
        except SOAPSecurityException:
            if enforce_auth:
                msg = '401 Unauthorized path_info:`{}`, cid:`{}`, e:`{}`'.format(path_info, cid, format_exc())
                error_msg = '401 Unauthorized'
                logger.error(msg)
                raise Unauthorized(cid, error_msg, None)
            else:
                return False

        # What the signature covered is recorded on the request context, and the payload resolution
        # checks the body it reads against it - that is what ties the verified message to the
        # processed one rather than leaving the two to be located independently.
        if soap_context:
            soap_context.verified_signature = verified

        return True

# ################################################################################################################################

    def check_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, config_manager, *,
        enforce_auth=True):
        """ Authenticates and authorizes a given request. Returns None on success
        """

        sec_def, sec_def_type = sec.sec_def, sec.sec_def['sec_type']

        # A definition of any other type has no inbound verification of its own, so there is nothing
        # a caller could present that would be checked.
        if sec_def_type not in _channel_sec_types:
            logger.error('Sec type `%s` cannot authenticate a channel, path_info:`%s`, cid:`%s`',
                sec_def_type, path_info, cid)
            raise Unauthorized(cid, '401 Unauthorized', None)

        handler_name = '_handle_security_%s' % sec_def_type.replace('-', '_')

        auth_result = getattr(self, handler_name)(cid, sec_def, path_info, payload, wsgi_environ, post_data, enforce_auth)
        if not auth_result:
            return False

        enrich_with_sec_data(wsgi_environ, sec_def, sec_def_type)

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
            sec_def = url_info.get('sec_def')

            # One entry with no security definition of its own says nothing about the rest,
            # so the remaining ones are still visited.
            if not sec_def:
                if url_info.get('data_format') != 'xml':
                    self.logger.warning('Missing sec_def for url_info -> %s', url_info)
                continue

            if sec_def != ZATO_NONE and sec_def.sec_type == sec_def_type:
                name = msg.get('old_name') if msg.get('old_name') else msg.get('name')
                if sec_def.name == name:
                    if delete:
                        del self.url_sec[target_match]
                    else:
                        for key, _ignored_new_value in msg.items():
                            if key in sec_def:
                                sec_def[key] = msg[key]

                            # Bearer token definitions keep their inbound verification fields
                            # in opaque attributes, so an edit may introduce keys that the
                            # definition did not carry before, e.g. an audience added later on.
                            elif sec_def_type == SEC_DEF_TYPE.OAUTH:
                                if key in _oauth_inbound_keys:
                                    sec_def[key] = msg[key]

                            # The same applies to mTLS definitions, whose match criteria
                            # are opaque attributes too.
                            elif sec_def_type == SEC_DEF_TYPE.MTLS:
                                if key in _mtls_inbound_keys:
                                    sec_def[key] = msg[key]

# ################################################################################################################################

    def _delete_channel_data(self, sec_type, sec_name):
        """ Removes every channel that used the given security definition, which is what the
        database does to the channel rows pointing at that definition when it is deleted.
        """
        remaining = []
        removed = []

        # A channel created without security has no sec_type of its own
        for item in self.channel_data:
            if item.get('sec_type') == sec_type:
                if item['security_name'] == sec_name:
                    removed.append(item)
                    continue

            remaining.append(item)

        # Nothing used that definition, so there is nothing to remove either
        if not removed:
            return

        self.channel_data[:] = remaining
        self.rebuild_match_target_index()

        # A target cached for a channel that is gone would go on resolving to it
        for item in removed:
            self._remove_from_cache(item['match_target'])

# ################################################################################################################################

    def _update_apikey(self, name, config):
        config.orig_header = config.header
        update_apikey_username_to_channel(config)
        self.apikey_config[name] = Bunch()
        self.apikey_config[name].config = config
        self._index_sec_def(SEC_DEF_TYPE.APIKEY, config)

    def apikey_get(self, name):
        """ Returns the configuration of the API key of the given name.
        """
        wait_for_dict_key(self.apikey_config, name)
        with self.url_sec_lock:
            return self.apikey_config.get(name)

    def apikey_get_by_id(self, def_id):
        """ Same as apikey_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(SEC_DEF_TYPE.APIKEY, def_id)

    def on_config_event_SECURITY_APIKEY_CREATE(self, msg, *args):
        """ Creates a new API key security definition.
        """
        with self.url_sec_lock:
            self._update_apikey(msg.name, msg)

    def on_config_event_SECURITY_APIKEY_EDIT(self, msg, *args):
        """ Updates an existing API key security definition.
        """
        with self.url_sec_lock:
            del self.apikey_config[msg.old_name]
            self._update_apikey(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.APIKEY)

    def on_config_event_SECURITY_APIKEY_DELETE(self, msg, *args):
        """ Deletes an API key security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('apikey', msg.name)
            self._unindex_sec_def(SEC_DEF_TYPE.APIKEY, msg.name)
            del self.apikey_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.APIKEY, True)

    def on_config_event_SECURITY_APIKEY_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an API key security definition.
        """
        wait_for_dict_key(self.apikey_config, msg.name)
        with self.url_sec_lock:
            self.apikey_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.APIKEY)

# ################################################################################################################################

    def _get_sec_def_by_id(self, sec_type, def_id):
        with self.url_sec_lock:
            return self._sec_def_by_id[sec_type].get(int(def_id))

# ################################################################################################################################

    def _update_basic_auth(self, name, config):
        self.basic_auth_config[name] = Bunch()
        self.basic_auth_config[name].config = config
        self._index_sec_def(SEC_DEF_TYPE.BASIC_AUTH, config)

    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition of the given name.
        """
        wait_for_dict_key(self.basic_auth_config._impl, name)
        with self.url_sec_lock:
            return self.basic_auth_config.get(name)

    def basic_auth_get_by_id(self, def_id):
        """ Same as basic_auth_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(SEC_DEF_TYPE.BASIC_AUTH, def_id)

    def on_config_event_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self._update_basic_auth(msg.name, msg)

    def on_config_event_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            current_config = self.basic_auth_config[msg.old_name]
            msg.password = current_config.config.password
            del self.basic_auth_config[msg.old_name]
            self._update_basic_auth(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH)

    def on_config_event_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('basic_auth', msg.name)
            self._unindex_sec_def(SEC_DEF_TYPE.BASIC_AUTH, msg.name)
            del self.basic_auth_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH, True)

    def on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        wait_for_dict_key(self.basic_auth_config, msg.name)

        with self.url_sec_lock:
            self.basic_auth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH)

# ################################################################################################################################

    def _update_mtls(self, name, config):
        self.mtls_config[name] = Bunch()
        self.mtls_config[name].config = config
        self._index_sec_def(SEC_DEF_TYPE.MTLS, config)

    def mtls_get(self, name):
        """ Returns the configuration of the mTLS security definition of the given name.
        """
        wait_for_dict_key(self.mtls_config, name)
        with self.url_sec_lock:
            return self.mtls_config.get(name)

    def mtls_get_by_id(self, def_id):
        """ Same as mtls_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(SEC_DEF_TYPE.MTLS, def_id)

    def on_config_event_SECURITY_MTLS_CREATE(self, msg, *args):
        """ Creates a new mTLS security definition.
        """
        with self.url_sec_lock:
            self._update_mtls(msg.name, msg)

    def on_config_event_SECURITY_MTLS_EDIT(self, msg, *args):
        """ Updates an existing mTLS security definition.
        """
        with self.url_sec_lock:
            del self.mtls_config[msg.old_name]
            self._update_mtls(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.MTLS)

    def on_config_event_SECURITY_MTLS_DELETE(self, msg, *args):
        """ Deletes an mTLS security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('mtls', msg.name)
            self._unindex_sec_def(SEC_DEF_TYPE.MTLS, msg.name)
            del self.mtls_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.MTLS, True)

# ################################################################################################################################

    def _update_ntlm(self, name, config):
        self.ntlm_config[name] = Bunch()
        self.ntlm_config[name].config = config
        self._index_sec_def(SEC_DEF_TYPE.NTLM, config)

    def ntlm_get(self, name):
        """ Returns the configuration of the NTLM security definition of the given name.
        """
        wait_for_dict_key(self.ntlm_config, name)
        with self.url_sec_lock:
            return self.ntlm_config.get(name)

    def on_config_event_SECURITY_NTLM_CREATE(self, msg, *args):
        """ Creates a new NTLM security definition.
        """
        with self.url_sec_lock:
            self._update_ntlm(msg.name, msg)

    def on_config_event_SECURITY_NTLM_EDIT(self, msg, *args):
        """ Updates an existing NTLM security definition.
        """
        with self.url_sec_lock:
            current_config = self.ntlm_config[msg.old_name]
            msg.password = current_config.config.password
            del self.ntlm_config[msg.old_name]
            self._update_ntlm(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.NTLM)

    def on_config_event_SECURITY_NTLM_DELETE(self, msg, *args):
        """ Deletes an NTLM security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('ntlm', msg.name)
            self._unindex_sec_def(SEC_DEF_TYPE.NTLM, msg.name)
            del self.ntlm_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.NTLM, True)

    def on_config_event_SECURITY_NTLM_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an NTLM security definition.
        """
        wait_for_dict_key(self.ntlm_config, msg.name)
        with self.url_sec_lock:
            self.ntlm_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.NTLM)

# ################################################################################################################################

    def _update_spnego(self, name, config):
        self.spnego_config[name] = Bunch()
        self.spnego_config[name].config = config
        self._index_sec_def(SEC_DEF_TYPE.SPNEGO, config)

    def spnego_get(self, name):
        """ Returns the configuration of the Kerberos (SPNEGO) security definition of the given name.
        """
        wait_for_dict_key(self.spnego_config, name)
        with self.url_sec_lock:
            return self.spnego_config.get(name)

    def spnego_get_by_id(self, def_id):
        """ Same as spnego_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(SEC_DEF_TYPE.SPNEGO, def_id)

    def on_config_event_SECURITY_SPNEGO_CREATE(self, msg, *args):
        """ Creates a new Kerberos (SPNEGO) security definition.
        """
        with self.url_sec_lock:
            self._update_spnego(msg.name, msg)

    def on_config_event_SECURITY_SPNEGO_EDIT(self, msg, *args):
        """ Updates an existing Kerberos (SPNEGO) security definition.
        """
        with self.url_sec_lock:
            del self.spnego_config[msg.old_name]
            self._update_spnego(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.SPNEGO)

    def on_config_event_SECURITY_SPNEGO_DELETE(self, msg, *args):
        """ Deletes a Kerberos (SPNEGO) security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('spnego', msg.name)
            self._unindex_sec_def(SEC_DEF_TYPE.SPNEGO, msg.name)
            del self.spnego_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.SPNEGO, True)

# ################################################################################################################################

    def _update_wss(self, name, config):
        self.wss_config[name] = Bunch()
        self.wss_config[name].config = config
        self._index_sec_def(SEC_DEF_TYPE.WSS, config)

    def wss_get(self, name):
        """ Returns the configuration of the WS-Security definition of the given name.
        """
        wait_for_dict_key(self.wss_config, name)
        with self.url_sec_lock:
            return self.wss_config.get(name)

    def wss_get_by_id(self, def_id):
        """ Same as wss_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(SEC_DEF_TYPE.WSS, def_id)

    def on_config_event_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        with self.url_sec_lock:
            self._update_wss(msg.name, msg)

    def on_config_event_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        with self.url_sec_lock:
            current_config = self.wss_config[msg.old_name]
            msg.password = current_config.config.password
            del self.wss_config[msg.old_name]
            self._update_wss(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.WSS)

            # The keystore built from the old configuration is no longer what this definition
            # says, and the files it points at may have been replaced without their paths changing.
            invalidate_keystores(msg.id)

    def on_config_event_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('wss', msg.name)
            self._unindex_sec_def(SEC_DEF_TYPE.WSS, msg.name)
            del self.wss_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.WSS, True)

            invalidate_keystores(msg.id)

    def on_config_event_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of a WS-Security definition.
        """
        wait_for_dict_key(self.wss_config, msg.name)
        with self.url_sec_lock:
            self.wss_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.WSS)

# ################################################################################################################################

    def _update_oauth(self, name, config):
        self.oauth_config[name] = Bunch()
        self.oauth_config[name].config = config
        self._index_sec_def(SEC_DEF_TYPE.OAUTH, config)

    def oauth_get(self, name):
        """ Returns the configuration of the OAuth account of the given name.
        """
        wait_for_dict_key(self.oauth_config, name)
        with self.url_sec_lock:
            return self.oauth_config.get(name)

    def oauth_get_by_id(self, def_id):
        """ Same as oauth_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(SEC_DEF_TYPE.OAUTH, def_id)

    def on_config_event_SECURITY_OAUTH_CREATE(self, msg, *args):
        """ Creates a new OAuth account.
        """
        with self.url_sec_lock:
            self._update_oauth(msg.name, msg)

    def on_config_event_SECURITY_OAUTH_EDIT(self, msg, *args):
        """ Updates an existing OAuth account.
        """
        with self.url_sec_lock:
            current_config = self.oauth_config[msg.old_name]
            msg.password = current_config.config.password
            del self.oauth_config[msg.old_name]
            self._update_oauth(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH)

    def on_config_event_SECURITY_OAUTH_DELETE(self, msg, *args):
        """ Deletes an OAuth account.
        """
        with self.url_sec_lock:
            self._delete_channel_data('oauth', msg.name)
            self._unindex_sec_def(SEC_DEF_TYPE.OAUTH, msg.name)
            del self.oauth_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH, True)

    def on_config_event_SECURITY_OAUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of an OAuth account.
        """
        wait_for_dict_key(self.oauth_config, msg.name)
        with self.url_sec_lock:
            config = self.oauth_config[msg.name]['config']
            config['password'] = msg.password

            # Static tokens used to be kept in the opaque attributes - the password column
            # is their only home now, so the old copy is blanked out here. The config object
            # is a broker message without a pop method, which is why the key itself stays in place.
            if config.get('static_token'):
                config['static_token'] = ''
                config['is_static_token'] = True

            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH)

            # The same blanking applies to security definitions attached to channels.
            for url_info in self.url_sec.values():
                sec_def = url_info.get('sec_def')
                if sec_def and sec_def != ZATO_NONE and sec_def.sec_type == SEC_DEF_TYPE.OAUTH and sec_def.name == msg.name:
                    if sec_def.get('static_token'):
                        sec_def['static_token'] = ''
                        sec_def['is_static_token'] = True

# ################################################################################################################################

    def get_channel_by_name(self, name, _channel=CONNECTION.CHANNEL):
        # type: (str, str) -> dict
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

        # Whatever channels there are now is what lookups by match target go against
        self.rebuild_match_target_index()

# ################################################################################################################################

    def _channel_item_from_msg(self, msg, match_target, old_data):
        """ Creates a channel info bunch out of an incoming CREATE_EDIT message. An edit arrives as
        a delete followed by a create, so old_data is what the channel held until now - empty for
        a channel being created.
        """
        # The runtime hands this very object to services and to the dispatcher, both of which
        # reach into it by attribute as well as by key.
        channel_item = Bunch()

        for name in('connection', 'content_type', 'data_format', 'host', 'id', 'impl_name', 'is_active',
            'is_internal', 'merge_url_params_req', 'method', 'name', 'params_pri', 'ping_method', 'pool_size', 'service_id',
            'service_name', 'soap_action', 'soap_version', 'transport', 'url_params_pri', 'url_path',
            'match_slash',
            'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding',
            'security_groups', 'security_groups_ctx', 'gateway_service_list', 'use_mtom', 'is_audit_log_active',
            'should_include_in_openapi', 'response_cache',
            'is_deprecated', 'deprecation_sunset', 'deprecation_successor', 'deprecation_since'):

            channel_item[name] = msg.get(name)

        # Dispatcher-handled channels, such as AS2 ones, have no service of their own,
        # so the message carries None - the runtime spells that as an empty string.
        if channel_item['service_name'] is None:
            channel_item['service_name'] = ''

        # AS4 channels carry their own configuration fields
        if channel_item['transport'] == URL_TYPE.AS4:
            for name in AS4.Common_Fields + AS4.Channel_Fields:
                channel_item[name] = msg.get(name)

        # AS2 channels carry their own configuration fields too
        if channel_item['transport'] == URL_TYPE.AS2:
            for name in AS2.Common_Fields + AS2.Channel_Fields:
                channel_item[name] = msg.get(name)

        if msg.get('security_id'):
            channel_item['sec_type'] = msg['sec_type']

            # The Dashboard sends the security definition id as a string, but it is a database id,
            # so it is kept as an int in the runtime channel data - the OpenAPI console compares it
            # against the caller's own definition id, which is an int too.
            channel_item['security_id'] = int(msg['security_id'])
            channel_item['security_name'] = msg['security_name']

        # A message that does not mention security groups at all leaves the channel with the ones it
        # already had - only an explicitly empty list clears them. The message never carries a context
        # of its own, so whatever groups apply are turned into one here.
        security_groups = msg.get('security_groups')

        if security_groups is None:
            security_groups = old_data.get('security_groups')

        if security_groups:
            channel_item['security_groups'] = security_groups
            self.config_manager.server.security_groups_ctx_builder.populate_members()
            security_groups_ctx = self.config_manager.server.security_groups_ctx_builder.build_ctx(channel_item['id'], security_groups)
            channel_item['security_groups_ctx'] = security_groups_ctx

        channel_item['service_impl_name'] = msg.get('impl_name')
        channel_item['match_target'] = match_target

        match_slash = resolve_match_slash(channel_item['match_slash'])
        channel_item['match_target_compiled'] = Matcher(channel_item['match_target'], match_slash)

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

        if msg.get('security_name'):
            sec_info.sec_def = Bunch()
            sec_config = getattr(self, '{}_config'.format(msg['sec_type']))
            config_item = sec_config[msg['security_name']]

            for k, _v in iteritems(config_item['config']):
                sec_info.sec_def[k] = config_item['config'][k]
        else:
            sec_info.sec_def = ZATO_NONE

        return sec_info

# ################################################################################################################################

    def _create_channel(self, msg, old_data):
        """ Creates a new channel, both its core data and the related security definition.
        Clears out URL cache for that entry, if it existed at all.
        """
        match_target = get_match_target(msg, http_methods_allowed_re=self.config_manager.server.http_methods_allowed_re)

        channel_item = self._channel_item_from_msg(msg, match_target, old_data)
        self.channel_data.append(channel_item)

        sec_info = self._sec_info_from_msg(msg)
        self.url_sec[match_target] = sec_info

        # Re-sort all elements to match against, which indexes the new channel too - the cache
        # invalidation below needs the new channel's own pattern to find what it takes over.
        self.sort_channel_data()

        self._remove_from_cache(match_target)

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
        }, http_methods_allowed_re=self.config_manager.server.http_methods_allowed_re)

        # Delete from URL cache
        self._remove_from_cache(old_match_target)

        # The channel is found by its target rather than by walking the list, which is what
        # keeps a cluster with many channels from paying for the walk on every configuration change
        item = self.match_target_index.get(old_match_target)

        if item is None:
            old_data = {}

        # .. the list is rebuilt without that one channel, compared by identity so that
        # .. two channels holding equal data cannot be confused for each other.
        else:
            old_data = item
            remaining = []

            for elem in self.channel_data:
                if elem is not item:
                    remaining.append(elem)

            self.channel_data[:] = remaining

        # Channel's security now
        del self.url_sec[old_match_target]

        # Re-sort all elements to match against
        self.sort_channel_data()

        return old_data

# ################################################################################################################################

    def on_config_event_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        with self.url_sec_lock:
            # Only edits have 'old_name', creates don't. So for edits we delete
            # the channel and later recreate it while create actions do not have anything to delete.
            if msg.get('old_name'):
                old_data = self._delete_channel(msg)
            else:
                old_data = {}

            self._create_channel(msg, old_data)

    def on_config_event_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP channel.
        """
        with self.url_sec_lock:
            self._delete_channel(msg)

# ################################################################################################################################
# ################################################################################################################################
