# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The demo-data import over a live server - the same import_demo_data function
# a dashboard view invokes, exercised end to end. The import creates the demo
# connections, stores the alert rules, seeds the backdated history into the
# server's audit database and sends the live burst through the main demo channel.

# stdlib
import json

# SQLAlchemy
from sqlalchemy import create_engine, func, select

# Zato
from zato.common.audit_log.api import event_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# A small run keeps the live test fast while covering every seeded story
_import_request = {
    'days': 3,
    'messages_per_day': 20,
    'burst_message_count': 10,
    'fhir_pair_count': 5,
}

# What the seeder names everything it creates
_cid_prefix = 'demo-'
_main_channel_name = 'demo.hl7.adt.main'

# How many live messages the import sends through the main channel -
# a fixed size of its own, separate from the seeded error burst
_live_burst_count = 20

# How many connections and rules the import manages
_connection_count = 5
_rule_count = 3

# ################################################################################################################################
# ################################################################################################################################

def _count_demo_events(audit_db_path:'str') -> 'int':
    """ Returns how many events in the server's audit database belong to the demo.
    """
    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(func.count()).select_from(event_table)
    query = query.where(event_table.c.cid.like(f'{_cid_prefix}%'))

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    engine.dispose()

    return out

# ################################################################################################################################

def _get_channel_states(zato_client:'any_') -> 'anydict':
    """ Returns the live state of every HL7 MLLP channel, keyed by channel name.
    """
    response = zato_client.invoke('zato.channel.hl7.get-current-state', {})
    report = json.loads(response['response_data'])

    out = {item['name']: item for item in report['channels']}
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDemoImport:

    first_event_count:'int' = 0

# ################################################################################################################################

    def test_01_import_seeds_everything(self, zato_client:'any_', zato_server:'anydict') -> 'None':
        """ One call sets the whole demo up - connections, rules, the backdated
        history and the live burst through the main channel.
        """
        result = zato_client.invoke('test.demo.import', _import_request)

        # Everything was created from scratch
        assert len(result['created_connections']) == _connection_count, result
        assert len(result['rule_names']) == _rule_count, result

        assert result['message_count'] > 0, result
        assert result['event_count'] > result['message_count'], result
        assert result['alert_count'] > 0, result
        assert result['fhir_pair_count'] == _import_request['fhir_pair_count'], result
        assert result['dedup_count'] > 0, result
        assert result['config_event_count'] > 0, result

        # The live burst went out through the running listener
        assert result['burst_count'] == _live_burst_count, result

        # The seeded rows are in the server's own audit database
        audit_db_path = zato_server['audit_db_path']
        demo_event_count = _count_demo_events(audit_db_path)
        assert demo_event_count >= result['event_count'], (demo_event_count, result['event_count'])

        self.__class__.first_event_count = demo_event_count

# ################################################################################################################################

    def test_02_the_live_burst_fills_the_counters(self, zato_client:'any_') -> 'None':
        """ The in-process counters of the main demo channel saw the burst -
        they live in memory, not in the audit database, so only live traffic
        makes them non-zero.
        """
        states = _get_channel_states(zato_client)

        assert _main_channel_name in states, sorted(states)

        main_state = states[_main_channel_name]
        assert main_state['is_listening'] is True, main_state
        assert main_state['received'] >= _live_burst_count, main_state
        assert main_state['last_message_time_iso'], main_state

# ################################################################################################################################

    def test_03_rerun_replaces_instead_of_stacking(self, zato_client:'any_', zato_server:'anydict') -> 'None':
        """ A second import replaces the previous demo data - the connections
        already exist and the event count stays put.
        """
        result = zato_client.invoke('test.demo.import', _import_request)

        # Nothing needed creating this time
        assert result['created_connections'] == [], result

        # The seeded rows were replaced, not appended to - the live burst adds its
        # own wire events on top, which is why this compares the demo-cid count.
        audit_db_path = zato_server['audit_db_path']
        demo_event_count = _count_demo_events(audit_db_path)

        assert demo_event_count == self.__class__.first_event_count, \
            (demo_event_count, self.__class__.first_event_count)

# ################################################################################################################################

    def test_04_removal_undoes_the_import(self, zato_client:'any_', zato_server:'anydict') -> 'None':
        """ The removal path deletes the connections, the rules and every demo
        audit row, so the other test modules start from a clean slate.
        """
        result = zato_client.invoke('test.demo.purge', {})

        assert len(result['deleted_connections']) == _connection_count, result
        assert len(result['deleted_rules']) == _rule_count, result

        # No demo rows are left in the audit database
        audit_db_path = zato_server['audit_db_path']
        assert _count_demo_events(audit_db_path) == 0

        # The demo channels are no longer on the live board
        states = _get_channel_states(zato_client)
        assert _main_channel_name not in states, sorted(states)

# ################################################################################################################################
# ################################################################################################################################
