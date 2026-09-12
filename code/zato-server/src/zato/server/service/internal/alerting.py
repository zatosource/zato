# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing

# Zato
from zato.common.api import Alerting, EMAIL, FileTransfer
from zato.common.alerting.collectors.evidence import collect_baseline, collect_measure_rows
from zato.common.alerting.engine import defaults_from_dict, dispatch_action, AlertDefaults, Empty_Explanation
from zato.common.alerting.explain.channel_info import describe_channel
from zato.common.alerting.explain.evidence import build_evidence_document, build_prompt, group_failures
from zato.common.alerting.explain.explanation import parse_explanation
from zato.common.alerting.explain.skill import get_skill_source, load_skill, Skills_Dir_Name
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.alerting.model import new_finding, new_rule
from zato.common.alerting.notification_config import read_notification_config, set_notification_config
from zato.common.alerting.object_config import alert_type_file_transfer, channel_sources, LLM_Connection_Config_Key
from zato.common.alerting.object_settings import load_object_settings
from zato.common.alerting.probes import parse_tls_target, run_certificate_probe, run_health_probe, run_test_transfer_probe
from zato.common.alerting.rendering import Template_Dir_Name
from zato.common.alerting.sweep import load_alert_rules, run_sweep
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn, IntervalBasedJob, Job
from zato.common.util.api import pluralize, utcnow
from zato.common.util.file_transfer_scheduler import get_schedule_list
from zato.common.util.scheduler import set_job_active
from zato.common.util.sql import get_dict_with_opaque
from zato.server.alerting_transports import build_alert_transports
from zato.server.generic.api.channel_hl7_mllp import get_current_metrics
from zato.server.generic.api.outconn_ftp import Outconn_FTP_Config_Defaults
from zato.server.generic.api.outconn_sftp import outconn_sftp_config_defaults
from zato.server.generic.api.outconn_smb import outconn_smb_config_defaults
from zato.server.rule_engine_api import get_backend
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.alerting.explain.skill import Skill
    from zato.common.typing_ import anydict, anylist, dictlist, stranydict, strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many seconds each unit of an interval-based job's definition is worth.
_seconds_per_week   = 7 * 24 * 3600
_seconds_per_day    = 24 * 3600
_seconds_per_hour   = 3600
_seconds_per_minute = 60

# Where the Microsoft service health overviews live, relative to the Graph service address
# the connection itself is configured with.
_graph_health_path = 'admin/serviceAnnouncement/healthOverviews'

# The test transfer's file - its name, its contents and the extra-data key
# naming the remote directory it goes to.
_test_transfer_file_name = 'zato-test-transfer.txt'
_test_transfer_contents = b'zato-test-transfer'
_test_transfer_extra_directory = 'directory'

# The per-object toggle saying whether a connection takes part in the test transfers at all
_test_transfers_field = 'test_transfers'

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
        """ Returns one key of the scheduler job's extra data, empty when the extra does not carry it.
        """
        if value := context.get(key):
            out = value
        else:
            out = ''

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

            # An inactive job is not expected to run, so it can never be overdue.
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

        # Every SFTP and SMB connection may carry schedules in its opaque attributes.
        with closing(self.odb.session()) as session:
            rows = session.query(GenericConn.id).\
                filter(GenericConn.type_.in_(FileTransfer.ConnTypeList)).\
                filter(GenericConn.cluster_id==self.server.cluster_id).\
                all()

            for row in rows:
                schedules = get_schedule_list(session, row.id)

                for schedule in schedules:

                    # A schedule switched off is not expected to receive anything.
                    if not schedule['is_active']:
                        continue

                    # Schedules created before the field existed carry no window.
                    if window := schedule.get('arrival_window'):
                        out[schedule['name']] = window

        return out

# ################################################################################################################################

    def _get_schedule_expectations(self) -> 'anydict':
        """ The daily expectation of each active file transfer schedule that declares one, by schedule name.
        """

        # Our response to produce
        out:'anydict' = {}

        # The schedules of every file transfer connection.
        with closing(self.odb.session()) as session:
            rows = session.query(GenericConn.id).\
                filter(GenericConn.type_.in_(FileTransfer.ConnTypeList)).\
                filter(GenericConn.cluster_id==self.server.cluster_id).\
                all()

            for row in rows:
                schedules = get_schedule_list(session, row.id)

                for schedule in schedules:

                    # An inactive schedule expects nothing.
                    if not schedule['is_active']:
                        continue

                    # A schedule without a count or a time of day expects nothing.
                    if not schedule['expected_files']:
                        continue

                    if not schedule['expected_by']:
                        continue

                    out[schedule['name']] = {
                        'expected_files': schedule['expected_files'],
                        'expected_by': schedule['expected_by'],
                        'expected_days': schedule['expected_days'],
                    }

        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        # The job's extra data arrives as a dict - an empty extra arrives as something else,
        # e.g. an empty string or bytes, which means nothing was configured.
        context = self.request.payload

        if not isinstance(context, dict):
            context = {}

        # One reference moment for the whole sweep.
        now = utcnow()

        # The rules live in the rule engine's SQL store - the live version of the alerts ruleset.
        backend = get_backend()
        rules = load_alert_rules(backend)

        # With nothing published there is nothing to match against.
        if not rules:
            self.logger.info('Alerting sweep found no published alert rules')
            return

        # The live channel metrics the feed-silent collector runs over.
        metrics_by_name = get_current_metrics()

        # Where the catch-all digest goes and where the links point to.
        default_to = self._get_extra(Alerting.Extra_Default_To, context)
        dashboard_url = self._get_extra(Alerting.Extra_Dashboard_URL, context)

        # The deployment-level targets a rule without its own delivers through.
        defaults = AlertDefaults()
        defaults.webhook_url = self._get_extra(Alerting.Extra_Webhook_URL, context)
        defaults.email_from = self._get_extra(Alerting.Extra_From, context)
        defaults.llm_connection = self._get_extra(Alerting.Extra_LLM_Connection, context)

        if default_to:
            email_to:'strlist' = []

            for item in default_to.split(','):
                email_to.append(item.strip())

            defaults.email_to = email_to

        transports = build_alert_transports(self, defaults.email_from)
        audit_log = AuditLog(self.server.name)
        engine = get_audit_engine()

        # The notification texts render from the server's own template files,
        # the copies create_server put next to the rest of the config - an environment
        # created before the templates existed renders from the shipped defaults.
        template_dir = os.path.join(self.server.repo_location, Template_Dir_Name)

        if not os.path.isdir(template_dir):
            template_dir = ''

        # The intervals the missed-run measure sizes itself against.
        job_intervals = self._get_job_intervals()

        # The windows the arrival-overdue measure sizes itself against.
        arrival_windows = self._get_arrival_windows()

        # The daily expectations of the schedules.
        schedule_expectations = self._get_schedule_expectations()

        # What each object's own Alerts tab says - its thresholds, toggles, window and email connection.
        with closing(self.odb.session()) as session:
            object_settings = load_object_settings(session, self.server.cluster_id)

        result = run_sweep(engine, rules, metrics_by_name, AuditSource.MLLP_Channel, transports, audit_log, self.cid, now,
            defaults=defaults, dashboard_url=dashboard_url, template_dir=template_dir, job_intervals=job_intervals,
            arrival_windows=arrival_windows, schedule_expectations=schedule_expectations, object_settings=object_settings)

        rule_label       = pluralize(result.rule_count, 'rule')
        fact_label       = pluralize(result.fact_count, 'fact')
        finding_label    = pluralize(result.finding_count, 'finding')
        dispatched_count = len(result.dispatched)

        self.logger.debug('Alerting sweep ran %s over %s - %s, %d raised, %d deduplicated, %d dispatched',
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
        """ Every active connection whose configuration names a TLS endpoint - REST and SOAP
        outgoing addresses that speak https, and email connections in direct-TLS mode.
        A STARTTLS connection's handshake starts in plaintext and needs the protocol's
        own upgrade step, so such connections are not here.
        """

        # Our response to produce
        out:'dictlist' = []

        config_store = self.server.config_manager.config_store

        # REST and SOAP outgoing connections with an https address.
        for config_dict in (config_store.out_plain_http, config_store.out_soap):
            for item in config_dict.values():

                config = item['config']

                # Internal connections are Zato's own plumbing, not something to alert about.
                if config['is_internal']:
                    continue

                # A connection switched off is not expected to be reachable at all.
                if not config['is_active']:
                    continue

                target = parse_tls_target(config['address'])

                if target:
                    host, port = target
                    out.append({'object_name': config['name'], 'host': host, 'port': port})

        # Email connections in direct-TLS mode - their host and port take a handshake as-is.
        for config_dict, tls_mode in (
            (config_store.email_smtp, EMAIL.SMTP.MODE.SSL),
            (config_store.email_imap, EMAIL.IMAP.MODE.SSL),
        ):
            for item in config_dict.values():

                config = item['config']

                if config['mode'] != tls_mode:
                    continue

                if not config['is_active']:
                    continue

                out.append({'object_name': config['name'], 'host': config['host'], 'port': config['port']})

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
    rules compare. The service returns without polling when no active Microsoft 365
    connection exists.
    """
    name = Alerting.Health_Service

    def _get_conn_name(self, conn_dict:'anydict') -> 'str':
        """ The name of the connection the probe polls through - the first active one
        by name, service health being tenant-wide, and an empty string when there is none.
        An inactive connection is left alone - its client authenticates on first use,
        which is a remote call an environment that switched the connection off never asked for.
        """
        for conn_name in sorted(conn_dict):
            item = conn_dict[conn_name]

            if item['is_active']:
                out = conn_name
                break
        else:
            out = ''

        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        conn_dict = self.server.config_manager.cloud_microsoft_365
        conn_name = self._get_conn_name(conn_dict)

        if not conn_name:
            return

        item = conn_dict[conn_name]
        client = item['conn'].shared_client

        def fetch() -> 'anylist':

            # The health overviews live under the service announcement API, at the Graph
            # address this connection is configured with.
            url = client.protocol.service_url + _graph_health_path
            response = client.connection.get(url)
            payload = response.json()

            out:'anylist' = []

            for overview in payload['value']:
                out.append((overview['service'], overview['status']))

            return out

        now = utcnow()
        audit_log = AuditLog(self.server.name)

        recorded = run_health_probe(audit_log, conn_name, fetch, now, cid=self.cid)

        service_label = pluralize(recorded, 'service')
        self.logger.info('Microsoft health probe recorded %s through `%s`', service_label, conn_name)

# ################################################################################################################################
# ################################################################################################################################

class AlertingTestTransfer(AdminService):
    """ Runs one test transfer per active file transfer connection that opted in through its
    own Alerts tab - upload, download, compare and delete a small test file - writing each
    outcome as an audit event the test transfer collector reads and rule Test_Transfer_Failing
    compares. The job ships inactive, like the rule, and both are activated together.
    """
    name = Alerting.Test_Transfer_Service

    def _wants_test_transfer(self, settings_by_object:'anydict', conn_name:'str') -> 'bool':
        """ Whether a connection's own settings say the test transfers run against it -
        a connection the settings do not know, e.g. one created during the sweep, is left alone.
        """
        if conn_name not in settings_by_object:
            return False

        out = settings_by_object[conn_name][_test_transfers_field] is True
        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        now = utcnow()
        audit_log = AuditLog(self.server.name)

        # Which connections opted in - the test transfer writes to the remote system, so each object says so itself.
        with closing(self.odb.session()) as session:
            object_settings = load_object_settings(session, self.server.cluster_id)

        settings_by_object = object_settings[alert_type_file_transfer]

        # The test transfer file's remote directory comes from the job's extra data when given.
        context = self.request.payload

        if not isinstance(context, dict):
            context = {}

        if directory := context.get(_test_transfer_extra_directory):
            directory = directory.rstrip('/')
            remote_path = f'{directory}/{_test_transfer_file_name}'
        else:
            remote_path = _test_transfer_file_name

        checked = 0

        # SMB connections - write, read back, compare and remove.
        outconn_smb = self.server.config_manager.outconn_smb

        for conn_name in sorted(outconn_smb):

            # An inactive connection has no pool behind it, so a transfer would only
            # wait for a client that is never built.
            item = outconn_smb[conn_name]

            if not item['is_active']:
                continue

            if not self._wants_test_transfer(settings_by_object, conn_name):
                continue

            def transfer_smb(conn_name:'str'=conn_name) -> 'None':
                conn = self.smb[conn_name]
                conn.write(_test_transfer_contents, remote_path)
                data = conn.read(remote_path)
                conn.delete_file(remote_path)
                if data != _test_transfer_contents:
                    raise Exception(f'The test transfer file came back different -> {data!r}')

            _ = run_test_transfer_probe(audit_log, conn_name, transfer_smb, now, cid=self.cid)
            checked += 1

        # SFTP connections - the same round trip over the SFTP command channel.
        outconn_sftp = self.server.config_manager.outconn_sftp

        for conn_name in sorted(outconn_sftp):

            item = outconn_sftp[conn_name]

            if not item['is_active']:
                continue

            if not self._wants_test_transfer(settings_by_object, conn_name):
                continue

            def transfer_sftp(conn_name:'str'=conn_name) -> 'None':
                conn = self.sftp[conn_name]
                conn.write(_test_transfer_contents, remote_path, overwrite=True)
                data = conn.read(remote_path)
                _ = conn.delete(remote_path)
                if data != _test_transfer_contents:
                    raise Exception(f'The test transfer file came back different -> {data!r}')

            _ = run_test_transfer_probe(audit_log, conn_name, transfer_sftp, now, cid=self.cid)
            checked += 1

        # FTP connections - the same round trip as with SMB.
        outconn_ftp = self.server.config_manager.outconn_ftp

        for conn_name in sorted(outconn_ftp):

            item = outconn_ftp[conn_name]

            if not item['is_active']:
                continue

            if not self._wants_test_transfer(settings_by_object, conn_name):
                continue

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

# The name explanations are stored under - the unique part is the id of the alert
# they explain, so one alert produces one explanation, not one per sweep.
_explanation_name_prefix = 'explanation.'

# The configuration keys of a REST or LLM connection that go into the Object section - addressing,
# timeouts and security identifiers only, never the credentials themselves.
_object_config_keys = (
    'name',
    'is_active',
    'address',
    'address_host',
    'address_url_path',
    'method',
    'model',
    'data_format',
    'content_type',
    'timeout',
    'pool_size',
    'validate_tls',
    'ping_method',
    'security_name',
    'sec_type',
    'username',
)

# What each file transfer connection type is called in the Object section
_file_transfer_type_labels = {
    FileTransfer.ConnType.SFTP: 'SFTP',
    FileTransfer.ConnType.FTP:  'FTP',
    FileTransfer.ConnType.SMB:  'SMB',
}

# The defaults of each file transfer connection type - a connection stored before a key existed reads at its default
_file_transfer_config_defaults = {
    FileTransfer.ConnType.SFTP: outconn_sftp_config_defaults,
    FileTransfer.ConnType.FTP:  Outconn_FTP_Config_Defaults,
    FileTransfer.ConnType.SMB:  outconn_smb_config_defaults,
}

# What a yes-or-no reads as in the Object section
_yes = 'yes'
_no = 'no'

# ################################################################################################################################
# ################################################################################################################################

class Explain(AdminService):
    """ Explains one alert and delivers it - the alerting engine hands over every alert the LLM
    is to explain, before the rule's own action runs. The service collects the evidence the
    alert's measures were counted from, has the LLM explain it against the skill of the alert's
    source, stores the explanation next to the alert and then runs the rule's action through
    the engine itself, with the explanation in the notification. An alert the LLM cannot
    explain - no skill for its source, no LLM connection - is delivered all the same,
    without the explanation paragraph.
    """
    name = Alerting.Service_Explain

    def handle(self) -> 'None':

        # The payload arrives from the alerting engine - anything else means a manual
        # invocation with nothing to work from.
        payload = self.request.payload

        if not isinstance(payload, dict):
            self.logger.info('Alert explanation received no alert payload, nothing to do')
            return

        explanation = self._get_explanation(payload)

        # .. and the rule's own action delivers the alert, explained or not.
        self._deliver(payload, explanation)

# ################################################################################################################################

    def _get_explanation(self, payload:'stranydict') -> 'stranydict':
        """ The explanation of one alert - the stored one when the alert was explained
        before, a new one from the LLM otherwise, and the empty one for a source
        without an explanation skill.
        """
        source = payload['source']
        object_name = payload['object_name']

        # Only sources with an explanation skill of their own can be explained ..
        skill = self._get_skill(source)

        if not skill:
            self.logger.info('No explanation skill exists for source `%s`, delivering `%s` unexplained', source, object_name)
            return Empty_Explanation

        # .. and one alert produces one explanation, not one per sweep - an error alert
        # dispatched again within its dedup window carries the explanation it already has.
        store = ExplanationStore(self.odb.session, self.server.cluster_id)
        name = _explanation_name_prefix + str(payload['alert_id'])

        if stored := store.get(name):
            self.logger.info('An explanation already exists for `%s`, delivering `%s` with it', name, object_name)
            return stored

        # Collect the evidence - the rows the measures were counted from, grouped and fitted
        # to the budget, the object's definition and the baseline around the failures ..
        now = utcnow()
        engine = get_audit_engine()
        fact = payload['fact']

        object_info, baseline_object_name, test_transfers_on = self._get_object_info(source, object_name)

        rows = collect_measure_rows(engine, fact, payload['measures'], now)
        groups = group_failures(rows, source)

        baseline = collect_baseline(engine, fact, now, baseline_object_name=baseline_object_name,
            test_transfers_on=test_transfers_on)

        alert = {
            'rule': payload['rule'],
            'severity': payload['severity'],
            'source': source,
            'object_name': object_name,
            'message': payload['message'],
            'fact': fact,
            'thresholds': payload['thresholds'],
            'measures': payload['measures'],
        }

        document = build_evidence_document(alert, object_info, groups, baseline, now)

        # .. have the LLM explain it ..
        out = self._explain(payload, skill, document)

        # .. store the explanation next to the alert, the document with it so a person can read what the LLM read ..
        details = {
            'object_name': object_name,
            'source': source,
            'rule': payload['rule'],
            'alert_id': payload['alert_id'],
            'count': payload['count'],
            'severity': payload['severity'],
            'message': payload['message'],
            'link': payload['link'],
            'evidence': document,
            'explanation': out['explanation'],
            'confidence': out['confidence'],
            'remediation': out['remediation'],
            'is_parsed': out['is_parsed'],
            'created_iso': now.isoformat(),
        }

        store.create(name, details)

        # .. and leave a trace in the audit log.
        audit_log = AuditLog(self.server.name)

        _ = audit_log.insert(source, AuditEvent.Alert_Explained, object_name,
            cid=self.cid, outcome=AuditOutcome.OK, data=payload['message'])

        self.logger.info('Alert `%s` explained for `%s` (%s)', name, object_name, payload['rule'])

        return out

# ################################################################################################################################

    def _get_skills_dir(self) -> 'str':
        """ The server's own skills directory - the shipped skills answer
        until an environment created before the directory existed is recreated.
        """
        out = os.path.join(self.server.repo_location, Skills_Dir_Name)

        if not os.path.isdir(out):
            out = ''

        return out

# ################################################################################################################################

    def _get_skill(self, source:'str') -> 'Skill | None':
        """ The skill explaining the alerts of a source - a probe's or a health check's alerts
        are explained with the skill of the connection they check.
        """
        out = load_skill(get_skill_source(source), self._get_skills_dir())
        return out

# ################################################################################################################################

    def _get_object_info(self, source:'str', object_name:'str') -> 'tuple[anylist, str, bool]':
        """ The Object section of the evidence - the object's definition as label and value pairs,
        secrets left out - along with the name the baseline is read under and whether test
        transfers are on for the object. A REST or an LLM connection is read off its facade,
        a file transfer connection or one of its schedules off the ODB, any other source
        contributes its name alone.
        """
        if source == AuditSource.REST_Outgoing:
            out = self._config_to_info(self.out.rest[object_name].config)
            return out, object_name, False

        if source == AuditSource.LLM:
            out = self._config_to_info(self.llm.conn_dict[object_name])
            return out, object_name, False

        if source in (AuditSource.File_Outgoing, AuditSource.Test_Transfer):
            out = self._get_file_transfer_info(object_name)
            if out is not None:
                return out

        if source in channel_sources:
            with closing(self.odb.session()) as session:
                channel_info = describe_channel(session, self.server.cluster_id, source, object_name)

            if channel_info is not None:
                return channel_info, object_name, False

        out = [('Name', object_name)]
        return out, object_name, False

# ################################################################################################################################

    def _config_to_info(self, config:'anydict') -> 'anylist':
        """ The keys of interest of a connection's configuration as label and value pairs - only the ones
        the configuration has, e.g. a connection with no security definition has no security_name at all.
        """

        # Our response to produce
        out:'anylist' = []

        for key in _object_config_keys:
            if key in config:
                out.append((key, config[key]))

        return out

# ################################################################################################################################

    def _get_file_transfer_info(self, object_name:'str') -> 'tuple[anylist, str, bool] | None':
        """ The definition of a file transfer connection, or of the connection owning the schedule
        the object name stands for - host, username, how it authenticates, its schedules and
        whether test transfers are on. None when no connection or schedule goes by the name.
        """
        with closing(self.odb.session()) as session:

            rows = session.query(GenericConn).\
                filter(GenericConn.type_.in_(FileTransfer.ConnTypeList)).\
                filter(GenericConn.cluster_id==self.server.cluster_id).\
                all()

            for row in rows:

                schedules = get_schedule_list(session, row.id)
                schedule_names:'strlist' = []

                for schedule in schedules:
                    schedule_names.append(schedule['name'])

                is_connection = row.name == object_name
                is_schedule = object_name in schedule_names

                if not (is_connection or is_schedule):
                    continue

                # The connection's columns and its opaque attributes together - host, username, key and the like -
                # with every key the connection was stored without at the default of its type
                config = get_dict_with_opaque(row)

                for key, default in _file_transfer_config_defaults[row.type_].items():
                    if key not in config or config[key] is None:
                        config[key] = default

                test_transfers_on = self._wants_test_transfer(session, row.name)

                out = self._describe_file_transfer(row, config, schedules, object_name, is_schedule, test_transfers_on)

                return out, row.name, test_transfers_on

        return None

# ################################################################################################################################

    def _describe_file_transfer(
        self,
        row:'GenericConn',
        config:'anydict',
        schedules:'dictlist',
        object_name:'str',
        is_schedule:'bool',
        test_transfers_on:'bool',
        ) -> 'anylist':
        """ The label and value pairs describing one file transfer connection.
        """

        # Our response to produce
        out:'anylist' = []

        type_label = _file_transfer_type_labels[row.type_]

        if is_schedule:
            out.append(('Schedule', f'{object_name}, of the {type_label} connection {row.name}'))

        out.append(('Name', row.name))
        out.append(('Type', type_label))
        out.append(('Active', _yes if row.is_active else _no))

        if row.type_ == FileTransfer.ConnType.SFTP:
            out.append(('Host', config['address']))
            out.append(('Username', config['username']))

            if config['private_key']:
                authentication = f'private key ({config["private_key"]})'
            else:
                authentication = 'password'

            host_key_checking = 'on' if config['strict_host_key_checking'] else 'off'
            out.append(('Authentication', f'{authentication}, host key checking {host_key_checking}'))

        elif row.type_ == FileTransfer.ConnType.FTP:
            out.append(('Host', f'{config["host"]}:{config["port"]}'))
            out.append(('Username', config['username']))

            tls = 'on' if config['use_ssl'] else 'off'
            out.append(('Authentication', f'password, TLS {tls}'))

        else:
            out.append(('Host', f'{config["host"]}:{config["port"]}'))
            out.append(('Username', config['username']))
            out.append(('Authentication', 'password'))

        for schedule in schedules:
            state = 'active' if schedule['is_active'] else 'inactive'
            description = f'{schedule["name"]} - watches {schedule["directory"]}, delivers to {schedule["service"]}, ' + \
                f'every {schedule["run_every"]} {schedule["run_unit"]}, {state}'
            out.append(('Schedule', description))

        if not schedules:
            out.append(('Schedules', 'none'))

        out.append(('Test transfers', 'on' if test_transfers_on else 'off'))

        return out

# ################################################################################################################################

    def _wants_test_transfer(self, session:'SASession', conn_name:'str') -> 'bool':
        """ Whether the connection's own Alerts tab has test transfers on.
        """
        settings_by_object = load_object_settings(session, self.server.cluster_id)[alert_type_file_transfer]

        if conn_name not in settings_by_object:
            return False

        out = settings_by_object[conn_name][_test_transfers_field] is True
        return out

# ################################################################################################################################

    def _get_llm_connection(self, payload:'stranydict') -> 'str':
        """ The LLM connection the explanation goes through - the object's own when its Alerts tab
        names one, the deployment's default otherwise, as long as it exists and is active.
        An empty name means no LLM is available and the alert goes out unexplained.
        """
        action_config = payload['action_config']

        if LLM_Connection_Config_Key in action_config:
            name = action_config[LLM_Connection_Config_Key]
        else:
            name = payload['defaults']['llm_connection']

        if not name:
            return ''

        if name not in self.llm.conn_dict:
            self.logger.info('LLM connection `%s` does not exist, storing the alert without an explanation', name)
            return ''

        item = self.llm.conn_dict[name]

        if not item['is_active']:
            self.logger.info('LLM connection `%s` is inactive, storing the alert without an explanation', name)
            return ''

        return name

# ################################################################################################################################

    def _explain(self, payload:'stranydict', skill:'Skill', document:'str') -> 'stranydict':
        """ Runs the LLM explanation, or produces an empty one when no LLM connection
        is available - the alert still goes out so a person can look at the evidence.
        """
        llm_connection = self._get_llm_connection(payload)

        if not llm_connection:

            self.logger.info('No LLM connection is available, storing the alert without an explanation')

            out:'stranydict' = {
                'explanation': '',
                'confidence': '',
                'remediation': None,
                'is_parsed': False,
            }

            return out

        prompt = build_prompt(skill.instructions, document)
        response = self.llm[llm_connection].invoke(prompt)

        out = parse_explanation(response['text'], skill.remediations)
        return out

# ################################################################################################################################

    def _get_template_dir(self) -> 'str':
        """ The server's own template directory - the bundled defaults answer
        until an environment created before the templates existed is recreated.
        """
        out = os.path.join(self.server.repo_location, Template_Dir_Name)

        if not os.path.isdir(out):
            out = ''

        return out

# ################################################################################################################################

    def _deliver(self, payload:'stranydict', explanation:'stranydict') -> 'None':
        """ Runs the rule's own action through the alerting engine, the way the sweep
        would have - the same transports, the same templates, the same deployment-level
        targets - with the explanation filled in. The explanation being present is what
        keeps the engine from handing the alert back here.
        """
        rule = new_rule(
            payload['rule'],
            payload['kind'],
            action=payload['action'],
            action_config=payload['action_config'],
            dedup_window_seconds=payload['dedup_window_seconds'],
            explain_with_llm=True,
        )

        finding = new_finding(payload['kind'], payload['source'], payload['object_name'], payload['message'],
            link=payload['link'], severity=payload['severity'], fact=payload['fact'], thresholds=payload['thresholds'],
            measures=payload['measures'])

        defaults = defaults_from_dict(payload['defaults'])
        transports = build_alert_transports(self, defaults.email_from)
        template_dir = self._get_template_dir()

        dispatch_action(rule, finding, payload['alert_id'], payload['count'], transports, defaults, template_dir,
            explanation)

# ################################################################################################################################
# ################################################################################################################################
