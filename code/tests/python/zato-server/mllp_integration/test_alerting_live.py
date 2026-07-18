# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socketserver
import threading
import time

# SQLAlchemy
from sqlalchemy import create_engine, select

# Zato
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditEvent
from zato.common.audit_log.common import alert_table
from zato.common.alerting.model import AlertAction, AlertState, FindingKind

# Zato - test helpers
from conftest import wait_for_port_open
from test_mllp_audit import _build_adt_a01, _send_and_receive, _wait_for_events

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist
    any_ = any_
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_connection_type_channel = 'channel-hl7-mllp'
_generic_service_name    = 'zato.generic.connection'
_smtp_service_name       = 'zato.email.smtp'

# The names of everything this module creates
_channel_name      = 'test-alerting-accept'
_error_channel_name = 'test-alerting-error'
_smtp_conn_name    = 'test-alerting-smtp'
_rule_name         = 'test-alerting-error-rate'

# The MSH-3 value routing messages to the error channel
_error_sender_application = 'ALERTING_ERROR_SYSTEM'

# Who the alert emails go to and who they come from
_alert_addresses = ['ops@example.com']
_alert_from      = 'alerts@example.com'

# How long to wait for routes and connection pools to settle after a create call
_settle_seconds = 1

# How long to wait for the captured email to arrive
_email_wait_seconds = 5.0

# ################################################################################################################################
# ################################################################################################################################

def _start_smtp_capture() -> 'tuple':
    """ Starts an SMTP server that captures every message body it receives.
    Returns (port, server, messages) - the caller invokes server.shutdown().
    """

    messages:'strlist' = []

    class _SMTPHandler(socketserver.StreamRequestHandler):

        def _send(self, line:'str') -> 'None':
            self.wfile.write((line + '\r\n').encode('ascii'))

        def handle(self) -> 'None':
            self._send('220 alerting-capture ESMTP')

            in_data = False
            data_lines:'strlist' = []

            while True:
                line = self.rfile.readline()
                if not line:
                    break
                text = line.decode('utf-8', 'replace').rstrip('\r\n')

                if in_data:

                    # The message body ends with a lone dot
                    if text == '.':
                        in_data = False
                        messages.append('\n'.join(data_lines))
                        data_lines = []
                        self._send('250 OK message accepted')
                    else:
                        data_lines.append(text)
                    continue

                verb = text.split(' ')[0].upper()

                if verb in ('EHLO', 'HELO'):
                    self._send('250-alerting-capture')
                    self._send('250 AUTH PLAIN LOGIN')
                elif verb == 'AUTH':
                    self._send('235 Authentication successful')
                elif verb in ('MAIL', 'RCPT', 'NOOP', 'RSET'):
                    self._send('250 OK')
                elif verb == 'DATA':
                    in_data = True
                    self._send('354 End data with <CR><LF>.<CR><LF>')
                elif verb == 'QUIT':
                    self._send('221 Bye')
                    break
                else:
                    self._send('250 OK')

    class _ThreadingTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    server = _ThreadingTCPServer(('127.0.0.1', 0), _SMTPHandler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    out = port, server, messages
    return out

# ################################################################################################################################

def _get_alerts(audit_db_path:'str', rule_name:'str') -> 'anylist':
    """ Returns the alert rows one rule raised, oldest first, each as a dict.
    """

    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(alert_table)
    query = query.where(alert_table.c.rule_name == rule_name)
    query = query.order_by(alert_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    engine.dispose()
    return out

# ################################################################################################################################

def _wait_for_messages(messages:'strlist', expected_count:'int') -> 'None':
    """ Polls until the SMTP capture received the expected number of messages.
    """

    deadline = time.monotonic() + _email_wait_seconds

    while time.monotonic() < deadline:
        if len(messages) >= expected_count:
            return
        time.sleep(0.1)

# ################################################################################################################################
# ################################################################################################################################

class TestAlertingLive:
    """ Live tests for scheduler-driven alerting - the sweep job exists by default,
    a rule stored as a generic object drives the collectors over real seeded traffic,
    and the dispatched email is captured by a local SMTP server.
    """

    channel_id:'int' = 0
    error_channel_id:'int' = 0
    smtp_conn_id:'int' = 0

# ################################################################################################################################

    def test_01_sweep_job_exists_by_default(self, zato_client:'any_') -> 'None':
        """ The server created the alerting job on boot - scheduler-driven means
        the job invokes the sweep service on its interval with no setup at all.
        """

        job = zato_client.invoke('zato.scheduler.job.get-by-name', {'cluster_id': 1, 'name': Alerting.Job_Name})

        assert job['name'] == Alerting.Job_Name, job
        assert job['service_name'] == Alerting.Service, job
        assert job['is_active'] is True, job
        assert job['minutes'] == Alerting.Job_Interval_Minutes, job

# ################################################################################################################################

    def test_02_create_channels_and_seed_traffic(
        self,
        zato_client:'any_',
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ Creates an audited accept route and an audited error route, then sends
        real MLLP traffic through both - the error channel accumulates the error
        outcomes the error-rate collector will notice.
        """
        audit_db_path = zato_server['audit_db_path']

        # The audited default route - healthy traffic
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_channel_name,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            is_default=True,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.channel_id = response['id']

        # The audited error route - its service always raises
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_error_channel_name,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.error',
            msh3_sending_app=_error_sender_application,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.error_channel_id = response['id']

        wait_for_port_open(mllp_port)

        # The routes settle asynchronously after the create calls return
        time.sleep(_settle_seconds)

        # One healthy message and two erroring ones - the error channel's
        # share of error outcomes lands well above the rule's threshold
        message_bytes = _build_adt_a01('ALERT-OK-001')
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
        assert b'MSA|AA|ALERT-OK-001' in ack_bytes

        for control_id in ('ALERT-ERR-001', 'ALERT-ERR-002'):
            message_bytes = _build_adt_a01(control_id, sender_application=_error_sender_application)
            ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
            assert b'MSA|AE|' in ack_bytes

        # The error outcomes are in the audit trail for the collector to find
        ack_events = _wait_for_events(audit_db_path, _error_channel_name, 2, AuditEvent.Ack_Sent)
        assert len(ack_events) == 2, ack_events

# ################################################################################################################################

    def test_03_sweep_raises_dispatches_and_deduplicates(
        self,
        zato_client:'any_',
        zato_server:'dict',
        ) -> 'None':
        """ The sweep service - what the scheduler job invokes - collects the seeded
        error rate, raises an alert, sends the email through the configured SMTP
        connection, and a second sweep only increments the count.
        """
        audit_db_path = zato_server['audit_db_path']

        smtp_port, smtp_server, messages = _start_smtp_capture()

        try:

            # The SMTP connection the sweep sends through
            response = zato_client.create(
                f'{_smtp_service_name}.create',
                cluster_id=1,
                name=_smtp_conn_name,
                is_active=True,
                host='127.0.0.1',
                port=smtp_port,
                timeout=30,
                is_debug=False,
                mode='plain',
                needs_tls_verify=False,
                ping_address=_alert_addresses[0],
                username='alerts-test',
            )

            assert 'id' in response
            self.__class__.smtp_conn_id = response['id']

            # The rule watching the error channel, stored as a generic object -
            # the same row the enmasse importer would create
            response = zato_client.invoke('test.alerting.rule.save', {
                'name': _rule_name,
                'kind': FindingKind.Error_Rate,
                'object_name': _error_channel_name,
                'action': AlertAction.Email_Digest,
                'action_config': {'addresses': _alert_addresses},
                'config': {'window_seconds': 3600, 'threshold': 0.4},
            })

            assert response['is_ok'], response

            # The connection pool settles asynchronously after the create call
            time.sleep(_settle_seconds)

            # The first sweep - exactly what the scheduler job invokes on its interval
            _ = zato_client.invoke(Alerting.Service, {
                Alerting.Extra_SMTP_Conn: _smtp_conn_name,
                Alerting.Extra_From: _alert_from,
            })

            # The alert was raised and dispatched ..
            alerts = _get_alerts(audit_db_path, _rule_name)

            assert len(alerts) == 1, alerts
            alert = alerts[0]

            assert alert['object_name'] == _error_channel_name, alert
            assert alert['kind'] == FindingKind.Error_Rate, alert
            assert alert['state'] == AlertState.Unobserved, alert
            assert alert['count'] == 1, alert
            assert 'Error rate on' in alert['message'], alert

            # .. every occurrence is an alert-raised audit event ..
            raised_events = _wait_for_events(audit_db_path, _error_channel_name, 1, AuditEvent.Alert_Raised)
            assert len(raised_events) == 1, raised_events

            # .. and the email went out through the captured SMTP connection.
            _wait_for_messages(messages, 1)
            assert len(messages) == 1, messages

            # Long headers arrive folded - unfolding makes the content assertable
            email_text = messages[0].replace('\n ', ' ')
            assert 'Error rate on' in email_text, email_text
            assert _error_channel_name in email_text, email_text
            assert _alert_addresses[0] in email_text, email_text

            # The second sweep, still inside the dedup window, only counts -
            # the alert's count grows and no second email goes out
            _ = zato_client.invoke(Alerting.Service, {
                Alerting.Extra_SMTP_Conn: _smtp_conn_name,
                Alerting.Extra_From: _alert_from,
            })

            alerts = _get_alerts(audit_db_path, _rule_name)

            assert len(alerts) == 1, alerts
            assert alerts[0]['count'] == 2, alerts

            # Every occurrence lands in the audit trail, deduplicated or not
            raised_events = _wait_for_events(audit_db_path, _error_channel_name, 2, AuditEvent.Alert_Raised)
            assert len(raised_events) == 2, raised_events

            # The dispatch itself was suppressed
            assert len(messages) == 1, messages

        finally:
            smtp_server.shutdown()
            smtp_server.server_close()

# ################################################################################################################################

    def test_04_cleanup(self, zato_client:'any_') -> 'None':
        """ Deletes everything this module created, so the other test modules
        start from the same clean slate as before.
        """

        response = zato_client.invoke('test.alerting.rule.delete', {'name': _rule_name})
        assert response['is_ok'], response

        if self.__class__.smtp_conn_id:
            _ = zato_client.delete(f'{_smtp_service_name}.delete', id=self.__class__.smtp_conn_id)

        for connection_id in (
            self.__class__.channel_id,
            self.__class__.error_channel_id,
        ):
            if connection_id:
                _ = zato_client.delete(f'{_generic_service_name}.delete', id=connection_id)

# ################################################################################################################################
# ################################################################################################################################
