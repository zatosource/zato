# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyYAML
import yaml

# Zato
from live_windows.containers import GuestInfo
from live_windows.enmasse import build_definitions, build_yaml, exchange_connection_name, landing_job_name, \
     ModuleCtx as EnmasseCtx, partner_connection_name, Services
from live_windows.layout import app_folder, Hub, layout_command, local_path, Shares
from live_windows.session import Sequences
from live_windows.settings import Accounts, Versions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The ports the two guests are published on in these tests
    Port_2025 = 10445
    Port_2022 = 20445

    # The schedules of each exchange connection - one per application of the hub, the documents, the shipping notices,
    # the failed trigger files of each of the two label sites, and the two outbound folders of the people share
    Schedule_Count = len(Hub.Apps) + 1 + 1 + 2 + 2

# ################################################################################################################################
# ################################################################################################################################

def _guest(version:'str', port:'int') -> 'GuestInfo':
    out = GuestInfo()
    out.version = version
    out.name = f'guest-{version}'
    out.port = port
    return out

# ################################################################################################################################

def _connection(definitions:'anydict', name:'str') -> 'anydict':
    for connection in definitions['smb']:
        if connection['name'] == name:
            return connection

    raise Exception(f'No connection {name} in {definitions}')

# ################################################################################################################################

def _schedule_names(connection:'anydict') -> 'strlist':
    out:'strlist' = []

    for schedule in connection['schedules']:
        out.append(schedule['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_exchange_connection() -> 'None':
    """ The exchange connection points to the published port of its guest and polls every folder of the layout.
    """
    guest = _guest(Versions.Server_2025, ModuleCtx.Port_2025)

    definitions = build_definitions(guest, guest)
    exchange_name = exchange_connection_name(guest)
    exchange = _connection(definitions, exchange_name)

    assert exchange['port'] == ModuleCtx.Port_2025
    assert exchange['username'] == Accounts.Exchange_Username
    assert exchange['password'] == Accounts.Exchange_Password

    names = _schedule_names(exchange)
    assert len(names) == ModuleCtx.Schedule_Count, names
    assert len(set(names)) == len(names), f'Schedule names repeat -> {names}'

    for app in Hub.Apps:
        assert f'hub.{app}' in names, f'No schedule for {app} -> {names}'

    for schedule in exchange['schedules']:
        assert schedule['should_claim'] is True
        assert schedule['run_every'] == EnmasseCtx.Run_Every
        assert schedule['stability_delay'] == EnmasseCtx.Stability_Delay
        assert schedule['max_attempts'] == EnmasseCtx.Max_Attempts

# ################################################################################################################################

def test_partner_on_other_guest() -> 'None':
    """ The partner connection follows the guest it is given, while the exchange connection stays with its own.
    """
    guest = _guest(Versions.Server_2025, ModuleCtx.Port_2025)
    partner = _guest(Versions.Server_2022, ModuleCtx.Port_2022)

    definitions = build_definitions(guest, partner)

    exchange_name = exchange_connection_name(guest)
    partner_name = partner_connection_name(guest)

    exchange = _connection(definitions, exchange_name)
    partner_connection = _connection(definitions, partner_name)

    assert exchange['port'] == ModuleCtx.Port_2025
    assert partner_connection['port'] == ModuleCtx.Port_2022
    assert 'schedules' not in partner_connection

# ################################################################################################################################

def test_contending_schedule() -> 'None':
    """ The contending schedule polls the same outbox, with the same pattern, as the regular schedule of the plant.
    """
    guest = _guest(Versions.Server_2022, ModuleCtx.Port_2022)

    definitions = build_definitions(guest, guest, has_contending_schedule=True)

    exchange_name = exchange_connection_name(guest)
    exchange = _connection(definitions, exchange_name)

    plant_names = f'hub.{Hub.Plant}', EnmasseCtx.Contending_Schedule
    plant:'anylist' = []

    for schedule in exchange['schedules']:
        if schedule['name'] in plant_names:
            plant.append(schedule)

    assert len(plant) == 2, plant

    first, second = plant
    assert first['directory'] == second['directory']
    assert first['pattern'] == second['pattern']

# ################################################################################################################################

def test_landing_job() -> 'None':
    """ The landing job names the exchange connection of its guest, and it is active only when asked for.
    """
    guest = _guest(Versions.Server_2025, ModuleCtx.Port_2025)

    inactive = build_definitions(guest, guest)
    active = build_definitions(guest, guest, is_landing_active=True)

    job_name = landing_job_name(guest)
    exchange_name = exchange_connection_name(guest)

    for definitions, is_active in (inactive, False), (active, True):

        jobs = definitions['scheduler']
        assert len(jobs) == 1, jobs

        job = jobs[0]
        assert job['name'] == job_name
        assert job['service'] == Services.Landing
        assert job['is_active'] is is_active
        assert job['extra'] == [exchange_name]

# ################################################################################################################################

def test_yaml_round_trip() -> 'None':
    """ The YAML text holds the same definitions as the dictionary it is made of.
    """
    guest = _guest(Versions.Server_2025, ModuleCtx.Port_2025)

    text = build_yaml(guest, guest)
    loaded = yaml.safe_load(text)

    assert sorted(loaded) == ['scheduler', 'smb']
    assert len(loaded['smb']) == 2

# ################################################################################################################################
# ################################################################################################################################

def test_layout_directories() -> 'None':
    """ The layout creates the outbox and the inbox of every application of the hub, and every route ends in an inbox.
    """
    command = layout_command()
    directories = command['directories']

    for app in Hub.Apps:
        for folder in Hub.Outbox, Hub.Inbox:
            path = app_folder(app, folder)
            directory = local_path(Shares.Exchange, path)
            assert directory in directories, f'No directory {directory}'

    for app, destinations in Hub.Routes.items():
        assert app in Hub.Apps, app
        for destination in destinations:
            assert destination in Hub.Apps, f'{app} routes to an unknown application {destination}'

    assert sorted(Hub.Routes) == sorted(Hub.Apps)

# ################################################################################################################################

def test_layout_shares() -> 'None':
    """ Every data share is published, only the landing zone requires encryption, and the harness can reach every share.
    """
    command = layout_command()

    names:'strlist' = []

    for share in command['shares']:
        names.append(share['name'])

        is_encrypted = share['name'] in Shares.Encrypted
        assert share['encrypt'] is is_encrypted, share

        assert Accounts.Exchange_Username in share['change'], share
        assert Accounts.Harness_Username in share['change'], share

    assert sorted(names) == sorted(Shares.All)

# ################################################################################################################################

def test_sequence_names() -> 'None':
    """ Sequence numbers increase across applications and keep the width of the hub.
    """
    sequences = Sequences()

    plant = sequences.next_names(Hub.Plant, 3)
    catalog = sequences.next_names(Hub.Catalog, 2)

    names = plant + catalog
    numbers:'list[int]' = []

    for name in names:
        sequence, _ = name.split('.')
        assert len(sequence) == Hub.Sequence_Digits, name
        numbers.append(int(sequence))

    assert numbers == sorted(numbers)
    assert len(set(numbers)) == len(numbers)

# ################################################################################################################################
# ################################################################################################################################
