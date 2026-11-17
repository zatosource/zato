# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.util.api import pluralize

# ################################################################################################################################
# ################################################################################################################################

class Scenario(NamedTuple):
    """ One topic with its own publishers and its own subscribers, each subscriber with a subscription of its own.
    """
    topic_name: 'str'
    publisher_count: 'int'
    subscriber_count: 'int'

scenariolist = list[Scenario]

def get_scenario_name(test_name:'str', scenario:'Scenario') -> 'str':
    """ Returns the name under which a test logs the progress and the results of a scenario, with its publishers and subscribers.
    """
    publishers = pluralize(scenario.publisher_count, 'publisher')
    subscribers = pluralize(scenario.subscriber_count, 'subscriber')

    out = f'{test_name} with {publishers} and {subscribers}'
    return out

# ################################################################################################################################
# ################################################################################################################################

# Each subscriber publishes one receipt per message in the transaction of its acknowledgement
Receipts_Topic = 'perf.receipts'

# Many publishers to many subscribers
Capacity_Scenario = Scenario('perf.capacity', 16, 16)

# The same, while the worker of the server is killed
Faults_Scenario = Scenario('perf.faults', 8, 8)

# As many publishers as subscribers, at rising levels
Level_Scenarios:'scenariolist' = [
    Scenario('perf.level.1', 1, 1),
    Scenario('perf.level.4', 4, 4),
    Scenario('perf.level.16', 16, 16),
    Scenario('perf.level.32', 32, 32),
]

All_Scenarios:'scenariolist' = [Capacity_Scenario, Faults_Scenario, *Level_Scenarios]

# ################################################################################################################################
# ################################################################################################################################

class Credentials:
    """ The username and the password of one API client.
    """

    def __init__(self, username:'str', password:'str') -> 'None':
        self.username = username
        self.password = password

credentialslist = list[Credentials]

# ################################################################################################################################
# ################################################################################################################################

class PerfConfig:
    """ The API clients of the performance tests, populated once the server of the session is ready.
    """

    # The publishers and the subscribers that the scenarios take theirs from, in order
    publishers:  'credentialslist'
    subscribers: 'credentialslist'

    # How long a pulled message stays reserved for its subscriber, in seconds
    lease_seconds: 'float'

# ################################################################################################################################
# ################################################################################################################################
