# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What every queue delivery suite runs its server's queues against - one pub/sub backend at a time.

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.common.pubsub.sql.config import ModuleCtx as PubSubDBCtx
from zato.common.test.rabbitmq_ import RabbitMQProcess

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths
    from zato.common.typing_ import strlist, strnone

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

Backend_SQLite   = 'sqlite'
Backend_AMQP     = 'amqp'
Backend_AMQP_SSL = 'amqp_ssl'

# Every backend, in the order they are run in
All_Backends = (
    Backend_SQLite,
    Backend_AMQP,
    Backend_AMQP_SSL,
)

# The backends whose queues live in a broker
Broker_Backends = (
    Backend_AMQP,
    Backend_AMQP_SSL,
)

# The CA every TLS client in a process trusts
SSL_CA_Env_Name = 'SSL_CERT_FILE'

# A comma-separated list of backend names that narrows the run
Backends_Env_Name = 'Zato_Test_PubSub_Backends'

SQLite_File_Name = 'pubsub.db'

# ################################################################################################################################
# ################################################################################################################################

def get_backend_names() -> 'strlist':
    """ The backends this run goes through.
    """
    requested = os.environ.get(Backends_Env_Name)

    if requested is None:
        out:'strlist' = list(All_Backends)
        return out

    out = []

    for name in requested.split(','):
        name = name.strip()

        if name not in All_Backends:
            raise ValueError(f'Unknown pub/sub backend `{name}` in {Backends_Env_Name}, expected one of {All_Backends}')

        out.append(name)

    return out

# ################################################################################################################################

@contextmanager
def pubsub_path_env(db_path:'str') -> 'envgen':
    """ Points Zato_PubSub_DB_Path at one SQLite file for as long as the context is open.
    """
    old_path = os.environ.get(PubSubDBCtx.Env_Path)
    os.environ[PubSubDBCtx.Env_Path] = db_path

    try:
        yield
    finally:
        if old_path is None:
            _ = os.environ.pop(PubSubDBCtx.Env_Path, None)
        else:
            os.environ[PubSubDBCtx.Env_Path] = old_path

# ################################################################################################################################
# ################################################################################################################################

class Backend:
    """ One backend a server runs its queues against.
    """

    def __init__(self, name:'str', db_path:'str') -> 'None':
        self.name = name
        self.db_path = db_path
        self.broker:'RabbitMQProcess | None' = None

        # Put back when a TLS broker stops
        self.previous_ca_file:'strnone' = None

# ################################################################################################################################

    @property
    def is_broker(self) -> 'bool':
        """ Whether the queues of this backend live in a broker rather than in the pub/sub database.
        """
        out = self.name in Broker_Backends
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the broker, if this backend has one.
        """
        if self.broker:
            self.broker.stop()

            if self.broker.needs_ssl:
                if self.previous_ca_file is None:
                    _ = os.environ.pop(SSL_CA_Env_Name, None)
                else:
                    os.environ[SSL_CA_Env_Name] = self.previous_ca_file

# ################################################################################################################################
# ################################################################################################################################

def _start_sqlite(data_directory:'str') -> 'Backend':
    """ An SQLite file of this session's own.
    """
    db_path = os.path.join(data_directory, SQLite_File_Name)

    out = Backend(Backend_SQLite, db_path)
    return out

# ################################################################################################################################

def _start_amqp(needs_ssl:'bool', data_directory:'str', certificates:'CertificatePaths') -> 'Backend':
    """ A private RabbitMQ node for the queues, next to an SQLite pub/sub database for everything else.
    """
    if needs_ssl:
        name = Backend_AMQP_SSL
    else:
        name = Backend_AMQP

    out = _start_sqlite(data_directory)
    out.name = name

    if needs_ssl:
        out.previous_ca_file = os.environ.get(SSL_CA_Env_Name)
        os.environ[SSL_CA_Env_Name] = certificates.ca_cert

        broker = RabbitMQProcess(needs_ssl=True, certificates=certificates)
    else:
        broker = RabbitMQProcess()

    broker.start()
    out.broker = broker

    return out

# ################################################################################################################################

def start_backend(name:'str', data_directory:'str', certificates:'CertificatePaths') -> 'Backend':
    """ Starts the backend of that name for one suite and returns it with the SQLite file the server's pub/sub uses.
    """
    if name == Backend_SQLite:
        out = _start_sqlite(data_directory)

    elif name == Backend_AMQP:
        out = _start_amqp(False, data_directory, certificates)

    elif name == Backend_AMQP_SSL:
        out = _start_amqp(True, data_directory, certificates)

    # .. anything else is not a recognized backend.
    else:
        raise ValueError(f'Unknown pub/sub backend `{name}`')

    return out

# ################################################################################################################################
# ################################################################################################################################
