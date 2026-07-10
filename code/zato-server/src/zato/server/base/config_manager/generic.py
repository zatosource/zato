# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC, HL7, LDAP, ZATO_NONE
from zato.common.broker_message import GENERIC as GENERIC_BROKER_MSG
from zato.common.const import SECRETS
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, parse_simple_type
from zato.common.util.config import replace_query_string_items_in_dict
from zato.server.base.config_manager.common import ConfigManagerImpl
from zato.server.generic.api.channel_hl7_mllp import channel_config_defaults, channel_int_config_keys
from zato.server.generic.api.cloud_aws import cloud_aws_config_defaults, cloud_aws_int_config_keys
from zato.server.generic.api.outconn_as2 import outconn_as2_bool_config_keys, outconn_as2_config_defaults, \
    outconn_as2_int_config_keys
from zato.server.generic.api.outconn_hl7_fhir import outconn_fhir_config_defaults, outconn_fhir_int_config_keys
from zato.server.generic.api.outconn_hl7_mllp import outconn_config_defaults, outconn_int_config_keys
from zato.server.generic.api.outconn_odata import outconn_odata_bool_config_keys, outconn_odata_config_defaults, \
    outconn_odata_int_config_keys
from zato.server.generic.api.outconn_sftp import outconn_sftp_bool_config_keys, outconn_sftp_config_defaults, \
    outconn_sftp_int_config_keys
from zato.server.generic.api.outconn_mongodb import outconn_mongodb_bool_config_keys, outconn_mongodb_config_defaults, \
    outconn_mongodb_int_config_keys
from zato.server.generic.api.outconn_smb import outconn_smb_config_defaults, outconn_smb_int_config_keys
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

_secret_prefixes = (SECRETS.Encrypted_Indicator, SECRETS.PREFIX)

# The prefix GenericConnection.from_model gives to column-backed fields
# that the incoming message did not carry at all.
_no_value_marker = '<no-value-given-'

# The auth types a FHIR outgoing connection's security definition can resolve to
_fhir_auth_type_basic = HL7.Const.FHIR_Auth_Type.Basic_Auth.id
_fhir_auth_type_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# ################################################################################################################################
# ################################################################################################################################

class Generic(ConfigManagerImpl):
    """ Handles broker messages destined for generic objects, such as connections.
    """
    logger: 'Logger'
    generic_conn_api: 'stranydict'
    _generic_conn_handler: 'stranydict'
    _get_generic_impl_func: 'callable_'

# ################################################################################################################################

    def _find_conn_info(self, item_id:'int', item_name:'str'='') -> 'tuple_':

        if item_id:
            search_key = 'id'
            search_value = int(item_id)
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
            msg = cast_('stranydict', conn.to_sql_dict(True))

        item = GenericConnection.from_bunch(msg)
        item_dict = cast_('stranydict', item.to_dict(True))

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

# ################################################################################################################################

    def _edit_generic_connection(self, msg:'stranydict', skip:'any_'=None, secret:'strnone'=None) -> 'None':

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

        # Connections managed by the queue bridge also need the new secret pushed there -
        # the edit above only rebuilt the server-side wrapper. The edit call stored
        # the new secret in the message, which is what the notifiers read.
        type_ = edit_msg['type_']

        if type_ in (COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA, COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ):
            self._notify_queue_bridge_channel('edit', edit_msg)

        elif type_ in (COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA, COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ):
            self._notify_queue_bridge_outconn('edit', edit_msg)

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

        self.on_config_event_GENERIC_CONNECTION_EDIT(edit_msg, ['conn', 'parent'])

# ################################################################################################################################

    def _on_config_event_GENERIC_CONNECTION_COMMON_ACTION(
        self,
        msg:'stranydict',
        *args: 'any_',
        **kwargs: 'any_'
    ) -> 'None':

        func = self._get_generic_impl_func(msg)
        if func:
            func(msg)

# ################################################################################################################################

    def on_config_event_GENERIC_CONNECTION_CREATE(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._on_config_event_GENERIC_CONNECTION_COMMON_ACTION(*args, **kwargs)

# ################################################################################################################################

    def on_config_event_GENERIC_CONNECTION_EDIT(
        self,
        msg:'stranydict',
        *args: 'any_',
        **kwargs: 'any_'
    ) -> 'None':

        return self._on_config_event_GENERIC_CONNECTION_COMMON_ACTION(msg, *args, **kwargs)

# ################################################################################################################################

    def on_config_event_GENERIC_CONNECTION_DELETE(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._on_config_event_GENERIC_CONNECTION_COMMON_ACTION(*args, **kwargs)

# ################################################################################################################################

    on_config_event_GENERIC_CONNECTION_CHANGE_PASSWORD = _change_password_generic_connection

# ################################################################################################################################

    def _generic_normalize_config_channel_hl7_mllp(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply,
        e.g. when a channel is created directly through zato.generic.connection.create,
        and coerces numeric fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None ..
        for key, default in channel_config_defaults.items():
            if config.get(key) is None:
                config[key] = default

        # .. and make sure numeric fields are integers.
        for key in channel_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

# ################################################################################################################################

    def _generic_normalize_config_cloud_aws(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply,
        e.g. when a connection is created directly through zato.generic.connection.create,
        and coerces numeric fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None ..
        for key, default in cloud_aws_config_defaults.items():
            if config.get(key) is None:
                config[key] = default

        # .. and make sure numeric fields are integers.
        for key in cloud_aws_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

# ################################################################################################################################

    def _generic_normalize_config_outconn_as2(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply and coerces
        numeric and boolean fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None - column-backed fields
        # the message did not carry arrive as no-value markers and count as missing too ..
        for key, default in outconn_as2_config_defaults.items():
            value = config.get(key)
            is_marker = isinstance(value, str) and value.startswith(_no_value_marker)
            if value is None or is_marker:
                config[key] = default

        # .. make sure numeric fields are integers ..
        for key in outconn_as2_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

        # .. and make sure boolean fields are booleans.
        for key in outconn_as2_bool_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = as_bool(value)

# ################################################################################################################################

    def _generic_normalize_config_outconn_hl7_fhir(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply, coerces numeric fields
        that may arrive as strings from opaque storage and resolves the connection's security definition
        into the fields the FHIR client reads.
        """

        # Apply a default for every field that is missing or None ..
        for key, default in outconn_fhir_config_defaults.items():
            if config.get(key) is None:
                config[key] = default

        # .. the Dashboard sends this marker when no security definition was selected ..
        if config['security_id'] == ZATO_NONE:
            config['security_id'] = 0

        # .. make sure numeric fields are integers ..
        for key in outconn_fhir_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

        # .. without a security definition, there is nothing more to resolve.
        security_id = config['security_id']
        if not security_id:
            return

        # A Basic Auth definition maps to the username and password the client sends ..
        if sec_def := self.basic_auth_get_by_id(security_id):
            config['auth_type'] = _fhir_auth_type_basic
            config['username'] = sec_def['username']
            config['secret'] = sec_def['password']

        # .. anything else is an OAuth one - the client needs the auth type only
        # .. because tokens are obtained per request through the bearer token manager.
        else:
            config['auth_type'] = _fhir_auth_type_oauth

# ################################################################################################################################

    def _generic_normalize_config_outconn_hl7_mllp(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply and coerces
        numeric fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None ..
        for key, default in outconn_config_defaults.items():
            if config.get(key) is None:
                config[key] = default

        # .. and make sure numeric fields are integers.
        for key in outconn_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

# ################################################################################################################################

    def _generic_normalize_config_outconn_odata(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply and coerces
        numeric and boolean fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None - column-backed fields
        # the message did not carry arrive as no-value markers and count as missing too ..
        for key, default in outconn_odata_config_defaults.items():
            value = config.get(key)
            is_marker = isinstance(value, str) and value.startswith(_no_value_marker)
            if value is None or is_marker:
                config[key] = default

        # .. make sure numeric fields are integers ..
        for key in outconn_odata_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

        # .. and make sure boolean fields are booleans.
        for key in outconn_odata_bool_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = as_bool(value)

# ################################################################################################################################

    def _generic_normalize_config_outconn_sftp(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply and coerces
        numeric and boolean fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None ..
        for key, default in outconn_sftp_config_defaults.items():
            if config.get(key) is None:
                config[key] = default

        # .. make sure numeric fields are integers ..
        for key in outconn_sftp_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

        # .. and make sure boolean fields are booleans.
        for key in outconn_sftp_bool_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = as_bool(value)

# ################################################################################################################################

    def _generic_normalize_config_outconn_mongodb(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply and coerces
        numeric and boolean fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None ..
        for key, default in outconn_mongodb_config_defaults.items():
            if config.get(key) is None:
                config[key] = default

        # .. make sure numeric fields are integers ..
        for key in outconn_mongodb_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

        # .. and make sure boolean fields are booleans.
        for key in outconn_mongodb_bool_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = as_bool(value)

# ################################################################################################################################

    def _generic_normalize_config_outconn_smb(self, config:'stranydict') -> 'None':
        """ Fills in defaults for fields that the create path did not supply and coerces
        numeric fields that may arrive as strings from opaque storage.
        """

        # Apply a default for every field that is missing or None ..
        for key, default in outconn_smb_config_defaults.items():
            if config.get(key) is None:
                config[key] = default

        # .. and make sure numeric fields are integers.
        for key in outconn_smb_int_config_keys:
            value = config[key]
            if isinstance(value, str):
                config[key] = int(value)

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
