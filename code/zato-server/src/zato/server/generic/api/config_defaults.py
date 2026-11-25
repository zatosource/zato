# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The defaults and the typed keys of the configuration of the generic connection types whose wrapper modules
# the config manager imports when it builds the first connection of each type. The module imports no client library.

# Zato
from zato.common.api import Atlassian, AWS, ES, GRPC, LDAP, MongoDB, SMB
from zato.common.file_transfer.api import Default_Verify_How

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

strobjectdict = dict[str, object]

# ################################################################################################################################
# ################################################################################################################################

# Defaults for fields that the create path may not have supplied,
# e.g. when a connection is created directly through zato.generic.connection.create.
cloud_aws_config_defaults = {
    'region': AWS.Default.Region,
    'endpoint_url': '',
    'access_key_id': '',
    'pool_size': AWS.Default.Pool_Size,
}

# Values of these configuration keys may arrive as strings from opaque storage and need to be integers.
cloud_aws_int_config_keys = ['pool_size']

# ################################################################################################################################
# ################################################################################################################################

# Defaults of the Jira and Confluence connections for fields that the create path may not have supplied,
# e.g. when a connection is created directly through zato.generic.connection.create.
cloud_atlassian_config_defaults = {
    'api_version': Atlassian.Default.API_Version,
    'is_cloud': Atlassian.Default.Is_Cloud,
}

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_es_config_defaults:'strobjectdict' = {
    'address_list': ES.Default.Address_List,
    'username': '',
    'timeout': ES.Default.Timeout,
    'tls_ca_certs_file': '',
    'tls_cert_key_file': '',
    'is_tls_validation_enabled': True,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_es_int_config_keys = ('timeout',)

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_es_bool_config_keys = ('is_tls_validation_enabled',)

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_grpc_config_defaults:'strobjectdict' = {
    'address': GRPC.Default.Address,
    'username': '',
    'is_tls': True,
    'tls_ca_certs_file': '',
    'proto_path': '',
    'stub_module': '',
    'stub_class': '',
    'ping_timeout': GRPC.Default.Ping_Timeout,
    'max_send_message_size': GRPC.Default.Max_Message_Size,
    'max_recv_message_size': GRPC.Default.Max_Message_Size,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_grpc_int_config_keys = ('ping_timeout', 'max_send_message_size', 'max_recv_message_size')

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_grpc_bool_config_keys = ('is_tls',)

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_ldap_config_defaults:'stranydict' = {
    'is_tls_enabled': False,
    'use_tls': False,
    'get_info': LDAP.GET_INFO.SCHEMA.id,
    'connect_timeout': LDAP.DEFAULT.CONNECT_TIMEOUT,
    'ip_mode': LDAP.IP_MODE.IP_SYSTEM_DEFAULT.id,
    'auto_bind': LDAP.AUTO_BIND.DEFAULT.id,
    'pool_ha_strategy': LDAP.POOL_HA_STRATEGY.ROUND_ROBIN.id,
    'pool_max_cycles': LDAP.DEFAULT.POOL_MAX_CYCLES,
    'pool_exhaust_timeout': LDAP.DEFAULT.POOL_EXHAUST_TIMEOUT,
    'pool_keep_alive': LDAP.DEFAULT.POOL_KEEP_ALIVE,
    'pool_lifetime': LDAP.DEFAULT.POOL_LIFETIME,
    'pool_name': '',
    'use_auto_range': True,
    'should_check_names': False,
    'should_return_empty_attrs': True,
    'is_read_only': False,
    'sasl_mechanism': '',
}

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_mongodb_config_defaults:'strobjectdict' = {
    'server_list': MongoDB.Default.Server_List,
    'username': '',
    'auth_source': MongoDB.Default.Auth_Source,
    'replica_set': '',
    'app_name': MongoDB.Default.App_Name,
    'pool_size_max': MongoDB.Default.Pool_Size_Max,
    'connect_timeout': MongoDB.Default.Connect_Timeout,
    'server_select_timeout': MongoDB.Default.Server_Select_Timeout,
    'is_tls_enabled': False,
    'tls_ca_certs_file': '',
    'tls_cert_key_file': '',
    'is_tls_validation_enabled': True,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_mongodb_int_config_keys = ('pool_size_max', 'connect_timeout', 'server_select_timeout')

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_mongodb_bool_config_keys = ('is_tls_enabled', 'is_tls_validation_enabled')

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_smb_config_defaults:'strobjectdict' = {
    'host': '',
    'port': SMB.DEFAULT.PORT,
    'username': '',
    'should_store_content': False,
    'verify_how': Default_Verify_How,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_smb_int_config_keys = ('port',)

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_smb_bool_config_keys = ('should_store_content',)

# Config keys that must be strings but may arrive as integers from opaque storage
outconn_smb_string_config_keys = ('host', 'username', 'verify_how')

# ################################################################################################################################
# ################################################################################################################################
