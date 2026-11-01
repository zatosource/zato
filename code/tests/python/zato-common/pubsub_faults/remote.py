# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A fault applied to a process from outside of it. The process that runs the traffic requests each step
# of the fault through a file of a control directory, and the test that started the process completes the step
# and confirms it through another file. The test also removes the fault once the fault has lasted its time,
# since the process may be frozen or starved by the fault and unable to request it.

# stdlib
import os
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from faults import Fault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

# The files of the control directory - the step requested and the step completed.
_request_file = 'request'
_reply_file = 'reply'

# The steps of a fault.
Step_Start_Baseline = 'start-baseline'
Step_End_Baseline   = 'end-baseline'
Step_Apply          = 'apply'
Step_Remove         = 'remove'

# How often each side reads the files of the other one, and how long a step may take, in seconds.
_poll_seconds = 0.1
_step_timeout = 600

# ################################################################################################################################
# ################################################################################################################################

def write_control_file(path:'str', value:'str') -> 'None':
    """ Replaces the contents of a file at once, so that its reader never sees a part of them.
    """
    temp_path = f'{path}.tmp'

    with open(temp_path, 'w') as control_file:
        _ = control_file.write(value)

    os.replace(temp_path, path)

# ################################################################################################################################

def _read(path:'str') -> 'str':

    if not os.path.exists(path):
        return ''

    with open(path) as control_file:
        out = control_file.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

class RemoteFault(Fault):
    """ The side of the process that runs the traffic - each step is requested and waited for.
    """

    def __init__(self, name:'str', control_dir:'str') -> 'None':
        self.name = name
        self.request_path = os.path.join(control_dir, _request_file)
        self.reply_path = os.path.join(control_dir, _reply_file)
        self._sequence = 0

# ################################################################################################################################

    def _request(self, step:'str') -> 'None':

        # Each request has a number of its own, so that a repeated step is a new request ..
        self._sequence += 1
        request = f'{self._sequence} {step}'

        write_control_file(self.request_path, request)

        # .. which is complete once the reply repeats it.
        deadline = monotonic() + _step_timeout

        while _read(self.reply_path) != request:
            assert monotonic() < deadline, f'Step `{request}` not completed after {_step_timeout}s'
            sleep(_poll_seconds)

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        self._request(Step_Start_Baseline)

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        self._request(Step_End_Baseline)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self._request(f'{Step_Apply} {level}')

# ################################################################################################################################

    def remove(self) -> 'None':
        self._request(Step_Remove)

# ################################################################################################################################
# ################################################################################################################################

class FaultDriver:
    """ The side of the test - completes each step that the process requests, and removes the fault
    once it has lasted its time.
    """

    def __init__(self, fault:'Fault', control_dir:'str', fault_seconds:'float') -> 'None':
        self.fault = fault
        self.request_path = os.path.join(control_dir, _request_file)
        self.reply_path = os.path.join(control_dir, _reply_file)
        self.fault_seconds = fault_seconds

        self.is_applied = False
        self.applied_at = 0.0

        self._last_request = ''
        self._greenlets:'anylist' = []

# ################################################################################################################################

    def _complete(self, request:'str') -> 'None':
        """ Completes one step of the fault.
        """
        _, step = request.split(' ', 1)

        if step == Step_Start_Baseline:
            self.fault.start_baseline()

        elif step == Step_End_Baseline:
            self.fault.end_baseline()

        elif step.startswith(Step_Apply):
            _, level = step.split()
            self.fault.apply(int(level))
            self.is_applied = True
            self.applied_at = monotonic()

        elif step == Step_Remove:
            self._remove()

        # .. anything else is not a step of a fault.
        else:
            raise Exception(f'Unknown step `{step}`')

# ################################################################################################################################

    def _remove(self) -> 'None':
        self.fault.remove()
        self.is_applied = False

# ################################################################################################################################

    def _run(self) -> 'None':

        while True:

            # A fault that has lasted its time is removed whether or not the process requested it ..
            if self.is_applied:
                applied_for = monotonic() - self.applied_at
                if applied_for >= self.fault_seconds:
                    self._remove()

            # .. and each new request is completed and confirmed.
            request = _read(self.request_path)

            if request:
                if request != self._last_request:
                    self._complete(request)
                    self._last_request = request
                    write_control_file(self.reply_path, request)

            sleep(_poll_seconds)

# ################################################################################################################################

    def start(self) -> 'None':
        greenlet = spawn(self._run)
        self._greenlets.append(greenlet)

# ################################################################################################################################

    def raise_failure(self) -> 'None':
        """ Raises the exception that ended the driver, which otherwise runs until it is stopped.
        """
        for greenlet in self._greenlets:
            if greenlet.dead:
                _ = greenlet.get()

# ################################################################################################################################

    def stop(self) -> 'None':
        for greenlet in self._greenlets:
            greenlet.kill()

        self._greenlets = []
        self._remove()

# ################################################################################################################################
# ################################################################################################################################
