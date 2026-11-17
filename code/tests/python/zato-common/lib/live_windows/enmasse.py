# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# PyYAML
import yaml

# Zato
from live_windows.layout import app_folder, Folders, Hub, remote_path, Shares
from live_windows.settings import Accounts

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.containers import GuestInfo
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class Services:

    # The services the schedules and the job invoke
    Route          = 'file-exchange.route'
    Documents      = 'file-exchange.documents'
    Labels         = 'file-exchange.labels'
    Label_Failures = 'file-exchange.label-failures'
    Landing        = 'file-exchange.landing-extract'
    Relay          = 'file-exchange.relay'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The host the published ports of the guests listen on
    Host = '127.0.0.1'

    # How often each schedule polls its directory, in seconds
    Run_Every = 1

    # How long a file must stay unchanged before it is picked up, in seconds
    Stability_Delay = 1

    # How often the landing zone job writes an extract, in seconds
    Landing_Every = 2

    # Each file that cannot be processed is quarantined after this many attempts
    Max_Attempts = 1

# ################################################################################################################################
# ################################################################################################################################

def exchange_connection_name(guest:'GuestInfo') -> 'str':
    out = f'exchange.win{guest.version}'
    return out

# ################################################################################################################################

def partner_connection_name(guest:'GuestInfo') -> 'str':
    out = f'partner.win{guest.version}'
    return out

# ################################################################################################################################

def landing_job_name(guest:'GuestInfo') -> 'str':
    out = f'file-exchange.landing.win{guest.version}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def _schedule(
    name:'str',
    directory:'str',
    service:'str',
    pattern:'str',
    start_date:'str',
    *,
    move_directory:'str'=Hub.Processed,
    ) -> 'anydict':
    """ Returns one schedule that claims each file, hands it to a service, and moves it away once processed,
    or into the quarantine directory once it could not be.
    """
    out = {
        'name': name,
        'directory': directory,
        'service': service,
        'pattern': pattern,
        'ready_how': 'stability',
        'stability_delay': ModuleCtx.Stability_Delay,
        'should_claim': True,
        'on_success': 'move',
        'move_directory': move_directory,
        'max_attempts': ModuleCtx.Max_Attempts,
        'quarantine_directory': Hub.Rejected,
        'run_every': ModuleCtx.Run_Every,
        'run_unit': 'seconds',
        'start_date': start_date,
    }

    return out

# ################################################################################################################################

def _schedules(start_date:'str') -> 'anylist':
    """ Returns every schedule of an exchange connection.
    """
    out:'anylist' = []

    # Each application's outbox in the hub ..
    for app in Hub.Apps:
        name = f'hub.{app}'
        pattern = f'*.{app}'
        folder = app_folder(app, Hub.Outbox)
        directory = remote_path(Shares.Exchange, folder)
        schedule = _schedule(name, directory, Services.Route, pattern, start_date)
        out.append(schedule)

    # .. the documents to distribute ..
    directory = remote_path(Shares.Documents, Folders.Documents_Outbox)
    schedule = _schedule('documents', directory, Services.Documents, 'DOC*.xml', start_date)
    out.append(schedule)

    # .. the shipment notices ..
    directory = remote_path(Shares.Shipping, Folders.Shipping_Outbox)
    schedule = _schedule('shipping', directory, Services.Labels, 'SHP*.txt', start_date)
    out.append(schedule)

    # .. the label trigger files that could not be printed ..
    for site in Folders.Label_Sites:
        name = f'labels.{site}.failed'
        directory = remote_path(Shares.Labels, site)
        schedule = _schedule(
            name, directory, Services.Label_Failures, '*.failed', start_date, move_directory=Folders.Label_Failed)
        out.append(schedule)

    # .. and the outbound folders of the HR and ERP applications.
    for folder in Folders.HR_Outbound, Folders.ERP_Outbound:
        name = f'people.{folder}'
        directory = remote_path(Shares.People, folder)
        schedule = _schedule(name, directory, Services.Relay, '*', start_date)
        out.append(schedule)

    return out

# ################################################################################################################################

def _connection(name:'str', port:'int', schedules:'anylist') -> 'anydict':

    out:'anydict' = {
        'name': name,
        'host': ModuleCtx.Host,
        'port': port,
        'username': Accounts.Exchange_Username,
        'password': Accounts.Exchange_Password,
    }

    if schedules:
        out['schedules'] = schedules

    return out

# ################################################################################################################################

def build_definitions(
    guest:'GuestInfo',
    partner:'GuestInfo',
    *,
    password:'str'=Accounts.Exchange_Password,
    is_landing_active:'bool'=False,
    ) -> 'anydict':
    """ Returns the enmasse definitions through which Zato reaches one guest - the exchange connection with its schedules,
    the connection to the partner drop, which may be on another guest, and the job that writes to the landing zone.
    """
    now = datetime.now(timezone.utc)
    start_date = now.isoformat()

    schedules = _schedules(start_date)

    exchange_name = exchange_connection_name(guest)
    partner_name = partner_connection_name(guest)

    exchange = _connection(exchange_name, guest.port, schedules)
    exchange['password'] = password

    partner_connection = _connection(partner_name, partner.port, [])

    landing_name = landing_job_name(guest)

    landing_job = {
        'name': landing_name,
        'service': Services.Landing,
        'job_type': 'interval_based',
        'start_date': start_date,
        'seconds': ModuleCtx.Landing_Every,
        'is_active': is_landing_active,
        'extra': [exchange_name],
    }

    out = {
        'smb': [exchange, partner_connection],
        'scheduler': [landing_job],
    }

    return out

# ################################################################################################################################

def build_yaml(
    guest:'GuestInfo',
    partner:'GuestInfo',
    *,
    password:'str'=Accounts.Exchange_Password,
    is_landing_active:'bool'=False,
    ) -> 'str':
    """ Returns the definitions of build_definitions as the text of an enmasse file.
    """
    definitions = build_definitions(guest, partner, password=password, is_landing_active=is_landing_active)

    out = yaml.safe_dump(definitions, sort_keys=False)
    return out

# ################################################################################################################################
# ################################################################################################################################
