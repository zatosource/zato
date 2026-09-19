# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.db_env.common import Type_SQLite
from zato.common.test.rabbitmq_ import RabbitMQProcess

# local
from live_sql.containers import start_mysql, start_oracle, start_postgresql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import CertificatePaths
    from zato.common.typing_ import stranydict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

Backend_SQLite         = 'sqlite'
Backend_PostgreSQL     = 'postgresql'
Backend_PostgreSQL_SSL = 'postgresql_ssl'
Backend_MySQL          = 'mysql'
Backend_MySQL_SSL      = 'mysql_ssl'
Backend_Oracle         = 'oracle'
Backend_AMQP           = 'amqp'
Backend_AMQP_SSL       = 'amqp_ssl'

# Every backend, in the order they are run in
All_Backends = (
    Backend_SQLite,
    Backend_PostgreSQL,
    Backend_PostgreSQL_SSL,
    Backend_MySQL,
    Backend_MySQL_SSL,
    Backend_Oracle,
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

# The prefix of the environment variables the server reads its pub/sub database from
PubSub_Env_Prefix = 'Zato_PubSub_DB_'

SQLite_File_Name = 'pubsub.db'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports of this suite's own, so it can run alongside the perf and backend suites
    PostgreSQL_Port     = 25472
    PostgreSQL_SSL_Port = 25473
    MySQL_Port          = 23372
    MySQL_SSL_Port      = 23373
    Oracle_Port         = 21572

    Container_Prefix = 'zato-queue-delivery-rest-'

    Username = 'zato_queue_delivery'
    Password = 'test-queue-delivery-password'
    DB_Name  = 'zato_queue_delivery'

    Oracle_Password = 'test.queue.delivery.password'

    # Oracle DB connections are enabled by the license key variable
    License_Key_Name  = 'Zato_License_Key'
    License_Key_Value = 'test.license.key'

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
# ################################################################################################################################

class Backend:
    """ One backend a server runs its queues against.
    """

    def __init__(self, name:'str', details:'stranydict', container_name:'str') -> 'None':
        self.name = name
        self.details = details
        self.container_name = container_name
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
        """ Removes the container or stops the broker, whichever this backend has.
        """
        if self.container_name:
            stop_container(self.container_name)

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
    path = os.path.join(data_directory, SQLite_File_Name)

    details = {
        'type': Type_SQLite,
        'name': path,
    }

    out = Backend(Backend_SQLite, details, '')
    return out

# ################################################################################################################################

def _start_postgresql(needs_ssl:'bool', certificates:'CertificatePaths') -> 'Backend':

    if needs_ssl:
        name = Backend_PostgreSQL_SSL
        port = ModuleCtx.PostgreSQL_SSL_Port
    else:
        name = Backend_PostgreSQL
        port = ModuleCtx.PostgreSQL_Port

    container_name = ModuleCtx.Container_Prefix + name

    server = start_postgresql(
        container_name=container_name,
        port=port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=needs_ssl,
        certificates=certificates,
    )

    out = Backend(name, server.details, container_name)
    return out

# ################################################################################################################################

def _start_mysql(needs_ssl:'bool', certificates:'CertificatePaths') -> 'Backend':

    if needs_ssl:
        name = Backend_MySQL_SSL
        port = ModuleCtx.MySQL_SSL_Port
    else:
        name = Backend_MySQL
        port = ModuleCtx.MySQL_Port

    container_name = ModuleCtx.Container_Prefix + name

    server = start_mysql(
        container_name=container_name,
        port=port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=needs_ssl,
        certificates=certificates,
    )

    out = Backend(name, server.details, container_name)
    return out

# ################################################################################################################################

def _start_oracle() -> 'Backend':
    """ Sets the Oracle license key variable.
    """
    if not os.environ.get(ModuleCtx.License_Key_Name):
        os.environ[ModuleCtx.License_Key_Name] = ModuleCtx.License_Key_Value

    container_name = ModuleCtx.Container_Prefix + Backend_Oracle

    server = start_oracle(
        container_name=container_name,
        port=ModuleCtx.Oracle_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Oracle_Password,
    )

    out = Backend(Backend_Oracle, server.details, container_name)
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
    """ Starts the backend of that name and returns it with the details the server's pub/sub is pointed at.
    """
    if name == Backend_SQLite:
        out = _start_sqlite(data_directory)

    elif name == Backend_PostgreSQL:
        out = _start_postgresql(False, certificates)

    elif name == Backend_PostgreSQL_SSL:
        out = _start_postgresql(True, certificates)

    elif name == Backend_MySQL:
        out = _start_mysql(False, certificates)

    elif name == Backend_MySQL_SSL:
        out = _start_mysql(True, certificates)

    elif name == Backend_Oracle:
        out = _start_oracle()

    elif name == Backend_AMQP:
        out = _start_amqp(False, data_directory, certificates)

    elif name == Backend_AMQP_SSL:
        out = _start_amqp(True, data_directory, certificates)

    else:
        raise ValueError(f'Unknown pub/sub backend `{name}`')

    return out

# ################################################################################################################################
# ################################################################################################################################
