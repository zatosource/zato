# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.pubsub.common import BrokerConfig

# ################################################################################################################################
# ################################################################################################################################

def get_broker_config() -> 'BrokerConfig':

    config = BrokerConfig()

    config.protocol = os.environ['Zato_Broker_Protocol']
    config.address = os.environ['Zato_Broker_Address']
    config.vhost = os.environ['Zato_Broker_Virtual_Host']
    config.username = os.environ['Zato_Broker_Username']
    config.password = os.environ['Zato_Broker_Password']

    return config

# ################################################################################################################################
# ################################################################################################################################
