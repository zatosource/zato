# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
from http.client import OK

# SQLAlchemy
from sqlalchemy import create_engine, func, select

# Zato
from zato.common.analytics.api import usage_table
from zato.common.audit_log.api import event_table, AuditSource
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from config_db_screen import get_sql_form_values, save_sql_database
from rest_channel import create_channel, invoke_until_status
from audit_toggle import get_audit_row_count
from server_restart import restart_server

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright')

_Test_Name_Prefix = 'test.config.db.audit.switch.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

# How many requests go out before the switch, after the switch and after the restart
_Count_Before_Switch = 3
_Count_After_Switch = 2
_Count_After_Restart = 1

# Every request produces two audit events - one received, one sent
_Events_Per_Request = 2

# How long the rollup subprocess may take
_Rollup_Timeout = 60

# State shared between the sequential tests of this module - the first one points
# the audit database at file A and the later ones switch, roll up, restart and restore
_shared_state = {} # type: dict

# ################################################################################################################################
# ################################################################################################################################

def _count_channel_events(db_path:'str', channel_name:'str') -> 'int':
    """ Counts the audit events of one channel in an SQLite file directly, with a throwaway
    engine, independently of what the server or the dashboard currently point at.
    """
    engine = create_engine(f'sqlite:///{db_path}')

    count_query = select(func.count())
    count_query = count_query.select_from(event_table)
    count_query = count_query.where(
        event_table.c.source == AuditSource.REST_Channel,
        event_table.c.object_name == channel_name,
    )

    with engine.connect() as connection:
        count_result = connection.execute(count_query)
        out = count_result.scalar()

    engine.dispose()
    return out

# ################################################################################################################################

def _sum_channel_requests(analytics_db_path:'str', channel_name:'str') -> 'int':
    """ Sums the aggregated request counts of one channel in an analytics SQLite file directly.
    """
    engine = create_engine(f'sqlite:///{analytics_db_path}')

    sum_query = select(func.coalesce(func.sum(usage_table.c.request_count), 0))
    sum_query = sum_query.where(usage_table.c.channel == channel_name)

    with engine.connect() as connection:
        sum_result = connection.execute(sum_query)
        out = sum_result.scalar()

    engine.dispose()
    return out

# ################################################################################################################################

def _run_rollup(temporary_dir:'str', audit_db_path:'str', analytics_db_path:'str') -> 'None':
    """ Runs the rollup CLI command the way cron would, in its own OS process,
    pointed at the given audit and analytics databases through an env file,
    the same way the containerized cron job passes one.
    """
    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

    # The env file carries the same variables the Config DB screen saves
    env_file_path = os.path.join(temporary_dir, 'rollup-env.ini')

    env_file_contents = '\n'.join([
        '[env]',
        'Zato_Audit_Log_DB_Type=sqlite',
        f'Zato_Audit_Log_DB_Name={audit_db_path}',
        'Zato_Analytics_DB_Type=sqlite',
        f'Zato_Analytics_DB_Name={analytics_db_path}',
        '',
    ])

    with open(env_file_path, 'w') as env_file:
        _ = env_file.write(env_file_contents)

    result = subprocess.run(
        [zato_bin, 'analytics', 'rollup', '--env-file', env_file_path],
        capture_output=True, text=True, timeout=_Rollup_Timeout)

    logger.info('[rollup] returncode=%d stdout=%s stderr=%s', result.returncode, result.stdout, result.stderr)
    assert result.returncode == 0, f'Rollup failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

# ################################################################################################################################

def _invoke_ok(server_port:'int', url_path:'str', how_many:'int') -> 'None':
    """ Invokes a REST channel the given number of times, expecting OK each time.
    """
    for index in range(how_many):
        payload = f'{{"index": {index}}}'
        response = invoke_until_status(server_port, url_path, OK, data=payload)
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

# ################################################################################################################################
# ################################################################################################################################

class TestConfigDBAuditSwitch:
    """ The audit database is switched on the fly through the Config DB SQL screen -
    new events go to the new database immediately, the old one keeps what it had,
    the analytics rollup and the dashboard follow, and the switch survives a restart.
    """

    def test_01_events_go_to_file_a(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Points the audit database at SQLite file A via the screen, creates an audited
        REST channel, sends requests and finds the events in file A by opening it directly.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        temporary_dir = zato_dashboard['temporary_dir']

        # Remember the original SQLite path so the last test can restore it ..
        original_values = get_sql_form_values(page, base_url, 'audit-log', ('name',))
        _shared_state['original_name'] = original_values['name']

        # .. the two files the audit database will be switched between ..
        file_a = os.path.join(temporary_dir, 'config-db-audit-a.db')
        file_b = os.path.join(temporary_dir, 'config-db-audit-b.db')

        _shared_state['file_a'] = file_a
        _shared_state['file_b'] = file_b

        # .. point the audit database at file A ..
        save_sql_database(page, base_url, 'audit-log', {'name': file_a})

        # .. create a REST channel with the audit toggle on, which is the default ..
        channel_name = _Test_Name_Prefix + 'channel'
        url_path = '/test/config-db/audit/switch/' + rand_string()

        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
        })

        _shared_state['channel_name'] = channel_name
        _shared_state['url_path'] = url_path

        # .. send the pre-switch requests ..
        _invoke_ok(server_port, url_path, _Count_Before_Switch)

        # .. and their events are physically in file A.
        event_count = _count_channel_events(file_a, channel_name)
        expected = _Count_Before_Switch * _Events_Per_Request

        assert event_count == expected, f'Expected {expected} events in file A, got {event_count}'

# ################################################################################################################################

    def test_02_switch_to_file_b(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Switches to file B on the fly - the new events land only in B
        and file A keeps its count, untouched.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        file_a = _shared_state['file_a']
        file_b = _shared_state['file_b']
        channel_name = _shared_state['channel_name']
        url_path = _shared_state['url_path']

        # Switch the audit database to file B ..
        save_sql_database(page, base_url, 'audit-log', {'name': file_b})

        # .. send the post-switch requests ..
        _invoke_ok(server_port, url_path, _Count_After_Switch)

        # .. they are all in file B ..
        event_count_b = _count_channel_events(file_b, channel_name)
        expected_b = _Count_After_Switch * _Events_Per_Request

        assert event_count_b == expected_b, f'Expected {expected_b} events in file B, got {event_count_b}'

        # .. and file A kept its pre-switch count.
        event_count_a = _count_channel_events(file_a, channel_name)
        expected_a = _Count_Before_Switch * _Events_Per_Request

        assert event_count_a == expected_a, f'Expected still {expected_a} events in file A, got {event_count_a}'

# ################################################################################################################################

    def test_03_rollup_follows(self, zato_dashboard:'anydict') -> 'None':
        """ The analytics rollup runs as its own OS process against each file in turn -
        the aggregate built from file A reflects only the pre-switch traffic
        and the one built from file B only the post-switch traffic.
        """
        temporary_dir = zato_dashboard['temporary_dir']

        file_a = _shared_state['file_a']
        file_b = _shared_state['file_b']
        channel_name = _shared_state['channel_name']

        analytics_x = os.path.join(temporary_dir, 'config-db-analytics-x.db')
        analytics_y = os.path.join(temporary_dir, 'config-db-analytics-y.db')

        # Aggregate file A into analytics file X - only the pre-switch requests are there ..
        _run_rollup(temporary_dir, file_a, analytics_x)

        request_count_x = _sum_channel_requests(analytics_x, channel_name)
        assert request_count_x == _Count_Before_Switch, \
            f'Expected {_Count_Before_Switch} requests in analytics X, got {request_count_x}'

        # .. and file B into analytics file Y - only the post-switch requests are there.
        _run_rollup(temporary_dir, file_b, analytics_y)

        request_count_y = _sum_channel_requests(analytics_y, channel_name)
        assert request_count_y == _Count_After_Switch, \
            f'Expected {_Count_After_Switch} requests in analytics Y, got {request_count_y}'

# ################################################################################################################################

    def test_04_dashboard_follows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The dashboard reads the audit database directly with its own environment,
        which the save updated too - its audit log page shows the post-switch events.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _shared_state['channel_name']

        row_count = get_audit_row_count(page, base_url, AuditSource.REST_Channel, channel_name)
        expected = _Count_After_Switch * _Events_Per_Request

        assert row_count == expected, f'Expected {expected} audit log rows after the switch, got {row_count}'

# ################################################################################################################################

    def test_05_switch_survives_restart(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The save persisted the variables into the server's env file - after a full
        restart, with no config events since, new events still land in file B.
        """
        server_port = zato_dashboard['server_port']

        file_a = _shared_state['file_a']
        file_b = _shared_state['file_b']
        channel_name = _shared_state['channel_name']
        url_path = _shared_state['url_path']

        # Restart the server - it reloads the saved variables from the env file on its own ..
        restart_server(zato_dashboard)

        # .. send more requests ..
        _invoke_ok(server_port, url_path, _Count_After_Restart)

        # .. they are in file B, on top of the post-switch ones ..
        event_count_b = _count_channel_events(file_b, channel_name)
        expected_b = (_Count_After_Switch + _Count_After_Restart) * _Events_Per_Request

        assert event_count_b == expected_b, f'Expected {expected_b} events in file B after the restart, got {event_count_b}'

        # .. and file A still kept its pre-switch count.
        event_count_a = _count_channel_events(file_a, channel_name)
        expected_a = _Count_Before_Switch * _Events_Per_Request

        assert event_count_a == expected_a, f'Expected still {expected_a} events in file A, got {event_count_a}'

# ################################################################################################################################

    def test_06_restore_original_values(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Restores the original SQLite path through the screen so later tests
        in the session see the environment they expect.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        original_name = _shared_state['original_name']

        save_sql_database(page, base_url, 'audit-log', {'name': original_name})

        # The form shows the restored path after a reload
        restored_values = get_sql_form_values(page, base_url, 'audit-log', ('name',))
        assert restored_values['name'] == original_name, \
            f'Expected the restored path `{original_name}`, got `{restored_values["name"]}`'

# ################################################################################################################################
# ################################################################################################################################
