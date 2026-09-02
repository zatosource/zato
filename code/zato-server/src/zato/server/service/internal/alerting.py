# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing

# requests
import requests

# Zato
from zato.common.api import Alerting, EMAIL, FileTransfer, SMTPMessage
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.names import get_notification_conn_name
from zato.common.alerting.notification_config import read_notification_config, set_notification_config
from zato.common.alerting.probes import parse_tls_target, run_certificate_probe, run_health_probe, run_test_transfer_probe
from zato.common.alerting.rendering import Template_Dir_Name
from zato.common.alerting.sweep import load_alert_rules, run_sweep
from zato.common.audit_log.api import get_audit_engine, AuditLog, AuditSource
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn, IntervalBasedJob, Job
from zato.common.util.api import pluralize, utcnow
from zato.common.util.file_transfer_scheduler import get_schedule_list
from zato.common.util.scheduler import set_job_active
from zato.server.generic.api.channel_hl7_mllp import get_current_metrics
from zato.server.rule_engine_api import get_backend
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, stranydict, strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long a webhook post may take before it is abandoned, in seconds.
_webhook_timeout = 10

# How many seconds each unit of an interval-based job's definition is worth.
_seconds_per_week   = 7 * 24 * 3600
_seconds_per_day    = 24 * 3600
_seconds_per_hour   = 3600
_seconds_per_minute = 60

# Where the Microsoft service health overviews live.
_graph_health_url = 'https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/healthOverviews'

# The test transfer's file - its name, its contents and the extra-data key
# naming the remote directory it goes to.
_test_transfer_file_name = 'zato-test-transfer.txt'
_test_transfer_contents = b'zato-test-transfer'
_test_transfer_extra_directory = 'directory'

# ################################################################################################################################
# ################################################################################################################################

class AlertingRun(AdminService):
    """ Runs one alerting sweep - the scheduler invokes this service on its interval.
    The collectors measure the audit database and the live channel metrics into facts,
    the `alerts` ruleset in the rule engine decides which facts matter, and the matches
    are deduplicated and dispatched through the actions their outcomes name.
    Email, Slack and Microsoft Teams go out through the connections that share
    the default notification name, as long as they exist and are active.
    """
    name = Alerting.Service

    def _get_extra(self, key:'str', context:'anydict') -> 'str':
        """ Returns one key of the scheduler job's extra data - the extra is user-editable
        in the scheduler UI, so a missing key simply means the feature it drives is off.
        """
        if value := context.get(key):
            out = value
        else:
            out = ''

        return out

# ################################################################################################################################

    def _build_transports(self, context:'anydict') -> 'AlertTransports':
        """ Wires the real delivery callables the engine dispatches through - email,
        Slack and Microsoft Teams ride on the connections that share the default
        notification name, next to the server's own invoker, pub/sub and HTTP
        for plain webhooks. The default connections ship inactive with placeholder
        details, so each of these callables skips quietly until a person fills
        its connection in and activates it.
        """
        conn_name = get_notification_conn_name()
        from_ = self._get_extra(Alerting.Extra_From, context)

        def send_email(addresses:'strlist', subject:'str', body:'str') -> 'None':

            # The email component may be disabled in server.conf
            if not self.email:
                self.logger.warning(
                    'Could not send an alerting email; is component_enabled.email set to True in server.conf?')
                return

            # A connection that does not exist sends nothing ..
            try:
                smtp_item = self.email.smtp.get(conn_name, True)
            except KeyError:
                self.logger.info('No SMTP connection `%s` exists, skipping an email to `%s`', conn_name, addresses)
                return

            # .. and neither does an inactive one.
            if not smtp_item.config['is_active']:
                self.logger.info('SMTP connection `%s` is inactive, skipping an email to `%s`', conn_name, addresses)
                return

            message = SMTPMessage()
            message.from_ = from_
            message.to = addresses
            message.subject = subject
            message.body = body

            smtp_item.conn.send(message)

        def invoke_service(service_name:'str', payload:'stranydict') -> 'None':
            _ = self.server.invoke(service_name, payload)

        def publish(topic_name:'str', payload:'stranydict') -> 'None':
            _ = self.server.pubsub_backend.publish(topic_name, payload, cid=self.cid, correl_id=self.cid)

        def send_slack(channel:'str', text:'str') -> 'None':

            # A connection that does not exist or is inactive sends nothing.
            if conn_name not in self.slack.conn_dict:
                self.logger.info('No Slack connection `%s` exists, skipping the notification', conn_name)
                return

            item = self.slack.conn_dict[conn_name]

            if not item['is_active']:
                self.logger.info('Slack connection `%s` is inactive, skipping the notification', conn_name)
                return

            _ = self.slack.send(conn_name, channel, text)

        def send_teams(to:'str', html:'str') -> 'None':

            # A connection that does not exist or is inactive sends nothing.
            if conn_name not in self.microsoft.teams.conn_dict:
                self.logger.info('No Microsoft Teams connection `%s` exists, skipping the notification', conn_name)
                return

            item = self.microsoft.teams.conn_dict[conn_name]

            if not item['is_active']:
                self.logger.info('Microsoft Teams connection `%s` is inactive, skipping the notification', conn_name)
                return

            _ = self.microsoft.teams.send(conn_name, to, html)

        def http_post(url:'str', payload:'stranydict') -> 'None':
            response = requests.post(url, json=payload, timeout=_webhook_timeout)
            if not response.ok:
                self.logger.warning('Alert webhook `%s` returned %s - %s', url, response.status_code, response.text)

        # Our response to produce
        out = AlertTransports()

        out.send_email = send_email
        out.invoke_service = invoke_service
        out.publish = publish
        out.send_slack = send_slack
        out.send_teams = send_teams
        out.http_post = http_post

        return out

# ################################################################################################################################

    def _get_job_intervals(self) -> 'strintdict':
        """ Returns the interval of every active interval-based job, in seconds, by job name -
        what the missed-run measure sizes itself against. Jobs with no interval,
        one-time jobs among them, have no notion of being overdue and are not here.
        """

        # Our response to produce
        out:'strintdict' = {}

        with closing(self.odb.session()) as session:
            rows = session.query(
                Job.name,
                Job.is_active,
                IntervalBasedJob.weeks,
                IntervalBasedJob.days,
                IntervalBasedJob.hours,
                IntervalBasedJob.minutes,
                IntervalBasedJob.seconds,
            ).outerjoin(IntervalBasedJob, Job.id==IntervalBasedJob.job_id).\
                filter(Job.cluster_id==self.server.cluster_id).\
                all()

        for row in rows:

            # An inactive job is not expected to run, so it can never be overdue
            if not row.is_active:
                continue

            # One-time jobs carry no interval columns at all - they arrive as None
            # from the outer join and contribute nothing.
            unit_values = (
                (row.weeks,   _seconds_per_week),
                (row.days,    _seconds_per_day),
                (row.hours,   _seconds_per_hour),
                (row.minutes, _seconds_per_minute),
                (row.seconds, 1),
            )

            interval = 0

            for value, seconds_per_unit in unit_values:
                if value is None:
                    value = 0
                interval += value * seconds_per_unit

            if interval:
                out[row.name] = interval

        return out

# ################################################################################################################################

    def _get_arrival_windows(self) -> 'strintdict':
        """ Returns the arrival window of every active file transfer schedule, in seconds,
        by schedule name - what the arrival-overdue measure sizes itself against.
        A schedule with no window declares no expectation and is not here.
        """

        # Our response to produce
        out:'strintdict' = {}

        # Every SFTP and SMB connection may carry schedules in its opaque attributes
        with closing(self.odb.session()) as session:
            rows = session.query(GenericConn.id).\
                filter(GenericConn.type_.in_(FileTransfer.ConnTypeList)).\
                filter(GenericConn.cluster_id==self.server.cluster_id).\
                all()

            for row in rows:
                schedules = get_schedule_list(session, row.id)

                for schedule in schedules:

                    # A schedule switched off is not expected to receive anything
                    if not schedule['is_active']:
                        continue

                    # Schedules created before the field existed carry no window
                    if window := schedule.get('arrival_window'):
                        out[schedule['name']] = window

        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        # The job's extra data arrives as a dict - an empty extra arrives as something else,
        # e.g. an empty string or bytes, which means nothing was configured.
        context = self.request.payload

        if not isinstance(context, dict):
            context = {}

        # One reference moment for the whole sweep
        now = utcnow()

        # The rules live in the rule engine's SQL store - the live version of the alerts ruleset
        backend = get_backend()
        rules = load_alert_rules(backend)

        # With nothing published there is nothing to match against
        if not rules:
            self.logger.info('Alerting sweep found no published alert rules')
            return

        # The live channel metrics the feed-silent collector runs over
        metrics_by_name = get_current_metrics()

        # Where the catch-all digest goes and where the links point to
        default_to = self._get_extra(Alerting.Extra_Default_To, context)
        dashboard_url = self._get_extra(Alerting.Extra_Dashboard_URL, context)

        # The deployment-level targets a rule without its own delivers through
        defaults = AlertDefaults()
        defaults.webhook_url = self._get_extra(Alerting.Extra_Webhook_URL, context)

        if default_to:
            email_to = []

            for item in default_to.split(','):
                email_to.append(item.strip())

            defaults.email_to = email_to

        transports = self._build_transports(context)
        audit_log = AuditLog(self.server.name)
        engine = get_audit_engine()

        # The notification texts render from the server's own template files,
        # the copies create_server put next to the rest of the config - an environment
        # created before the templates existed renders from the shipped defaults.
        template_dir = os.path.join(self.server.repo_location, Template_Dir_Name)

        if not os.path.isdir(template_dir):
            template_dir = ''

        # The intervals the missed-run measure sizes itself against
        job_intervals = self._get_job_intervals()

        # The windows the arrival-overdue measure sizes itself against
        arrival_windows = self._get_arrival_windows()

        result = run_sweep(engine, rules, metrics_by_name, AuditSource.MLLP_Channel, transports, audit_log, self.cid, now,
            defaults=defaults, dashboard_url=dashboard_url, template_dir=template_dir, job_intervals=job_intervals,
            arrival_windows=arrival_windows)

        rule_label       = pluralize(result.rule_count, 'rule')
        fact_label       = pluralize(result.fact_count, 'fact')
        finding_label    = pluralize(result.finding_count, 'finding')
        dispatched_count = len(result.dispatched)

        self.logger.info('Alerting sweep ran %s over %s - %s, %d raised, %d deduplicated, %d dispatched',
            rule_label, fact_label, finding_label, result.raised_count, result.deduplicated_count, dispatched_count)

# ################################################################################################################################
# ################################################################################################################################

class AlertingCertCheck(AdminService):
    """ Measures the TLS certificate of every TLS-bearing connection - the default daily
    probe job invokes this service. One audit event per connection carries the days-left
    measure the certificate collector reads and rule Certificate_Expiring compares.
    """
    name = Alerting.Cert_Service

    def _get_targets(self) -> 'dictlist':
        """ Every connection whose configuration names a TLS endpoint - REST and SOAP
        outgoing addresses that speak https, and email connections in direct-TLS mode.
        STARTTLS connections are not here because their handshake starts in plaintext
        and needs the protocol's own upgrade dance, not a plain TLS connection.
        """

        # Our response to produce
        out:'dictlist' = []

        config_store = self.server.config_manager.config_store

        # REST and SOAP outgoing connections with an https address
        for config_dict in (config_store.out_plain_http, config_store.out_soap):
            for item in config_dict.values():

                config = item['config']

                # Internal connections are Zato's own plumbing, not something to alert about
                if config['is_internal']:
                    continue

                target = parse_tls_target(config['address'])

                if target:
                    host, port = target
                    out.append({'object_name': config['name'], 'host': host, 'port': port})

        # Email connections in direct-TLS mode - their host and port take a handshake as-is
        for config_dict, tls_mode in (
            (config_store.email_smtp, EMAIL.SMTP.MODE.SSL),
            (config_store.email_imap, EMAIL.IMAP.MODE.SSL),
        ):
            for item in config_dict.values():

                config = item['config']

                if config['mode'] != tls_mode:
                    continue

                out.append({'object_name': config['name'], 'host': config['host'], 'port': int(config['port'])})

        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        now = utcnow()
        audit_log = AuditLog(self.server.name)

        targets = self._get_targets()
        checked = run_certificate_probe(audit_log, targets, now, cid=self.cid)

        connection_label = pluralize(checked, 'connection')
        self.logger.info('Certificate check measured %s', connection_label)

# ################################################################################################################################
# ################################################################################################################################

class AlertingMicrosoftHealth(AdminService):
    """ Polls the Microsoft Graph service-health endpoint through the first active
    Microsoft 365 connection - the default probe job invokes this service every
    quarter of an hour. One audit event per Microsoft service carries the normalized
    health state the collector reads and the Service_Degraded and Service_Interrupted
    rules compare. The service no-ops quietly when no Microsoft 365 connection exists.
    """
    name = Alerting.Health_Service

    def handle(self) -> 'None':

        conn_dict = self.server.config_manager.cloud_microsoft_365

        # No connection means the probe has nothing to poll - quietly, because the job
        # exists in every environment while the connection is the opt-in part.
        if not conn_dict:
            return

        # The first connection is as good as any - service health is tenant-wide
        conn_name = sorted(conn_dict)[0]
        item = conn_dict[conn_name]
        client = item['conn'].shared_client

        # The health overviews live under the service announcement API
        response = client.connection.get(_graph_health_url)
        payload = response.json()

        states = []

        for overview in payload['value']:
            states.append((overview['service'], overview['status']))

        now = utcnow()
        audit_log = AuditLog(self.server.name)

        recorded = run_health_probe(audit_log, states, now, cid=self.cid)

        service_label = pluralize(recorded, 'service')
        self.logger.info('Microsoft health probe recorded %s through `%s`', service_label, conn_name)

# ################################################################################################################################
# ################################################################################################################################

class AlertingTestTransfer(AdminService):
    """ Runs one test transfer per active file transfer connection - upload, download,
    compare and delete a small test file - writing each outcome as an audit event the
    test transfer collector reads and rule Test_Transfer_Failing compares. The job ships
    inactive, like the rule, because the test transfer writes to remote systems -
    activating both is the documented opt-in.
    """
    name = Alerting.Test_Transfer_Service

    def handle(self) -> 'None':

        now = utcnow()
        audit_log = AuditLog(self.server.name)

        # The test transfer file's remote directory comes from the job's extra data when given
        context = self.request.payload

        if not isinstance(context, dict):
            context = {}

        if directory := context.get(_test_transfer_extra_directory):
            directory = directory.rstrip('/')
            remote_path = f'{directory}/{_test_transfer_file_name}'
        else:
            remote_path = _test_transfer_file_name

        checked = 0

        # SMB connections - write, read back, compare and remove
        for conn_name in sorted(self.server.config_manager.outconn_smb):

            def transfer_smb(conn_name:'str'=conn_name) -> 'None':
                conn = self.smb[conn_name]
                conn.write(_test_transfer_contents, remote_path)
                data = conn.read(remote_path)
                conn.delete_file(remote_path)
                if data != _test_transfer_contents:
                    raise Exception(f'The test transfer file came back different -> {data!r}')

            _ = run_test_transfer_probe(audit_log, conn_name, transfer_smb, now, cid=self.cid)
            checked += 1

        # SFTP connections - the same round trip over the SFTP command channel
        for conn_name in sorted(self.server.config_manager.outconn_sftp):

            def transfer_sftp(conn_name:'str'=conn_name) -> 'None':
                conn = self.sftp[conn_name]
                conn.write(_test_transfer_contents, remote_path, overwrite=True)
                data = conn.read(remote_path)
                _ = conn.delete(remote_path)
                if data != _test_transfer_contents:
                    raise Exception(f'The test transfer file came back different -> {data!r}')

            _ = run_test_transfer_probe(audit_log, conn_name, transfer_sftp, now, cid=self.cid)
            checked += 1

        # FTP connections - the same round trip as with SMB
        for conn_name in sorted(self.server.config_manager.outconn_ftp):

            def transfer_ftp(conn_name:'str'=conn_name) -> 'None':
                conn = self.ftp[conn_name]
                conn.write(_test_transfer_contents, remote_path)
                data = conn.read(remote_path)
                conn.delete_file(remote_path)
                if data != _test_transfer_contents:
                    raise Exception(f'The test transfer file came back different -> {data!r}')

            _ = run_test_transfer_probe(audit_log, conn_name, transfer_ftp, now, cid=self.cid)
            checked += 1

        connection_label = pluralize(checked, 'connection')
        self.logger.info('Test transfer probe checked %s', connection_label)

# ################################################################################################################################
# ################################################################################################################################

class AlertingGetNotificationConfig(AdminService):
    """ Returns the notification targets the alerting sweep job's extra holds -
    what the config screen's notifications row shows.
    """
    name = Alerting.Get_Notification_Config_Service
    output = 'response_data'

    def handle(self) -> 'None':

        with closing(self.odb.session()) as session:
            job = session.query(Job).\
                filter(Job.name==Alerting.Job_Name).\
                filter(Job.cluster_id==self.server.cluster_id).\
                one()
            extra = job.extra

        values = read_notification_config(extra)

        self.response.payload.response_data = dumps(values)

# ################################################################################################################################
# ################################################################################################################################

class AlertingSetNotificationConfig(AdminService):
    """ Writes the notification targets into the alerting sweep job's extra -
    what the config screen's notifications row saves through, and the very
    next sweep already delivers with the new values.
    """
    name = Alerting.Set_Notification_Config_Service

    def handle(self) -> 'None':

        values = self.request.payload

        with closing(self.odb.session()) as session:
            changed = set_notification_config(session, self.server.cluster_id, values)
            session.commit()

        self.logger.info('Alerting notification config saved (changed=%s)', changed)

# ################################################################################################################################
# ################################################################################################################################

class AlertingSetTestTransferState(AdminService):
    """ Flips the test transfer scheduler job's active flag in ODB - the config screen's
    test transfers checkbox drives this service next to its flip of the
    Test_Transfer_Failing rule, so the job and the rule always move together.
    """
    name = Alerting.Set_Test_Transfer_State_Service

    def handle(self) -> 'None':

        is_active = self.request.payload['is_active']

        with closing(self.odb.session()) as session:
            changed = set_job_active(session, self.server.cluster_id, Alerting.Test_Transfer_Job_Name, is_active)
            session.commit()

        self.logger.info('Test transfer job `%s` set to is_active=%s (changed=%s)',
            Alerting.Test_Transfer_Job_Name, is_active, changed)

# ################################################################################################################################
# ################################################################################################################################
