# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.common.util import asbool
from zato.server.base.worker.common import WorkerImpl
from zato.server.generic.connection import GenericConnection

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
            conn_dict.conn.delete()
            del conn_value[conn_dict['name']]

# ################################################################################################################################

    def _create_generic_connection(self, msg, needs_roundtrip=False, skip=None):

        # This roundtrip is needed to re-format msg in the format the underlying .from_bunch expects
        # in case this is a broker message rather than a startup one.
        if needs_roundtrip:
            conn = GenericConnection.from_dict(msg, skip)
            msg = conn.to_sql_dict(True)

        item = GenericConnection.from_bunch(msg)
        item_dict = item.to_dict(True)

        item_dict.queue_build_cap = self.server.fs_server_config.misc.queue_build_cap
        item_dict.auth_url = msg.address

        # Normalize the contents of the configuration message
        self.generic_normalize_config(item_dict)

        config_attr = self.generic_conn_api[item.type_]
        wrapper = self._generic_conn_handler[item.type_]

        config_attr[msg.name] = item_dict
        config_attr[msg.name].conn = wrapper(item_dict, self.server)
        config_attr[msg.name].conn.build_queue()

# ################################################################################################################################

    def _edit_generic_connection(self, msg, skip=None):
        self._delete_generic_connection(msg)
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
        #conn_dict.conn.change_password(msg)

        # Create a new message without live Python objects
        edit_msg = Bunch()
        for key, value in conn_dict.items():
            if key in ('conn', 'parent'):
                continue
            edit_msg[key] = value

        # Now, edit the connection which will actually delete it and create again
        self._edit_generic_connection(edit_msg)

# ################################################################################################################################

    def reconnect_generic(self, conn_id):
        found_conn_dict, found_name = self._find_conn_info(conn_id)
        self.on_broker_msg_GENERIC_CONNECTION_EDIT(found_conn_dict, ['conn', 'parent'])

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
        config.use_auto_range = asbool(config.use_auto_range)
        config.use_sasl_external = asbool(config.use_sasl_external)
        config.use_tls = asbool(config.use_tls)

        # Initially, this will be a string but during ChangePassword we are reusing
        # the same configuration object in which case it will be already a list.
        if not isinstance(config.server_list, list):
            config.server_list = [elem.strip() for elem in config.server_list.splitlines()]

# ################################################################################################################################

    def generic_normalize_config(self, config):

        # Normalize type name to one that can potentially point to a method of ours
        type_ = config['type_'] # type: str
        preprocess_type = type_.replace('-', '_')

        # Check if there is such a method and if so, invoke it to preprocess the message
        func = getattr(self, '_generic_normalize_config_{}'.format(preprocess_type), None)
        if func:
            func(config)

# ################################################################################################################################
