# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import errno
import os
from dataclasses import dataclass
from http.client import OK

# gevent
from gevent.event import Event
from gevent.pywsgi import WSGIServer

# greenlet
import greenlet

# Zato
from zato.common.test.reservation import PortInUse, start_on_reserved_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reservation import PortReservation
    from zato.common.typing_ import any_, anylist, callable_, strlist

    any_ = any_
    anylist = anylist
    callable_ = callable_
    PortReservation = PortReservation
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The address that the REST push endpoints listen on
    Push_Host = '127.0.0.1'

    # The purpose under which a REST push endpoint reserves its port
    Push_Port_Purpose = 'pub/sub in-process push endpoint'

    # The response that a REST push endpoint returns for each message
    Push_Status = f'{OK} OK'
    Push_Headers = [('Content-Type', 'application/json')]
    Push_Response = b'{}'

    # The variable with the path to the control file of fsfault.so, which the process loads through LD_PRELOAD
    Env_FSFault_Control = 'ZATO_FSFAULT_CONTROL'

    # The calls of fsfault.so that a fault applies to
    FSFault_Calls_Sync  = 'sync'
    FSFault_Calls_Write = 'write'

    # The share of the calls that fail when a fault returns an error
    FSFault_All_Calls = 100

    # The events of greenlet tracing that move execution from one greenlet to another
    Switch_Events = frozenset({'switch', 'throw'})

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GreenletSwitch:
    event: 'str'
    origin: 'any_'
    target: 'any_'

# ################################################################################################################################
# ################################################################################################################################

class RESTPushEndpoint:
    """ An HTTP endpoint on a reserved port that receives the messages of a REST push subscriber.
    """

    def __init__(self) -> 'None':
        self.messages:'strlist' = []
        self.port = 0
        self._server:'WSGIServer | None' = None
        self._reservation:'PortReservation | None' = None
        self._message_received = Event()

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts listening on a reserved port.
        """
        reserved = start_on_reserved_port(ModuleCtx.Push_Port_Purpose, self._start_on_port)

        self._reservation = reserved.reservation
        self._server = reserved.result
        self.port = reserved.reservation.port

# ################################################################################################################################

    def _start_on_port(self, port:'int') -> 'WSGIServer':
        """ Binds the port, raising PortInUse when a process that does not reserve ports took it already.
        """
        out = WSGIServer((ModuleCtx.Push_Host, port), self._handle, log=None)

        try:
            out.start()
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                raise PortInUse(f'Port {port} is in use') from e
            else:
                raise

        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops listening and releases the port.
        """
        if self._server:
            self._server.stop()

        if self._reservation:
            self._reservation.release()

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        out = f'http://{ModuleCtx.Push_Host}:{self.port}'
        return out

# ################################################################################################################################

    def _handle(self, environ:'any_', start_response:'callable_') -> 'anylist':
        """ Records the body of a message and confirms it.
        """
        content_length = environ['CONTENT_LENGTH']
        content_length = int(content_length)

        body = environ['wsgi.input'].read(content_length)
        body = body.decode('utf8')

        self.messages.append(body)
        self._message_received.set()

        start_response(ModuleCtx.Push_Status, ModuleCtx.Push_Headers)

        out = [ModuleCtx.Push_Response]
        return out

# ################################################################################################################################

    def wait_for_messages(self, count:'int', timeout:'float') -> 'bool':
        """ Waits until the endpoint received at least count messages and returns whether it did within the timeout.
        """
        while len(self.messages) < count:

            self._message_received.clear()

            if not self._message_received.wait(timeout):
                break

        received = len(self.messages)

        out = received >= count
        return out

# ################################################################################################################################
# ################################################################################################################################

class FilesystemFault:
    """ Controls fsfault.so in this process, which delays or fails the syncs and writes of files under a path prefix.
    """

    def __init__(self, prefix:'str') -> 'None':
        self.prefix = prefix
        self.control_path = os.environ[ModuleCtx.Env_FSFault_Control]

# ################################################################################################################################

    def _write(self, lines:'strlist') -> 'None':
        """ Replaces the control file in one step, so that fsfault.so never reads a part of it.
        """
        content = '\n'.join(lines) + '\n'
        temporary_path = self.control_path + '.tmp'

        with open(temporary_path, 'w') as control_file:
            _ = control_file.write(content)

        os.replace(temporary_path, self.control_path)

# ################################################################################################################################

    def delay_syncs(self, delay_ms:'int') -> 'None':
        """ Delays each sync of a file under the prefix.
        """
        delay_us = delay_ms * 1000

        self._write([
            f'prefix={self.prefix}',
            f'delay_us={delay_us}',
            f'calls={ModuleCtx.FSFault_Calls_Sync}',
        ])

# ################################################################################################################################

    def fail_writes(self, error_name:'str') -> 'None':
        """ Fails each write of a file under the prefix with the error, e.g. EIO or ENOSPC.
        """
        self._write([
            f'prefix={self.prefix}',
            f'error_percent={ModuleCtx.FSFault_All_Calls}',
            f'errno={error_name}',
            f'calls={ModuleCtx.FSFault_Calls_Write}',
        ])

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Removes the fault, after which the files under the prefix are synced and written as usual.
        """
        self._write([f'prefix={self.prefix}'])

# ################################################################################################################################
# ################################################################################################################################

class SwitchObserver:
    """ Records each switch between greenlets while it is entered.
    """

    def __init__(self) -> 'None':
        self.switches:'anylist' = []
        self._previous_trace:'any_' = None

# ################################################################################################################################

    def __enter__(self) -> 'SwitchObserver':
        self._previous_trace = greenlet.settrace(self._trace)
        return self

# ################################################################################################################################

    def __exit__(self, *args:'any_') -> 'None':
        _ = greenlet.settrace(self._previous_trace)

# ################################################################################################################################

    def _trace(self, event:'str', args:'any_') -> 'None':
        """ Records a switch and passes the event to the trace that was installed before.
        """
        if event in ModuleCtx.Switch_Events:
            origin, target = args

            switch = GreenletSwitch()
            switch.event = event
            switch.origin = origin
            switch.target = target

            self.switches.append(switch)

        if self._previous_trace:
            self._previous_trace(event, args)

# ################################################################################################################################
# ################################################################################################################################
