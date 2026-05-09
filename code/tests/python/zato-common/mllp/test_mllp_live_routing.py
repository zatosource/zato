# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.hl7.mllp.router import HL7MessageRouter

# ################################################################################################################################
# ################################################################################################################################

# A standard ADT^A01 MSH line for routing tests
_adt_a01_msh = 'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CTRL001|P|2.5'

# An ORU^R01 MSH line that does not match the ADT^A01 routing criteria
_oru_r01_msh = 'MSH|^~\\&|LabSys|LabFac|OrderSys|OrderFac|20230101130000||ORU^R01|CTRL002|P|2.5'

# A completely unknown MSH line with fields that match no specific route
_unknown_msh = 'MSH|^~\\&|UnknownApp|UnknownFac|NoMatch|NoMatch|20230101140000||ZZZ^Z99|CTRL003|P|2.5'

# ################################################################################################################################
# ################################################################################################################################

def _noop_callback(message_text:'str') -> 'None':
    """ A no-op callback for routing tests that only need to verify route matching.
    """
    return None

# ################################################################################################################################
# ################################################################################################################################

class TestIsActiveRouting(TestCase):
    """ Verifies that the is_active flag controls whether a channel's route is registered.
    These tests operate directly on the HL7MessageRouter to simulate what the wrapper does.
    """

    def test_inactive_channel_not_routed(self) -> 'None':
        """ An inactive channel has no route registered, so its messages are unmatched.
        """
        router = HL7MessageRouter()

        # .. do NOT add a route (simulating is_active=False in the wrapper) ..

        result = router.match(_adt_a01_msh)

        self.assertIsNone(result)

# ################################################################################################################################

    def test_active_channel_routed(self) -> 'None':
        """ An active channel has its route registered and matches incoming messages.
        """
        router = HL7MessageRouter()

        router.add_route(
            channel_name='active-channel',
            service_name='test.hl7.mllp.echo',
            callback=_noop_callback,
            msh9_message_type='ADT',
        )

        result = router.match(_adt_a01_msh)

        self.assertIsNotNone(result)
        self.assertEqual(result.channel_name, 'active-channel') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_toggle_active_off(self) -> 'None':
        """ Remove a route (simulating toggle to inactive), verify messages are unmatched.
        """
        router = HL7MessageRouter()

        router.add_route(
            channel_name='toggle-channel',
            service_name='test.hl7.mllp.echo',
            callback=_noop_callback,
            msh9_message_type='ADT',
        )

        # .. verify it matches first ..
        result = router.match(_adt_a01_msh)
        self.assertIsNotNone(result)

        # .. remove the route (simulating is_active=False) ..
        router.remove_route('toggle-channel')

        result = router.match(_adt_a01_msh)
        self.assertIsNone(result)

# ################################################################################################################################

    def test_toggle_active_on(self) -> 'None':
        """ Start without a route, then add one (simulating toggle to active), verify messages match.
        """
        router = HL7MessageRouter()

        # .. no route registered, so no match ..
        result = router.match(_adt_a01_msh)
        self.assertIsNone(result)

        # .. add the route (simulating is_active=True) ..
        router.add_route(
            channel_name='toggle-on-channel',
            service_name='test.hl7.mllp.echo',
            callback=_noop_callback,
            msh9_message_type='ADT',
        )

        result = router.match(_adt_a01_msh)

        self.assertIsNotNone(result)
        self.assertEqual(result.channel_name, 'toggle-on-channel') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

class TestIsDefaultRouting(TestCase):
    """ Verifies that the is_default flag enables catch-all routing behavior.
    """

    def test_is_default_catches_all(self) -> 'None':
        """ A default route catches messages that do not match any specific route.
        """
        router = HL7MessageRouter()

        router.add_route(
            channel_name='default-channel',
            service_name='test.hl7.mllp.default',
            callback=_noop_callback,
            is_default=True,
        )

        # .. a message with unknown fields should be caught by the default route ..
        result = router.match(_unknown_msh)

        self.assertIsNotNone(result)
        self.assertEqual(result.channel_name, 'default-channel') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_is_default_false_no_catch_all(self) -> 'None':
        """ A non-default route with specific criteria does not catch unmatched messages.
        """
        router = HL7MessageRouter()

        router.add_route(
            channel_name='specific-channel',
            service_name='test.hl7.mllp.specific',
            callback=_noop_callback,
            msh9_message_type='ADT',
            is_default=False,
        )

        # .. a message with a different type should not match ..
        result = router.match(_unknown_msh)

        self.assertIsNone(result)

# ################################################################################################################################

    def test_toggle_default_on(self) -> 'None':
        """ Start with a non-default route, remove it, re-add as default, verify it catches all.
        """
        router = HL7MessageRouter()

        # .. add as non-default with specific criteria ..
        router.add_route(
            channel_name='toggle-default-channel',
            service_name='test.hl7.mllp.echo',
            callback=_noop_callback,
            msh9_message_type='ADT',
            is_default=False,
        )

        # .. unknown message should not match ..
        result = router.match(_unknown_msh)
        self.assertIsNone(result)

        # .. remove and re-add as default ..
        router.remove_route('toggle-default-channel')

        router.add_route(
            channel_name='toggle-default-channel',
            service_name='test.hl7.mllp.echo',
            callback=_noop_callback,
            is_default=True,
        )

        # .. now the unknown message should match the default route ..
        result = router.match(_unknown_msh)

        self.assertIsNotNone(result)
        self.assertEqual(result.channel_name, 'toggle-default-channel') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_toggle_default_off(self) -> 'None':
        """ Start with a default route, remove it, re-add as non-default with specific fields, verify no catch-all.
        """
        router = HL7MessageRouter()

        # .. add as default ..
        router.add_route(
            channel_name='toggle-off-channel',
            service_name='test.hl7.mllp.echo',
            callback=_noop_callback,
            is_default=True,
        )

        # .. unknown message should match ..
        result = router.match(_unknown_msh)
        self.assertIsNotNone(result)

        # .. remove and re-add as non-default with specific criteria ..
        router.remove_route('toggle-off-channel')

        router.add_route(
            channel_name='toggle-off-channel',
            service_name='test.hl7.mllp.echo',
            callback=_noop_callback,
            msh9_message_type='ADT',
            is_default=False,
        )

        # .. unknown message should no longer match ..
        result = router.match(_unknown_msh)
        self.assertIsNone(result)

# ################################################################################################################################
# ################################################################################################################################
