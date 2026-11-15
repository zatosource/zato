# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The order in which a worker applies configuration events. Every ODB transaction that changes configuration increments
# config_version, and its event carries the new value. A worker, the originating one included, holds a received event
# until its version is the next one after the version in effect, and skips an event whose version is in effect already.
# A reload reads the configuration together with config_version, which puts every event up to that version in effect.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, dict_

    any_ = any_
    callable_ = callable_

    versionevents = dict_[int, any_]

# ################################################################################################################################
# ################################################################################################################################

class ConfigVersionGate:
    """ Applies the configuration events of a worker in the order of their versions, each one once.
    """
    def __init__(self, version:'int', apply:'callable_') -> 'None':

        # The highest configuration version in effect in the worker
        self.version = version

        # Applies one event to the configuration of the worker
        self.apply = apply

        # The events received whose version is not the next one yet, by version
        self.held:'versionevents' = {}

        # Whether a greenlet of the worker is applying held events
        self.is_applying = False

# ################################################################################################################################

    def receive(self, version:'int', event:'any_') -> 'None':
        """ Accepts one event, whether relayed by the arbiter or published by this worker.
        """
        # An event whose version is in effect already is skipped ..
        if version <= self.version:
            return

        # .. and any other is held until its version is the next one.
        self.held[version] = event
        self._apply_next()

# ################################################################################################################################

    def reload(self, version:'int') -> 'None':
        """ Records the configuration version that a reload read together with the configuration.
        """
        self.version = version

        # The reload put in effect every held event up to its version ..
        held_versions = list(self.held)

        for held_version in held_versions:
            if held_version <= version:
                del self.held[held_version]

        # .. and the held events that follow it are applied in order.
        self._apply_next()

# ################################################################################################################################

    def _apply_next(self) -> 'None':

        # An event may switch greenlets while it is applied, and the greenlet applying it applies the events
        # received meanwhile, so that the events of one worker are applied one at a time
        if self.is_applying:
            return

        self.is_applying = True

        try:
            next_version = self.version + 1

            while next_version in self.held:
                event = self.held.pop(next_version)

                # The version is in effect before the event is applied, so a copy received meanwhile is skipped
                self.version = next_version
                self.apply(event)

                next_version = self.version + 1

        finally:
            self.is_applying = False

# ################################################################################################################################
# ################################################################################################################################
