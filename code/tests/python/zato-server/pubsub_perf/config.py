# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from zato.common.test.client import AdminClient
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.test.pubsub_database import PubSubDatabase

    AdminClient = AdminClient
    Logger = Logger
    PubSubDatabase = PubSubDatabase
    SessionState = SessionState

# ################################################################################################################################
# ################################################################################################################################

class Scenario(NamedTuple):
    """ One topic with its own publishers and its own subscribers, each subscriber with a subscription of its own.
    """
    topic_name: 'str'
    publisher_count: 'int'
    subscriber_count: 'int'

scenariolist = list[Scenario]

# ################################################################################################################################

def _get_count_text(count:'int', noun:'str') -> 'str':
    """ Returns a count followed by a noun in the singular or in the plural, as the count requires.
    """
    if count == 1:
        out = f'{count} {noun}'
    else:
        out = f'{count} {noun}s'

    return out

# ################################################################################################################################

def get_scenario_name(test_name:'str', scenario:'Scenario') -> 'str':
    """ Returns the name under which a test logs the progress and records the results of a scenario,
    with its publishers and subscribers.
    """
    publishers = _get_count_text(scenario.publisher_count, 'publisher')
    subscribers = _get_count_text(scenario.subscriber_count, 'subscriber')

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
    """ The server of the performance tests and its API clients, populated once the server of the session is ready.
    """

    # The address of the REST interface of the server and the port that it listens on
    base_url: 'str'
    server_port: 'int'

    # The session that started the server, and the logger of the session
    session_state: 'SessionState'
    logger: 'Logger'

    # The client of the services of the server, and its PostgreSQL database, or None for a database that the session did not start
    client: 'AdminClient'
    database: 'PubSubDatabase | None'

    # The publishers and the subscribers that the scenarios take theirs from, in order
    publishers:  'credentialslist'
    subscribers: 'credentialslist'

    # The client that reads the receipts of the subscribers
    receipt_reader: 'Credentials'

    # How long a pulled message stays reserved for its subscriber, in seconds, as the server reports it
    lease_seconds: 'float'

# ################################################################################################################################
# ################################################################################################################################
