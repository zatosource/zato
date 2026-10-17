# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the file transfer demo consists of - its connections, the directories each one polls,
# the four schedule shapes they share, the feeder job and the services, all known up front.

# stdlib
from typing import NamedTuple

# Zato
from zato.common.api import FileTransfer, GENERIC
from zato.common.util.file_transfer_scheduler import get_job_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

connection_spec_list = list['ConnectionSpec']

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The connection types the demo creates
Type_SFTP = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
Type_FTP  = GENERIC.CONNECTION.TYPE.OUTCONN_FTP
Type_SMB  = GENERIC.CONNECTION.TYPE.OUTCONN_SMB

# The four shapes of schedules - every pair of connections has all of them, so the protocols can be compared
Shape_Invoices  = 'invoices'
Shape_Orders    = 'orders'
Shape_Shipments = 'shipments'
Shape_Reports   = 'reports'

# The first connection of each pair polls these ..
Shapes_First = [Shape_Invoices, Shape_Orders]

# .. and the second one polls these.
Shapes_Second = [Shape_Shipments, Shape_Reports]

# The job that keeps dropping new files and the service it invokes share this name
Feeder_Name = 'demo.file-transfer.feed'

# How often the feeder runs, in seconds
Feeder_Interval = 20

# The service each schedule shape invokes for each file
Target_Services = {
    Shape_Invoices:  'demo.file-transfer.invoices',
    Shape_Orders:    'demo.file-transfer.orders',
    Shape_Shipments: 'demo.file-transfer.shipments',
    Shape_Reports:   'demo.file-transfer.reports',
}

# The file in the hot-deployment directory that all the demo services are deployed from
Services_File_Name = 'demo_file_transfer_services.py'

# How far apart the first runs of two consecutive schedules are, in seconds
Schedule_Start_Step = 2

# ################################################################################################################################
# ################################################################################################################################

# What each schedule shape does - which files it takes, how it knows a file is complete,
# what happens to the file afterwards and how often it runs.
_shape_options:'stranydict' = {
    Shape_Invoices: {
        'pattern': '*.csv',
        'ready_how': _scheduler.ReadyHow.Stability,
        'on_success': _scheduler.OnSuccess.Move,
        'run_every': 15,
        'max_attempts': 2,
        'retry_backoff': 10,
    },
    Shape_Orders: {
        'pattern': '*.json',
        'ready_how': _scheduler.ReadyHow.Marker,
        'on_success': _scheduler.OnSuccess.Delete,
        'run_every': 20,
    },
    Shape_Shipments: {
        'pattern': '*.xml',
        'ready_how': _scheduler.ReadyHow.Stability,
        'should_claim': True,
        'on_success': _scheduler.OnSuccess.Move,
        'run_every': 30,
    },
    Shape_Reports: {
        'pattern': '*.txt',
        'ready_how': _scheduler.ReadyHow.Stability,
        'on_success': _scheduler.OnSuccess.Move,
        'run_every': 60,
    },
}

# ################################################################################################################################
# ################################################################################################################################

class ConnectionSpec(NamedTuple):
    """ One demo connection - its name, its type, the account it logs in as and the schedule shapes it polls.
    """
    name: 'str'
    conn_type: 'str'
    account: 'str'
    shapes: 'strlist'

# ################################################################################################################################
# ################################################################################################################################

SFTP_Connections = [
    ConnectionSpec('demo.sftp.acme',   Type_SFTP, 'acme',   Shapes_First),
    ConnectionSpec('demo.sftp.globex', Type_SFTP, 'globex', Shapes_Second),
]

FTP_Connections = [
    ConnectionSpec('demo.ftp.initech',   Type_FTP, 'initech',  Shapes_First),
    ConnectionSpec('demo.ftps.umbrella', Type_FTP, 'umbrella', Shapes_Second),
]

SMB_Connections = [
    ConnectionSpec('demo.smb.hooli', Type_SMB, 'hooli', Shapes_First),
    ConnectionSpec('demo.smb.wonka', Type_SMB, 'wonka', Shapes_Second),
]

All_Connections = SFTP_Connections + FTP_Connections + SMB_Connections

# ################################################################################################################################
# ################################################################################################################################

def get_connection_names(connections:'connection_spec_list') -> 'strlist':
    """ The names of the given demo connections, in order.
    """
    out:'strlist' = []

    for spec in connections:
        out.append(spec.name)

    return out

# ################################################################################################################################

def get_schedule_job_names() -> 'strlist':
    """ The names of the scheduler jobs linked to the demo schedules, one per schedule of each connection.
    """
    out:'strlist' = []

    for spec in All_Connections:
        for shape in spec.shapes:
            job_name = get_job_name(spec.conn_type, spec.name, shape)
            out.append(job_name)

    return out

# ################################################################################################################################

def get_service_names() -> 'strlist':
    """ The names of all the services the demo deploys.
    """
    out = [Feeder_Name]

    for service_name in Target_Services.values():
        out.append(service_name)

    return out

# ################################################################################################################################

def build_schedule(shape:'str', directory:'str', start_date:'str') -> 'stranydict':
    """ The YAML definition of one schedule of the given shape, polling the given directory.
    """
    out:'stranydict' = {
        'name': shape,
        'directory': directory,
        'service': Target_Services[shape],
        'run_unit': _scheduler.Unit.Seconds,
        'start_date': start_date,
    }

    shape_options = _shape_options[shape]
    out.update(shape_options)

    return out

# ################################################################################################################################
# ################################################################################################################################
