# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from json import dumps
from pathlib import Path

# redis
from redis import Redis

# SQLAlchemy
from sqlalchemy import select

# PyYAML
from yaml import safe_load as yaml_load

# Zato
from live_environment.quickstart import Host
from live_kafka.containers import create_topic, KafkaCluster
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from live_kafka.bridge import BridgeParts
    from live_kafka.containers import KafkaServer
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, anylist, callable_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable that turns the skip into a failure when the suite runs on purpose
    Required_Variable = 'Zato_Test_Kafka'

    # The services the suites drive, deployed to the test server - they live next to the single-instance suite
    Services_File = Path(__file__).parent.parent.parent.parent / 'zato-server' / 'kafka' / '_services.py'

    # The shared queue delivery services - the DLQ and topic readers that know nothing of Kafka
    Shared_Services_File = Path(__file__).parent.parent / 'queue_delivery' / 'shared_services.py'

    Invoke_Service = 'test.kafka.invoke'

    # How long the deployed services have to appear
    Deploy_Timeout = 60

    # How long a message has to reach a receiver
    Receive_Timeout = 30.0
    Poll_Interval = 0.2

    # The stream the bridge writes a channel's messages to, the channel's id follows
    Recv_Stream_Prefix = 'zato:queue_bridge:stream:recv:'

    # The consumer group the server reads a recv stream as
    Recv_Group = 'server-recv'

    # Where the server's audit log is, for the tests to read it from the same file
    Audit_DB_Variable = 'Zato_Audit_Log_DB_Name'

    # The pub/sub database the server's queues and DLQs live in
    PubSub_DB_Type_Variable = 'Zato_PubSub_DB_Type'
    PubSub_DB_Name_Variable = 'Zato_PubSub_DB_Name'
    PubSub_DB_Type = 'sqlite'
    PubSub_DB_File_Name = 'pubsub.db'

# ################################################################################################################################
# ################################################################################################################################

class KafkaSuite:
    """ Everything a test case reaches - the server, Kafka, the bridge's Redis and the helpers around them.
    Kafka is either one container or a cluster of them, the subclasses say which.
    """

    def __init__(
        self,
        zato:'ZatoEnvironment',
        kafka:'KafkaServer | KafkaCluster',
        bridge:'BridgeParts',
        server_environment:'dict[str, str]',
        ) -> 'None':
        self.zato = zato
        self.kafka = kafka
        self.bridge = bridge
        self.server_environment = server_environment
        self.client:'AdminClient' = zato.client()
        self.redis = Redis(host=Host, port=bridge.redis_port, decode_responses=True)

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ The address a connection points at - for a cluster, the first instance's only, so that discovery of the rest
        is what a test exercises.
        """
        if isinstance(self.kafka, KafkaCluster):
            out = self.kafka[0].address
        else:
            out = self.kafka.address

        return out

# ################################################################################################################################

    def invoke(self, mode:'str', **fields:'any_') -> 'anydict':
        """ One call to the invoker deployed to the test server.
        """
        request = {'mode': mode, **fields}
        out = self.client.invoke(ModuleCtx.Invoke_Service, request)

        return out

# ################################################################################################################################

    def invoke_service(self, service:'str', request:'anydict | None'=None) -> 'any_':
        """ Invokes any of the server's services through the invoker, so the response is what the service returned.
        """
        out = self.invoke('invoke', service=service, request=request or {})['response']
        return out

# ################################################################################################################################

    def wait_until_deployed(self) -> 'None':
        """ Waits for the hot-deployed invoker to answer.
        """
        deadline = time.monotonic() + ModuleCtx.Deploy_Timeout

        while time.monotonic() < deadline:
            try:
                _ = self.invoke('ping')
            except Exception:
                time.sleep(1)
            else:
                return

        raise Exception(f'Service {ModuleCtx.Invoke_Service} did not deploy within {ModuleCtx.Deploy_Timeout}s')

# ################################################################################################################################

    def new_name(self, what:'str') -> 'str':
        """ A name no earlier test used, for a connection, a topic or a group.
        """
        out = f'test.kafka.{what}.{CryptoManager.generate_hex_string()}'
        return out

# ################################################################################################################################

    def create_topic(self, topic:'str', partitions:'int'=1, **kwargs:'any_') -> 'None':
        if isinstance(self.kafka, KafkaCluster):
            self.kafka.create_topic(topic, partitions, **kwargs)
        else:
            create_topic(self.kafka.container_name, topic, partitions)

# ################################################################################################################################

    def import_yaml(self, definitions:'str') -> 'None':
        """ Imports the definitions and waits until the bridge knows each outgoing connection among them - the server
        tells the bridge of them a moment after the import, and a send before that is a send through an unknown connection.
        """
        file_name = f'kafka_{CryptoManager.generate_hex_string()}.yaml'
        _ = self.zato.import_yaml(file_name, definitions)

        for item in yaml_load(definitions).get('outgoing_kafka') or []:
            self.wait_until_connection_known(item['name'])

# ################################################################################################################################

    def wait_until_connection_known(self, conn_name:'str') -> 'None':
        """ Waits until a ping through an outgoing connection goes through, so the bridge has its definition.
        """
        deadline = time.monotonic() + ModuleCtx.Deploy_Timeout
        result:'anydict' = {}

        while time.monotonic() < deadline:
            result = self.invoke('ping-connection', connection=conn_name)

            if result['is_ok']:
                return

            time.sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Connection `{conn_name}` was not known within {ModuleCtx.Deploy_Timeout}s: {result}')

# ################################################################################################################################

    def send(self, connection:'str', payload:'str', **fields:'any_') -> 'anydict':
        """ One send through an outgoing connection, failing the test unless the send went through.
        """
        out = self.invoke('send', connection=connection, payload=payload, **fields)
        assert out['is_ok'], out

        return out

# ################################################################################################################################

    def received(self, service:'str'='') -> 'anylist':
        """ What the receivers were invoked with since the last clear, oldest first, optionally of one receiver.
        """
        items = self.invoke('get-received')['received']

        if service:
            items = [elem for elem in items if elem['service'] == service]

        return items

# ################################################################################################################################

    def clear_received(self) -> 'None':
        _ = self.invoke('clear-received')

# ################################################################################################################################

    def set_behaviour(self, service:'str', **settings:'any_') -> 'None':
        _ = self.invoke('set-behaviour', service=service, **settings)

# ################################################################################################################################

    def reset_behaviour(self) -> 'None':
        """ Every receiver answers at once and never fails.
        """
        for service in ('test.kafka.receiver', 'test.kafka.receiver.two', 'test.kafka.receiver.three'):
            self.set_behaviour(service)

# ################################################################################################################################

    def wait_for_received(
        self,
        matches:'callable_',
        count:'int'=1,
        *,
        timeout:'float'=ModuleCtx.Receive_Timeout,
        service:'str'='',
        ) -> 'anylist':
        """ Waits until that many recorded invocations match and returns them.
        """
        deadline = time.monotonic() + timeout
        found:'anylist' = []

        while time.monotonic() < deadline:
            found = [elem for elem in self.received(service) if matches(elem)]

            if len(found) >= count:
                return found

            time.sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Expected {count} matching invocations within {timeout}s, found {len(found)}: {found}')

# ################################################################################################################################

    def wait_for_payload(self, payload:'str', count:'int'=1, **kwargs:'any_') -> 'anylist':
        """ Waits until a payload was received that many times.
        """
        out = self.wait_for_received(lambda elem: elem['data'] == payload, count, **kwargs)
        return out

# ################################################################################################################################

    def not_received(self, matches:'callable_', *, within:'float') -> 'None':
        """ Asserts that nothing matching arrives for a while.
        """
        time.sleep(within)
        found = [elem for elem in self.received() if matches(elem)]

        assert not found, found

# ################################################################################################################################

    def connection(self, name:'str') -> 'anydict':
        out = self.invoke('get-connection', connection=name)
        return out

# ################################################################################################################################

    def edit_connection(self, conn_name:'str', **changes:'any_') -> 'None':
        _ = self.invoke('edit-connection', connection=conn_name, changes=changes)

# ################################################################################################################################

    def delete_connection(self, name:'str') -> 'None':
        _ = self.invoke('delete-connection', connection=name)

# ################################################################################################################################

    def recv_stream(self, channel_id:'int') -> 'str':
        out = f'{ModuleCtx.Recv_Stream_Prefix}{channel_id}'
        return out

# ################################################################################################################################

    def pending_count(self, channel_id:'int') -> 'int':
        """ How many entries of a channel's recv stream the server has read but not acknowledged yet.
        """
        stream = self.recv_stream(channel_id)

        if not self.redis.exists(stream):
            return 0

        try:
            info = self.redis.xpending(stream, ModuleCtx.Recv_Group)
        except Exception:
            return 0

        out = int(info['pending'])
        return out

# ################################################################################################################################

    def stream_length(self, channel_id:'int') -> 'int':
        out = int(self.redis.xlen(self.recv_stream(channel_id)))
        return out

# ################################################################################################################################

    def dlq(self, conn_name:'str') -> 'anydict':
        """ What a connection's DLQ holds - its sub key, its topic and the documents, oldest first.
        """
        out = self.client.invoke('test.queue-delivery.get-dlq', {'conn_name': conn_name})
        return out

# ################################################################################################################################

    def wait_for_dlq_count(self, conn_name:'str', expected:'int', *, timeout:'float'=ModuleCtx.Receive_Timeout) -> 'anydict':
        """ Waits until a DLQ holds that many messages and returns what it holds.
        """
        deadline = time.monotonic() + timeout
        out = self.dlq(conn_name)

        while time.monotonic() < deadline:
            out = self.dlq(conn_name)

            if len(out['messages']) == expected:
                return out

            time.sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'DLQ of `{conn_name}` did not hold {expected} messages within {timeout}s: {out}')

# ################################################################################################################################

    def run_dlq_rule(self) -> 'anydict':
        out = self.client.invoke('zato.pubsub.dlq.run')['counts']
        return out

# ################################################################################################################################

    def subscribe_topic(self, topic_name:'str', sub_key:'str') -> 'None':
        _ = self.client.invoke('test.queue-delivery.subscribe-topic', {'topic_name': topic_name, 'sub_key': sub_key})

# ################################################################################################################################

    def topic_messages(self, topic_name:'str', sub_key:'str') -> 'anylist':
        """ What was published to a topic for a sub key since it was last read, taken off the topic.
        """
        response = self.client.invoke('test.queue-delivery.get-topic-messages', {'topic_name': topic_name, 'sub_key': sub_key})
        out = response['messages']

        return out

# ################################################################################################################################

    def topic_subscribers(self, topic_name:'str') -> 'anylist':
        response = self.client.invoke('test.queue-delivery.get-topic-subscribers', {'topic_name': topic_name})
        out = response['sub_key_list']

        return out

# ################################################################################################################################

    def dlq_action(self, service:'str', **request:'any_') -> 'anydict':
        """ One of the DLQ services - retry, forward or discard, of one message or of all of them.
        """
        out = self.client.invoke(f'zato.pubsub.dlq.{service}', request)
        return out

# ################################################################################################################################

    def dlq_page(self, conn_name:'str', **request:'any_') -> 'anydict':
        """ What the channel's delivery page lists of its DLQ.
        """
        connection = self.connection(conn_name)
        request = {'conn_type': connection['conn_type'], 'conn_id': connection['id'], 'kind': 'dlq', **request}
        out = self.client.invoke('zato.pubsub.outgoing.get-message-list', request)

        return out

# ################################################################################################################################

    def dlq_page_message(self, conn_name:'str', msg_id:'str') -> 'anydict':
        """ One message as the page's details window shows it.
        """
        connection = self.connection(conn_name)
        request = {'conn_type': connection['conn_type'], 'conn_id': connection['id'], 'kind': 'dlq', 'msg_id': msg_id}
        out = self.client.invoke('zato.pubsub.outgoing.get-message', request)

        return out

# ################################################################################################################################

    def dlq_page_action(self, conn_name:'str', action:'str', msg_id_list:'anylist') -> 'anydict':
        """ What the page's buttons do with the selected messages.
        """
        connection = self.connection(conn_name)
        request = {
            'conn_type': connection['conn_type'],
            'conn_id': connection['id'],
            'kind': 'dlq',
            'action': action,
            'msg_id_list': dumps(msg_id_list),
        }
        out = self.client.invoke('zato.pubsub.outgoing.message-action', request)

        return out

# ################################################################################################################################

    def audit_events(self, cid:'str', event_type:'str'='') -> 'anylist':
        """ The events the server's audit log holds under one cid, oldest first.
        """
        engine = get_audit_engine()

        query = select(event_table).where(event_table.c.cid == cid)

        if event_type:
            query = query.where(event_table.c.event_type == event_type)

        query = query.order_by(event_table.c.id)

        out:'anylist' = []

        with engine.connect() as connection:
            for row in connection.execute(query):
                out.append(dict(row._mapping))

        return out

# ################################################################################################################################

    def wait_for_audit_events(self, cid:'str', expected:'int', *, timeout:'float'=ModuleCtx.Receive_Timeout) -> 'anylist':
        """ Waits until at least that many events are in the audit log under a cid.
        """
        deadline = time.monotonic() + timeout
        out:'anylist' = []

        while time.monotonic() < deadline:
            out = self.audit_events(cid)

            if len(out) >= expected:
                return out

            time.sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Expected {expected} audit events under `{cid}` within {timeout}s, found {len(out)}: {out}')

# ################################################################################################################################

    def restart_server(self) -> 'None':
        """ Stops the server and starts it again, the broker, Redis and the bridge stay as they are.
        """
        self.zato.restart(self.server_environment)
        self.client = self.zato.client()
        self.wait_until_deployed()

# ################################################################################################################################
# ################################################################################################################################
