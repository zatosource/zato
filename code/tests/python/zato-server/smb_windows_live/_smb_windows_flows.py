# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.layout import app_folder, Hub, local_path, Shares

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from live_windows.progress import Monitor
    from live_windows.session import GuestHandle
    from zato.common.typing_ import anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a test waits after its last file arrived, so that a file processed twice has the time to arrive again, in seconds
    Settle_Seconds = 2

    # The pattern of the files the hub writes into each inbox
    Hub_Pattern = f'*{Hub.Out_Suffix}'

    # The suffixes of the files that exist only while they are written or claimed - by the hub, by the other services,
    # by the producers and by the schedules
    Transient_Suffixes = Hub.Lock_Suffix, '.tmp', '.part', '.processing'

    # The label sites, the queue of each and the prefix of each trigger file, the same as in the labels service
    Label_Sites  = 'site-a', 'site-b'
    Label_Queues = {'site-a': 'DOCKA', 'site-b': 'DOCKB'}
    Label_Prefix = 'LB'

# ################################################################################################################################
# ################################################################################################################################

def file_key(share:'str', folder:'str', name:'str') -> 'str':
    """ Returns the path on the guest of a file, in the form that consumer events are compared in.
    """
    directory = local_path(share, folder)

    out = f'{directory}\\{name}'
    return out

# ################################################################################################################################

def consumed_key(event:'anydict') -> 'str':
    out = f'{event["directory"]}\\{event["name"]}'
    return out

# ################################################################################################################################

def share_path(folder:'str', name:'str') -> 'str':
    """ Returns the path of a file relative to its share, in the form that observer events report it in.
    """
    folder = folder.replace('/', '\\')

    out = f'{folder}\\{name}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def wait_produced(monitor:'Monitor', version:'str', run:'str', count:'int') -> 'strstrdict':
    """ Waits until a guest produced the given number of files in a run and returns the digest of each by its name.
    """
    def _is_done() -> 'bool':
        events = monitor.events(version, 'produced', run)

        out = len(events) >= count
        return out

    monitor.wait_until(_is_done, f'win{version} produced {count} files')

    out:'strstrdict' = {}

    for event in monitor.events(version, 'produced', run):
        out[event['name']] = event['sha256']

    return out

# ################################################################################################################################

def wait_consumed(monitor:'Monitor', version:'str', run:'str', expected:'strstrdict', what:'str') -> 'None':
    """ Waits until the consumers of a guest read each expected file, given as its digest by its consumed_key.
    """
    def _is_done() -> 'bool':

        keys:'strlist' = []

        for event in monitor.events(version, 'consumed', run):
            key = consumed_key(event)
            keys.append(key)

        for key in expected:
            if key not in keys:
                return False

        return True

    count = len(expected)
    monitor.wait_until(_is_done, f'win{version} {what}, {count} files')

# ################################################################################################################################

def assert_consumed_once(monitor:'Monitor', version:'str', run:'str', expected:'strstrdict', what:'str') -> 'None':
    """ Fails unless each expected file was read exactly once, with the content it was produced with, and nothing else was read.
    """
    seen:'strlist' = []

    for event in monitor.events(version, 'consumed', run):

        key = consumed_key(event)

        assert key in expected, f'{what} -> unexpected file {key}'
        assert key not in seen, f'{what} -> file {key} delivered more than once'
        assert event['sha256'] == expected[key], f'{what} -> content of {key} differs from what was produced'

        seen.append(key)

    for key in expected:
        assert key in seen, f'{what} -> file {key} not delivered'

# ################################################################################################################################

def wait_appeared(monitor:'Monitor', version:'str', run:'str', paths:'strlist', what:'str') -> 'None':
    """ Waits until an observer of a guest saw each of the given paths appear.
    """
    def _is_done() -> 'bool':
        appeared = monitor.paths(version, 'appeared', run)

        for path in paths:
            if path not in appeared:
                return False

        return True

    count = len(paths)
    monitor.wait_until(_is_done, f'win{version} {what}, {count} files')

# ################################################################################################################################

def assert_appeared_once(monitor:'Monitor', version:'str', run:'str', paths:'strlist', what:'str') -> 'None':
    appeared = monitor.paths(version, 'appeared', run)

    for path in paths:
        count = appeared.count(path)
        assert count == 1, f'{what} -> {path} appeared {count} times'

# ################################################################################################################################

def assert_nothing_under(monitor:'Monitor', version:'str', run:'str', prefix:'str', what:'str') -> 'None':
    """ Fails if an observer of a guest saw any file appear under the given path.
    """
    for path in monitor.paths(version, 'appeared', run):
        assert not path.startswith(prefix), f'{what} -> unexpected file {path}'

# ################################################################################################################################

def assert_no_leftovers(monitor:'Monitor', version:'str', run:'str', what:'str') -> 'None':
    """ Fails if an observer of a guest saw a temporary or a claimed file appear that did not disappear again.
    """
    disappeared = monitor.paths(version, 'disappeared', run)

    for path in monitor.paths(version, 'appeared', run):
        if path.endswith(ModuleCtx.Transient_Suffixes):
            assert path in disappeared, f'{what} -> {path} was left behind'

# ################################################################################################################################
# ################################################################################################################################

def hub_outbox(app:'str') -> 'str':
    out = app_folder(app, Hub.Outbox)
    return out

# ################################################################################################################################

def hub_processed_path(app:'str', name:'str') -> 'str':
    outbox = hub_outbox(app)
    folder = f'{outbox}/{Hub.Processed}'

    out = share_path(folder, name)
    return out

# ################################################################################################################################

def hub_rejected_path(app:'str', name:'str') -> 'str':
    outbox = hub_outbox(app)
    folder = f'{outbox}/{Hub.Rejected}'

    out = share_path(folder, name)
    return out

# ################################################################################################################################

def hub_processed_paths(sources:'strstrdict') -> 'strlist':
    """ Returns where each file of an outbox goes once the hub processed it, given the files by their names.
    """
    out:'strlist' = []

    for name in sources:
        app = name.split('.')[1]
        path = hub_processed_path(app, name)
        out.append(path)

    return out

# ################################################################################################################################

def hub_expected(sources:'strstrdict') -> 'strstrdict':
    """ Returns the digest of each file the hub writes into the inboxes, by its consumed_key,
    given the files the applications wrote into their outboxes, by their names.
    """
    out:'strstrdict' = {}

    for name, digest in sources.items():

        sequence, app = name.split('.')
        routed_name = f'{app}.{sequence}{Hub.Out_Suffix}'

        for destination in Hub.Routes[app]:
            inbox = app_folder(destination, Hub.Inbox)
            key = file_key(Shares.Exchange, inbox, routed_name)
            out[key] = digest

    return out

# ################################################################################################################################

def start_hub(handle:'GuestHandle', run:'str', apps:'strlist') -> 'None':
    """ Starts an observer of the exchange share and a consumer of the inbox of each application
    that the given applications send their files to.
    """
    _ = handle.observe(run, Shares.Exchange)

    destinations:'strlist' = []

    for app in apps:
        for destination in Hub.Routes[app]:
            if destination not in destinations:
                destinations.append(destination)

    for destination in destinations:
        inbox = app_folder(destination, Hub.Inbox)
        _ = handle.consume(run, Shares.Exchange, inbox, ModuleCtx.Hub_Pattern)

# ################################################################################################################################

def verify_hub(monitor:'Monitor', version:'str', run:'str', sources:'strstrdict', what:'str') -> 'None':
    """ Waits until each file of the outboxes was routed to its inboxes and moved to its processed directory,
    then lets a file processed twice arrive again and fails if any was.
    """
    expected = hub_expected(sources)
    processed = hub_processed_paths(sources)

    wait_consumed(monitor, version, run, expected, f'{what} routed')
    wait_appeared(monitor, version, run, processed, f'{what} moved to processed')

    monitor.pause(ModuleCtx.Settle_Seconds)

    assert_consumed_once(monitor, version, run, expected, what)
    assert_appeared_once(monitor, version, run, processed, what)
    assert_no_leftovers(monitor, version, run, what)

# ################################################################################################################################
# ################################################################################################################################

def document_name(number:'int', when:'datetime') -> 'str':
    """ Returns the name of a document, which ends with its date and time, e.g. DOC1001-2026-11-17-181500.xml.
    """
    stamp = when.strftime('%Y-%m-%d-%H%M%S')

    out = f'DOC{number}-{stamp}.xml'
    return out

# ################################################################################################################################

def archive_path(name:'str', when:'datetime') -> 'str':
    """ Returns where a document is stored in the archive share, in a directory of its date.
    """
    folder = when.strftime('%Y/%m/%d')

    out = share_path(folder, name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def shipment_name(number:'int') -> 'str':
    out = f'SHP{number}.txt'
    return out

# ################################################################################################################################

def label_site(number:'int') -> 'str':
    """ Returns the site that ships a job - even jobs ship from the first site.
    """
    index = number % 2

    out = ModuleCtx.Label_Sites[index]
    return out

# ################################################################################################################################

def label_name(number:'int') -> 'str':
    site = label_site(number)
    queue = ModuleCtx.Label_Queues[site]

    out = f'{ModuleCtx.Label_Prefix}{queue}_{number}.csv'
    return out

# ################################################################################################################################
# ################################################################################################################################
