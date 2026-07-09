# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.common.test.rabbitmq_ import RabbitMQProcess, declare_and_bind
from zato.common.util.api import new_cid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def rabbitmq_broker() -> 'any_':
    """ Module-scoped private RabbitMQ broker with a ready-made exchange, queue and binding.
    Imported only by the AMQP test files so non-AMQP dashboard tests never pay for a broker.
    """

    # Start a private broker on random ports in a tmp directory ..
    broker = RabbitMQProcess()
    broker.start()

    # .. declare a default exchange, queue and binding for the tests to use ..
    suffix = new_cid()

    exchange = 'test.exchange.' + suffix
    queue = 'test.queue.' + suffix
    routing_key = 'test.key.' + suffix

    declare_and_bind(broker.amqp_url, exchange, queue, routing_key)

    yield {
        'broker': broker,
        'amqp_url': broker.amqp_url,
        'amqp_port': broker.amqp_port,
        'exchange': exchange,
        'queue': queue,
        'routing_key': routing_key,
    }

    # .. stop the node and remove its directory on teardown.
    broker.stop()

# ################################################################################################################################
# ################################################################################################################################

def deploy_service(server_dir:'str', file_name:'str', source:'str') -> 'str':
    """ Writes a service module into the server's hot-deploy pickup directory,
    the listener deploys it immediately. Returns the file path.
    """
    pickup_directory = os.path.join(server_dir, 'pickup', 'incoming', 'services')
    file_path = os.path.join(pickup_directory, file_name)

    with open(file_path, 'w') as service_file:
        _ = service_file.write(source)

    return file_path

# ################################################################################################################################
# ################################################################################################################################
