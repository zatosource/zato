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
from zato.common.ext.bunch import Bunch
from zato.common.api import CHANNEL, CONNECTION, MISC, SEC_DEF_TYPE, ZATO_NONE
from zato.common.broker_message import code_to_name, SECURITY
from zato.common.dispatch import dispatcher
from zato.common.util.api import update_apikey_username_to_channel, wait_for_dict_key
from zato.common.util.auth import enrich_with_sec_data, on_basic_auth
from zato.common.util.url_dispatcher import get_match_target
from zato.server.connection.http_soap import Unauthorized
from zato.server.connection.http_soap.url_dispatcher import Matcher, PyURLData

# ################################################################################################################################

if 0:
    from zato.server.base.config_manager import ConfigManager
    ConfigManager = ConfigManager

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class URLData(PyURLData):
    """ Performs URL matching and security checks.
    """
    def __init__(self, config_manager, channel_data=None, url_sec=None, basic_auth_config=None, ntlm_config=None, \
                 oauth_config=None, apikey_config=None, config_dispatcher=None, odb=None):
        super(URLData, self).__init__(channel_data)

        self.config_manager = config_manager
        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.ntlm_config = ntlm_config
        self.oauth_config = oauth_config
        self.apikey_config = apikey_config
        self.config_dispatcher = config_dispatcher
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
        handler_name = 'on_config_event_{}'.format(code_to_name[event])
        logger.info('URLData.dispatcher_callback: event=%s, handler=%s, ctx.name=%s',
            event, handler_name, ctx.get('name') if hasattr(ctx, 'get') else 'N/A')
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

    def check_security(self, sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, config_manager, *,
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
        logger.info('_update_url_sec: msg.name=%s, sec_def_type=%s, delete=%s, url_sec count=%d',
            msg.get('name'), sec_def_type, delete, len(items))
        for target_match, url_info in items:
            sec_def = url_info.get('sec_def')
            if not sec_def:
                if url_info.get('data_format') != 'xml':
                    self.logger.warn('Missing sec_def for url_info -> %s', url_info)
                return
            if sec_def != ZATO_NONE and sec_def.sec_type == sec_def_type:
                name = msg.get('old_name') if msg.get('old_name') else msg.get('name')
                if sec_def.name == name:
                    logger.info('_update_url_sec: match found, target=%s, sec_def.name=%s, delete=%s',
                        target_match, sec_def.name, delete)
                    if delete:
                        del self.url_sec[target_match]
                    else:
                        for key, _ignored_new_value in msg.items():
                            if key in sec_def:
                                sec_def[key] = msg[key]

# ################################################################################################################################

    def _delete_channel_data(self, sec_type, sec_name):
        logger.info('_delete_channel_data: sec_type=%s, sec_name=%s, channel_data count=%d',
            sec_type, sec_name, len(self.channel_data))
        match_idx = ZATO_NONE
        for item in self.channel_data:
            if item.get('sec_type') == sec_type and item['security_name'] == sec_name:
                match_idx = self.channel_data.index(item)

        # No error, let's delete channel info
        if match_idx != ZATO_NONE:
            logger.info('_delete_channel_data: found match at idx=%s for sec_name=%s', match_idx, sec_name)
            self.channel_data.pop(match_idx)
        else:
            logger.info('_delete_channel_data: no match found for sec_type=%s, sec_name=%s', sec_type, sec_name)

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

    def _get_sec_def_by_id(self, def_type, def_id):
        def_id = int(def_id)
        item_names = list(def_type.keys())
        logger.info('_get_sec_def_by_id: looking for def_id=%s, item count=%d, names=%s', def_id, len(item_names), item_names)
        with self.url_sec_lock:
            for item_name in item_names:
                item = def_type[item_name]
                item_keys = list(item.keys()) if hasattr(item, 'keys') else 'N/A'
                has_config = hasattr(item, 'config')
                logger.info('_get_sec_def_by_id: item_name=%s, type=%s, keys=%s, has .config=%s',
                    item_name, type(item).__name__, item_keys, has_config)
                if not has_config:
                    logger.warning('_get_sec_def_by_id: item_name=%s has NO .config, full item=%s', item_name, dict(item) if hasattr(item, 'keys') else item)
                    continue
                config_keys = list(item.config.keys()) if hasattr(item.config, 'keys') else 'N/A'
                has_id = 'id' in item.config if hasattr(item.config, '__contains__') else False
                logger.info('_get_sec_def_by_id: item_name=%s, config keys=%s, has id=%s', item_name, config_keys, has_id)
                if not has_id:
                    logger.warning('_get_sec_def_by_id: item_name=%s config has NO id key, config=%s', item_name, dict(item.config) if hasattr(item.config, 'keys') else item.config)
                    continue
                item_id = int(item.config['id'])
                logger.info('_get_sec_def_by_id: item_name=%s, item_id=%s, match=%s', item_name, item_id, item_id == def_id)
                if item_id == def_id:
                    return item.config
        logger.warning('_get_sec_def_by_id: def_id=%s NOT FOUND among %d items', def_id, len(item_names))

# ################################################################################################################################

    def _update_basic_auth(self, name, config):
        logger.info('_update_basic_auth: name=%s, config type=%s, config keys=%s',
            name, type(config).__name__, list(config.keys()) if hasattr(config, 'keys') else 'N/A')
        self.basic_auth_config[name] = Bunch()
        self.basic_auth_config[name].config = config
        logger.info('_update_basic_auth: stored name=%s, has .config=%s, config.id=%s',
            name, hasattr(self.basic_auth_config[name], 'config'),
            self.basic_auth_config[name].config.get('id', 'MISSING') if hasattr(self.basic_auth_config[name].config, 'get') else 'N/A')

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

    def on_config_event_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition.
        """
        logger.info('on_config_event_SECURITY_BASIC_AUTH_CREATE: msg.name=%s, msg.id=%s, msg keys=%s',
            msg.get('name'), msg.get('id'), list(msg.keys()) if hasattr(msg, 'keys') else 'N/A')
        with self.url_sec_lock:
            self._update_basic_auth(msg.name, msg)
        config_names = list(self.basic_auth_config.keys())
        logger.info('on_config_event_SECURITY_BASIC_AUTH_CREATE: done, basic_auth_config now has %d items, names=%s',
            len(config_names), config_names)

    def on_config_event_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        logger.info('on_config_event_SECURITY_BASIC_AUTH_EDIT: msg.name=%s, msg.old_name=%s, msg.id=%s',
            msg.get('name'), msg.get('old_name'), msg.get('id'))
        with self.url_sec_lock:
            current_config = self.basic_auth_config[msg.old_name]
            logger.info('on_config_event_SECURITY_BASIC_AUTH_EDIT: current_config has .config=%s',
                hasattr(current_config, 'config'))
            msg.password = current_config.config.password
            del self.basic_auth_config[msg.old_name]
            self._update_basic_auth(msg.name, msg)
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH)
        logger.info('on_config_event_SECURITY_BASIC_AUTH_EDIT: done, basic_auth_config now has %d items', len(list(self.basic_auth_config.keys())))

    def on_config_event_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        logger.info('on_config_event_SECURITY_BASIC_AUTH_DELETE: msg.name=%s, msg.id=%s', msg.get('name'), msg.get('id'))
        with self.url_sec_lock:
            self._delete_channel_data('basic_auth', msg.name)
            del self.basic_auth_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH, True)
        logger.info('on_config_event_SECURITY_BASIC_AUTH_DELETE: done, basic_auth_config now has %d items', len(list(self.basic_auth_config.keys())))

    def on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        logger.info('on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD: msg.name=%s, msg.id=%s, msg keys=%s',
            msg.get('name'), msg.get('id'), list(msg.keys()) if hasattr(msg, 'keys') else 'N/A')
        config_names = list(self.basic_auth_config.keys())
        logger.info('on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD: basic_auth_config has %d items, names=%s',
            len(config_names), config_names)

        # Log every item in basic_auth_config to see which ones have .config and which don't ..
        for item_name, item in self.basic_auth_config.items():
            logger.info('on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD: item_name=%s, type=%s, has .config=%s, keys=%s',
                item_name, type(item).__name__, hasattr(item, 'config'),
                list(item.keys()) if hasattr(item, 'keys') else 'N/A')

        wait_for_dict_key(self.basic_auth_config, msg.name)

        logger.info('on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD: found msg.name=%s in basic_auth_config, has .config=%s',
            msg.name, hasattr(self.basic_auth_config[msg.name], 'config'))

        with self.url_sec_lock:
            self.basic_auth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, SEC_DEF_TYPE.BASIC_AUTH)
        logger.info('on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD: done for msg.name=%s', msg.name)

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
            del self.oauth_config[msg.name]
            self._update_url_sec(msg, SEC_DEF_TYPE.OAUTH, True)

    def on_config_event_SECURITY_OAUTH_CHANGE_PASSWORD(self, msg, *args):
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
            'content_encoding', 'match_slash',
            'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding',
            'security_groups', 'security_groups_ctx', 'gateway_service_list'):

            channel_item[name] = msg.get(name)

        if msg.get('security_id'):
            channel_item['sec_type'] = msg['sec_type']
            channel_item['security_id'] = msg['security_id']
            channel_item['security_name'] = msg['security_name']

        if security_groups := msg.get('security_groups'):
            channel_item['security_groups'] = security_groups
            self.config_manager.server.security_groups_ctx_builder.populate_members()
            security_groups_ctx = self.config_manager.server.security_groups_ctx_builder.build_ctx(channel_item['id'], security_groups)
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
        match_target = get_match_target(msg, http_methods_allowed_re=self.config_manager.server.http_methods_allowed_re)

        channel_item = self._channel_item_from_msg(msg, match_target, old_data)
        self.channel_data.append(channel_item)

        sec_info = self._sec_info_from_msg(msg)
        self.url_sec[match_target] = sec_info

        self._remove_from_cache(match_target)

        self.sort_channel_data()

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
