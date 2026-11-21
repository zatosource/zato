# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import time
from urllib.parse import parse_qs, urlparse

# psutil
import psutil

# PyYAML
import yaml

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import PublishClient, PullClient
from zato.common.test.playwright_pubsub import create_basic_auth, create_permission_with_two_patterns, create_topic, \
    navigate_to_page, open_edit_dialog, open_publish_overlay, open_subscription_create_dialog, pick_subscription_topic, \
    select_subscription_create_option, subscription_create_field_selector, submit_edit_form, \
    submit_subscription_create_dialog
from zato.common.test.pubsub_database import connect, get_db_mode, is_postgresql_mode
from zato.server.arbiter_config_process import ConfigProcessCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anydict, anylist, callable_, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    Page = Page
    PubSubDatabase = PubSubDatabase
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The pages of Dashboard that the suite reads and changes
    Subscription_Page = '/zato/pubsub/subscription/'
    Topic_Page        = '/zato/pubsub/topic/'

    # The link of a subscription row to the queue browser of its subscriber, and the states the queue browser shows
    Queue_Link          = 'a[href^="/zato/pubsub/subscription/queue/"]'
    Queue_State_Pending = 'state=pending'
    Queue_State_All     = 'state=all'
    Queue_Body          = '#messages-body'

    # The statuses of a pair of the subscription list
    Status_Confirmed       = 'confirmed'
    Status_Pending         = 'pending'
    Status_Pending_Removal = 'pending-removal'

    # How long a condition that the suite waits for may take to hold, in seconds, and how often it is checked
    Wait_Timeout  = 120.0
    Poll_Interval = 1.0

    # How long a dialog may take to open or to close, in milliseconds
    Dialog_Timeout = 15000

    # How long a publication from the topic page may take, in milliseconds, which covers a wait behind a lock
    Publish_Timeout = 60000

    # How long a publication is given to reach the lock that holds it, in seconds
    Publish_Hold_Seconds = 1.0

    # The beginning of the status line of the publish overlay after an accepted publication
    Publish_Accepted = '200'

    # How long one REST call of a publisher or a subscriber may take, in seconds
    Client_Timeout = 60.0

    # The topics of the client of each test match this pattern under the prefix of the test
    Topic_Pattern = 'topic.*'

    # The topic checkboxes of the edit form of a subscription
    Edit_Topics = '#id_edit-multi-select-div'

    # The states of a topic checkbox, which has three, and how many clicks pass through all of them
    Topic_On  = 'on'
    Topic_Off = 'off'
    Tri_State_Clicks = 3

    # The message that Dashboard shows when a save fails
    User_Message_Failure = '#user-message.user-message-failure'

    # The length of the random part of each name of a test
    Name_Hex_Length = 32

    # The delivery type of a pull subscriber
    Delivery_Pull = 'pull'

    # The markers the server writes for each enmasse import that it runs
    Marker_Started   = 'Invoking command'
    Marker_Import    = '--import'
    Marker_Completed = 'Enmasse stderr'
    Marker_Failed    = 'Enmasse import failed'

    Log_Path = os.path.join('logs', 'server.log')
    Pickup_Path = os.path.join('pickup', 'incoming', 'services')

    # The table of PostgreSQL that holds the rows of the pairs, locked against writes by the write lock of the suite
    Table_Lock_Statement = 'lock table pubsub_topic_sub in exclusive mode'

# ################################################################################################################################
# ################################################################################################################################

_pair_status_script = """
(item_id) => {
    const row = document.getElementById('tr_' + item_id);
    if (row === null) {
        return null;
    }
    const out = {};
    for (const link of row.querySelectorAll('a[href^="/zato/pubsub/topic/?query="]')) {
        const next = link.nextElementSibling;
        let status = 'confirmed';
        if (next !== null) {
            if (next.classList.contains('ps-pair-status')) {
                status = next.textContent;
            }
        }
        out[link.textContent] = status;
    }
    return out;
}
"""

_queue_previews_script = """
() => {
    const out = [];
    for (const cell of document.querySelectorAll('#messages-body td.data-preview')) {
        out.push(cell.textContent);
    }
    return out;
}
"""

_topic_state_script = """
(element) => {
    if (element.checked) {
        return 'on';
    }
    if (element.classList.contains('indeterminate')) {
        return 'partial';
    }
    return 'off';
}
"""

_publish_completed_script = """
() => {
    const status = document.querySelector('#invoker-modal-status');
    if (status === null) {
        return false;
    }
    const text = status.textContent.trim();
    if (text.length === 0) {
        return false;
    }
    return text.indexOf('Invoking') === -1;
}
"""

_set_payload_script = '(value) => $.fn.zato.invoker._request_pane.setValue(value)'

# ################################################################################################################################
# ################################################################################################################################

def wait_for(check:'callable_', what:'str', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'None':
    """ Polls a check until it returns True and raises once the timeout passes.
    """
    deadline = time.monotonic() + timeout

    while not check():
        if time.monotonic() > deadline:
            raise Exception(f'{what} did not happen within {timeout}s')
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def is_postgresql() -> 'bool':
    """ Whether the suite runs on PostgreSQL.
    """
    mode = get_db_mode()

    out = is_postgresql_mode(mode)
    return out

# ################################################################################################################################

def new_prefix(label:'str') -> 'str':
    """ Returns the prefix of the names of the objects of one test.
    """
    suffix = CryptoManager.generate_hex_string(ModuleCtx.Name_Hex_Length)

    out = f'ui.{label}.{suffix}.'
    return out

# ################################################################################################################################

def new_marker(label:'str') -> 'str':
    """ Returns a message payload that no other message of the suite carries.
    """
    suffix = CryptoManager.generate_hex_string(ModuleCtx.Name_Hex_Length)

    out = f'marker.{label}.{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TableWriteLock:
    """ Holds a lock of the table of pairs on PostgreSQL that lets no other session write to it or lock its rows.
    """

    def __init__(self, database:'PubSubDatabase') -> 'None':
        self.database = database
        self._connection:'any_' = None

    def acquire(self) -> 'None':
        self._connection = connect(self.database)
        cursor = self._connection.cursor()
        cursor.execute(ModuleCtx.Table_Lock_Statement)

    def release(self) -> 'None':
        if self._connection is None:
            return

        self._connection.rollback()
        self._connection.close()
        self._connection = None

# ################################################################################################################################

class RowLock:
    """ Holds a lock on the rows that one statement selects for update, from a session of the test.
    """

    def __init__(self, database:'PubSubDatabase', statement:'str', params:'anylist') -> 'None':
        self.database = database
        self.statement = statement
        self.params = params
        self._connection:'any_' = None

    def acquire(self) -> 'None':
        self._connection = connect(self.database)
        cursor = self._connection.cursor()
        cursor.execute(self.statement, self.params)

    def release(self) -> 'None':
        if self._connection is None:
            return

        self._connection.rollback()
        self._connection.close()
        self._connection = None

# ################################################################################################################################
# ################################################################################################################################

class Pickup:
    """ Places enmasse files in the pickup directory of the server and waits for the server to import each one.
    """

    def __init__(self, server_dir:'str') -> 'None':
        self.pickup_dir = os.path.join(server_dir, ModuleCtx.Pickup_Path)
        self.log_path = os.path.join(server_dir, ModuleCtx.Log_Path)

    def count_markers(self) -> 'tuple[int, int, int]':
        """ How many enmasse imports the log of the server says started, completed and failed.
        """
        started = 0
        completed = 0
        failed = 0

        with open(self.log_path) as log_file:
            content = log_file.read()

        for line in content.splitlines():
            if ModuleCtx.Marker_Started in line:
                if ModuleCtx.Marker_Import in line:
                    started += 1
            elif ModuleCtx.Marker_Completed in line:
                completed += 1
            elif ModuleCtx.Marker_Failed in line:
                failed += 1

        out = started, completed, failed
        return out

    def apply(self, file_name:'str', definitions:'str') -> 'None':
        """ Writes an enmasse file into the pickup directory and waits for the import to complete.
        """
        _, completed_before, failed_before = self.count_markers()
        path = os.path.join(self.pickup_dir, file_name)

        with open(path, 'w') as enmasse_file:
            _ = enmasse_file.write(definitions)

        def _is_imported() -> 'bool':
            started, completed, failed = self.count_markers()

            if failed > failed_before:
                raise Exception(f'The server could not import {file_name}, see {self.log_path}')

            if completed > completed_before:
                out = started == completed
            else:
                out = False

            return out

        wait_for(_is_imported, f'The import of {file_name}')

# ################################################################################################################################

def yaml_subscription(security_name:'str', topic_names:'strlist') -> 'str':
    """ Returns an enmasse file that subscribes a pull subscriber to exactly the given topics.
    """
    definition = {
        'pubsub_subscription': [{
            'security': security_name,
            'delivery_type': ModuleCtx.Delivery_Pull,
            'topic_list': topic_names,
        }],
    }

    out = yaml.dump(definition)
    return out

# ################################################################################################################################
# ################################################################################################################################

def create_client(page:'Page', base_url:'str', prefix:'str', suffix:'str') -> 'anydict':
    """ Creates an API client that may publish and subscribe to each topic under the prefix.
    """
    out = create_basic_auth(page, base_url, prefix, suffix)
    pattern = prefix + ModuleCtx.Topic_Pattern

    _ = create_permission_with_two_patterns(page, base_url, out['name'], pattern, pattern)

    return out

# ################################################################################################################################

def create_topics(page:'Page', base_url:'str', prefix:'str', count:'int') -> 'anylist':
    """ Creates topics under the prefix, each matching the pattern of the clients of the test.
    """
    topic_prefix = prefix + 'topic.'
    out:'anylist' = []

    for index in range(count):
        suffix = f'{index}'
        topic = create_topic(page, base_url, topic_prefix, suffix)
        out.append(topic)

    return out

# ################################################################################################################################

def create_pull_subscription_to(page:'Page', base_url:'str', sec_name:'str', topic_names:'strlist') -> 'None':
    """ Creates a pull subscription of an API client to each of the topics.
    """
    open_subscription_create_dialog(page, base_url)
    select_subscription_create_option(page, 'client', sec_name)

    delivery_selector = subscription_create_field_selector('delivery')
    _ = page.select_option(delivery_selector, value=ModuleCtx.Delivery_Pull)

    for topic_name in topic_names:
        pick_subscription_topic(page, topic_name)

    submit_subscription_create_dialog(page)

# ################################################################################################################################
# ################################################################################################################################

def subscription_item_id(page:'Page', base_url:'str', link_text:'str') -> 'str':
    """ Returns the ID of the subscription whose row links to the subscriber of the given name.
    """
    navigate_to_page(page, base_url, ModuleCtx.Subscription_Page)

    row_selector = f'#data-table tbody tr:has(td:has(a:text-is("{link_text}")))'
    row = page.wait_for_selector(row_selector, state='attached', timeout=ModuleCtx.Dialog_Timeout)

    if row is None:
        raise Exception(f'There is no subscription of {link_text}')

    row_id = row.get_attribute('id')

    if row_id is None:
        raise Exception(f'The subscription row of {link_text} has no ID')

    out = row_id.replace('tr_', '')
    return out

# ################################################################################################################################

def _queue_href(page:'Page', base_url:'str', item_id:'str') -> 'str':
    navigate_to_page(page, base_url, ModuleCtx.Subscription_Page)

    link_selector = f'#tr_{item_id} {ModuleCtx.Queue_Link}'
    href = page.get_attribute(link_selector, 'href')

    if href is None:
        raise Exception(f'The subscription {item_id} has no link to its queue')

    return href

# ################################################################################################################################

def queue_path(page:'Page', base_url:'str', item_id:'str', state:'str') -> 'str':
    """ Returns the path of the queue browser of the subscriber of a subscription, showing messages in the given state.
    """
    href = _queue_href(page, base_url, item_id)

    out = href.replace(ModuleCtx.Queue_State_Pending, state)
    return out

# ################################################################################################################################

def sub_key_of(page:'Page', base_url:'str', item_id:'str') -> 'str':
    """ Returns the sub key of a subscription.
    """
    href = _queue_href(page, base_url, item_id)
    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    sub_keys = query['sub_key']

    out = sub_keys[0]
    return out

# ################################################################################################################################

def pair_statuses(page:'Page', base_url:'str', item_id:'str') -> 'anydict | None':
    """ Returns the status of each topic that the subscriptions page lists for a subscription,
    or None if the page lists no such subscription.
    """
    navigate_to_page(page, base_url, ModuleCtx.Subscription_Page)

    out = page.evaluate(_pair_status_script, item_id)
    return out

# ################################################################################################################################

def wait_for_statuses(page:'Page', base_url:'str', item_id:'str', expected:'anydict | None', what:'str') -> 'None':
    """ Waits until the subscriptions page lists exactly the expected status of each topic of a subscription.
    """
    def _has_statuses() -> 'bool':
        statuses = pair_statuses(page, base_url, item_id)

        out = statuses == expected
        return out

    wait_for(_has_statuses, what)

# ################################################################################################################################
# ################################################################################################################################

def queue_previews(page:'Page', base_url:'str', path:'str') -> 'strlist':
    """ Returns the data preview of each message that the queue browser shows.
    """
    url = base_url + path

    _ = page.goto(url)
    _ = page.wait_for_selector(ModuleCtx.Queue_Body, state='attached', timeout=ModuleCtx.Dialog_Timeout)

    out = page.evaluate(_queue_previews_script)
    return out

# ################################################################################################################################

def is_queued(page:'Page', base_url:'str', path:'str', marker:'str') -> 'bool':
    """ Whether the queue browser shows a message with the marker.
    """
    previews = queue_previews(page, base_url, path)

    for preview in previews:
        if marker in preview:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def wait_for_queued(page:'Page', base_url:'str', path:'str', marker:'str') -> 'None':
    """ Waits until the queue browser shows a message with the marker.
    """
    def _is_queued() -> 'bool':
        out = is_queued(page, base_url, path, marker)
        return out

    wait_for(_is_queued, f'The queueing of {marker}')

# ################################################################################################################################

def wait_for_not_queued(page:'Page', base_url:'str', path:'str', marker:'str') -> 'None':
    """ Waits until the queue browser no longer shows a message with the marker.
    """
    def _is_not_queued() -> 'bool':
        is_found = is_queued(page, base_url, path, marker)

        out = not is_found
        return out

    wait_for(_is_not_queued, f'The removal of {marker} from the queue')

# ################################################################################################################################
# ################################################################################################################################

def start_publication(page:'Page', base_url:'str', topic_id:'str', marker:'str') -> 'None':
    """ Publishes a message from the topic page without waiting for the result.
    """
    navigate_to_page(page, base_url, ModuleCtx.Topic_Page)
    open_publish_overlay(page, topic_id)

    _ = page.evaluate(_set_payload_script, marker)
    page.click('#invoker-modal-invoke-button')

# ################################################################################################################################

def wait_for_publication(page:'Page') -> 'str':
    """ Waits for the result of a publication from the topic page and returns its status line.
    """
    _ = page.wait_for_function(_publish_completed_script, timeout=ModuleCtx.Publish_Timeout)

    out = page.inner_text('#invoker-modal-status')
    return out

# ################################################################################################################################

def publish(page:'Page', base_url:'str', topic_id:'str', marker:'str') -> 'str':
    """ Publishes a message from the topic page and returns the status line of the result.
    """
    start_publication(page, base_url, topic_id, marker)

    out = wait_for_publication(page)
    return out

# ################################################################################################################################

def publish_accepted(page:'Page', base_url:'str', topic_id:'str', marker:'str') -> 'None':
    """ Publishes a message from the topic page and raises unless the server accepted it.
    """
    status = publish(page, base_url, topic_id, marker)

    if not status.startswith(ModuleCtx.Publish_Accepted):
        raise Exception(f'The publication of {marker} was not accepted, the status was `{status}`')

# ################################################################################################################################
# ################################################################################################################################

def open_subscription_edit(page:'Page', base_url:'str', item_id:'str', current_topics:'strlist') -> 'None':
    """ Opens the edit form of a subscription once it shows each of its current topics as subscribed.
    """
    navigate_to_page(page, base_url, ModuleCtx.Subscription_Page)
    open_edit_dialog(page, 'subscription', item_id)

    for topic_name in current_topics:
        selector = f'{ModuleCtx.Edit_Topics} input[name="topic_name"][value="{topic_name}"]:checked'
        _ = page.wait_for_selector(selector, state='attached', timeout=ModuleCtx.Dialog_Timeout)

# ################################################################################################################################

def set_edit_topic(page:'Page', topic_name:'str', is_subscribed:'bool') -> 'None':
    """ Subscribes the subscription of the open edit form to a topic or unsubscribes it from the topic.
    """
    if is_subscribed:
        expected = ModuleCtx.Topic_On
    else:
        expected = ModuleCtx.Topic_Off

    selector = f'{ModuleCtx.Edit_Topics} input[name="topic_name"][value="{topic_name}"]'
    _ = page.wait_for_selector(selector, state='visible', timeout=ModuleCtx.Dialog_Timeout)

    for _ in range(ModuleCtx.Tri_State_Clicks):
        state = page.eval_on_selector(selector, _topic_state_script)
        if state == expected:
            break
        page.click(selector)
    else:
        raise Exception(f'The checkbox of {topic_name} did not reach the state `{expected}`')

# ################################################################################################################################

def save_edit(page:'Page') -> 'float':
    """ Saves the open edit form, raises if Dashboard reports an error and returns how long the save took, in seconds.
    """
    started = time.monotonic()
    submit_edit_form(page, ModuleCtx.Dialog_Timeout)
    elapsed = time.monotonic() - started

    if page.is_visible(ModuleCtx.User_Message_Failure):
        message = page.inner_text(ModuleCtx.User_Message_Failure)
        raise Exception(f'The save was not accepted: {message}')

    return elapsed

# ################################################################################################################################

def change_topics(page:'Page', base_url:'str', item_id:'str', current_topics:'strlist', changes:'anydict') -> 'float':
    """ Subscribes a subscription to or unsubscribes it from topics in Dashboard and returns how long the save took.
    """
    open_subscription_edit(page, base_url, item_id, current_topics)

    for topic_name, is_subscribed in changes.items():
        set_edit_topic(page, topic_name, is_subscribed)

    out = save_edit(page)
    return out

# ################################################################################################################################
# ################################################################################################################################

def server_url(zato_dashboard:'anydict') -> 'str':
    """ Returns the address of the REST API of the server.
    """
    host = zato_dashboard['host']
    port = zato_dashboard['server_port']

    out = f'http://{host}:{port}'
    return out

# ################################################################################################################################

def client_publish_accepted(base_url:'str', client:'anydict', topic_name:'str', marker:'str') -> 'None':
    """ Publishes a message as an API client through the REST API of the server.
    """
    publisher = PublishClient(base_url, client['username'], client['password'], ModuleCtx.Client_Timeout)
    _ = publisher.publish(topic_name, marker)

# ################################################################################################################################

def is_client_refused(base_url:'str', client:'anydict', topic_name:'str', marker:'str') -> 'bool':
    """ Whether the server refuses a message that an API client publishes through the REST API.
    """
    publisher = PublishClient(base_url, client['username'], client['password'], ModuleCtx.Client_Timeout)

    try:
        _ = publisher.publish(topic_name, marker)
    except Exception:
        out = True
    else:
        out = False

    return out

# ################################################################################################################################

def client_pull(base_url:'str', client:'anydict') -> 'strlist':
    """ Pulls and acknowledges the messages of an API client and returns the payload of each.
    """
    puller = PullClient(base_url, client['username'], client['password'], ModuleCtx.Client_Timeout)
    response = puller.pull()

    out:'strlist' = []

    for message in response['messages']:
        data = message['data']
        out.append(data)

    return out

# ################################################################################################################################
# ################################################################################################################################

def kill_config_process(server_pid:'int') -> 'None':
    """ Kills the config process of the server with SIGKILL.
    """
    server_process = psutil.Process(server_pid)
    descendants = server_process.children(recursive=True)

    for process in descendants:
        if process.name() == ConfigProcessCtx.Process_Name:
            os.kill(process.pid, signal.SIGKILL)
            break
    else:
        raise Exception(f'The server {server_pid} has no config process')

# ################################################################################################################################
# ################################################################################################################################
