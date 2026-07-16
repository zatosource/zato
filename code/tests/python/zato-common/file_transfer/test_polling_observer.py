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
from base64 import b64decode
from json import loads
from typing import NamedTuple

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.file_transfer.listener import watch_directory

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from watchdog.observers.api import BaseObserver
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long to wait, in total, for a deployment to be reported
_deploy_timeout = 10.0

# How often to check whether a deployment was reported
_check_interval = 0.2

# How long to wait after starting an observer so its baseline snapshot is taken
_observer_warmup = 1.5

# The URL template the listener posts deployments to - never actually connected to in these tests
_invoke_url = 'http://localhost:17010/zato/api/invoke/{}'

# The name of the symlink kubelet points at the current data directory
_data_link_name = '..data'

# ################################################################################################################################
# ################################################################################################################################

class _Deployment(NamedTuple):
    name: str
    content: str

# ################################################################################################################################
# ################################################################################################################################

class _StubResponse(NamedTuple):
    ok: bool

# ################################################################################################################################
# ################################################################################################################################

deployment_list = list['_Deployment']

# ################################################################################################################################
# ################################################################################################################################

class _RecordingSession:
    """ Stands in for a requests session and records every deployment the listener attempts.
    """
    def __init__(self) -> 'None':
        self.deployments:'deployment_list' = []

# ################################################################################################################################

    def post(self, url:'str', data:'str') -> '_StubResponse':

        # Decode the request the same way the server would ..
        request = loads(data)
        payload = b64decode(request['payload']).decode('utf8')

        # .. and store it for the tests to assert on.
        deployment = _Deployment(request['payload_name'], payload)
        self.deployments.append(deployment)

        out = _StubResponse(ok=True)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _write_file(path:'str', content:'str') -> 'None':
    with open(path, 'w') as file_object:
        _ = file_object.write(content)

# ################################################################################################################################
# ################################################################################################################################

def _create_configmap_volume(volume_directory:'str', file_name:'str', content:'str') -> 'None':
    """ Lays out a directory the way kubelet lays out a ConfigMap volume - the real file lives in a hidden,
    timestamped data directory, a '..data' symlink points to that directory, and the visible file name
    is a symlink through '..data'.
    """
    # Create the hidden data directory with the real file ..
    data_directory_name = '..data_' + CryptoManager.generate_hex_string()
    data_directory = os.path.join(volume_directory, data_directory_name)
    os.mkdir(data_directory)

    file_path = os.path.join(data_directory, file_name)
    _write_file(file_path, content)

    # .. point '..data' at it ..
    data_link = os.path.join(volume_directory, _data_link_name)
    os.symlink(data_directory_name, data_link)

    # .. and expose the visible file name through '..data'.
    visible_path = os.path.join(volume_directory, file_name)
    relative_target = os.path.join(_data_link_name, file_name)
    os.symlink(relative_target, visible_path)

# ################################################################################################################################
# ################################################################################################################################

def _update_by_symlink_swap(volume_directory:'str', file_name:'str', content:'str') -> 'None':
    """ Updates the file's content the way kubelet's atomic writer does it - a new hidden data directory is written
    in full, then the '..data' symlink is repointed at it with one atomic rename, then the old directory is removed.
    The visible file is never written to directly, which is exactly what inotify cannot see.
    """
    data_link = os.path.join(volume_directory, _data_link_name)
    old_data_directory_name = os.readlink(data_link)

    # Write the new hidden data directory in full ..
    new_data_directory_name = '..data_' + CryptoManager.generate_hex_string()
    new_data_directory = os.path.join(volume_directory, new_data_directory_name)
    os.mkdir(new_data_directory)

    file_path = os.path.join(new_data_directory, file_name)
    _write_file(file_path, content)

    # .. repoint '..data' at it with one atomic rename ..
    temporary_link = os.path.join(volume_directory, _data_link_name + '_tmp')
    os.symlink(new_data_directory_name, temporary_link)
    os.rename(temporary_link, data_link)

    # .. and remove the previous data directory, again the way kubelet does it.
    old_data_directory = os.path.join(volume_directory, old_data_directory_name)
    shutil.rmtree(old_data_directory)

# ################################################################################################################################
# ################################################################################################################################

def _start_polling_observer(volume_directory:'str', recording_session:'any_') -> 'BaseObserver':
    """ Starts the listener's polling observer over the given directory and waits until its baseline snapshot exists,
    so that only later changes produce events.
    """
    observer = watch_directory(
        volume_directory,
        [volume_directory],
        session=recording_session,
        invoke_url=_invoke_url,
        event_types=None,
        file_patterns=None,
        observer_type='polling',
    )
    observer.start()

    # Let the observer take its baseline snapshot before the test changes anything
    time.sleep(_observer_warmup)

    return observer

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_deployment(recording_session:'any_', file_path:'str', content:'str') -> 'bool':
    """ Waits until the listener deploys the given path with the given content.
    """
    deadline = time.monotonic() + _deploy_timeout

    # Keep checking until the deployment shows up or we run out of time ..
    while time.monotonic() < deadline:
        for deployment in recording_session.deployments:
            if deployment.name == file_path:
                if deployment.content == content:
                    return True
        time.sleep(_check_interval)

    # .. nothing matched within the timeout.
    return False

# ################################################################################################################################
# ################################################################################################################################

def test_symlink_swap_deploys_enmasse_file() -> 'None':
    """ An enmasse file updated through a ConfigMap-style symlink swap is deployed with its new content.
    """
    initial_content = '''channel_rest:
  - name: "orders.channel"
    service: "orders.get-list"
    url_path: "/orders"
    security: "anonymous"
'''

    updated_content = '''channel_rest:
  - name: "orders.channel"
    service: "orders.get-list"
    url_path: "/orders/v2"
    security: "anonymous"
'''

    volume_directory = tempfile.mkdtemp(prefix='zato_test_configmap_')
    file_name = 'enmasse.yaml'

    _create_configmap_volume(volume_directory, file_name, initial_content)

    recording_session = _RecordingSession()
    observer = _start_polling_observer(volume_directory, recording_session)

    try:
        # Update the file the way kubelet does it ..
        _update_by_symlink_swap(volume_directory, file_name, updated_content)

        # .. and confirm the listener deployed the visible path with the new content.
        visible_path = os.path.join(volume_directory, file_name)
        was_deployed = _wait_for_deployment(recording_session, visible_path, updated_content)

        assert was_deployed, f'Expected {visible_path} to be deployed with updated content, got: {recording_session.deployments}'

    finally:
        observer.stop()
        observer.join()
        shutil.rmtree(volume_directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

def test_symlink_swap_deploys_service_file() -> 'None':
    """ A Python service file updated through a ConfigMap-style symlink swap is deployed with its new content.
    """
    initial_content = '''
from zato.server.service import Service

class GetOrderStatus(Service):
    name = 'orders.get-status'

    def handle(self):
        self.response.payload = 'status-initial'
'''

    updated_content = '''
from zato.server.service import Service

class GetOrderStatus(Service):
    name = 'orders.get-status'

    def handle(self):
        self.response.payload = 'status-updated'
'''

    volume_directory = tempfile.mkdtemp(prefix='zato_test_configmap_')
    file_name = 'order_status.py'

    _create_configmap_volume(volume_directory, file_name, initial_content)

    recording_session = _RecordingSession()
    observer = _start_polling_observer(volume_directory, recording_session)

    try:
        # Update the file the way kubelet does it ..
        _update_by_symlink_swap(volume_directory, file_name, updated_content)

        # .. and confirm the listener deployed the visible path with the new content.
        visible_path = os.path.join(volume_directory, file_name)
        was_deployed = _wait_for_deployment(recording_session, visible_path, updated_content)

        assert was_deployed, f'Expected {visible_path} to be deployed with updated content, got: {recording_session.deployments}'

    finally:
        observer.stop()
        observer.join()
        shutil.rmtree(volume_directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

def test_direct_write_deploys_file() -> 'None':
    """ A file written directly into a watched directory is deployed under the polling observer,
    the same as it would be under inotify.
    """
    service_content = '''
from zato.server.service import Service

class GetInvoiceDetails(Service):
    name = 'invoices.get-details'

    def handle(self):
        self.response.payload = 'invoice-details'
'''

    watched_directory = tempfile.mkdtemp(prefix='zato_test_direct_write_')

    recording_session = _RecordingSession()
    observer = _start_polling_observer(watched_directory, recording_session)

    try:
        # Write the file directly, no symlinks involved ..
        file_path = os.path.join(watched_directory, 'invoice_details.py')
        _write_file(file_path, service_content)

        # .. and confirm the listener deployed it.
        was_deployed = _wait_for_deployment(recording_session, file_path, service_content)

        assert was_deployed, f'Expected {file_path} to be deployed, got: {recording_session.deployments}'

    finally:
        observer.stop()
        observer.join()
        shutil.rmtree(watched_directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
