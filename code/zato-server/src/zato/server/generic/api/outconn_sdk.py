# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from inspect import getmodule, isclass
from logging import getLogger
from time import time

# gevent
from gevent import sleep, spawn, Timeout
from gevent.lock import RLock
from gevent.queue import Empty, Queue

# Bunch
from zato.common.ext.bunch import Bunch, bunchify

# Zato
from zato.common.broker_message import GENERIC as BROKER_MSG_GENERIC
from zato.common.facade import PubSubFacade
from zato.common.sdk import Connector, ConnectionLost, CredentialsExpired, Field, PooledConnector, SubscribingConnector
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

# The watchdog timeout around every invocation when a definition carries no timeout of its own, in seconds.
default_invoke_timeout = 60

# How long to wait before the first reconnect attempt and the cap the delay grows to, in seconds.
reconnect_backoff_initial = 0.5
reconnect_backoff_max = 30

# How often the framework confirms that a subscribing connector's connection is still alive, in seconds.
subscribing_monitor_interval = 2

# How long a per-tenant client can stay unused before it is stopped, and how often expiry runs, in seconds.
tenant_idle_expiry = 900
tenant_sweep_interval = 30

# The names of the methods the framework calls itself - everything else that is public and callable
# on a connector is an invocation method and services get it wrapped with the framework behaviors.
lifecycle_method_names = {
    'create_client', 'ping', 'on_stop', 'validate', 'refresh_credentials', 'start_process',
    'get_connection', 'on_get_from_pool', 'on_return_to_pool', 'on_started', 'invoke', 'publish',
}

# ################################################################################################################################
# ################################################################################################################################

class InvocationTimeout(Exception):
    """ Raised in the calling service when the watchdog timeout around an invocation passes (4.4).
    """

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

        while True:

            # A freshly built connection needs no validation below.
            is_fresh = False

            # An idle connection is used right away and building a new one is preferred over waiting ..
            with self._lock:
                try:
                    conn = self._idle.get_nowait()
                except Empty:
                    if self._created < self.size:
                        conn = self.connector.create_client()
                        self._created += 1
                        is_fresh = True
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

            # A reused connection is validated before use - one that is no longer usable
            # is discarded and the loop builds or waits for another one (4.2).
            if not is_fresh:
                try:
                    self.connector.validate(conn)
                except Exception:
                    logger.info('Discarding a pooled connection of `%s` that failed validation', self.connector.name)
                    self._discard(conn)
                    continue

            # The hook lets the author reset any conversational state before the connection is used.
            self.connector.on_get_from_pool(conn)

            return conn

# ################################################################################################################################

    def _discard(self, conn:'any_') -> 'None':
        """ Closes a connection that failed validation and makes room in the pool for its replacement.
        """
        try:
            self.connector.on_stop(conn)
        except Exception:
            # The connection is already unusable, so failures while closing it change nothing.
            pass

        # Room for a replacement connection to be built.
        with self._lock:
            self._created -= 1

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

def resolve_invoke_timeout(config:'stranydict') -> 'int':
    """ Returns the watchdog timeout for a definition - its own timeout column if it carries one,
    the default otherwise. The value can arrive as a string or a no-value marker from opaque storage.
    """
    value = config.get('timeout')

    if isinstance(value, str):
        value = int(value) if value.isdigit() else 0

    if not value:
        value = default_invoke_timeout

    return value

# ################################################################################################################################
# ################################################################################################################################

class SDKConnectorWrapper(Wrapper):
    """ Hosts a single instance of a hot-deployed SDK connector along with the client the connector built.
    """
    wrapper_type = 'SDK connector'

    def __init__(self, config:'stranydict', server:'ParallelServer'=None) -> 'None':
        super().__init__(config, server)
        self.connector:'Connector | None' = None

        # The watchdog timeout around every invocation, overridable per call (4.4).
        self.invoke_timeout = resolve_invoke_timeout(config)

        # Per-tenant connectors, keyed by their resolved config overrides (4.6).
        self.tenants:'stranydict' = {}

        # Whether the greenlet that expires idle tenant clients is already running.
        self._tenant_sweep_started = False

# ################################################################################################################################

    def _build_connector(self, overrides:'stranydict | None'=None) -> 'Connector':
        """ Builds a new connector instance with all its ambient attributes and resolved config,
        optionally overlaid with per-tenant overrides (4.6).
        """

        # Look up the class registered for our connection type ..
        server = cast_('ParallelServer', self.server)
        connector_class = server.config_manager.sdk_connector_types[self.config['type_']]

        # .. build a new connector instance ..
        connector = connector_class()

        # .. give it its ambient attributes (6.8) ..
        connector.name = self.config['name']
        connector.invoke = server.invoke
        connector.publish = PubSubFacade(server, self.config['name']).publish

        # .. helper processes the connector starts report their unexpected exits here ..
        connector._on_process_died = self._on_process_died

        # .. resolve the fields the class declares into the connector's own config ..
        schema = get_schema(connector_class)
        config = Bunch()

        for field_name in schema:
            config[field_name] = self.config[field_name]

        # .. per-tenant overrides take precedence over the definition's own values ..
        if overrides:
            for field_name, value in overrides.items():
                config[field_name] = value

        connector.config = config

        return connector

# ################################################################################################################################

    def _build_client(self, connector:'Connector') -> 'any_':
        """ Builds the client for a connector - a framework-owned pool for pooled connectors,
        a single shared client built through create_client for everyone else.
        """

        # Pooled connectors get a pool that builds connections lazily through create_client ..
        if isinstance(connector, PooledConnector):

            # A definition without a pool size of its own uses the default one, e.g. one imported with enmasse.
            pool_size = self.config.get('pool_size')
            if not pool_size:
                pool_size = default_pool_size

            client = SDKConnectionPool(connector, pool_size)
            connector._pool = client

        # .. everyone else gets a single shared client built now.
        else:
            client = connector.create_client()

        connector.client = client
        return client

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        connector = self._build_connector()
        client = self._build_client(connector)

        # Subscribing connectors subscribe now, before anyone can use the connection (2.3).
        if isinstance(connector, SubscribingConnector):
            connector.on_started(client)

        # Expose both the connector and its client for later use ..
        self.connector = connector
        self._impl = client
        self.is_connected = True

        # .. and watch subscribing connections so a lost one reconnects and resubscribes on its own (4.3).
        if isinstance(connector, SubscribingConnector):
            _ = spawn(self._monitor_subscribing, connector, client)

# ################################################################################################################################

    def _stop_client(self, connector:'Connector') -> 'None':
        """ Stops a connector's client - each pooled connection through on_stop for pools,
        the one shared client otherwise - and stops the helper processes the connector started.
        """
        client = connector.client

        try:
            # A pool closes each of its connections through the connector's on_stop hook.
            if isinstance(client, SDKConnectionPool):
                client.stop()
            else:
                connector.on_stop(client)
        except Exception:
            # The connection is going away, so failures while closing it change nothing.
            logger.warning('Could not stop the client of `%s`', connector.name, exc_info=True)

        # Helper processes die with the connection they belong to (6.9).
        for process in connector._processes:
            process.stop()

# ################################################################################################################################

    def _rebuild_with_backoff(self, failed_client:'any_') -> 'None':
        """ Evicts the current client and rebuilds the connection, retrying with a growing delay
        until it succeeds or the definition is deleted (4.3).
        """
        with self.update_lock:

            # Someone else already rebuilt the connection, e.g. a concurrent invocation noticed the loss first.
            if self._impl is not failed_client:
                return

            # The old client goes away no matter what state it is in ..
            self._stop_client(cast_('Connector', self.connector))

            # .. and the new one is built with a growing delay between attempts.
            delay = reconnect_backoff_initial

            while not self.delete_requested:
                try:
                    self._init_impl()
                except Exception:
                    logger.warning('Could not reconnect `%s`, retrying in %ss', self.config['name'], delay, exc_info=True)
                    sleep(delay)
                    delay = min(delay * 2, reconnect_backoff_max)
                else:
                    logger.info('Reconnected `%s`', self.config['name'])
                    return

# ################################################################################################################################

    def _on_process_died(self, process:'any_') -> 'None':
        """ Called by a helper process's watcher when the process exits unexpectedly -
        the whole connection is rebuilt with backoff, which re-runs create_client (3.1).
        """

        # The definition is going away, so the death needs no reaction.
        if self.delete_requested:
            return

        logger.warning('Helper process of `%s` died, rebuilding the connection', self.config['name'])

        # A moment of backoff before the restart, in case the process dies right away again.
        sleep(reconnect_backoff_initial)

        self._rebuild_with_backoff(self._impl)

# ################################################################################################################################

    def _monitor_subscribing(self, connector:'Connector', client:'any_') -> 'None':
        """ Confirms periodically that a subscribing connector's connection is still alive and,
        when it is not, rebuilds it - which re-runs on_started, resubscribing (4.3).
        """
        while True:
            sleep(subscribing_monitor_interval)

            # The definition was deleted, so there is nothing to watch anymore.
            if self.delete_requested:
                return

            # The connection was rebuilt or edited - its new incarnation has its own monitor.
            if self.connector is not connector:
                return

            try:
                connector.validate(client)
            except Exception:
                logger.warning('Connection of `%s` is down, reconnecting', self.config['name'])
                self._rebuild_with_backoff(client)
                return

# ################################################################################################################################

    def get_tenant_connector(self, overrides:'stranydict') -> 'Connector':
        """ Returns the connector serving one distinct set of config overrides, building it
        on first use - one definition, one client per distinct resolved credential set (4.6).
        """
        key = tuple(sorted(overrides.items()))

        with self.update_lock:

            entry = self.tenants.get(key)

            # The tenant already has a live client, so only its idle clock is reset.
            if entry:
                entry['last_used'] = time()
                return entry['connector']

            # First use of this credential set - build a connector and client of its own.
            connector = self._build_connector(overrides)
            _ = self._build_client(connector)

            self.tenants[key] = {'connector': connector, 'last_used': time()}

            # The sweep greenlet starts with the first tenant and serves all of them.
            if not self._tenant_sweep_started:
                self._tenant_sweep_started = True
                _ = spawn(self._sweep_tenants)

            return connector

# ################################################################################################################################

    def evict_tenant(self, connector:'Connector') -> 'None':
        """ Removes a tenant's client after its connection was lost - the next use builds a new one.
        """
        with self.update_lock:
            for key, entry in list(self.tenants.items()):
                if entry['connector'] is connector:
                    del self.tenants[key]
                    self._stop_client(connector)
                    return

# ################################################################################################################################

    def _sweep_tenants(self) -> 'None':
        """ Stops per-tenant clients that have been idle for too long (4.6).
        """
        while not self.delete_requested:
            sleep(tenant_sweep_interval)

            now = time()

            with self.update_lock:
                for key, entry in list(self.tenants.items()):
                    if now - entry['last_used'] > tenant_idle_expiry:
                        logger.info('Stopping an idle tenant client of `%s`', self.config['name'])
                        del self.tenants[key]
                        self._stop_client(entry['connector'])

# ################################################################################################################################

    def _delete(self) -> 'None':

        # There is nothing to close if the client was never built, e.g. the connection was inactive.
        if not self.connector:
            return

        # The main client goes first ..
        self._stop_client(self.connector)

        # .. and each tenant's client follows.
        with self.update_lock:
            for entry in self.tenants.values():
                self._stop_client(entry['connector'])
            self.tenants.clear()

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

def build_invocation(wrapper:'SDKConnectorWrapper', overrides:'stranydict | None', name:'str') -> 'any_':
    """ Wraps one invocation method with the framework behaviors - a watchdog timeout overridable
    per call (4.4), validate-before-use (4.2), a one-time retry after credential refresh (4.5)
    and eviction with reconnect when the connection is lost (4.3).
    """
    def _invocation(*args:'any_', **kwargs:'any_') -> 'any_':

        # The caller can override the definition's watchdog timeout for this one call.
        timeout = kwargs.pop('timeout', None)
        if timeout is None:
            timeout = wrapper.invoke_timeout

        timeout_exception = InvocationTimeout('Call `{}` to `{}` timed out after {}s'.format(
            name, wrapper.config['name'], timeout))

        # Everything below - validation, the call itself and any retry - runs under the watchdog.
        with Timeout(timeout, timeout_exception):

            connector = _resolve_connector(wrapper, overrides)

            # Shared clients are validated before each use - pooled connections validate
            # at checkout inside the pool instead (4.2).
            if not isinstance(connector, PooledConnector):
                try:
                    connector.validate(connector.client)
                except CredentialsExpired:
                    # The client is alive, only its credentials expired - refresh and carry on (4.5).
                    connector.refresh_credentials()
                except InvocationTimeout:
                    # The watchdog fired while validation was stuck - the caller gets the timeout as is.
                    raise
                except Exception:
                    # The client is gone - evict it, reconnect and use the new instance.
                    _evict(wrapper, connector, overrides)
                    connector = _resolve_connector(wrapper, overrides)

            method = getattr(connector, name)

            try:
                return method(*args, **kwargs)
            except CredentialsExpired:
                # Refresh the credentials and retry the invocation once (4.5).
                connector.refresh_credentials()
                return method(*args, **kwargs)
            except ConnectionLost:
                # The connection is gone - reconnect in the background and let the caller know (4.3).
                _evict_async(wrapper, connector, overrides)
                raise

    return _invocation

# ################################################################################################################################

def _resolve_connector(wrapper:'SDKConnectorWrapper', overrides:'stranydict | None') -> 'Connector':
    """ Returns the connector an invocation goes to - the definition's main one or a tenant's own.
    """
    if overrides is None:
        out = cast_('Connector', wrapper.connector)
    else:
        out = wrapper.get_tenant_connector(overrides)

    return out

# ################################################################################################################################

def _evict(wrapper:'SDKConnectorWrapper', connector:'Connector', overrides:'stranydict | None') -> 'None':
    """ Evicts a client that failed validation and rebuilds it now, in the caller's own greenlet.
    """
    if overrides is None:
        with wrapper.update_lock:
            # Only rebuild if no concurrent invocation was faster.
            if wrapper.connector is connector:
                wrapper._stop_client(connector)
                wrapper._init_impl()
    else:
        wrapper.evict_tenant(connector)

# ################################################################################################################################

def _evict_async(wrapper:'SDKConnectorWrapper', connector:'Connector', overrides:'stranydict | None') -> 'None':
    """ Evicts a client whose connection was lost mid-call - the main client reconnects with backoff
    in the background, a tenant's client is simply removed and rebuilt on its next use.
    """
    if overrides is None:
        _ = spawn(wrapper._rebuild_with_backoff, connector.client)
    else:
        wrapper.evict_tenant(connector)

# ################################################################################################################################
# ################################################################################################################################

class ConnectorProxy:
    """ What a service gets from self.out - forwards attribute access to the connector while wrapping
    every public invocation method with the framework behaviors (see build_invocation).
    """
    __slots__ = ('_wrapper', '_overrides')

    def __init__(self, wrapper:'SDKConnectorWrapper', overrides:'stranydict | None'=None) -> 'None':
        self._wrapper = wrapper
        self._overrides = overrides

# ################################################################################################################################

    def with_config(self, **overrides:'any_') -> 'ConnectorProxy':
        """ Returns access to a client built for this distinct set of config overrides -
        one definition, one client per credential set, with idle expiry (4.6).
        """
        out = ConnectorProxy(self._wrapper, overrides)
        return out

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':

        connector = _resolve_connector(self._wrapper, self._overrides)
        item = getattr(connector, name)

        # Only public invocation methods get the framework behaviors - lifecycle methods
        # belong to the framework and plain attributes pass through as they are.
        if name.startswith('_') or name in lifecycle_method_names or not callable(item):
            return item

        out = build_invocation(self._wrapper, self._overrides, name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class ConnectorContainer:
    """ Dict-like access to all the connection definitions of one connector type, e.g. self.out.crm['My CRM'].
    """
    __slots__ = ('_container',)

    def __init__(self, container:'stranydict') -> 'None':
        self._container = container

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'ConnectorProxy':

        # This raises a KeyError if there is no definition of that name ..
        item = self._container[name]

        # .. the wrapper hosts the connector instance that services interact with ..
        wrapper = item['conn']

        # .. accessing the client builds it now if it does not exist yet ..
        client = wrapper.client

        # .. no client at this point means the build failed and the reason is in the server log.
        if client is None:
            raise Exception('Connection `{}` could not be built'.format(name))

        out = ConnectorProxy(wrapper)
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
