# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC, LDAP, ZATO_NONE
from zato.common.broker_message import GENERIC as GENERIC_BROKER_MSG
from zato.common.const import SECRETS
from zato.common.util.api import as_bool, parse_simple_type
from zato.common.util.config import replace_query_string_items_in_dict
from zato.distlock import PassThrough as PassThroughLock
from zato.server.base.worker.common import WorkerImpl
from zato.server.generic.connection import GenericConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from zato.common.typing_ import any_, callable_, stranydict, strnone, tuple_
    from zato.server.connection.queue import Wrapper
    Wrapper = Wrapper

# ################################################################################################################################
# ################################################################################################################################

_type_outconn_wsx = COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_WSX
_type_channel_file_transfer = COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER
_secret_prefixes = (SECRETS.Encrypted_Indicator, SECRETS.PREFIX)

# ################################################################################################################################
# ################################################################################################################################

class Generic(WorkerImpl):
    """ Handles broker messages destined for generic objects, such as connections.
    """
    logger: 'Logger'
    generic_conn_api: 'stranydict'
    _generic_conn_handler: 'stranydict'
    _get_generic_impl_func: 'callable_'
    _delete_file_transfer_channel: 'callable_'
    _edit_file_transfer_channel: 'callable_'
    _create_file_transfer_channel: 'callable_'

# ################################################################################################################################

    def _find_conn_info(self, item_id:'int', item_name:'str'='') -> 'tuple_':

        if item_id:
            search_key = 'id'
            search_value = item_id
        else:
            search_key = 'name'
            search_value = item_name

        found_conn_dict = None
        found_name = None

        for _ignored_conn_type, value in self.generic_conn_api.items():
            for _ignored_conn_name, conn_dict in value.items():
                if conn_dict[search_key] == search_value:
                    return conn_dict, value

        return found_conn_dict, found_name

# ################################################################################################################################

    def get_conn_dict_by_id(self, conn_id:'int') -> 'dict | None':
        conn_dict, _ = self._find_conn_info(conn_id)
        return conn_dict

# ################################################################################################################################

    def is_active_generic_conn(self, conn_id:'int') -> 'bool':

        # Try to find such a connection ..
        conn_dict = self.get_conn_dict_by_id(conn_id)

        # .. if it exists, we can check if it is active ..
        if conn_dict:
            return conn_dict['is_active']

        # .. otherwise, assume that it is not.
        else:
            return False

# ################################################################################################################################

    def _delete_generic_connection(self, msg:'stranydict') -> 'None':

        conn_dict, conn_value = self._find_conn_info(msg['id'], msg['name'])
        if not conn_dict:
            raise Exception('Could not find configuration matching input message `{}`'.format(msg))
        else:

            # Delete the connection object ..
            conn = conn_dict.conn # type: Wrapper

            # .. provide the reason code if the connection type supports it ..
            has_delete_reasons = getattr(conn, 'has_delete_reasons', None)
            if has_delete_reasons:
                conn.delete(reason=COMMON_GENERIC.DeleteReason)
            else:
                conn.delete()

            # .. and delete the connection from the configuration object.
            conn_name = conn_dict['name']
            _ = conn_value.pop(conn_name, None)

        # Run a special path for file transfer channels
        if msg['type_'] == _type_channel_file_transfer:
            self._delete_file_transfer_channel(msg)

# ################################################################################################################################

    def _create_generic_connection(
        self,
        msg:'stranydict',
        needs_roundtrip:'bool'=False,
        skip:'any_'=None,
        raise_exc:'bool'=True,
        is_starting:'bool'=False
    ) -> 'None':

        # This roundtrip is needed to re-format msg in the format the underlying .from_bunch expects
        # in case this is a broker message rather than a startup one.
        if needs_roundtrip:
            conn = GenericConnection.from_dict(msg, skip)
            msg = conn.to_sql_dict(True)

        item = GenericConnection.from_bunch(msg)
        item_dict = item.to_dict(True) # type: stranydict

        for key in msg:
            if key not in item_dict:
                if key != 'action':
                    item_dict[key] = msg[key]

        item_dict['queue_build_cap'] = self.server.fs_server_config.misc.queue_build_cap
        item_dict['auth_url'] = msg.get('address')

        # Normalize the contents of the configuration message
        self.generic_normalize_config(item_dict)

        config_attr = self.generic_conn_api.get(item.type_)

        if config_attr is None:
            self.logger.info('No config attr found for generic connection `%s`', item.type_)
            return

        wrapper = self._generic_conn_handler[item.type_]

        msg_name = msg['name'] # type: str

        # It is possible that some of the input keys point to secrets
        # and other data that will be encrypted. In such a case,
        # decrypt them all here upfront.
        for key, value in item_dict.items():
            if isinstance(value, str):
                if value.startswith(_secret_prefixes):
                    value = self.server.decrypt(value)
                    item_dict[key] = value

        # Mask out all the relevant attributes
        replace_query_string_items_in_dict(self.server, item_dict)

        config_attr[msg_name] = item_dict
        conn_wrapper = wrapper(item_dict, self.server)
        config_attr[msg_name].conn = conn_wrapper
        config_attr[msg_name].conn.build_wrapper()

        if not is_starting:

            # Run a special path for file transfer channels
            if msg['type_'] == _type_channel_file_transfer:
                self._create_file_transfer_channel(msg)

# ################################################################################################################################

    def _edit_generic_connection(self, msg:'stranydict', skip:'any_'=None, secret:'strnone'=None) -> 'None':

        # Special-case file transfer channels
        if msg['type_'] == _type_channel_file_transfer:
            self._edit_file_transfer_channel(msg)
            return

        # If we do not have a secret on input, we need to look it up in the incoming message.
        # If it is still not there, assume that we are going to reuse the same secret
        # that we already have defined for the object

        if not secret:
            secret = msg.get('secret', ZATO_NONE)

        if secret == ZATO_NONE:
            conn_dict, _ = self._find_conn_info(msg['id'])
            secret = conn_dict['secret']

        # Delete the connection
        self._delete_generic_connection(msg)

        # Recreate it now but make sure to include the secret too
        msg['secret'] = secret
        self._create_generic_connection(msg, True, skip)

# ################################################################################################################################

    def ping_generic_connection(self, conn_id:'int') -> 'None':
        conn_dict, _ = self._find_conn_info(conn_id)

        self.logger.info('About to ping generic connection `%s` (%s)', conn_dict.name, conn_dict.type_)
        conn = conn_dict['conn']
        conn.ping()
        self.logger.info('Generic connection `%s` pinged successfully (%s)', conn_dict.name, conn_dict.type_)

# ################################################################################################################################

    def _change_password_generic_connection(self, msg:'stranydict') -> 'None':

        conn_dict, _ = self._find_conn_info(msg['id'])

        # Create a new message without live Python objects
        edit_msg = Bunch()
        for key, value in conn_dict.items():
            if key in ('conn', 'parent'):
                continue
            edit_msg[key] = value

        # Now, edit the connection which will actually delete it and create again
        self._edit_generic_connection(edit_msg, secret=msg['password'])

# ################################################################################################################################

    def reconnect_generic(self, conn_id:'int') -> 'None':
        found_conn_dict, _ = self._find_conn_info(conn_id)

        if not found_conn_dict:
            return

        edit_msg = Bunch()
        edit_msg['action'] = GENERIC_BROKER_MSG.CONNECTION_EDIT.value

        for k, v in found_conn_dict.items():
            if k in ('conn', 'parent'):
                continue
            else:
                edit_msg[k] = v

        self.on_broker_msg_GENERIC_CONNECTION_EDIT(edit_msg, ['conn', 'parent'])

# ################################################################################################################################

    def _on_broker_msg_GENERIC_CONNECTION_COMMON_ACTION(
        self,
        msg:'stranydict',
        *args: 'any_',
        **kwargs: 'any_'
    ) -> 'None':

        func = self._get_generic_impl_func(msg)
        if func:
            func(msg)

# ################################################################################################################################

    def on_broker_msg_GENERIC_CONNECTION_CREATE(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._on_broker_msg_GENERIC_CONNECTION_COMMON_ACTION(*args, **kwargs)

# ################################################################################################################################

    def _get_edit_generic_lock(self, is_outconn_wsx:'bool', msg:'stranydict') -> 'callable_':

        # Outgoing WSX connections that connect to Zato use a specific lock type ..
        if is_outconn_wsx:
            lock = self.server.wsx_connection_pool_wrapper.get_update_lock(is_zato=msg['is_zato'])
            return lock

        # .. if we are here, we use a pass-through lock.
        return PassThroughLock

# ################################################################################################################################

    def on_broker_msg_GENERIC_CONNECTION_EDIT(
        self,
        msg:'stranydict',
        *args: 'any_',
        **kwargs: 'any_'
    ) -> 'None':

        # Local variables
        _is_outconn_wsx = msg['type_'] == _type_outconn_wsx

        # Find out what kind of a lock to use ..
        _lock = self._get_edit_generic_lock(_is_outconn_wsx, msg)

        # .. do use it ..
        with _lock(msg['id']):

            # .. and update the connection now.
            return self._on_broker_msg_GENERIC_CONNECTION_COMMON_ACTION(msg, *args, **kwargs)

# ################################################################################################################################

    def on_broker_msg_GENERIC_CONNECTION_DELETE(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._on_broker_msg_GENERIC_CONNECTION_COMMON_ACTION(*args, **kwargs)

# ################################################################################################################################

    on_broker_msg_GENERIC_CONNECTION_CHANGE_PASSWORD = _change_password_generic_connection

# ################################################################################################################################

    def _generic_normalize_config_outconn_ldap(self, config:'stranydict') -> 'None':

        config['pool_max_cycles'] = int(config['pool_max_cycles'])
        config['pool_keep_alive'] = int(config['pool_keep_alive'])
        config['use_auto_range'] = as_bool(config['use_auto_range'])
        config['use_tls'] = as_bool(config['use_tls'])

        # If GSS-API SASL method is used, the username may be a set of credentials actually
        if config['sasl_mechanism'] == LDAP.SASL_MECHANISM.GSSAPI.id:
            sasl_credentials = []
            if config['username']:
                for elem in config['username'].split():
                    elem = elem.strip()
                    elem = parse_simple_type(elem)
                    sasl_credentials.append(elem)
            config['sasl_credentials'] = sasl_credentials
        else:
            config['sasl_credentials'] = None

        # Initially, this will be a string but during ChangePassword we are reusing
        # the same configuration object in which case it will be already a list.
        if not isinstance(config['server_list'], list):
            config['server_list'] = [server.strip() for server in config['server_list'].splitlines()]

# ################################################################################################################################

    def generic_normalize_config(self, config:'stranydict') -> 'None':

        # Normalize type name to one that can potentially point to a method of ours
        type_ = config['type_'] # type: str
        preprocess_type = type_.replace('-', '_')

        # Check if there is such a method and if so, invoke it to preprocess the message
        func = getattr(self, '_generic_normalize_config_{}'.format(preprocess_type), None)
        if func:
            try:
                func(config)
            except Exception:
                self.logger.warning('Could not invoke `%s` with `%r`', func, config)
                raise

# ################################################################################################################################
# ################################################################################################################################
