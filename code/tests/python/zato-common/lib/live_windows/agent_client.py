# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from time import monotonic, sleep

# Zato
from live_windows.settings import Control, Paths
from live_windows.share_client import ShareClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, callable_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often a wait for an event reads the events file, in seconds
    Poll_Interval = 0.2

    # The line separator of the events file
    Line_Separator = b'\n'

# ################################################################################################################################
# ################################################################################################################################

class AgentError(Exception):
    """ Raised when the agent reports an error, or when an event it should have sent did not arrive in time.
    """

# ################################################################################################################################
# ################################################################################################################################

class AgentClient:
    """ Sends commands to the agent of one guest and reads the events it appends to the control share.
    """
    def __init__(self, client:'ShareClient', prefix:'str') -> 'None':
        self.client = client
        self.prefix = prefix
        self.offset = 0
        self.partial_line = b''
        self.command_sequence = 0
        self.events:'dictlist' = []

# ################################################################################################################################

    def upload_agent(self) -> 'None':
        """ Uploads the agent script and then the file that tells the bootstrap to start it.
        """
        script = Paths.Agent_Path.read_bytes()

        self.client.makedirs(Control.Share, Control.Agent_Dir)
        self.client.write_bytes(Control.Share, Control.Agent_Script, script)
        self.client.write_text(Control.Share, Control.Agent_Start, '{}')

# ################################################################################################################################

    def send(self, kind:'str', run:'str', fields:'anydict | None'=None) -> 'None':
        """ Writes one command into the commands directory, under a name that keeps the commands in the order they were sent.
        """
        self.command_sequence += 1

        command = {
            'kind': kind,
            'run': run,
        }

        if fields:
            command.update(fields)

        document = json.dumps(command)
        path = f'{Control.Commands_Dir}\\{self.command_sequence:08d}-{kind}.json'

        self.client.write_text(Control.Share, path, document)

# ################################################################################################################################

    def read_events(self) -> 'dictlist':
        """ Returns the events appended since the previous call. A line the agent is still writing is kept for the next call.
        """
        out:'dictlist' = []

        if not self.client.exists(Control.Share, Control.Events):
            return out

        data = self.client.read_bytes(Control.Share, Control.Events, self.offset)
        self.offset += len(data)

        data = self.partial_line + data
        lines = data.split(ModuleCtx.Line_Separator)

        # The last element is either empty or a line without its separator yet
        self.partial_line = lines.pop()

        for line in lines:
            event = json.loads(line)
            out.append(event)

        self.events.extend(out)

        return out

# ################################################################################################################################

    def read_heartbeat(self) -> 'anydict':
        document = self.client.read_text(Control.Share, Control.Heartbeat)

        out = json.loads(document)
        return out

# ################################################################################################################################

    def read_agent_error(self) -> 'str':
        """ Returns what the bootstrap recorded when the agent stopped, or an empty string if it did not stop.
        """
        if self.client.exists(Control.Share, Control.Agent_Error):
            out = self.client.read_text(Control.Share, Control.Agent_Error)
        else:
            out = ''

        return out

# ################################################################################################################################

    def wait_for_event(self, matches:'callable_', what:'str', timeout:'float') -> 'anydict':
        """ Reads events until one of them matches, failing at once on an error the agent reports.
        """
        deadline = monotonic() + timeout

        # Events read before this call count too ..
        for event in self.events:
            if matches(event):
                return event

        while True:

            # .. then each new event is checked as it arrives ..
            for event in self.read_events():

                if event['kind'] == 'error':
                    raise AgentError(f'{self.prefix} Agent error while waiting for {what} -> {event}')

                if matches(event):
                    return event

            # .. an agent that stopped will not send anything more ..
            if agent_error := self.read_agent_error():
                raise AgentError(f'{self.prefix} The agent stopped while waiting for {what} -> {agent_error}')

            # .. and the wait has a limit.
            if monotonic() > deadline:
                raise AgentError(f'{self.prefix} No {what} within {timeout}s')

            sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def run_command(self, kind:'str', run:'str', fields:'anydict | None', timeout:'float') -> 'anydict':
        """ Sends a command and waits until the agent reports that it has run it.
        """
        self.send(kind, run, fields)

        def _is_done(event:'anydict') -> 'bool':
            if event['kind'] == 'command-done':
                if event['run'] == run:
                    if event['command'] == kind:
                        return True
            return False

        out = self.wait_for_event(_is_done, f'the completion of {kind}', timeout)
        return out

# ################################################################################################################################
# ################################################################################################################################
