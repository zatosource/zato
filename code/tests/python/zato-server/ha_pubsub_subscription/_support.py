# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from dataclasses import dataclass

# pg8000
import pg8000.dbapi

# PyYAML
import yaml

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import PublishClient, PullClient
from zato.common.test.pubsub_database import build_ssl_context, ModuleCtx as DatabaseModuleCtx
from zato.common.test.zato_database import ModuleCtx as ZatoDatabaseCtx

# Live environment
from live_environment.quickstart import Host

# Fault tools
from toxiproxy import Toxiproxy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import anydict, anylist, callable_, strlist, strset, strstrdict

    AdminClient = AdminClient
    PubSubDatabase = PubSubDatabase
    ZatoEnvironment = ZatoEnvironment
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    strlist = strlist
    strset = strset
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The services the suite deploys - its own, which reads the worker, and the test services of the pub/sub REST suites
    Runtime_Service      = 'ha.pubsub.subscription.runtime'
    Runtime_Service_File = 'ha_pubsub_subscription_runtime.py'
    REST_Services_File   = 'ha_pubsub_subscription_rest.py'

    Get_Sub_Keys_Service     = 'test.pubsub-rest.get-sub-keys'
    Get_Queue_Depths_Service = 'test.pubsub-rest.get-queue-depths'
    Get_Topic_Rows_Service   = 'test.pubsub-rest.get-topic-rows'

    # The markers the server writes for each enmasse import that it runs
    Marker_Started   = 'Invoking command'
    Marker_Import    = '--import'
    Marker_Completed = 'Enmasse stderr'
    Marker_Failed    = 'Enmasse import failed'

    Log_Path = os.path.join('logs', 'server.log')

    # How long a condition that the suite waits for may take to hold, in seconds, and how often it is checked
    Wait_Timeout  = 180.0
    Poll_Interval = 0.5

    # How long one REST call of a publisher or a subscriber may take, in seconds
    Client_Timeout = 60.0

    # How long one call of the services that the suite deployed may take, in seconds - above the read timeout
    # and the connect timeout of PostgreSQL, within which a call that waits for the database fails
    Runtime_Client_Timeout = 180.0

    # The status of a pair whose rows match the subscription list
    Status_Confirmed = 'confirmed'

    # The lock that a session of the test holds on PostgreSQL to fail the writes of subscription rows past the lock timeout
    # of the server, which leaves plain reads of the table and every other table to proceed
    Table_Write_Lock = 'lock table pubsub_topic_sub in exclusive mode'

    # How long a session of the test may take to connect to PostgreSQL, in seconds
    Connect_Timeout = 10

# ################################################################################################################################
# ################################################################################################################################

def wait_for(check:'callable_', what:'str', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'None':
    """ Polls a check until it returns True and raises once the timeout passes.
    """
    deadline = time.monotonic() + timeout

    while not check():
        if time.monotonic() > deadline:
            raise Exception(f'{what} did not happen within {timeout}s')
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

class Names:
    """ The object names of one live environment of the suite.
    """

    def __init__(self) -> 'None':
        suffix = CryptoManager.generate_hex_string(32)

        self.security_pull = f'ha.sub.sec.pull.{suffix}'
        self.security_second = f'ha.sub.sec.second.{suffix}'
        self.topic_pull = f'ha.sub.topic.pull.{suffix}'
        self.topic_second = f'ha.sub.topic.second.{suffix}'
        self.password = 'password.' + CryptoManager.generate_hex_string()

# ################################################################################################################################

    def placeholders(self) -> 'strstrdict':
        """ Returns the placeholders of the enmasse template.
        """
        out = {
            'security_pull': self.security_pull,
            'security_second': self.security_second,
            'topic_pull': self.topic_pull,
            'topic_second': self.topic_second,
            'password': self.password,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class DatabaseProxy:
    """ The PostgreSQL database of a module and the proxy of Toxiproxy through which the server reaches it.
    """
    database: 'PubSubDatabase'
    toxiproxy: 'Toxiproxy'
    listen_port: 'int'

# ################################################################################################################################
# ################################################################################################################################

class Pickup:
    """ Places enmasse files in the pickup directory and waits for the server to import each one.
    """

    def __init__(self, environment:'ZatoEnvironment') -> 'None':
        self.environment = environment
        self.counter = 0
        self.log_path = os.path.join(environment.server_directory, ModuleCtx.Log_Path)

# ################################################################################################################################

    def _read_log(self) -> 'str':
        if not os.path.isfile(self.log_path):
            return ''

        with open(self.log_path) as log_file:
            out = log_file.read()

        return out

# ################################################################################################################################

    def count_markers(self) -> 'tuple[int, int, int]':
        """ How many enmasse imports the log of the server says started, completed and failed.
        """
        started = 0
        completed = 0
        failed = 0

        for line in self._read_log().splitlines():
            if ModuleCtx.Marker_Started in line and ModuleCtx.Marker_Import in line:
                started += 1
            elif ModuleCtx.Marker_Completed in line:
                completed += 1
            elif ModuleCtx.Marker_Failed in line:
                failed += 1

        out = started, completed, failed
        return out

# ################################################################################################################################

    def wait_for_import(self, completed_before:'int', failed_before:'int', what:'str') -> 'None':
        """ Waits until the server completes one more enmasse import and has none running, and raises if one failed.
        """
        def _is_imported() -> 'bool':
            started, completed, failed = self.count_markers()

            if failed > failed_before:
                raise Exception(f'The server could not import {what}, see {self.log_path}')

            out = completed > completed_before and started == completed + failed
            return out

        wait_for(_is_imported, f'The import of {what}')

# ################################################################################################################################

    def place(self, name:'str', definitions:'str') -> 'str':
        """ Writes an enmasse file into the pickup directory and returns its name, without waiting for the import.
        """
        self.counter += 1

        out = f'enmasse-{self.counter:04d}-{name}.yaml'
        path = os.path.join(self.environment.pickup_directory, out)

        with open(path, 'w') as enmasse_file:
            _ = enmasse_file.write(definitions)

        return out

# ################################################################################################################################

    def apply(self, name:'str', definitions:'str') -> 'None':
        """ Writes an enmasse file into the pickup directory and waits for the import to complete.
        """
        _, completed_before, failed_before = self.count_markers()

        file_name = self.place(name, definitions)
        self.wait_for_import(completed_before, failed_before, file_name)

# ################################################################################################################################
# ################################################################################################################################

class Runtime:
    """ Invokes the services that the suite deployed into the live server.
    """

    def __init__(self, client:'AdminClient') -> 'None':
        self.client = client

# ################################################################################################################################

    def _invoke_runtime(self, action:'str') -> 'anydict':
        out = self.client.invoke(ModuleCtx.Runtime_Service, {'action': action})
        return out

# ################################################################################################################################

    def governed_pairs(self) -> 'set[tuple[str, str]]':
        """ Returns the governed subscriber and topic pairs that the pub/sub database has rows of.
        """
        response = self._invoke_runtime('governed_pairs')

        out:'set[tuple[str, str]]' = set()

        for sub_key, topic_name in response['pairs']:
            out.add((sub_key, topic_name))

        return out

# ################################################################################################################################

    def statuses(self) -> 'anylist':
        """ Returns each pair of the subscription list of the worker with its status.
        """
        response = self._invoke_runtime('statuses')
        out = response['statuses']
        return out

# ################################################################################################################################

    def has_unconfirmed(self) -> 'bool':
        """ Whether any pair of the subscription list waits for its rows to be written or deleted.
        """
        for _sub_key, _topic_name, status in self.statuses():
            if status != ModuleCtx.Status_Confirmed:
                return True

        return False

# ################################################################################################################################

    def listed_pairs(self) -> 'set[tuple[str, str]]':
        """ Returns the pairs of the subscription list of the worker.
        """
        out:'set[tuple[str, str]]' = set()

        for sub_key, topic_name, _status in self.statuses():
            out.add((sub_key, topic_name))

        return out

# ################################################################################################################################

    def kill_worker(self) -> 'None':
        """ Sends SIGKILL to the worker process of the server, which ends the request that asks for it.
        """
        _ = self._invoke_runtime('kill_worker')

# ################################################################################################################################

    def sub_key(self, security_name:'str') -> 'str':
        """ Returns the subscription key of the subscriber with the given security definition.
        """
        response = self.client.invoke(ModuleCtx.Get_Sub_Keys_Service, {})
        out = response['sub_keys'][security_name]
        return out

# ################################################################################################################################

    def queue_depth(self, sub_key:'str') -> 'int':
        """ Returns how many deliveries the queue of a subscriber holds.
        """
        response = self.client.invoke(ModuleCtx.Get_Queue_Depths_Service, {'sub_keys': [sub_key]})
        out = response['depths'][sub_key]
        return out

# ################################################################################################################################

    def topic_deliveries(self, topic_name:'str') -> 'int':
        """ Returns how many deliveries of the messages of a topic the queues of all subscribers hold.
        """
        response = self.client.invoke(ModuleCtx.Get_Topic_Rows_Service, {'topic_name': topic_name.lower()})
        out = response['deliveries']
        return out

# ################################################################################################################################
# ################################################################################################################################

class WriteFault:
    """ Fails the writes of the server to the subscription rows of the pub/sub database while its reads proceed,
    through an exclusive lock of the table of subscription rows held by a session of the test past the lock timeout.
    """

    def __init__(self, environment:'ZatoEnvironment', database_proxy:'DatabaseProxy') -> 'None':
        self.table_lock = RowLock(database_proxy.database, environment, ModuleCtx.Table_Write_Lock, [])

# ################################################################################################################################

    def apply(self) -> 'None':
        self.table_lock.acquire()

# ################################################################################################################################

    def remove(self) -> 'None':
        self.table_lock.release()

# ################################################################################################################################
# ################################################################################################################################

def connect_environment(database:'PubSubDatabase', environment:'ZatoEnvironment') -> 'pg8000.dbapi.Connection':
    """ Opens a pg8000 connection to the database of a live environment, outside of any engine and of the proxy.
    """
    if database.env.get('Zato_Database_SSL'):
        ssl_context = build_ssl_context(database)
    else:
        ssl_context = False

    db_name = environment.database_env[ZatoDatabaseCtx.Env_Name]

    out = pg8000.dbapi.connect(user=DatabaseModuleCtx.Username, password=database.password, host=database.host,
        port=database.port, database=db_name, ssl_context=ssl_context, timeout=ModuleCtx.Connect_Timeout)

    return out

# ################################################################################################################################
# ################################################################################################################################

class RowLock:
    """ Holds a lock on rows of a pub/sub table of PostgreSQL from a session of the test.
    """

    def __init__(
        self,
        database:'PubSubDatabase',
        environment:'ZatoEnvironment',
        statement:'str',
        params:'anylist',
        ) -> 'None':
        self.database = database
        self.environment = environment
        self.statement = statement
        self.params = params
        self.connection = None

# ################################################################################################################################

    def acquire(self) -> 'None':
        """ Opens a session, whose first statement begins its transaction, and locks the rows.
        """
        self.connection = connect_environment(self.database, self.environment)
        cursor = self.connection.cursor()
        cursor.execute(self.statement, self.params)

# ################################################################################################################################

    def release(self) -> 'None':
        """ Rolls the transaction back, which releases the locks, and closes the session.
        """
        if self.connection is None:
            return

        self.connection.rollback()
        self.connection.close()
        self.connection = None

# ################################################################################################################################
# ################################################################################################################################

def render_template(template_path:'str', placeholders:'strstrdict') -> 'str':
    """ Returns the enmasse YAML with the placeholders substituted.
    """
    with open(template_path) as template_file:
        template = template_file.read()

    out = template.format(**placeholders)
    return out

# ################################################################################################################################

def yaml_subscription(security_name:'str', topic_names:'strlist') -> 'str':
    """ Returns an enmasse file that subscribes a pull subscriber to exactly the given topics.
    """
    definition = {
        'pubsub_subscription': [{
            'security': security_name,
            'delivery_type': 'pull',
            'topic_list': topic_names,
        }],
    }
    out = yaml.dump(definition)
    return out

# ################################################################################################################################

def wait_for_unconfirmed(runtime:'Runtime', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'None':
    """ Waits until the worker has a pair whose rows it could not write or delete yet.
    """
    wait_for(runtime.has_unconfirmed, 'A pair of the subscription list becoming unconfirmed', timeout)

# ################################################################################################################################

def wait_for_no_unconfirmed(runtime:'Runtime') -> 'None':
    """ Waits until the rows of every pair of the subscription list are written or deleted.
    """
    def _is_confirmed() -> 'bool':
        out = not runtime.has_unconfirmed()
        return out

    wait_for(_is_confirmed, 'The confirmation of every pair of the subscription list')

# ################################################################################################################################

def assert_rows_equal_list(runtime:'Runtime') -> 'None':
    """ Confirms that the governed rows of the pub/sub database are exactly the pairs of the subscription list.
    """
    rows = runtime.governed_pairs()
    listed = runtime.listed_pairs()

    assert rows == listed, f'Rows {sorted(rows)} differ from the subscription list {sorted(listed)}'

# ################################################################################################################################

def publish_client(environment:'ZatoEnvironment', names:'Names') -> 'PublishClient':
    """ A publisher with the security definition of the second subscriber, which may publish to both topics.
    """
    base_url = f'http://{Host}:{environment.server_port}'
    out = PublishClient(base_url, names.security_second, names.password, timeout=ModuleCtx.Client_Timeout)
    return out

# ################################################################################################################################

def pull_client(environment:'ZatoEnvironment', names:'Names', security_name:'str') -> 'PullClient':
    """ A subscriber that pulls with the given security definition.
    """
    base_url = f'http://{Host}:{environment.server_port}'
    out = PullClient(base_url, security_name, names.password, timeout=ModuleCtx.Client_Timeout)
    return out

# ################################################################################################################################

def publish_accepted(client:'PublishClient', topic_name:'str', data:'str') -> 'str':
    """ Publishes a message, again after each refusal during a fault, and returns the ID of the message accepted.
    """
    deadline = time.monotonic() + ModuleCtx.Wait_Timeout

    while True:
        try:
            response = client.publish(topic_name, data)
        except Exception as e:
            if time.monotonic() > deadline:
                raise Exception(f'Publication to {topic_name} not accepted within {ModuleCtx.Wait_Timeout}s -> {e}')
            time.sleep(ModuleCtx.Poll_Interval)
        else:
            out = response['msg_id']
            return out

# ################################################################################################################################

def wait_for_worker(runtime:'Runtime') -> 'None':
    """ Waits until a worker of the server answers the runtime service, e.g. the worker that replaced a killed one.
    """
    def _answers() -> 'bool':
        try:
            _ = runtime.statuses()
        except Exception:
            return False
        else:
            return True

    wait_for(_answers, 'The answer of the worker')

# ################################################################################################################################

def get_msg_ids(messages:'anylist') -> 'strset':
    """ Returns the IDs of pulled messages.
    """
    out:'strset' = set()

    for message in messages:
        out.add(message['meta']['msg_id'])

    return out

# ################################################################################################################################

def pull_all(client:'PullClient') -> 'anylist':
    """ Pulls and acknowledges messages until the queue of the subscriber is empty and returns all of them.
    """
    out:'anylist' = []

    while True:
        response = client.pull(max_messages=50)
        messages = response['messages']

        if not messages:
            break

        out.extend(messages)

    return out

# ################################################################################################################################
# ################################################################################################################################
