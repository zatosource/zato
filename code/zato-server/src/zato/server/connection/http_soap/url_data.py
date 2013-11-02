# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from hashlib import sha256
from threading import RLock
from traceback import format_exc

# Bunch
from bunch import Bunch

# parse
from parse import compile as parse_compile

# sec-wall
from secwall.server import on_basic_auth, on_wsse_pwd
from secwall.wsse import WSSE

# Zato
from zato.common import MISC, URL_TYPE, ZATO_NONE
from zato.common.util import security_def_type, TRACE1
from zato.server.connection.http_soap import Unauthorized

logger = logging.getLogger(__name__)

class URLData(object):
    """ Performs URL matching and all the HTTP/SOAP-related security checks.
    """
    def __init__(self, channel_data=None, url_sec=None, basic_auth_config=None,
                 tech_acc_config=None, wss_config=None):
        self.channel_data = channel_data
        self.url_sec = url_sec 
        self.basic_auth_config = basic_auth_config
        self.tech_acc_config = tech_acc_config
        self.wss_config = wss_config
        self.url_sec_lock = RLock()
        self._wss = WSSE()
        self._target_separator = MISC.SEPARATOR

    def _handle_security_basic_auth(self, cid, sec_def, path_info, body, headers):
        """ Performs the authentication using HTTP Basic Auth.
        """
        env = {'HTTP_AUTHORIZATION':headers.get('HTTP_AUTHORIZATION')}
        url_config = {'basic-auth-username':sec_def.username, 'basic-auth-password':sec_def.password}
        
        result = on_basic_auth(env, url_config, False)
        
        if not result:
            msg = 'UNAUTHORIZED path_info:[{}], cid:[{}], sec-wall code:[{}], description:[{}]\n'.format(
                path_info, cid, result.code, result.description)
            logger.error(msg)
            raise Unauthorized(cid, msg, 'Basic realm="{}"'.format(sec_def.realm))
        
    def _handle_security_wss(self, cid, sec_def, path_info, body, headers):
        """ Performs the authentication using WS-Security.
        """
        if not body:
            raise Unauthorized(cid, 'No message body found in [{}]'.format(body), 'zato-wss')
            
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
            msg = 'Could not parse the WS-Security data, body:[{}], e:[{}]'.format(body, format_exc(e))
            raise Unauthorized(cid, msg, 'zato-wss')
        
        if not result:
            msg = 'UNAUTHORIZED path_info:[{}], cid:[{}], sec-wall code:[{}], description:[{}]\n'.format(
                path_info, cid, result.code, result.description)
            logger.error(msg)
            raise Unauthorized(cid, msg, 'zato-wss')
        
    def _handle_security_tech_acc(self, cid, sec_def, path_info, body, headers):
        """ Performs the authentication using technical accounts.
        """
        zato_headers = ('HTTP_X_ZATO_USER', 'HTTP_X_ZATO_PASSWORD')
        
        for header in zato_headers:
            if not headers.get(header, None):
                error_msg = ("[{}] The header [{}] doesn't exist or is empty, URI:[{}, headers:[{}]]").\
                    format(cid, header, path_info, headers)
                logger.error(error_msg)
                raise Unauthorized(cid, error_msg, 'zato-tech-acc')

        # Note that logs get a specific information what went wrong whereas the
        # user gets a generic 'username or password' message
        msg_template = '[{}] The {} is incorrect, URI:[{}], X_ZATO_USER:[{}]'

        if headers['HTTP_X_ZATO_USER'] != sec_def.name:
            error_msg = msg_template.format(cid, 'username', path_info, headers['HTTP_X_ZATO_USER'])
            user_msg = msg_template.format(cid, 'username or password', path_info, headers['HTTP_X_ZATO_USER'])
            logger.error(error_msg)
            raise Unauthorized(cid, user_msg, 'zato-tech-acc')
        
        incoming_password = sha256(headers['HTTP_X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()
        
        if incoming_password != sec_def.password:
            error_msg = msg_template.format(cid, 'password', path_info, headers['HTTP_X_ZATO_USER'])
            user_msg = msg_template.format(cid, 'username or password', path_info, headers['HTTP_X_ZATO_USER'])
            logger.error(error_msg)
            raise Unauthorized(cid, user_msg, 'zato-tech-acc')
        
# ##############################################################################

    def match(self, url_path, soap_action):
        """ Attemps to match the combination of SOAP Action and URL path against 
        the list of HTTP channel targets.
        """
        target = '{}{}{}'.format(soap_action, self._target_separator, url_path)
        for item in self.channel_data:
            match = item.match_target_compiled.parse(target)
            if match:
                if logger.isEnabledFor(TRACE1):
                    logger.log(TRACE1, 'Matched target:[%s] with:[%r]', target, item)
                return match, item

        return None, None
            
    def check_security(self, cid, channel_item, path_info, payload, wsgi_environ):
        """ Authenticates and authorizes a given request. Returns None on success
        or raises an exception otherwise.
        """
        sec = self.url_sec[channel_item.match_target]
        if sec.sec_def != ZATO_NONE:
            sec_def, sec_def_type = sec.sec_def, sec.sec_def.sec_type
            handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
            getattr(self, handler_name)(cid, sec_def, path_info, payload, wsgi_environ)
        
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

# ##############################################################################

    def _delete_channel_data(self, sec_type, sec_name):
        match_idx = ZATO_NONE
        for item in self.channel_data:
            if item.sec_type == sec_type and item.security_name == sec_name:
                match_idx = self.channel_data.index(item)
                
        # No error, let's delete channel info
        if match_idx != ZATO_NONE:
            self.channel_data.pop(match_idx)

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
        """ Creates a new HTTP Basic Auth security definition
        """
        with self.url_sec_lock:
            self._update_basic_auth(msg.name, msg)
        
    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            del self.basic_auth_config[msg.old_name]
            self._update_basic_auth(msg.name, msg)
            self._update_url_sec(msg, security_def_type.basic_auth)
            
    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('basic_auth', msg.name)
            del self.basic_auth_config[msg.name]
            self._update_url_sec(msg, security_def_type.basic_auth, True)
        
    def on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self.basic_auth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, security_def_type.basic_auth)

# ##############################################################################

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
            self._update_url_sec(msg, security_def_type.tech_account)
        
    def on_broker_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        with self.url_sec_lock:
            self._delete_channel_data('tech_acc', msg.name)
            del self.tech_acc_config[msg.name]
            self._update_url_sec(msg, security_def_type.tech_account, True)
        
    def on_broker_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        with self.url_sec_lock:
            # The message's 'password' attribute already takes the salt 
            # into account (pun intended ;-))
            self.tech_acc_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, security_def_type.tech_account)
            
# ##############################################################################

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
            self._update_url_sec(msg, security_def_type.wss)
        
    def on_broker_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        with self.url_sec_lock:
            self._delete_channel_data('wss', msg.name)
            del self.wss_config[msg.name]
            self._update_url_sec(msg, security_def_type.wss, True)
        
    def on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        with self.url_sec_lock:
            # The message's 'password' attribute already takes the salt 
            # into account.
            self.wss_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, security_def_type.wss)
            
# ##############################################################################

    def _channel_item_from_msg(self, msg, match_target):
        """ Creates a channel info bunch out of an incoming CREATE_EDIT message.
        """
        channel_item = Bunch()
        for name in('connection', 'data_format', 'host', 'id', 'is_active',
            'is_internal', 'method', 'name', 'ping_method', 'pool_size', 
            'service_id',  'impl_name', 'service_name',
            'soap_action', 'soap_version', 'transport', 'url_path',
            'merge_url_params_req', 'url_params_pri', 'params_pri'):
            
            channel_item[name] = msg[name]
            
        if msg.get('security_id'):
            channel_item['sec_type'] = msg['sec_type']
            channel_item['security_id'] = msg['security_id']
            channel_item['security_name'] = msg['security_name']
        
        channel_item.service_impl_name = msg.impl_name
        channel_item.match_target = match_target
        channel_item.match_target_compiled = parse_compile(channel_item.match_target)
        
        return channel_item
        
    def _sec_info_from_msg(self, msg):
        """ Creates a security info bunch out of an incoming CREATE_EDIT message.
        """
        sec_info = Bunch()
        sec_info.is_active = msg.is_active
        sec_info.data_format = msg.data_format
        sec_info.transport = msg.transport
        
        if msg.get('security_name'):
            sec_info.sec_def = Bunch()
            sec_config = getattr(self, '{}_config'.format(msg['sec_type']))
            config_item = sec_config[msg['security_name']]
            
            for k, v in config_item['config'].items():
                sec_info.sec_def[k] = config_item['config'][k]
        else:
            sec_info.sec_def = ZATO_NONE
        
        return sec_info
    
    def _create_channel(self, msg):
        """ Creates a new channel, both its core data and the related security definition.
        """
        match_target = '{}{}{}'.format(msg.soap_action, MISC.SEPARATOR, msg.url_path)
        self.channel_data.append(self._channel_item_from_msg(msg, match_target))
        self.url_sec[match_target] = self._sec_info_from_msg(msg)
        
    def _delete_channel(self, msg):
        """ Deletes a channel, both its core data and the related security definition.
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
            self.channel_data.pop(match_idx)
            
        # Channel's security now
        del self.url_sec[old_match_target]

    def on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        with self.url_sec_lock:
            # Only edits have 'old_name', creates don't. So for edits we delete
            # the channel and later recreate it while creates, obviously,
            # get to creation only.
            if msg.get('old_name'):
                self._delete_channel(msg)
                
            self._create_channel(msg)
            
    def on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        with self.url_sec_lock:
            self._delete_channel(msg)

# ##############################################################################
