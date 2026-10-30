# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
import time
from json import loads
from typing import NamedTuple

# pytest
import pytest

# Zato
from zato.common.file_transfer.listener import TLS_Material_Patterns, TLSMaterialEventHandler, watch_directory

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from watchdog.observers.api import BaseObserver
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long to wait, in total, for a file to be reported
_report_timeout = 10.0

# How often to check whether a file was reported
_check_interval = 0.2

# How long to wait after starting an observer so that it is watching before the test changes anything
_observer_warmup = 1.5

# The URL template the listener posts to - never actually connected to in these tests
_invoke_url = 'http://localhost:17010/zato/api/invoke/{}'

# Each test runs with the observer the image uses by default and with the one Kubernetes needs
_observer_types = ['inotify', 'polling']

# ################################################################################################################################
# ################################################################################################################################

class _StubResponse(NamedTuple):
    ok: bool

# ################################################################################################################################
# ################################################################################################################################

request_list = list['anydict']

# ################################################################################################################################
# ################################################################################################################################

class _RecordingSession:
    """ Stands in for a requests session and records every request the listener sends.
    """
    def __init__(self) -> 'None':
        self.requests:'request_list' = []

# ################################################################################################################################

    def post(self, url:'str', data:'str') -> '_StubResponse':
        request = loads(data)
        self.requests.append(request)

        out = _StubResponse(ok=True)
        return out

# ################################################################################################################################

    def get_reported_paths(self) -> 'strlist':
        out:'strlist' = []
        for request in self.requests:
            out.append(request['payload_name'])
        return out

# ################################################################################################################################
# ################################################################################################################################

def _write_file(path:'str', content:'str') -> 'None':
    with open(path, 'w') as file_object:
        _ = file_object.write(content)

# ################################################################################################################################

def _start_observer(watched_directory:'str', recording_session:'_RecordingSession', observer_type:'str') -> 'BaseObserver':
    """ Starts the listener in TLS material mode over the given directory.
    """
    observer = watch_directory(
        watched_directory,
        [watched_directory],
        session=recording_session, # type: ignore
        invoke_url=_invoke_url,
        event_types=None,
        file_patterns=TLS_Material_Patterns,
        observer_type=observer_type,
        handler_class=TLSMaterialEventHandler,
    )
    observer.start()

    # Let the observer start watching before the test changes anything
    time.sleep(_observer_warmup)

    return observer

# ################################################################################################################################

def _wait_for_report(recording_session:'_RecordingSession', file_path:'str') -> 'bool':
    """ Waits until the listener reports the given path.
    """
    deadline = time.monotonic() + _report_timeout

    # Keep checking until the path is reported or we run out of time ..
    while time.monotonic() < deadline:
        if file_path in recording_session.get_reported_paths():
            return True
        time.sleep(_check_interval)

    # .. nothing was reported within the timeout.
    return False

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('observer_type', _observer_types)
def test_nested_pem_is_reported_by_path_only(observer_type:'str') -> 'None':
    """ A certificate written into a subdirectory of the watched directory is reported by its path,
    and the request does not contain the file's contents.
    """
    watched_directory = tempfile.mkdtemp(prefix='zato_test_tls_material_')

    nested_directory = os.path.join(watched_directory, 'outgoing', 'crm')
    os.makedirs(nested_directory)

    recording_session = _RecordingSession()
    observer = _start_observer(watched_directory, recording_session, observer_type)

    try:
        file_path = os.path.join(nested_directory, 'client-cert.pem')
        _write_file(file_path, '-----BEGIN CERTIFICATE-----\n')

        was_reported = _wait_for_report(recording_session, file_path)
        assert was_reported, f'Expected {file_path} to be reported, got: {recording_session.requests}'

        # Each request names the file and nothing else
        for request in recording_session.requests:
            assert request == {'payload_name': file_path}, f'Unexpected request: {request}'

    finally:
        observer.stop()
        observer.join()
        shutil.rmtree(watched_directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('observer_type', _observer_types)
def test_other_files_are_not_reported(observer_type:'str') -> 'None':
    """ Files that are not PEM files are not reported, even when they are services or enmasse files.
    """
    watched_directory = tempfile.mkdtemp(prefix='zato_test_tls_material_')

    recording_session = _RecordingSession()
    observer = _start_observer(watched_directory, recording_session, observer_type)

    try:
        other_paths = [
            os.path.join(watched_directory, 'my_service.py'),
            os.path.join(watched_directory, 'enmasse.yaml'),
            os.path.join(watched_directory, 'client.key'),
        ]

        for other_path in other_paths:
            _write_file(other_path, 'abc')

        # A PEM file written after the others is a marker that every earlier change was processed
        marker_path = os.path.join(watched_directory, 'marker.pem')
        _write_file(marker_path, '-----BEGIN CERTIFICATE-----\n')

        was_reported = _wait_for_report(recording_session, marker_path)
        assert was_reported, f'Expected {marker_path} to be reported, got: {recording_session.requests}'

        reported_paths = recording_session.get_reported_paths()

        for other_path in other_paths:
            assert other_path not in reported_paths, f'Did not expect {other_path} to be reported'

    finally:
        observer.stop()
        observer.join()
        shutil.rmtree(watched_directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('observer_type', _observer_types)
def test_rename_into_place_is_reported(observer_type:'str') -> 'None':
    """ A certificate replaced by a rename into place, the way renewal tools replace it, is reported by its final path.
    """
    watched_directory = tempfile.mkdtemp(prefix='zato_test_tls_material_')

    # The certificate exists before the listener starts ..
    file_path = os.path.join(watched_directory, 'client-cert.pem')
    _write_file(file_path, '-----BEGIN CERTIFICATE-----\nfirst\n')

    recording_session = _RecordingSession()
    observer = _start_observer(watched_directory, recording_session, observer_type)

    try:
        # .. its successor is written under a name that the listener ignores ..
        temporary_path = file_path + '.tmp'
        _write_file(temporary_path, '-----BEGIN CERTIFICATE-----\nsecond\n')

        # .. and renamed over it.
        os.replace(temporary_path, file_path)

        was_reported = _wait_for_report(recording_session, file_path)
        assert was_reported, f'Expected {file_path} to be reported, got: {recording_session.requests}'

        reported_paths = recording_session.get_reported_paths()
        assert temporary_path not in reported_paths, f'Did not expect {temporary_path} to be reported'

    finally:
        observer.stop()
        observer.join()
        shutil.rmtree(watched_directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
