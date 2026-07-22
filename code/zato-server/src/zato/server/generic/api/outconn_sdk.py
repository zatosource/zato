# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from inspect import getmodule, isclass
from logging import getLogger

# Bunch
from zato.common.ext.bunch import Bunch, bunchify

# Zato
from zato.common.broker_message import GENERIC as BROKER_MSG_GENERIC
from zato.common.sdk import Connector, Field
from zato.common.sdk.connector import get_schema
from zato.common.typing_ import cast_, list_
from zato.common.util.api import as_bool
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import module_, stranydict, strtuple
    from zato.server.base.config_manager import ConfigManager
    from zato.server.base.parallel import ParallelServer
    ConfigManager = ConfigManager
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

connector_class_list = list_[type[Connector]]

# The prefix that turns a connector's short type name, e.g. 'crm', into the full connection type, e.g. 'outconn-crm'.
type_prefix = 'outconn-'

# The prefix GenericConnection.from_model gives to column-backed fields that the incoming message did not carry at all.
_no_value_marker = '<no-value-given-'

# ################################################################################################################################
# ################################################################################################################################

class SDKConnectorWrapper(Wrapper):
    """ Hosts a single instance of a hot-deployed SDK connector along with the client the connector built.
    """
    wrapper_type = 'SDK connector'

    def __init__(self, config:'stranydict', server:'ParallelServer'=None) -> 'None':
        super().__init__(config, server)
        self.connector:'Connector | None' = None

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        # Look up the class registered for our connection type ..
        server = cast_('ParallelServer', self.server)
        connector_class = server.config_manager.sdk_connector_types[self.config['type_']]

        # .. build a new connector instance ..
        connector = connector_class()

        # .. give it its ambient attributes ..
        connector.name = self.config['name']

        # .. resolve the fields the class declares into the connector's own config ..
        schema = get_schema(connector_class)
        config = Bunch()

        for field_name in schema:
            config[field_name] = self.config[field_name]

        connector.config = config

        # .. let the author's code build the underlying client ..
        client = connector.create_client()

        # .. and expose both the connector and its client for later use.
        connector.client = client
        self.connector = connector
        self._impl = client
        self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':

        # There is nothing to close if the client was never built, e.g. the connection was inactive.
        if not self.connector:
            return

        self.connector.on_stop(self._impl)

# ################################################################################################################################

    def _ping(self) -> 'None':

        # The base class made sure the client exists before this method ran.
        connector = cast_('Connector', self.connector)
        connector.ping(self._impl)

# ################################################################################################################################
# ################################################################################################################################

class ConnectorContainer:
    """ Dict-like access to all the connection definitions of one connector type, e.g. self.out.crm['My CRM'].
    """
    __slots__ = ('_container',)

    def __init__(self, container:'stranydict') -> 'None':
        self._container = container

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'Connector':

        # This raises a KeyError if there is no definition of that name ..
        item = self._container[name]

        # .. the wrapper hosts the connector instance that services interact with ..
        wrapper = item['conn']

        # .. accessing the client builds it now if it does not exist yet ..
        client = wrapper.client

        # .. no client at this point means the build failed and the reason is in the server log.
        if client is None:
            raise Exception('Connection `{}` could not be built'.format(name))

        out = wrapper.connector
        return out

# ################################################################################################################################
# ################################################################################################################################

def attach_connector_type(config_manager:'ConfigManager', type_:'str') -> 'None':
    """ Attaches a registered connector type to the config manager's generic connection maps.
    Called both when a type is first registered and after a configuration reload rebuilds the maps.
    """

    # The container with the type's connection definitions - an existing one survives redeployments ..
    if type_ not in config_manager.generic_conn_api:
        config_manager.generic_conn_api[type_] = {}

    # .. the wrapper class that hosts connector instances ..
    config_manager._generic_conn_handler[type_] = SDKConnectorWrapper

    # .. and the handlers for configuration messages about this type.
    impl_map = config_manager.generic_impl_func_map.setdefault(type_, {})
    impl_map[BROKER_MSG_GENERIC.CONNECTION_CREATE.value] = config_manager._create_generic_connection
    impl_map[BROKER_MSG_GENERIC.CONNECTION_EDIT.value] = config_manager._edit_generic_connection
    impl_map[BROKER_MSG_GENERIC.CONNECTION_DELETE.value] = config_manager._delete_generic_connection
    impl_map[BROKER_MSG_GENERIC.CONNECTION_CHANGE_PASSWORD.value] = config_manager._change_password_generic_connection

# ################################################################################################################################
# ################################################################################################################################

def register_connector_type(config_manager:'ConfigManager', connector_class:'type[Connector]') -> 'str':
    """ Registers a connector class under its full type name and starts any definitions of that type
    that are already stored in the configuration store. Returns the full type name.
    """

    # E.g. 'crm' becomes 'outconn-crm'.
    type_ = type_prefix + connector_class.type

    # A redeployment of an already registered type only swaps the class - definitions that are running
    # keep their current instances and clients built from now on use the new class.
    is_new = type_ not in config_manager.sdk_connector_types
    config_manager.sdk_connector_types[type_] = connector_class

    if not is_new:
        logger.info('Updated connector type `%s` (%s)', type_, connector_class.__name__)
        return type_

    # Attach the type to all the config maps ..
    attach_connector_type(config_manager, type_)

    logger.info('Registered connector type `%s` (%s)', type_, connector_class.__name__)

    # .. and start the definitions of this type that were stored when the server was starting -
    # .. they could not start back then because the type was not registered yet.
    for config_dict in config_manager.config_store.generic_connection.values():
        if config_dict:
            config = config_dict.get('config')
            if config:
                if config['type_'] == type_:
                    config_manager._create_generic_connection(bunchify(config), raise_exc=False, is_starting=True)

    return type_

# ################################################################################################################################
# ################################################################################################################################

def extract_connector_classes(mod:'module_') -> 'connector_class_list':
    """ Returns all the Connector subclasses defined directly in the given module.
    """
    out:'connector_class_list' = []

    for name in sorted(dir(mod)):
        item = getattr(mod, name)

        # Only classes can be connectors ..
        if not isclass(item):
            continue

        # .. the base class itself is not one ..
        if item is Connector:
            continue

        # .. it must subclass the base class ..
        if not issubclass(item, Connector):
            continue

        # .. it must be defined in this very module, not merely imported into it ..
        if getmodule(item) is not mod:
            continue

        # .. and it must name its type.
        if not item.type:
            continue

        out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################

def normalize_connector_config(connector_class:'type[Connector]', config:'stranydict') -> 'None':
    """ Fills in defaults for declared fields that the create path did not supply and coerces
    integer and boolean fields that may arrive as strings from opaque storage.
    """
    schema = get_schema(connector_class)

    for field_name, field in schema.items():

        value = config.get(field_name)

        # Apply the declared default if the field is missing or carries a no-value marker ..
        is_marker = isinstance(value, str) and value.startswith(_no_value_marker)
        if value is None or is_marker:
            config[field_name] = field.default
            continue

        # .. make sure integer fields are integers - an empty string means
        # .. the create path had no value for the field, so its default applies ..
        if isinstance(field, Field.Int):
            if isinstance(value, str):
                if value:
                    config[field_name] = int(value)
                else:
                    config[field_name] = field.default

        # .. and make sure boolean fields are booleans.
        elif isinstance(field, Field.Bool):
            if isinstance(value, str):
                config[field_name] = as_bool(value)

# ################################################################################################################################
# ################################################################################################################################

def get_secret_field_names(config_manager:'ConfigManager', type_:'str') -> 'strtuple':
    """ Returns the names of all the Secret fields the connector type declares
    or an empty tuple if the type is not a registered connector type.
    """
    connector_class = config_manager.sdk_connector_types.get(type_)
    if not connector_class:
        return ()

    names = []
    schema = get_schema(connector_class)

    for field_name, field in schema.items():
        if isinstance(field, Field.Secret):
            names.append(field_name)

    out = tuple(names)
    return out

# ################################################################################################################################
# ################################################################################################################################
