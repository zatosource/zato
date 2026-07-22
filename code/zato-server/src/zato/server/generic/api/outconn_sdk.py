# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from inspect import getmodule, isclass
from logging import getLogger

# gevent
from gevent.lock import RLock
from gevent.queue import Empty, Queue

# Bunch
from zato.common.ext.bunch import Bunch, bunchify

# Zato
from zato.common.broker_message import GENERIC as BROKER_MSG_GENERIC
from zato.common.sdk import Connector, Field, PooledConnector
from zato.common.sdk.connector import get_schema
from zato.common.typing_ import cast_, list_
from zato.common.util.api import as_bool
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, module_, stranydict, strtuple
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

# How many connections a pool holds when a definition carries no pool size of its own.
default_pool_size = 10

# How long a caller waits for a free pooled connection before giving up, in seconds.
pool_acquire_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class SDKConnectionPool:
    """ A framework-owned pool of connections for PooledConnector subclasses. Connections are built
    lazily through the connector's create_client, up to the pool's size, and callers borrow them
    one at a time through the acquire context manager.
    """

    def __init__(self, connector:'PooledConnector', size:'int') -> 'None':
        self.connector = connector
        self.size = size

        # Guards the creation counter so the pool never grows beyond its size.
        self._lock = RLock()

        # Connections that are built and idle.
        self._idle = Queue()

        # How many connections have been built so far.
        self._created = 0

        # Once the pool is stopped, returned connections are closed instead of being pooled again.
        self._is_stopped = False

# ################################################################################################################################

    @contextmanager
    def acquire(self):
        """ Borrows a connection for the duration of a with block, running the connector's
        pool hooks on the way out and back in.
        """
        conn = self._checkout()

        try:
            yield conn
        finally:
            self._checkin(conn)

# ################################################################################################################################

    def _checkout(self) -> 'any_':

        # An idle connection is used right away and building a new one is preferred over waiting ..
        with self._lock:
            try:
                conn = self._idle.get_nowait()
            except Empty:
                if self._created < self.size:
                    conn = self.connector.create_client()
                    self._created += 1
                else:
                    conn = None

        # .. with the pool exhausted, wait until someone returns a connection - outside the lock,
        # .. so that returning callers are not blocked from doing so.
        if conn is None:
            try:
                conn = self._idle.get(timeout=pool_acquire_timeout)
            except Empty:
                raise Exception('No free pooled connection for `{}` after {}s'.format(
                    self.connector.name, pool_acquire_timeout))

        # The hook lets the author reset any conversational state before the connection is used.
        self.connector.on_get_from_pool(conn)

        return conn

# ################################################################################################################################

    def _checkin(self, conn:'any_') -> 'None':

        # The hook lets the author clean up before the connection is available to others.
        self.connector.on_return_to_pool(conn)

        # A connection returned after the pool stopped is closed, not pooled again.
        if self._is_stopped:
            self.connector.on_stop(conn)
        else:
            self._idle.put(conn)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Closes all the idle connections and marks the pool stopped, which makes
        any connection still borrowed close upon its return.
        """
        self._is_stopped = True

        while True:
            try:
                conn = self._idle.get_nowait()
            except Empty:
                break
            else:
                self.connector.on_stop(conn)

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

        # .. pooled connectors get a framework-owned pool that builds connections lazily
        # .. through create_client, everyone else gets a single shared client built now ..
        if isinstance(connector, PooledConnector):

            # A definition without a pool size of its own uses the default one, e.g. one imported with enmasse.
            pool_size = self.config.get('pool_size')
            if not pool_size:
                pool_size = default_pool_size

            client = SDKConnectionPool(connector, pool_size)
            connector._pool = client
        else:
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

        # A pool closes each of its connections through the connector's on_stop hook.
        if isinstance(self._impl, SDKConnectionPool):
            self._impl.stop()
        else:
            self.connector.on_stop(self._impl)

# ################################################################################################################################

    def _ping(self) -> 'None':

        # The base class made sure the client exists before this method ran.
        connector = cast_('Connector', self.connector)

        # A pooled connector pings a connection borrowed from the pool.
        if isinstance(self._impl, SDKConnectionPool):
            with self._impl.acquire() as conn:
                connector.ping(conn)
        else:
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
