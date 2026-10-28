# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from time import time

# gevent
from gevent import sleep

# Zato
from zato.common.b2b.ebms2.business_signals import BusinessSignal
from zato.common.b2b.ebms2.common import SyncReplyMode
from zato.common.test.b2b_cpa import AgreementSettings, build_cpa, new_settings
from zato.common.test.b2b_perf_common import Default_Document_Size, Host_Name, MessageKind, Notification_Action, \
    Notification_CPA_Id, Notification_Service, PartyConfig, Partner_Name, perf_durations, PerfMode, PerfPath, PerfRole, \
    Request_Action, Request_Response_CPA_Id, Request_Response_Service, Response_Action, save_config, start_command_body, \
    StartCommand
from zato.common.test.b2b_perf_control import free_port, is_idle, Local_Host, MemorySampler, party_command, party_url, \
    Party_Program, run_recovery, sleep_until, start_party, write_file, write_pem_pair
from zato.common.test.b2b_perf_results import compute_result, read_records
from zato.common.test.b2b_pki import rsa_parties

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.test.b2b_cpa import PartySettings
    from zato.common.test.b2b_perf_control import RecoveryResult
    from zato.common.test.b2b_perf_results import PerfResult, recordlist
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import stranydict
    Certificate = Certificate
    PartySettings = PartySettings
    PerfResult = PerfResult
    recordlist = recordlist
    RecoveryResult = RecoveryResult
    stranydict = stranydict
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# How a party delivers a message again - often enough to outlast a restart of the host, and soon after a failure.
_retries        = 10
_retry_interval = 'PT2S'

# How long the receiver of a notification has to acknowledge its receipt with a business signal.
_time_to_acknowledge_receipt = 'PT5M'

# The roles of the parties in both agreements.
_host_role    = 'Seller'
_partner_role = 'Buyer'

# How long after the commands are sent the parties start sending, in seconds.
Start_Delay = 2

# How long a run has to complete what it sent, and how long a stopped party has to end, in seconds.
Drain_Timeout = 120
Exit_Timeout  = 60

# How often the run asks the parties whether they are idle, in seconds.
Status_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PerfSettings:
    """ What one run varies by.
    """
    work_dir: str

    # The environment variables the host connects to the audit log database with.
    database_env: 'stranydict'

    # How many requests the partner and how many notifications the host start per second.
    request_rate:      float
    notification_rate: float

    warmup_seconds:   int
    duration_seconds: int
    document_size:    int = Default_Document_Size

    # The percentage of the deliveries of the host the partner refuses or discards the acknowledgment of,
    # and of the messages of the partner it posts twice.
    refuse_percent:    float = 0.0
    drop_ack_percent:  float = 0.0
    duplicate_percent: float = 0.0

    # How many seconds into the measurement window the host is killed and started again, if at all.
    kill_after_seconds: float = 0.0

# ################################################################################################################################

@dataclass(init=False)
class RestartTimes:
    """ When the host was killed, started again, and when it accepted connections again, as seconds since the epoch.
    """
    killed_at:  float = 0.0
    started_at: float = 0.0
    ready_at:   float = 0.0

# ################################################################################################################################
# ################################################################################################################################

def new_perf_settings(work_dir:'str', database_env:'stranydict', request_rate:'float', notification_rate:'float') -> 'PerfSettings':
    """ Returns the settings of a run with the durations the environment sets.
    """
    durations = perf_durations()

    out = PerfSettings()
    out.work_dir = work_dir
    out.database_env = database_env
    out.request_rate = request_rate
    out.notification_rate = notification_rate
    out.warmup_seconds = durations.warmup_seconds
    out.duration_seconds = durations.duration_seconds

    return out

# ################################################################################################################################

def _set_party(settings:'PartySettings', name:'str', role:'str', endpoint:'str', certificate:'Certificate') -> 'None':
    settings.name = name
    settings.party_id = name
    settings.role = role
    settings.endpoint = endpoint
    settings.certificate = certificate

# ################################################################################################################################

def _new_agreement(
    parties:'TestParties',
    now:'datetime',
    cpa_id:'str',
    service:'str',
    action:'str',
    reply_action:'str',
    ) -> 'AgreementSettings':
    """ Returns the settings of an agreement in which the receiver of the action sends the reply action back,
    acknowledging each message on the connection it arrived on, with the parties left for the caller to name.
    """
    out = new_settings(parties, now)
    out.cpa_id = cpa_id
    out.service = service
    out.action = action
    out.reply_actions = [reply_action]
    out.retries = _retries
    out.retry_interval = _retry_interval
    out.business_channel.sync_reply_mode = SyncReplyMode.MSH_Signals_Only

    return out

# ################################################################################################################################
# ################################################################################################################################

class PerfRun:
    """ One performance run - the host and the partner in processes of their own, the commands that start
    and stop them, and the measurements read from what they recorded.
    """

    def __init__(self, settings:'PerfSettings') -> 'None':

        self.settings = settings
        self.host_port = free_port(Local_Host)
        self.partner_port = free_port(Local_Host)

        work_dir = settings.work_dir

        self.host_records = os.path.join(work_dir, 'host-records.jsonl')
        self.partner_records = os.path.join(work_dir, 'partner-records.jsonl')
        self.host_config_path = os.path.join(work_dir, 'host-config.json')
        self.partner_config_path = os.path.join(work_dir, 'partner-config.json')
        self.recovery_config_path = os.path.join(work_dir, 'recovery-config.json')
        self.host_errors = os.path.join(work_dir, 'host-errors.log')
        self.partner_errors = os.path.join(work_dir, 'partner-errors.log')

        self.restart = RestartTimes()

        self._write_party_files()

# ################################################################################################################################

    def _write_party_files(self) -> 'None':
        """ Writes the key material of both parties, the two agreements between them and the configuration of each.
        """
        work_dir = self.settings.work_dir
        parties = rsa_parties()
        now = datetime.now(timezone.utc)

        # The host signs with the key of the receiver of the generated parties and the partner with that of the sender.
        host_key_path = os.path.join(work_dir, 'host-key.pem')
        host_certificate_path = os.path.join(work_dir, 'host-certificate.pem')
        partner_key_path = os.path.join(work_dir, 'partner-key.pem')
        partner_certificate_path = os.path.join(work_dir, 'partner-certificate.pem')

        write_pem_pair(host_key_path, host_certificate_path, parties.receiver.key, parties.receiver.certificate)
        write_pem_pair(partner_key_path, partner_certificate_path, parties.sender.key, parties.sender.certificate)

        host_request_response = party_url(Local_Host, self.host_port, PerfPath.Request_Response)
        host_notification = party_url(Local_Host, self.host_port, PerfPath.Notification)
        partner_request_response = party_url(Local_Host, self.partner_port, PerfPath.Request_Response)
        partner_notification = party_url(Local_Host, self.partner_port, PerfPath.Notification)

        # The partner sends the requests and the host answers each one with a response ..
        request_response = _new_agreement(parties, now, Request_Response_CPA_Id, Request_Response_Service, Request_Action,
            Response_Action)

        _set_party(request_response.sender, Partner_Name, _partner_role, partner_request_response,
            parties.sender.certificate)
        _set_party(request_response.receiver, Host_Name, _host_role, host_request_response, parties.receiver.certificate)

        # .. while the host sends the notifications and the partner acknowledges each one with a business signal.
        notification = _new_agreement(parties, now, Notification_CPA_Id, Notification_Service, Notification_Action,
            BusinessSignal.Receipt_Acknowledgement)
        notification.time_to_acknowledge_receipt = _time_to_acknowledge_receipt

        _set_party(notification.sender, Host_Name, _host_role, host_notification, parties.receiver.certificate)
        _set_party(notification.receiver, Partner_Name, _partner_role, partner_notification, parties.sender.certificate)

        request_response_path = os.path.join(work_dir, 'request-response-cpa.xml')
        notification_path = os.path.join(work_dir, 'notification-cpa.xml')

        request_response_cpa = build_cpa(request_response)
        notification_cpa = build_cpa(notification)

        write_file(request_response_path, request_response_cpa)
        write_file(notification_path, notification_cpa)

        agreements = {
            PerfPath.Request_Response: request_response_path,
            PerfPath.Notification: notification_path,
        }

        settings = self.settings

        host = PartyConfig()
        host.role = PerfRole.Host
        host.mode = PerfMode.Load
        host.listen_host = Local_Host
        host.port = self.host_port
        host.agreements = agreements
        host.key_path = host_key_path
        host.certificate_path = host_certificate_path
        host.records_path = self.host_records
        host.send_rate = settings.notification_rate
        host.send_kind = MessageKind.Notification
        host.document_size = settings.document_size
        host.refuse_percent = 0.0
        host.drop_ack_percent = 0.0
        host.duplicate_percent = 0.0

        partner = PartyConfig()
        partner.role = PerfRole.Partner
        partner.mode = PerfMode.Load
        partner.listen_host = Local_Host
        partner.port = self.partner_port
        partner.agreements = agreements
        partner.key_path = partner_key_path
        partner.certificate_path = partner_certificate_path
        partner.records_path = self.partner_records
        partner.send_rate = settings.request_rate
        partner.send_kind = MessageKind.Request
        partner.document_size = settings.document_size
        partner.refuse_percent = settings.refuse_percent
        partner.drop_ack_percent = settings.drop_ack_percent
        partner.duplicate_percent = settings.duplicate_percent

        save_config(host, self.host_config_path)
        save_config(partner, self.partner_config_path)

        host.mode = PerfMode.Recover
        save_config(host, self.recovery_config_path)

# ################################################################################################################################

    def _host_env(self) -> 'stranydict':
        out = dict(os.environ)
        out.update(self.settings.database_env)

        return out

# ################################################################################################################################

    def _drain(self) -> 'None':
        """ Waits until both parties completed what they sent, or until the time the run has for it ends.
        """
        started_at = time()
        deadline = started_at + Drain_Timeout

        while time() < deadline:
            if is_idle(Local_Host, self.host_port):
                if is_idle(Local_Host, self.partner_port):
                    break

            sleep(Status_Interval)

# ################################################################################################################################

    def run(self) -> 'PerfResult':
        """ Runs the warm-up and the measurement, kills and starts the host again in the middle if the settings say so,
        waits until everything sent was completed, stops both parties and returns the measurements.
        """
        settings = self.settings
        host_env = self._host_env()
        partner_env = dict(os.environ)

        host = start_party(Party_Program, self.host_config_path, self.host_errors, host_env)
        partner = start_party(Party_Program, self.partner_config_path, self.partner_errors, partner_env)

        command_time = time()

        command = StartCommand()
        command.start_at = command_time + Start_Delay
        command.warmup_seconds = settings.warmup_seconds
        command.duration_seconds = settings.duration_seconds

        body = start_command_body(command)

        _ = party_command(Local_Host, self.host_port, PerfPath.Start, body)
        _ = party_command(Local_Host, self.partner_port, PerfPath.Start, body)

        window_start = command.start_at + command.warmup_seconds
        window_end = window_start + command.duration_seconds

        # The memory of the host is sampled through the measurement window, from whichever process runs at the moment.
        sleep_until(window_start)
        sampler = MemorySampler(host.pid)

        if settings.kill_after_seconds:
            kill_at = window_start + settings.kill_after_seconds
            sleep_until(kill_at)

            host.kill()
            _ = host.wait()
            self.restart.killed_at = time()

            self.restart.started_at = time()
            host = start_party(Party_Program, self.host_config_path, self.host_errors, host_env)
            self.restart.ready_at = time()

            sampler.pid = host.pid
            _ = party_command(Local_Host, self.host_port, PerfPath.Start, body)

        sleep_until(window_end)
        rss_samples_kb = sampler.stop()

        self._drain()

        _ = party_command(Local_Host, self.host_port, PerfPath.Stop, b'')
        _ = party_command(Local_Host, self.partner_port, PerfPath.Stop, b'')

        _ = host.wait(Exit_Timeout)
        _ = partner.wait(Exit_Timeout)

        records = self.read_records()

        out = compute_result(records, window_start, window_end, rss_samples_kb)
        return out

# ################################################################################################################################

    def read_records(self) -> 'recordlist':
        """ Returns the records of the host followed by those of the partner.
        """
        out = read_records(self.host_records)
        partner_records = read_records(self.partner_records)
        out.extend(partner_records)

        return out

# ################################################################################################################################

    def run_recovery(self) -> 'RecoveryResult':
        """ Starts the host in a process of its own that reads what the audit log has to recover, and returns
        how long that took, in how many statements, and the resident memory of the process afterwards.
        """
        env = self._host_env()

        out = run_recovery(Party_Program, self.recovery_config_path, self.host_errors, env, self.host_records)
        return out

# ################################################################################################################################
# ################################################################################################################################
