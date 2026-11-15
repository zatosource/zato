# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from multiprocessing import get_context

# gevent
import gevent

# Zato
from writer_common import get_message_ids, new_message_values, run_in_child
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.pubsub.sql.writes import new_pending_publication, PubSubWriter
from zato.common.pubsub.writer_process.client import WriterClient
from zato.common.pubsub.writer_process.frames import ItemKind
from zato.common.pubsub.writer_process.server import new_listening_socket, WriterServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict
    MonkeyPatch = MonkeyPatch
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# The supervisor is forked, as the arbiter forks the writer, so that it inherits the listening socket
_context = get_context('fork')

# How long the publisher waits for its reply, and how long the traces are kept at least, in seconds
_deadline = 20.0
_grace_seconds = 600

# The exit code of the writer that terminates after its commit
_crash_exit_code = 9

# How long the second writer runs after its reply, in seconds
_exit_delay = 1

_first_msg_id = 'msg-1'
_second_msg_id = 'msg-2'

# ################################################################################################################################
# ################################################################################################################################

def _run_writer(listen_fd:'int', generation:'int') -> 'None':
    """ A writer that commits each publication through PubSubWriter, the first one of which terminates
    after its commit and before its reply.
    """
    writer = PubSubWriter()

    def publish(body:'anydict') -> 'anydict':
        pending = new_pending_publication(body)
        writer.publish(pending)

        if generation == 1:
            os._exit(_crash_exit_code)

        _ = gevent.spawn_later(_exit_delay, os._exit, 0)

        out = {'subscriber_keys': pending.subscriber_keys}
        return out

    server = WriterServer(listen_fd, {ItemKind.Publish: publish})
    server.serve_forever()

# ################################################################################################################################

def _sweep() -> 'None':
    """ Makes the first message a trace above the per-topic cap of one, and runs the sweeps of the cleanup.
    """
    writer = PubSubWriter()
    writer.publish(new_pending_publication(new_message_values(_second_msg_id)))

    _ = PubSubCleanup().sweep_once()

# ################################################################################################################################

def _run_child(target:'any_', *args:'any_') -> 'None':
    pid = os.fork()

    if pid == 0:
        gevent.reinit()
        target(*args)
        os._exit(0)

    _ = os.waitpid(pid, 0)

# ################################################################################################################################

def _supervise(listen_fd:'int') -> 'None':
    """ Runs the first writer, the cleanup before the restart of the writer, and the second writer.
    """
    _run_child(_run_writer, listen_fd, 1)
    _run_child(_sweep)
    _run_child(_run_writer, listen_fd, 2)

# ################################################################################################################################
# ################################################################################################################################

def _publish_across_a_sweep(tmp_dir:'str') -> 'None':
    address = os.path.join(tmp_dir, 'writer.sock')
    listener = new_listening_socket(address)

    supervisor = _context.Process(target=_supervise, args=(listener.fileno(),))
    supervisor.start()

    client = WriterClient(address, _deadline, lambda: None)
    client_greenlet = client.start()

    # The first writer commits the publication and terminates, the sweep runs, and the second writer receives
    # the publication again ..
    reply = client.call(ItemKind.Publish, new_message_values(_first_msg_id))

    supervisor.join(_deadline)

    # .. which finds the message that the first writer committed, kept by its grace period, and does not insert it twice.
    assert reply == {'subscriber_keys': []}
    assert get_message_ids(_first_msg_id) == [1]
    assert get_message_ids(_second_msg_id) == [2]

    client.close()
    gevent.kill(client_greenlet)
    listener.close()

# ################################################################################################################################
# ################################################################################################################################

def test_a_publication_sent_again_after_a_sweep_is_committed_once(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'None':
    monkeypatch.setenv(ModuleCtx.Env_Path, str(tmp_path / 'pubsub.db'))
    monkeypatch.setenv(ModuleCtx.Env_Delivered_Max_Messages, '1')
    monkeypatch.setenv(ModuleCtx.Env_Trace_Grace_Seconds, str(_grace_seconds))

    run_in_child(_publish_across_a_sweep, (str(tmp_path),))

# ################################################################################################################################
# ################################################################################################################################
