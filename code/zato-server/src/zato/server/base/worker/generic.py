# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC, LDAP
from zato.common.broker_message import GENERIC as GENERIC_BROKER_MSG
from zato.common.util.api import as_bool, parse_simple_type
from zato.server.base.worker.common import WorkerImpl
from zato.server.generic.connection import GenericConnection

# ################################################################################################################################
# ################################################################################################################################

_channel_file_transfer = COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER

# ################################################################################################################################
# ################################################################################################################################

class Generic(WorkerImpl):
    """ Handles broker messages destined for generic objects, such as connections.
    """
    def __init__(self):
        super(Generic, self).__init__()

# ################################################################################################################################

    def _find_conn_info(self, item_id):

        found_conn_dict = None
        found_name = None

        for conn_type, value in self.generic_conn_api.items():
            for conn_name, conn_dict in value.items():
                if conn_dict['id'] == item_id:
                    return conn_dict, value

        return found_conn_dict, found_name

# ################################################################################################################################

    def _delete_generic_connection(self, msg):

        conn_dict, conn_value = self._find_conn_info(msg.id)
        if not conn_dict:
            raise Exception('Could not find configuration matching input message `{}`'.format(msg))
        else:

            # Delete the connection object ..
            conn = conn_dict.conn
            conn.delete()

            # .. and delete the connection from the configuration object.
            conn_name = conn_dict['name']
            del conn_value[conn_name]

        # Run a special path for file transfer channels
        if msg['type_'] == _channel_file_transfer:
            self._delete_file_transfer_channel(msg)

# ################################################################################################################################

    def _create_generic_connection(self, msg, needs_roundtrip=False, skip=None, raise_exc=True, is_starting=False):

        # This roundtrip is needed to re-format msg in the format the underlying .from_bunch expects
        # in case this is a broker message rather than a startup one.
        if needs_roundtrip:
            conn = GenericConnection.from_dict(msg, skip)
            msg = conn.to_sql_dict(True)

        item = GenericConnection.from_bunch(msg)
        item_dict = item.to_dict(True)

        for key in msg:
            if key not in item_dict:
                if key != 'action':
                    item_dict[key] = msg[key]

        item_dict.queue_build_cap = self.server.fs_server_config.misc.queue_build_cap
        item_dict.auth_url = msg.get('address')

        # Normalize the contents of the configuration message
        self.generic_normalize_config(item_dict)

        config_attr = self.generic_conn_api[item.type_]
        wrapper = self._generic_conn_handler[item.type_]

        config_attr[msg.name] = item_dict
        config_attr[msg.name].conn = wrapper(item_dict, self.server)
        config_attr[msg.name].conn.build_wrapper()

        if not is_starting:

            # Run a special path for file transfer channels
            if msg['type_'] == _channel_file_transfer:
                self._create_file_transfer_channel(msg)

# ################################################################################################################################

    def _edit_generic_connection(self, msg, skip=None, secret=None):

        # Special-case file transfer channels
        if msg['type_'] == _channel_file_transfer:
            self._edit_file_transfer_channel(msg)
            return

        # Find and store connection password/secret for later use
        # if we do not have it already and we will if we are called from ChangePassword.
        if not secret:
            conn_dict, _ = self._find_conn_info(msg.id)
            secret = conn_dict['secret']

        # Delete the connection
        self._delete_generic_connection(msg)

        # Recreate it now but make sure to include the secret too
        msg['secret'] = secret
        self._create_generic_connection(msg, True, skip)

# ################################################################################################################################

    def ping_generic_connection(self, conn_id):
        conn_dict, _ = self._find_conn_info(conn_id)

        self.logger.info('About to ping generic connection `%s` (%s)', conn_dict.name, conn_dict.type_)
        conn_dict.conn.ping()
        self.logger.info('Generic connection `%s` pinged successfully (%s)', conn_dict.name, conn_dict.type_)

# ################################################################################################################################

    def _change_password_generic_connection(self, msg):
        conn_dict, _ = self._find_conn_info(msg['id'])

        # Create a new message without live Python objects
        edit_msg = Bunch()
        for key, value in conn_dict.items():
            if key in ('conn', 'parent'):
                continue
            edit_msg[key] = value

        # Now, edit the connection which will actually delete it and create again
        self._edit_generic_connection(edit_msg, secret=msg.password)

# ################################################################################################################################

    def reconnect_generic(self, conn_id):
        found_conn_dict, found_name = self._find_conn_info(conn_id)

        edit_msg = Bunch()
        edit_msg['action'] = GENERIC_BROKER_MSG.CONNECTION_EDIT.value

        for k, v in found_conn_dict.items():
            if k in ('conn', 'parent'):
                continue
            else:
                edit_msg[k] = v

        self.on_broker_msg_GENERIC_CONNECTION_EDIT(edit_msg, ['conn', 'parent'])

# ################################################################################################################################

    def on_broker_msg_GENERIC_CONNECTION_CREATE(self, msg, *args, **kwargs):

        func = self._get_generic_impl_func(msg)
        func(msg)

    on_broker_msg_GENERIC_CONNECTION_EDIT            = on_broker_msg_GENERIC_CONNECTION_CREATE
    on_broker_msg_GENERIC_CONNECTION_DELETE          = on_broker_msg_GENERIC_CONNECTION_CREATE
    on_broker_msg_GENERIC_CONNECTION_CHANGE_PASSWORD = on_broker_msg_GENERIC_CONNECTION_CREATE

# ################################################################################################################################

    def _generic_normalize_config_outconn_ldap(self, config):

        config.pool_max_cycles = int(config.pool_max_cycles)
        config.pool_keep_alive = int(config.pool_keep_alive)
        config.use_auto_range = as_bool(config.use_auto_range)
        config.use_tls = as_bool(config.use_tls)

        # If GSS-API SASL method is used, the username may be a set of credentials actually
        if config.sasl_mechanism == LDAP.SASL_MECHANISM.GSSAPI.id:
            sasl_credentials = []
            if config.username:
                for elem in config.username.split():
                    elem = elem.strip()
                    elem = parse_simple_type(elem)
                    sasl_credentials.append(elem)
            config.sasl_credentials = sasl_credentials
        else:
            config.sasl_credentials = None

        # Initially, this will be a string but during ChangePassword we are reusing
        # the same configuration object in which case it will be already a list.
        if not isinstance(config.server_list, list):
            config.server_list = [server.strip() for server in config.server_list.splitlines()]

# ################################################################################################################################

    def generic_normalize_config(self, config):

        # Normalize type name to one that can potentially point to a method of ours
        type_ = config['type_'] # type: str
        preprocess_type = type_.replace('-', '_')

        # Check if there is such a method and if so, invoke it to preprocess the message
        func = getattr(self, '_generic_normalize_config_{}'.format(preprocess_type), None)
        if func:
            try:
                func(config)
            except Exception:
                self.logger.warn('Could not invoke `%s` with `%r`', func, config)
                raise

# ################################################################################################################################
