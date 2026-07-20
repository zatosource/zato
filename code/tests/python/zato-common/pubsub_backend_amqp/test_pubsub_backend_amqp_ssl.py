# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import run_inbound_delivery_scenario, run_outconn_publish_scenario, \
    run_override_lifecycle_scenario, run_redelivery_scenario, run_tls_rejects_plain_scenario
from live_amqp.env import audit_log_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.rabbitmq_ import RabbitMQProcess

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_amqp_ssl(rabbitmq_ssl_broker:'RabbitMQProcess', tmp_path:'os.PathLike') -> 'None':
    """ The complete AMQP pub/sub contract against a broker that accepts TLS connections only.
    """
    with audit_log_env(str(tmp_path)):
        run_tls_rejects_plain_scenario(rabbitmq_ssl_broker)
        run_outconn_publish_scenario(rabbitmq_ssl_broker)
        run_inbound_delivery_scenario(rabbitmq_ssl_broker)
        run_redelivery_scenario(rabbitmq_ssl_broker)
        run_override_lifecycle_scenario(rabbitmq_ssl_broker)

# ################################################################################################################################
# ################################################################################################################################
