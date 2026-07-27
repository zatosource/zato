# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a service says about what its channel's destinations receive, reached as self.destination.
# Setting .payload changes what all of them are sent, setting one by name changes that one alone,
# and setting one to nothing drops it for this message. A service that says nothing leaves every
# destination receiving the message the way it arrived, which is what lets a channel have no
# service at all.

# Zato
from zato.common.destination.payload import new_overrides, resolve_payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.payload import PayloadOverrides
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class DestinationFacade:
    """ Provides access to a channel's destinations from services via self.destination.
    """
    _overrides: 'PayloadOverrides'
    _request_payload: 'any_'

    def init(self, request_payload:'any_') -> 'None':
        self._overrides = new_overrides()
        self._request_payload = request_payload

# ################################################################################################################################

    def __repr__(self) -> 'str':
        overrides = self._overrides
        return f'DestinationFacade(broadcast={overrides.has_broadcast}, named={list(overrides.per_destination)})'

# ################################################################################################################################

    def __setitem__(self, name:'str', data:'any_') -> 'None':
        self._overrides.per_destination[name] = data

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'any_':
        """ Returns what that destination is to be sent as things stand, which is the message
        as it arrived until the service says otherwise.
        """
        out = resolve_payload(name, self._overrides, self._request_payload)
        return out

# ################################################################################################################################

    @property
    def payload(self) -> 'any_':
        """ What every destination is to be sent.
        """
        out = self._overrides.broadcast
        return out

    @payload.setter
    def payload(self, data:'any_') -> 'None':
        self._overrides.broadcast = data
        self._overrides.has_broadcast = True

# ################################################################################################################################

    def get_overrides(self) -> 'PayloadOverrides':
        """ Returns what the service said, for the engine that delivers on it.
        """
        out = self._overrides
        return out

# ################################################################################################################################

    def to_dict(self) -> 'anydict':
        overrides = self._overrides

        out = {
            'payload': overrides.broadcast,
            'has_payload': overrides.has_broadcast,
            'per_destination': overrides.per_destination,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################
