# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from drain import run_drain_scenario
from fanout import run_fanout_scenario
from live_amqp.env import audit_log_env
from perf import Min_Delivery_Rate_Per_Second_SSL, Min_Fanout_Delivery_Rate_Per_Second_SSL, Min_Publish_Rate_Per_Second_SSL
from throughput import run_delivery_scenario, run_publish_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.rabbitmq_ import RabbitMQProcess

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_amqp_perf_ssl(rabbitmq_ssl_broker:'RabbitMQProcess', tmp_path:'os.PathLike') -> 'None':
    """ The AMQP pub/sub performance scenarios against a broker that accepts TLS connections only.
    """
    with audit_log_env(str(tmp_path)):
        run_publish_scenario(rabbitmq_ssl_broker, Min_Publish_Rate_Per_Second_SSL)
        run_delivery_scenario(rabbitmq_ssl_broker, Min_Delivery_Rate_Per_Second_SSL)
        run_fanout_scenario(rabbitmq_ssl_broker, Min_Publish_Rate_Per_Second_SSL, Min_Fanout_Delivery_Rate_Per_Second_SSL)
        run_drain_scenario(rabbitmq_ssl_broker, Min_Publish_Rate_Per_Second_SSL, Min_Delivery_Rate_Per_Second_SSL)

# ################################################################################################################################
# ################################################################################################################################
