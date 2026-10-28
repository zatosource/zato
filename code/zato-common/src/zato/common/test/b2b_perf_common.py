# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from json import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strstrdict
    stranydict = stranydict
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The environment variables the warm-up and the measurement durations of a run are read from, in seconds.
Env_Warmup_Seconds   = 'Zato_B2B_Perf_Warmup_Seconds'
Env_Duration_Seconds = 'Zato_B2B_Perf_Duration_Seconds'

# The durations of a run when the environment does not set them.
Default_Warmup_Seconds   = 60
Default_Duration_Seconds = 300

# The criteria a steady run passes by.
Min_Transactions_Per_Second = 100
Max_Ack_Latency_P99_Ms      = 500
Max_Commits_Per_Second      = 12
Max_Statements_Per_Second   = 80

# The longest a recovery of the audit log takes for the run that measures it to pass.
Max_Recovery_Seconds = 10

# How often the host ends the business transactions whose deadline passed, in seconds.
Expiry_Interval_Seconds = 1

# The rate of transactions of a steady run.
Steady_Rate = 100

# The parties of the agreements and the servers they run as.
Host_Name           = 'b2b-perf-host'
Partner_Name        = 'b2b-perf-partner'
Host_Server_Name    = 'b2b-perf-host-server'
Partner_Server_Name = 'b2b-perf-partner-server'

# The agreement of the requests of the partner and the responses of the host ..
Request_Response_CPA_Id  = 'b2b-perf-request-response'
Request_Response_Service = 'urn:zato:b2b:perf:orders'
Request_Action           = 'SubmitOrder'
Response_Action          = 'SubmitOrderResponse'

# .. and the agreement of the notifications of the host and the business signals of the partner.
Notification_CPA_Id  = 'b2b-perf-notification'
Notification_Service = 'urn:zato:b2b:perf:order-status'
Notification_Action  = 'NotifyOrderStatus'

# The line a party process prints once it accepts connections.
Line_Ready = 'ready'

# The size of the business document of each message, in bytes.
Default_Document_Size = 4096

# The line of /proc/<pid>/status with the resident memory of a process, in kilobytes.
_rss_prefix = 'VmRSS:'

# ################################################################################################################################
# ################################################################################################################################

class PerfRole:
    Host    = 'host'
    Partner = 'partner'

# ################################################################################################################################

class PerfMode:

    # The party exchanges messages until it is stopped.
    Load = 'load'

    # The party reads what the audit log has to recover, records how long that took, and ends.
    Recover = 'recover'

# ################################################################################################################################

class PerfPath:
    Request_Response = '/request-response'
    Notification     = '/notification'
    Start            = '/perf/start'
    Status           = '/perf/status'
    Stop             = '/perf/stop'

# ################################################################################################################################

class MessageKind:
    Request      = 'request'
    Response     = 'response'
    Notification = 'notification'
    Signal       = 'signal'

# ################################################################################################################################

class RecordType:
    Sent      = 'sent'
    Attempt   = 'attempt'
    Ack       = 'ack'
    Failed    = 'failed'
    Delivered = 'delivered'
    Matched   = 'matched'
    Fault     = 'fault'
    Summary   = 'summary'
    Recovery  = 'recovery'

    # The receiver answered a message on the connection it arrived on ..
    Received = 'received'

    # .. or ended its business transaction once a deadline passed.
    Timed_Out = 'timed-out'

# ################################################################################################################################

class FaultType:

    # The partner answers a delivery with 503 before it reads the message ..
    Refused = 'refused'

    # .. answers with 503 after it received the message ..
    Ack_Dropped = 'ack-dropped'

    # .. or posts its own message a second time.
    Duplicated = 'duplicated'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PartyConfig:
    """ What one party process runs with.
    """
    role: str
    mode: str

    # The address and the port the party listens on.
    listen_host: str
    port:        int

    # The agreement files by the path each one receives its messages at, and the key material of the party.
    agreements:       'strstrdict'
    key_path:         str
    certificate_path: str

    # Where the party appends a record of each event of each message.
    records_path: str

    # How many messages per second the party starts, and of which kind.
    send_rate: float
    send_kind: str

    document_size: int

    # The percentage of deliveries and posts of the partner with a fault.
    refuse_percent:    float
    drop_ack_percent:  float
    duplicate_percent: float

# ################################################################################################################################

@dataclass(init=False)
class StartCommand:
    """ When the parties start sending, as seconds since the epoch, and for how long.
    """
    start_at:         float
    warmup_seconds:   int
    duration_seconds: int

# ################################################################################################################################

@dataclass(init=False)
class PerfDurations:
    warmup_seconds:   int
    duration_seconds: int

# ################################################################################################################################
# ################################################################################################################################

def save_config(config:'PartyConfig', path:'str') -> 'None':

    data:'stranydict' = {
        'role': config.role,
        'mode': config.mode,
        'listen_host': config.listen_host,
        'port': config.port,
        'agreements': config.agreements,
        'key_path': config.key_path,
        'certificate_path': config.certificate_path,
        'records_path': config.records_path,
        'send_rate': config.send_rate,
        'send_kind': config.send_kind,
        'document_size': config.document_size,
        'refuse_percent': config.refuse_percent,
        'drop_ack_percent': config.drop_ack_percent,
        'duplicate_percent': config.duplicate_percent,
    }

    text = dumps(data)

    with open(path, 'w', encoding='utf8') as config_file:
        _ = config_file.write(text)

# ################################################################################################################################

def load_config(path:'str') -> 'PartyConfig':

    with open(path, encoding='utf8') as config_file:
        text = config_file.read()

    data = loads(text)

    out = PartyConfig()
    out.role = data['role']
    out.mode = data['mode']
    out.listen_host = data['listen_host']
    out.port = data['port']
    out.agreements = data['agreements']
    out.key_path = data['key_path']
    out.certificate_path = data['certificate_path']
    out.records_path = data['records_path']
    out.send_rate = data['send_rate']
    out.send_kind = data['send_kind']
    out.document_size = data['document_size']
    out.refuse_percent = data['refuse_percent']
    out.drop_ack_percent = data['drop_ack_percent']
    out.duplicate_percent = data['duplicate_percent']

    return out

# ################################################################################################################################

def start_command_body(command:'StartCommand') -> 'bytes':

    data:'stranydict' = {
        'start_at': command.start_at,
        'warmup_seconds': command.warmup_seconds,
        'duration_seconds': command.duration_seconds,
    }

    text = dumps(data)

    out = text.encode('utf8')
    return out

# ################################################################################################################################

def parse_start_command(body:'bytes') -> 'StartCommand':

    data = loads(body)

    out = StartCommand()
    out.start_at = data['start_at']
    out.warmup_seconds = data['warmup_seconds']
    out.duration_seconds = data['duration_seconds']

    return out

# ################################################################################################################################

def perf_durations() -> 'PerfDurations':
    """ Returns the warm-up and the measurement durations of a run, as the environment sets them or by default.
    """
    out = PerfDurations()

    if warmup_seconds := os.environ.get(Env_Warmup_Seconds):
        out.warmup_seconds = int(warmup_seconds)
    else:
        out.warmup_seconds = Default_Warmup_Seconds

    if duration_seconds := os.environ.get(Env_Duration_Seconds):
        out.duration_seconds = int(duration_seconds)
    else:
        out.duration_seconds = Default_Duration_Seconds

    return out

# ################################################################################################################################

def resident_memory_kb(pid:'int') -> 'int':
    """ Returns the resident memory of a process, in kilobytes.
    """
    with open(f'/proc/{pid}/status', encoding='utf8') as status_file:
        lines = status_file.readlines()

    for line in lines:
        if line.startswith(_rss_prefix):
            fields = line.split()
            size = fields[1]
            out = int(size)
            break
    else:
        raise Exception(f'Process {pid} reports no resident memory')

    return out

# ################################################################################################################################
# ################################################################################################################################
