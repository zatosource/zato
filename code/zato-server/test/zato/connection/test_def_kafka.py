# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# Zato
from zato.common import Kafka
from zato.server.generic.api.def_kafka import DefKafkaWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch

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
            'username': 'user',
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

    def test_ping(self):
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn_name = 'DefKafkaTestCase.test_ping'
        config = self.get_config(conn_name)

        client = DefKafkaWrapper(config)
        client.ping()

# ################################################################################################################################

    def test_publish(self):
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # conn_name = 'DefKafkaTestCase.test_publish'
        # config = self.get_config(conn_name)
        # client = DefKafkaWrapper(config)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
