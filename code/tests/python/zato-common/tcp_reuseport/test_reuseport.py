# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import socket
import time
import traceback
from collections import Counter
from multiprocessing import get_context

# Zato
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.util.tcp import ZatoStreamServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.context import ForkProcess
    from zato.common.typing_ import list_

    ForkProcess = ForkProcess
    processlist = list_[ForkProcess]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Host = '127.0.0.1'

    # How many workers listen on the port, and how many connections the client opens at most, one message on each
    Worker_Count = 2
    Max_Connection_Count = 1000

    # The prefix of MSH-3 in the acknowledgment of each worker, followed by the index of the worker
    Worker_Prefix = 'WORKER_'

    Start_Sequence = b'\x0b'
    End_Sequence   = b'\x1c\x0d'

    # How long the client waits for the listeners and for each reply, in seconds
    Connect_Timeout = 20.0
    Reply_Timeout = 10.0
    Connect_Interval = 0.05

    # How long the test waits for a worker to exit, in seconds
    Join_Timeout = 20.0

# ################################################################################################################################
# ################################################################################################################################

# The workers of the tests are forked, as the workers of a server are
_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def _get_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ModuleCtx.Host, 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################

def _run_mllp_worker(index:'int', address:'str') -> 'None':
    """ Runs one MLLP listener on the shared port, answering each message with an acknowledgment that names this worker.
    """
    exit_code = 1

    try:

        # The worker patches itself the same way a server does before its listener starts
        from gevent.monkey import patch_all
        _ = patch_all()

        from zato.common.hl7.mllp.router import HL7MessageRouter
        from zato.common.hl7.mllp.server import HL7MLLPServer
        from zato.common.hl7.mllp.settings import ListenerConfig, RouteSettings

        def reply(message_text:'str', cid:'str') -> 'str':
            msh_line = message_text.split('\r', 1)[0]
            control_id = extract_control_id(msh_line)

            out = (
                f'MSH|^~\\&|{ModuleCtx.Worker_Prefix}{index}|FACILITY|CLIENT|CLIENT|20260101000000||ACK|{control_id}|P|2.5\r'
                f'MSA|AA|{control_id}'
            )
            return out

        settings = RouteSettings(should_parse_on_input=False)

        router = HL7MessageRouter()
        router.add_route(channel_name='test', service_name='test', callback=reply, is_default=True, settings=settings)

        server = HL7MLLPServer(ListenerConfig(address), router)

        def on_sigterm(signum:'int', frame:'object') -> 'None':
            server.stop()

        _ = signal.signal(signal.SIGTERM, on_sigterm)

        server.start()
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _send_message(port:'int', control_id:'str') -> 'str':
    """ Sends one message on a new connection and returns MSH-3 of the acknowledgment.
    """
    message = f'MSH|^~\\&|CLIENT|CLIENT|ZATO|ZATO|20260101000000||ADT^A01|{control_id}|P|2.5\rPID|1||{control_id}'
    frame = ModuleCtx.Start_Sequence + message.encode() + ModuleCtx.End_Sequence

    deadline = time.monotonic() + ModuleCtx.Connect_Timeout

    # The listeners of the workers may not be bound yet
    while True:
        try:
            sock = socket.create_connection((ModuleCtx.Host, port), ModuleCtx.Reply_Timeout)
            break
        except ConnectionRefusedError:
            if time.monotonic() > deadline:
                raise
            time.sleep(ModuleCtx.Connect_Interval)

    with sock:
        sock.sendall(frame)
        response = b''

        while not response.endswith(ModuleCtx.End_Sequence):
            chunk = sock.recv(4096)
            assert chunk, response
            response += chunk

    ack = response[1:-2].decode()
    out = ack.split('|')[2]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_two_listeners_bind_the_same_port() -> 'None':
    port = _get_free_port()
    address = (ModuleCtx.Host, port)

    first = ZatoStreamServer.get_listener(address, family=socket.AF_INET)
    second = ZatoStreamServer.get_listener(address, family=socket.AF_INET)

    try:
        assert first.getsockname() == second.getsockname()
    finally:
        first.close()
        second.close()

# ################################################################################################################################

def test_every_mllp_worker_accepts_connections_on_the_shared_port() -> 'None':
    port = _get_free_port()
    address = f'{ModuleCtx.Host}:{port}'

    workers:'processlist' = []

    for index in range(ModuleCtx.Worker_Count):
        process = _context.Process(target=_run_mllp_worker, args=(index, address))
        process.start()
        workers.append(process)

    expected = {f'{ModuleCtx.Worker_Prefix}{index}' for index in range(ModuleCtx.Worker_Count)}
    answered_by:'Counter[str]' = Counter()

    try:

        # The kernel distributes the connections among the listeners that are bound to the port, which the workers
        # bind one after another, so the client continues until every worker answered ..
        for number in range(ModuleCtx.Max_Connection_Count):
            worker = _send_message(port, f'MSG-{number:05d}')
            answered_by[worker] += 1

            if set(answered_by) == expected:
                break

    finally:
        for process in workers:
            process.terminate()

        for process in workers:
            process.join(ModuleCtx.Join_Timeout)
            assert process.exitcode == 0

    # .. and no connection was answered by anything other than a worker.
    assert set(answered_by) == expected

# ################################################################################################################################
# ################################################################################################################################
