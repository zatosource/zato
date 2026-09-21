# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What every group of shared scenarios builds on. A type's suite subclasses SharedScenarios and names its type, pytest
# collects the inherited test methods and each runs through the type's connections, receivers and services.

# Test support
from queue_delivery.client import get_receiver
from queue_delivery.type_under_test import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist
    from queue_delivery.receiver import RecordingReceiver
    from queue_delivery.type_under_test import TypeUnderTest

# ################################################################################################################################
# ################################################################################################################################

class ScenarioBase:
    """ The type under test and the shortcuts every scenario reaches for.
    """

    # A type's suite sets this, the harness points TestConfig at the same object
    type_under_test:'TypeUnderTest' = None # type: ignore[assignment]

# ################################################################################################################################

    @property
    def t(self) -> 'TypeUnderTest':
        """ The type under test, as the harness knows it.
        """
        out = TestConfig.type_under_test
        return out

# ################################################################################################################################

    def conn(self, key:'str') -> 'str':
        """ The name of the connection under that key.
        """
        out = self.t.connections[key]
        return out

# ################################################################################################################################

    def receiver(self, key:'str') -> 'RecordingReceiver':
        """ The endpoint of the connection under that key.
        """
        out = get_receiver(key)
        return out

# ################################################################################################################################

    def bodies(self, requests:'anylist') -> 'anylist':
        """ The documents a run of recorded requests carried, in the order they arrived.
        """
        out = [self.t.body_of(request) for request in requests]
        return out

# ################################################################################################################################
# ################################################################################################################################
