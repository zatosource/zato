# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from base64 import b64encode
from operator import itemgetter
from threading import RLock
from traceback import format_exc
from uuid import uuid4

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems
from zato.common.py23_.past.builtins import unicode

# Zato
from zato.bunch import Bunch
from zato.common.api import CHANNEL, CONNECTION, MISC, SEC_DEF_TYPE, ZATO_NONE
from zato.common.broker_message import code_to_name, SECURITY
from zato.common.dispatch import dispatcher
from zato.common.util.api import update_apikey_username_to_channel, wait_for_dict_key
from zato.common.util.auth import enrich_with_sec_data, on_basic_auth
from zato.common.util.url_dispatcher import get_match_target
from zato.server.connection.http_soap import Forbidden, Unauthorized
from zato.url_dispatcher import CyURLData, Matcher

# ################################################################################################################################

if 0:
    from zato.server.base.worker import WorkerStore
    WorkerStore = WorkerStore

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class URLData(CyURLData):
    """ Performs URL matching and security checks.
    """
    def __init__(self, worker, channel_data=None, url_sec=None, basic_auth_config=None, ntlm_config=None, \
                 oauth_config=None, apikey_config=None, broker_client=None, odb=None):
        super(URLData, self).__init__(channel_data)

        self.worker = worker
        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.ntlm_config = ntlm_config
        self.oauth_config = oauth_config
        self.apikey_config = apikey_config
        self.broker_client = broker_client
        self.odb = odb

        self.sec_config_getter = Bunch()
        self.sec_config_getter[SEC_DEF_TYPE.BASIC_AUTH] = self.basic_auth_get
        self.sec_config_getter[SEC_DEF_TYPE.APIKEY] = self.apikey_get

        self.url_sec_lock = RLock()
        self.update_lock = RLock()
        self._target_separator = MISC.SEPARATOR

        dispatcher.listen_for_updates(SECURITY, self.dispatcher_callback)

        # Needs always to be sorted by name in case of conflicts in paths resolution
        self.sort_channel_data()

# ################################################################################################################################

    def set_security_objects(self, *, url_sec, basic_auth_config, ntlm_config, oauth_config, apikey_config):

        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.ntlm_config = ntlm_config
        self.oauth_config = oauth_config
        self.apikey_config = apikey_config

# ################################################################################################################################

    def dispatcher_callback(self, event, ctx, **opaque):
        getattr(self, 'on_broker_msg_{}'.format(code_to_name[event]))(ctx)

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

        expected_key = sec_def.get('password', '')

        # Passwords are not required
        if expected_key and wsgi_environ[sec_def['header']] != expected_key:
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

    def check_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store, *,
        enforce_auth=True):
        """ Authenticates and authorizes a given request. Returns None on success
        """

        sec_def, sec_def_type = sec.sec_def, sec.sec_def['sec_type']
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
            if not sec_def:
                if url_info.get('data_format') != 'xml':
                    self.logger.warn('Missing sec_def for url_info -> %s', url_info)
                return
            if sec_def != ZATO_NONE and sec_def.sec_type == sec_def_type:
                name = msg.get('old_name') if msg.get('old_name') else msg.get('name')
                if sec_def.name == name:
                    if delete:
                        del self.url_sec[target_match]
                    else:
                        for key, _ignored_new_value in msg.items():
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
        config.orig_header = config.header
        update_apikey_username_to_channel(config)
        self.apikey_config[name] = Bunch()
        self.apikey_config[name].config = config

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
            return self._get_sec_def_by_id(self.apikey_config, def_id)

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
        wait_for_dict_key(self.apikey_config, msg.name)
        with self.url_sec_lock:
            self.apikey_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.APIKEY)

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
        wait_for_dict_key(self.basic_auth_config._impl, name)
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

    def on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        wait_for_dict_key(self.basic_auth_config, msg.name)
        with self.url_sec_lock:
            self.basic_auth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH)

# ################################################################################################################################

    def _update_ntlm(self, name, config):
        self.ntlm_config[name] = Bunch()
        self.ntlm_config[name].config = config

    def ntlm_get(self, name):
        """ Returns the configuration of the NTLM security definition of the given name.
        """
        wait_for_dict_key(self.ntlm_config, name)
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
            current_config = self.ntlm_config[msg.old_name]
            msg.password = current_config.config.password
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
        wait_for_dict_key(self.ntlm_config, msg.name)
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
        wait_for_dict_key(self.oauth_config, name)
        with self.url_sec_lock:
            return self.oauth_config.get(name)

    def oauth_get_by_id(self, def_id):
        """ Same as oauth_get but returns information by definition ID.
        """
        with self.url_sec_lock:
            return self._get_sec_def_by_id(self.oauth_config, def_id)

    def on_broker_msg_SECURITY_OAUTH_CREATE(self, msg, *args):
        """ Creates a new OAuth account.
        """
        with self.url_sec_lock:
            self._update_oauth(msg.name, msg)

    def on_broker_msg_SECURITY_OAUTH_EDIT(self, msg, *args):
        """ Updates an existing OAuth account.
        """
        with self.url_sec_lock:
            current_config = self.oauth_config[msg.old_name]
            msg.password = current_config.config.password
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
        wait_for_dict_key(self.oauth_config, msg.name)
        with self.url_sec_lock:
            self.oauth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH)

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

    def _channel_item_from_msg(self, msg, match_target, old_data=None):
        """ Creates a channel info bunch out of an incoming CREATE_EDIT message.
        """
        old_data = old_data or {}
        channel_item = {}
        for name in('connection', 'content_type', 'data_format', 'host', 'id', 'impl_name', 'is_active',
            'is_internal', 'merge_url_params_req', 'method', 'name', 'params_pri', 'ping_method', 'pool_size', 'service_id',
            'service_name', 'soap_action', 'soap_version', 'transport', 'url_params_pri', 'url_path',
            'cache_type', 'cache_id', 'cache_name', 'cache_expiry', 'content_encoding', 'match_slash',
            'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding',
            'security_groups', 'security_groups_ctx'):

            channel_item[name] = msg.get(name)

        if msg.get('security_id'):
            channel_item['sec_type'] = msg['sec_type']
            channel_item['security_id'] = msg['security_id']
            channel_item['security_name'] = msg['security_name']

        if security_groups := msg.get('security_groups'):
            channel_item['security_groups'] = security_groups
            self.worker.server.security_groups_ctx_builder.populate_members()
            security_groups_ctx = self.worker.server.security_groups_ctx_builder.build_ctx(channel_item['id'], security_groups)
            channel_item['security_groups_ctx'] = security_groups_ctx

        channel_item['service_impl_name'] = msg['impl_name']
        channel_item['match_target'] = match_target
        channel_item['match_target_compiled'] = Matcher(channel_item['match_target'], channel_item['match_slash'])

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
        logger.info('BBB-3 %s %s', msg, old_data)

        match_target = get_match_target(msg, http_methods_allowed_re=self.worker.server.http_methods_allowed_re)
        logger.info('BBB-4 %s', match_target)

        channel_item = self._channel_item_from_msg(msg, match_target, old_data)
        logger.info('BBB-5 %s', channel_item)

        self.channel_data.append(channel_item)

        sec_info = self._sec_info_from_msg(msg)
        logger.info('BBB-6 %s', sec_info)

        self.url_sec[match_target] = sec_info

        self._remove_from_cache(match_target)
        self.sort_channel_data()

        logger.info('BBB-7 %s', self.channel_data.keys()

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

        return old_data

# ################################################################################################################################

    def on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        logger.info('BBB-2 %s', msg)
        with self.url_sec_lock:
            # Only edits have 'old_name', creates don't. So for edits we delete
            # the channel and later recreate it while create actions do not have anything to delete.
            if msg.get('old_name'):
                old_data = self._delete_channel(msg)
            else:
                old_data = {}

            self._create_channel(msg, old_data)

    def on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP channel.
        """
        with self.url_sec_lock:
            self._delete_channel(msg)

# ################################################################################################################################
# ################################################################################################################################
