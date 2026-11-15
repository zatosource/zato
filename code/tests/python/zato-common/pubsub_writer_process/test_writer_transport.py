# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import socket
from multiprocessing import get_context
from time import monotonic

# gevent
import gevent
import gevent.socket
import pytest

# Zato
from zato.common.pubsub.writer_process.client import WriterClient, WriterTimeout
from zato.common.pubsub.writer_process.frames import FrameReader, ItemKind, new_error_reply, new_item, new_reply, \
    WriterItemError
from zato.common.pubsub.writer_process.server import new_listening_socket, WriterServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from gevent import Greenlet
    from zato.common.typing_ import any_, anydict, intlist, list_, strlist

    any_ = any_
    anydict = anydict
    Greenlet = Greenlet
    intlist = intlist
    Path = Path
    strlist = strlist

    dictlist     = list_['anydict']
    greenletlist = list_['Greenlet']

# ################################################################################################################################
# ################################################################################################################################

# The supervisor is forked, as the arbiter forks the writer, so that it inherits the listening socket
_context = get_context('fork')

# How long a caller waits for a reply in the tests that expect one, in seconds
_long_deadline = 20.0

# How long a caller waits for a reply in the test that expects none, in seconds
_short_deadline = 0.3

# How far in the past the expired item of a test expired, in seconds
_expired_by = 1.0

# How many publications the test of a terminated writer sends, and the one during which the first writer terminates
_publication_count = 30
_fatal_msg_id = 'msg-12'

# The exit code of a writer that terminates during a publication
_crash_exit_code = 9

# ################################################################################################################################
# ################################################################################################################################

def _read_commits(commits_path:'str') -> 'strlist':
    with open(commits_path) as commits_file:
        out = commits_file.read().split()
    return out

# ################################################################################################################################

def _run_writer(listen_fd:'int', commits_path:'str', generation:'int') -> 'None':
    """ A writer that commits each publication once by its msg_id, and whose first generation terminates
    after committing the fatal publication and before replying to it.
    """
    def publish(body:'anydict') -> 'anydict':
        msg_id = body['msg_id']

        if msg_id in _read_commits(commits_path):
            return {'is_repeated': True}

        with open(commits_path, 'a') as commits_file:
            _ = commits_file.write(msg_id + '\n')

        if msg_id == _fatal_msg_id:
            if generation == 1:
                os._exit(_crash_exit_code)

        return {'is_repeated': False}

    server = WriterServer(listen_fd, {ItemKind.Publish: publish})
    server.serve_forever()

# ################################################################################################################################

def _supervise_writer(listen_fd:'int', commits_path:'str') -> 'None':
    """ Forks the writer and forks a replacement each time it terminates abnormally, as the arbiter does.
    """
    writer_pid = 0

    def on_sigterm(signum:'int', frame:'any_') -> 'None':
        os.kill(writer_pid, signal.SIGKILL)
        os._exit(0)

    _ = signal.signal(signal.SIGTERM, on_sigterm)

    generation = 0

    while True:
        generation += 1
        writer_pid = os.fork()

        if writer_pid == 0:
            gevent.reinit()
            _run_writer(listen_fd, commits_path, generation)
            os._exit(0)

        _, status = os.waitpid(writer_pid, 0)

        if os.waitstatus_to_exitcode(status) != _crash_exit_code:
            break

# ################################################################################################################################
# ################################################################################################################################

def test_frames_are_read_whatever_the_boundaries_of_the_reads() -> 'None':
    stream = new_item(ItemKind.Publish, 1, 1.5, {'msg_id': 'a', 'payload': 'x' * 100_000})
    stream += new_reply(1, {'subscriber_keys': ['sk-1']})
    stream += new_error_reply(2, ValueError('no such topic'))

    # The stream arrives in reads of every size from one byte on ..
    for read_size in (1, 3, 4, 5, 7, 4096, len(stream)):
        reader = FrameReader()
        messages:'dictlist' = []

        for start in range(0, len(stream), read_size):
            data = stream[start:start + read_size]
            messages.extend(reader.feed(data))

        # .. and each one yields the same three messages in their order.
        assert len(messages) == 3
        assert messages[0]['expires_at'] == 1.5
        assert messages[0]['body']['payload'] == 'x' * 100_000
        assert messages[1] == {'item_id': 1, 'body': {'subscriber_keys': ['sk-1']}}
        assert messages[2] == {'item_id': 2, 'error_type': 'ValueError', 'error': 'no such topic'}
        assert reader.buffer == b''

# ################################################################################################################################

def test_items_are_run_in_the_order_of_their_callers_and_errors_reach_them(tmp_path:'Path') -> 'None':
    address = str(tmp_path / 'writer.sock')
    listener = new_listening_socket(address)

    handled:'intlist' = []

    def publish(body:'anydict') -> 'anydict':
        handled.append(body['index'])

        if body['index'] == 7:
            raise ValueError('topic not found')

        return {'index': body['index']}

    # The writer runs in this process and holds a descriptor of its own, as a forked writer does
    server = WriterServer(os.dup(listener.fileno()), {ItemKind.Publish: publish})
    server_greenlet = gevent.spawn(server.serve_forever)

    client = WriterClient(address, _long_deadline, lambda: None)
    client_greenlet = client.start()

    # Callers in greenlets of their own send their items in the order in which they run ..
    def call(index:'int') -> 'any_':
        try:
            out = client.call(ItemKind.Publish, {'index': index})
        except WriterItemError as e:
            out = e
        return out

    callers:'greenletlist' = []

    for index in range(20):
        caller = gevent.spawn(call, index)
        callers.append(caller)

    _ = gevent.joinall(callers, timeout=_long_deadline)

    # .. the writer runs them in that order ..
    assert handled == list(range(20))

    # .. and each caller receives its own reply, or the error of its own item.
    for index, caller in enumerate(callers):
        if index == 7:
            assert isinstance(caller.value, WriterItemError)
            assert caller.value.error_type == 'ValueError'
            assert caller.value.error == 'topic not found'
        else:
            assert caller.value == {'index': index}

    client.close()
    gevent.killall([client_greenlet, server_greenlet])
    server.close()
    listener.close()

# ################################################################################################################################

def test_a_terminated_writer_loses_no_publication_and_commits_none_twice(tmp_path:'Path') -> 'None':
    address = str(tmp_path / 'writer.sock')
    commits_path = str(tmp_path / 'commits')

    with open(commits_path, 'w'):
        pass

    # The supervisor holds the listening socket across the restarts of the writer ..
    listener = new_listening_socket(address)
    supervisor = _context.Process(target=_supervise_writer, args=(listener.fileno(), commits_path))
    supervisor.start()

    reconnects:'intlist' = []

    def on_reconnect() -> 'None':
        reconnects.append(1)

    client = WriterClient(address, _long_deadline, on_reconnect)
    client_greenlet = client.start()

    # .. publishers send their publications at once, and the first writer terminates during one of them ..
    msg_ids:'strlist' = []
    publishers:'greenletlist' = []

    for index in range(_publication_count):
        msg_id = f'msg-{index}'
        msg_ids.append(msg_id)

        publisher = gevent.spawn(client.call, ItemKind.Publish, {'msg_id': msg_id})
        publishers.append(publisher)

    _ = gevent.joinall(publishers, timeout=_long_deadline)

    # .. every publisher receives a reply, the publication during which the writer terminated as a repeated one ..
    for publisher in publishers:
        assert publisher.successful()

    fatal_index = msg_ids.index(_fatal_msg_id)
    assert publishers[fatal_index].value == {'is_repeated': True}

    # .. every publication is committed once ..
    commits = _read_commits(commits_path)
    assert sorted(commits) == sorted(msg_ids)

    # .. and the worker learned once that it was served by a replacement.
    assert reconnects == [1]

    client.close()
    gevent.kill(client_greenlet)

    supervisor.terminate()
    supervisor.join(_long_deadline)
    listener.close()

# ################################################################################################################################

def test_the_writer_does_not_run_an_item_whose_caller_stopped_waiting(tmp_path:'Path') -> 'None':
    address = str(tmp_path / 'writer.sock')
    listener = new_listening_socket(address)

    handled:'intlist' = []

    def publish(body:'anydict') -> 'anydict':
        handled.append(body['index'])
        return {}

    server = WriterServer(os.dup(listener.fileno()), {ItemKind.Publish: publish})
    server_greenlet = gevent.spawn(server.serve_forever)

    # A copy of an item read after the instant at which its caller stopped waiting ..
    conn = gevent.socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.connect(address)
    conn.sendall(new_item(ItemKind.Publish, 1, monotonic() - _expired_by, {'index': 1}))

    reader = FrameReader()
    messages:'dictlist' = []

    while not messages:
        messages.extend(reader.feed(conn.recv(4096)))

    # .. is not run, and its reply is an error.
    assert handled == []
    assert messages[0]['item_id'] == 1
    assert messages[0]['error_type'] == 'WriterItemExpired'

    conn.close()
    gevent.kill(server_greenlet)
    server.close()
    listener.close()

# ################################################################################################################################

def test_a_caller_receives_an_error_when_no_writer_replies_within_the_deadline(tmp_path:'Path') -> 'None':
    address = str(tmp_path / 'writer.sock')

    # The listening socket accepts connections into its backlog, and no writer takes them ..
    listener = new_listening_socket(address)

    client = WriterClient(address, _short_deadline, lambda: None)
    client_greenlet = client.start()

    # .. so the caller receives an error once the deadline passes ..
    with pytest.raises(WriterTimeout):
        _ = client.call(ItemKind.Publish, {'msg_id': 'msg-1'})

    # .. and the item is no longer sent again.
    assert client.pending == {}

    client.close()
    gevent.kill(client_greenlet)
    listener.close()

# ################################################################################################################################
# ################################################################################################################################
