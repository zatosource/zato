# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The routes of the control channel between the worker and the config process, which the hub of the arbiter follows.
# A forwarded invocation goes to the config process and its result goes back to the worker that forwarded it,
# after the events of the change, because both reach the worker through the same queue of its slot. The arbiter
# records the load requests that the config process has not served and the marks that no load report followed,
# so that a replacement config process continues from them, and it discards what a terminated process left behind.

# stdlib
from logging import getLogger

# Zato
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx
from zato.server.control.envelope import encode, join, MessageType, new_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, dict_
    from zato.server.control.hub import ControlHub, SlotChannel

    anydict = anydict
    anylist = anylist
    ControlHub = ControlHub
    SlotChannel = SlotChannel

    intstrdict = dict_[int, str]
    strintdict = dict_[str, int]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What a worker is told when the config process cannot run its forwarded invocation
    Config_Unavailable = 'The config process of the server is not running'

# ################################################################################################################################
# ################################################################################################################################

def new_unavailable_result() -> 'anydict':
    """ Returns the result of a forwarded invocation that the config process never received or never answered.
    """
    out = {
        'error': {
            'is_reportable': False,
            'is_zato': True,
            'message': ModuleCtx.Config_Unavailable,
            'status': 0,
            'needs_msg': False,
        }
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class ConfigRoute:
    """ Routes the forwarded invocations and the loads of configuration between the worker and the config process.
    """

    def __init__(self, hub:'ControlHub') -> 'None':
        self.hub = hub

        # The load request of the worker that the config process has not served, by the slot of the worker,
        # with its correlation ID
        self.requested:'intstrdict' = {}

        # The mark of the worker that has not reported its load yet, by the slot of the worker, with its correlation ID
        self.loading:'intstrdict' = {}

        # The slot of the worker that forwarded each invocation in progress, by its correlation ID
        self.forwards:'strintdict' = {}

# ################################################################################################################################

    def get_config_channel(self) -> 'SlotChannel | None':
        """ Returns the channel of the config process, which it has no channel of while it awaits its respawn.
        """
        channels = self.hub.channels
        config_slot = WorkerSlotCtx.Config_Slot

        if config_slot in channels:
            out = channels[config_slot]
        else:
            out = None

        return out

# ################################################################################################################################

    def _to_config(self, origin_slot:'int', header:'anydict', body:'bytes') -> 'None':
        """ Sends a message of a worker to the config process, or holds it until the config process reports ready.
        """
        config_channel = self.get_config_channel()

        # The arbiter recorded the message already, and a replacement config process receives it from that record
        if not config_channel:
            return

        header['slot'] = origin_slot
        datagram = join(header, body)

        self.hub.deliver(config_channel, datagram)

# ################################################################################################################################

    def _send_result(self, slot:'int', cid:'str', body:'anydict') -> 'None':
        """ Sends the result of a forwarded invocation to the worker, if the worker still runs.
        """
        if slot not in self.hub.channels:
            return

        channel = self.hub.channels[slot]
        message = new_message(MessageType.Forward_Result, body, cid, slot)

        datagram = encode(message, self.hub.body_dir)
        self.hub.send(channel, datagram)

# ################################################################################################################################

    def on_forward(self, channel:'SlotChannel', header:'anydict', body:'bytes') -> 'None':
        """ Sends an invocation that a worker forwarded to the config process, or fails it if there is no config process.
        """
        cid = header['cid']

        if self.get_config_channel():
            self.forwards[cid] = channel.slot
            self._to_config(channel.slot, header, body)

        else:
            datagram = join(header, body)
            self.hub.remove_body_file(datagram)

            result = new_unavailable_result()
            self._send_result(channel.slot, cid, result)

# ################################################################################################################################

    def on_forward_result(self, header:'anydict', datagram:'bytes') -> 'None':
        """ Sends the result of a forwarded invocation to the worker that forwarded it, after the events of its change.
        """
        cid = header['cid']

        # The worker that forwarded the invocation terminated, and nothing reads the result
        if cid not in self.forwards:
            self.hub.remove_body_file(datagram)
            return

        slot = self.forwards.pop(cid)

        if slot in self.hub.channels:
            channel = self.hub.channels[slot]
            self.hub.send(channel, datagram)
        else:
            self.hub.remove_body_file(datagram)

# ################################################################################################################################

    def on_load_request(self, channel:'SlotChannel', header:'anydict', body:'bytes') -> 'None':
        """ Records the load request of a worker and sends it to the config process.
        """
        self.requested[channel.slot] = header['cid']
        self._to_config(channel.slot, header, body)

# ################################################################################################################################

    def on_mark(self, header:'anydict', datagram:'bytes') -> 'None':
        """ Sends the mark of the config process to the worker that requested its load, discarding the events
        held for that worker if it is starting, because its load contains them already.
        """
        slot = header['target']
        cid = header['cid']

        # A mark of a request that a terminated worker sent, or that a replacement already received, is not delivered
        if slot not in self.requested:
            return

        if self.requested[slot] != cid:
            return

        _ = self.requested.pop(slot)
        self.loading[slot] = cid

        channel = self.hub.channels[slot]

        if not channel.is_ready:
            self.hub.discard_startup_buffer(channel)

        self.hub.send(channel, datagram)

# ################################################################################################################################

    def on_load_done(self, channel:'SlotChannel', header:'anydict', body:'bytes') -> 'None':
        """ Records that a worker loaded its configuration and tells the config process, which then resumes its changes.
        """
        slot = channel.slot
        cid = header['cid']

        if slot in self.loading:
            if self.loading[slot] == cid:
                _ = self.loading.pop(slot)

        self._to_config(slot, header, body)

# ################################################################################################################################

    def on_config_opened(self, config_channel:'SlotChannel') -> 'None':
        """ Gives a new config process the marks that no load report followed and the load requests that its predecessor
        did not serve, ahead of everything else that it receives.
        """
        loading:'anylist' = []

        for slot, cid in sorted(self.loading.items()):
            loading.append([slot, cid])

        message = new_message(MessageType.Loading_State, loading)
        datagram = encode(message, self.hub.body_dir)
        config_channel.startup_buffer.append(datagram)

        for slot, cid in sorted(self.requested.items()):
            message = new_message(MessageType.Load_Request, None, cid)
            message.slot = slot

            datagram = encode(message, self.hub.body_dir)
            config_channel.startup_buffer.append(datagram)

# ################################################################################################################################

    def on_slot_closed(self, slot:'int') -> 'None':
        """ Fails the invocations that a terminated config process did not answer, or discards what a terminated worker
        left and tells the config process that the worker terminated.
        """
        if slot == WorkerSlotCtx.Config_Slot:
            forwards = self.forwards
            self.forwards = {}

            for cid, origin_slot in sorted(forwards.items()):
                result = new_unavailable_result()
                self._send_result(origin_slot, cid, result)

            return

        # The results of the invocations that the worker forwarded have no reader ..
        for cid, origin_slot in list(self.forwards.items()):
            if origin_slot == slot:
                _ = self.forwards.pop(cid)

        # .. its request and its mark no longer hold any load back ..
        if slot in self.requested:
            _ = self.requested.pop(slot)

        if slot in self.loading:
            _ = self.loading.pop(slot)

        # .. and the config process learns of it in the order of everything else that it receives.
        message = new_message(MessageType.Worker_Gone, slot)
        datagram = encode(message, self.hub.body_dir)

        if config_channel := self.get_config_channel():
            self.hub.deliver(config_channel, datagram)
        else:
            self.hub.remove_body_file(datagram)

# ################################################################################################################################
# ################################################################################################################################
