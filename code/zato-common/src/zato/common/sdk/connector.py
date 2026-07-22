# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.sdk.process import Process
from zato.common.typing_ import dict_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

class ConnectionLost(Exception):
    """ Raised by a connector's ping, validate or any invocation method to signal that the underlying
    connection is gone - the framework evicts the client and reconnects with backoff.
    """

# ################################################################################################################################
# ################################################################################################################################

class CredentialsExpired(Exception):
    """ Raised by a connector's invocation method to signal that its credentials expired -
    the framework calls refresh_credentials and retries the invocation once.
    """

# ################################################################################################################################
# ################################################################################################################################

class _FieldBase:
    """ Base class for the schema field types that connectors declare their configuration with.
    """
    def __init__(self, default:'any_'=None) -> 'None':
        self.default = default

# ################################################################################################################################
# ################################################################################################################################

fielddict = dict_[str, _FieldBase]

# ################################################################################################################################
# ################################################################################################################################

class Field:
    """ Schema field types. A connector declares its configuration as class attributes of these types
    and the framework stores, resolves and delivers their values through the connector's self.config.
    """

    class Text(_FieldBase):
        """ A text field.
        """
        def __init__(self, default:'str'='') -> 'None':
            super().__init__(default)

    class Int(_FieldBase):
        """ An integer field.
        """
        def __init__(self, default:'int'=0) -> 'None':
            super().__init__(default)

    class Bool(_FieldBase):
        """ A boolean field.
        """
        def __init__(self, default:'bool'=False) -> 'None':
            super().__init__(default)

    class Secret(_FieldBase):
        """ A field whose value is a secret - it is stored encrypted and it is never returned in listings.
        """
        def __init__(self) -> 'None':
            super().__init__('')

# ################################################################################################################################
# ################################################################################################################################

class Connector:
    """ Base class for user-defined outgoing connection types. A subclass sets the type attribute,
    declares its configuration schema with Field types and implements create_client and ping.
    Invocation methods are plain methods the subclass adds freely - the framework never calls them, services do.
    """

    # The short type name, e.g. 'crm', under which services access connections of this type as self.out.crm.
    type:'str' = ''

    def __init__(self) -> 'None':

        # The name of the connection definition this instance serves.
        self.name = ''

        # The resolved values of the fields the subclass declares.
        self.config = Bunch()

        # The object returned by create_client, set by the framework once the client is built.
        self.client:'any_' = None

        # A logger for the connector to use.
        self.logger = getLogger('zato')

        # Hands a message over to a service, matching self.invoke in services. Set by the framework.
        self.invoke:'any_' = None

        # Publishes a message to a pub/sub topic, matching self.publish in services. Set by the framework.
        self.publish:'any_' = None

        # The helper processes this connector started, stopped by the framework with the connection.
        self._processes:'list[Process]' = []

        # What start_process gives each process to call if it dies unexpectedly. Set by the framework.
        self._on_process_died:'any_' = None

# ################################################################################################################################

    def create_client(self) -> 'any_':
        """ Builds and returns the underlying client object. Called by the framework when the connection starts.
        """
        raise Exception('Method create_client must be implemented by connector subclasses')

# ################################################################################################################################

    def ping(self, client:'any_') -> 'None':
        """ Confirms that the connection is usable, raising an exception if it is not.
        Called by the framework when the connection is pinged.
        """
        raise Exception('Method ping must be implemented by connector subclasses')

# ################################################################################################################################

    def on_stop(self, client:'any_') -> 'None':
        """ Closes the client. Called by the framework when the definition is deleted or edited
        and when the server shuts down. The default implementation does nothing.
        """

# ################################################################################################################################

    def validate(self, client:'any_') -> 'None':
        """ Checks whether the client is still usable before each use, raising an exception
        to make the framework evict it and reconnect. The default implementation calls self.ping.
        """
        self.ping(client)

# ################################################################################################################################

    def refresh_credentials(self) -> 'None':
        """ Called by the framework when an invocation raises CredentialsExpired, after which
        the invocation is retried once. The default implementation does nothing.
        """

# ################################################################################################################################

    def start_process(self, command:'strlist') -> 'Process':
        """ Starts and supervises a helper process. Provided by the framework, never overridden.
        Any '{port}' placeholder in the command is replaced with a local port allocated for the process.
        The process is stopped with the connection and, if it dies unexpectedly, the framework
        rebuilds the whole connection with backoff, re-running create_client.
        """
        process = Process(command, self._on_process_died)
        self._processes.append(process)
        return process

# ################################################################################################################################
# ################################################################################################################################

class SubscribingConnector(Connector):
    """ Base class for connection types where the remote side pushes messages on its own.
    The framework calls on_started when the connection first starts and again after every reconnect,
    which is the moment to subscribe and replay state. Received messages are handed over to services
    with self.invoke or published to pub/sub topics with self.publish.
    """

    def on_started(self, client:'any_') -> 'None':
        """ Subscribes and replays state. Called by the framework when the connection first starts
        and again after every reconnect. The default implementation does nothing.
        """

# ################################################################################################################################
# ################################################################################################################################

class PooledConnector(Connector):
    """ Base class for connection types whose connections hold per-connection state, e.g. a logon
    handshake followed by one call at a time. The framework owns a pool of connections - create_client
    builds one connection and invocation methods borrow one for the duration of each call
    through the get_connection context manager.
    """

    def __init__(self) -> 'None':
        super().__init__()

        # The framework-owned pool, set when the connection starts.
        self._pool:'any_' = None

# ################################################################################################################################

    def get_connection(self) -> 'any_':
        """ Returns a context manager that borrows a connection from the pool for the duration
        of a with block. Provided by the framework, never overridden.
        """
        return self._pool.acquire()

# ################################################################################################################################

    def on_get_from_pool(self, conn:'any_') -> 'None':
        """ Resets conversational state when a connection is taken from the pool.
        Called by the framework each time get_connection hands a connection out.
        The default implementation does nothing.
        """

# ################################################################################################################################

    def on_return_to_pool(self, conn:'any_') -> 'None':
        """ Cleans up when a connection goes back to the pool. Called by the framework
        each time a with block using get_connection ends. The default implementation does nothing.
        """

# ################################################################################################################################
# ################################################################################################################################

def get_schema(connector_class:'type[Connector]') -> 'fielddict':
    """ Returns all the fields the connector class declares, mapping each field's name to its Field instance.
    """
    out:'fielddict' = {}

    for name in dir(connector_class):
        item = getattr(connector_class, name)
        if isinstance(item, _FieldBase):
            out[name] = item

    return out

# ################################################################################################################################
# ################################################################################################################################
