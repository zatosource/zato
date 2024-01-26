# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent.monkey import patch_all
_ = patch_all()

# stdlib
import logging
import os
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# Zato
from zato.common import Kafka
from zato.common.typing_ import cast_
from zato.server.generic.api.def_kafka import DefKafkaWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from pykafka import KafkaClient
    KafkaClient = KafkaClient

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

# ################################################################################################################################
# ################################################################################################################################

default = Kafka.Default
timeout = default.Timeout

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_Kafka'

# ################################################################################################################################
# ################################################################################################################################

class DefKafkaTestCase(TestCase):

    def get_config(self, conn_name:'str') -> 'Bunch':

        config = bunchify({
            'name': conn_name,
            'is_active': True,
            'username': 'kafka_user',
            'secret': 'kafka_password',
            'server_list': default.Server_List,
            'should_use_zookeeper': True,
            'socket_timeout': timeout.Socket,
            'offset_timeout': timeout.Offsets,
            'should_exclude_internal_topics': True,
            'source_address': None,
            'broker_version': default.Broker_Version,
            'is_tls_enabled': False,
        })

        return config

# ################################################################################################################################

    def xtest_ping(self):
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn_name = 'DefKafkaTestCase.test_ping'
        config = self.get_config(conn_name)

        wrapper = DefKafkaWrapper(config)
        wrapper.ping()

# ################################################################################################################################

    def test_publish(self):
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn_name = 'DefKafkaTestCase.test_publish'
        config = self.get_config(conn_name)

        wrapper = DefKafkaWrapper(config)
        client = cast_('KafkaClient', wrapper.client)

        topic = client.topics['my.test']

        """
        with topic.get_sync_producer() as producer:
            for x in range(40000):
                msg = f'Test message #{x}'
                msg = msg.encode('utf8')
                producer.produce(msg)
        """

        consumer = topic.get_simple_consumer()
        print(111, consumer)
        # for message in consumer:
        #    print(111, message.offset, message.value)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
