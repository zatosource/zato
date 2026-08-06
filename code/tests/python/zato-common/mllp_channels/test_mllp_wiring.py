# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import ExitStack
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import HL7
from zato.common.destination.constants import Default_Delivery_Mode, Respond_From_Service
from zato.common.typing_ import cast_
from zato.server.generic.api.channel_hl7_mllp import ChannelHL7MLLPWrapper, _shared_state

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hl7.mllp.settings import RouteSettings
    from zato.common.typing_ import any_
    RouteSettings = RouteSettings
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The port the listener is taken to have settled on, which nothing here depends on the value of
_test_internal_port = 19000

# ################################################################################################################################
# ################################################################################################################################

def _make_config(**overrides:'object') -> 'MagicMock':
    """ Builds a mock Bunch-like config object with all MLLP channel fields populated.
    """

    defaults:'dict[str, object]' = {
        'id': 1,
        'name': 'test-mllp-channel',
        'service': 'test.hl7.mllp.echo',
        'is_active': True,
        'is_internal': False,
        'data_format': 'hl7-v2',
        'username': '',
        'username_pretty': '',

        # Protocol fields
        'start_seq': '0b',
        'end_seq': '1c0d',
        'recv_timeout': 30000,
        'idle_timeout': HL7.Default.idle_timeout,
        'keepalive_idle': HL7.Default.keepalive_idle,
        'keepalive_interval': HL7.Default.keepalive_interval,
        'keepalive_probe_count': HL7.Default.keepalive_probe_count,
        'max_msg_size': 2,
        'max_msg_size_unit': 'mb',
        'default_character_encoding': 'utf-8',

        # Quirks
        'normalize_line_endings': True,
        'restore_truncated_msh': True,
        'split_concatenated_messages': True,
        'force_standard_delimiters': True,
        'use_msh18_encoding': True,

        # Tolerance toggles
        'normalize_obx2_value_type': True,
        'replace_invalid_obx2_value_type': True,
        'normalize_invalid_escape_sequences': True,
        'normalize_obx8_abnormal_flags': True,
        'normalize_quadruple_quoted_empty': True,
        'allow_short_encoding_characters': True,
        'fix_off_by_one_field_index': False,

        # Logging
        'should_log_messages': False,
        'should_return_errors': False,
        'is_audit_log_active': False,

        # Parsing
        'should_parse_on_input': True,
        'should_validate': False,

        # Deduplication
        'dedup_ttl_value': 0,
        'dedup_ttl_unit': '',

        # Who the channel accepts a message from
        'security_id': 0,
        'allowed_networks': '',

        # Routing
        'msh3_sending_app': '',
        'msh4_sending_facility': '',
        'msh5_receiving_app': '',
        'msh6_receiving_facility': '',
        'msh9_message_type': '',
        'msh9_trigger_event': '',
        'msh11_processing_id': '',
        'msh12_version_id': '',
        'is_default': False,

        # Destinations
        'destinations': '',
        'respond_from': Respond_From_Service,
        'delivery_mode': Default_Delivery_Mode,

        # REST bridge
        'use_rest': False,
        'rest_only': False,
        'rest_channel_id': 0,
    }

    defaults.update(overrides)
    config = MagicMock()

    for key, value in defaults.items():
        setattr(config, key, value)

    return config

# ################################################################################################################################

def _reset_shared_state() -> 'None':
    """ Resets the module-level shared state so each test starts fresh.
    """
    _shared_state.server = None
    _shared_state.router._routes = []
    _shared_state.listener_channel_count = 0
    _shared_state.internal_port = 0

# ################################################################################################################################
# ################################################################################################################################

class _WiringTestCase(TestCase):
    """ Stands everything the wrapper reaches outside its own process off to one side - the
    listener and the greenlet it would run on - so that what the wrapper hands each of them
    can be read back.
    """

    def setUp(self) -> 'None':

        _reset_shared_state()

        self._patches = ExitStack()

        def _start(name:'str', **kwargs:'any_') -> 'MagicMock':
            return self._patches.enter_context(patch(f'zato.server.generic.api.channel_hl7_mllp.{name}', **kwargs))

        self.mock_server_class = _start('HL7MLLPServer')
        self.mock_spawn = _start('spawn_greenlet')
        self.mock_resolve_port = _start('resolve_internal_port', return_value=_test_internal_port)

    def tearDown(self) -> 'None':
        self._patches.close()
        _reset_shared_state()

# ################################################################################################################################

    def make_wrapper(self, **overrides:'object') -> 'ChannelHL7MLLPWrapper':
        """ Builds a wrapper around a config without running the base class machinery.
        """

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = _make_config(**overrides)
        wrapper.server = MagicMock()

        return wrapper

# ################################################################################################################################

    def get_invoker(self, wrapper:'ChannelHL7MLLPWrapper') -> 'MagicMock':
        """ Returns the stand-in the wrapper reaches the rest of the server through.
        """
        return cast_('MagicMock', wrapper.server)

# ################################################################################################################################

    def get_only_route_settings(self) -> 'RouteSettings':
        """ Returns the settings of the one route registered, which is where everything a
        channel decides about its own messages now lives.
        """

        routes = _shared_state.router._routes
        self.assertEqual(len(routes), 1, 'Expected exactly one route to have been registered')

        return routes[0].settings

# ################################################################################################################################
# ################################################################################################################################

class TestResolveMaxMsgSize(TestCase):
    """ Tests for ChannelHL7MLLPWrapper._resolve_max_msg_size.
    """

    def _make_wrapper(self, max_msg_size:'int', max_msg_size_unit:'str') -> 'ChannelHL7MLLPWrapper':
        """ Creates a wrapper with only the fields needed for _resolve_max_msg_size.
        """
        config = _make_config(max_msg_size=max_msg_size, max_msg_size_unit=max_msg_size_unit)
        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config

        return wrapper

# ################################################################################################################################

    def test_max_msg_size_kb(self) -> 'None':
        """ Config max_msg_size=500 with unit='kb' produces 512000 bytes.
        """
        wrapper = self._make_wrapper(500, 'kb')

        result = wrapper._resolve_max_msg_size()

        self.assertEqual(result, 500 * 1024)

# ################################################################################################################################

    def test_max_msg_size_mb(self) -> 'None':
        """ Config max_msg_size=2 with unit='mb' produces 2097152 bytes.
        """
        wrapper = self._make_wrapper(2, 'mb')

        result = wrapper._resolve_max_msg_size()

        self.assertEqual(result, 2 * 1048576)

# ################################################################################################################################
# ################################################################################################################################

class TestRouteSettingsWiring(_WiringTestCase):
    """ Tests that each channel's own configuration reaches the route registered for it, which
    is what the listener reads once a message has been matched to that channel.
    """

# ################################################################################################################################

    def test_recv_timeout_conversion(self) -> 'None':
        """ Config recv_timeout=250 (milliseconds) is passed as 0.25 seconds.
        """
        wrapper = self.make_wrapper(recv_timeout=250)

        wrapper._init_impl()

        self.assertAlmostEqual(self.get_only_route_settings().recv_timeout, 0.25)

# ################################################################################################################################

    def test_encoding_passed(self) -> 'None':
        """ Config default_character_encoding='iso-8859-1' reaches the route.
        """
        wrapper = self.make_wrapper(default_character_encoding='iso-8859-1')

        wrapper._init_impl()

        self.assertEqual(self.get_only_route_settings().default_character_encoding, 'iso-8859-1')

# ################################################################################################################################

    def test_quirks_all_off(self) -> 'None':
        """ All 5 quirks set to False reach the route as False.
        """
        wrapper = self.make_wrapper(
            normalize_line_endings=False,
            restore_truncated_msh=False,
            split_concatenated_messages=False,
            force_standard_delimiters=False,
            use_msh18_encoding=False,
        )

        wrapper._init_impl()

        settings = self.get_only_route_settings()

        self.assertFalse(settings.should_normalize_line_endings)
        self.assertFalse(settings.should_restore_truncated_msh)
        self.assertFalse(settings.should_split_concatenated_messages)
        self.assertFalse(settings.should_force_standard_delimiters)
        self.assertFalse(settings.should_use_msh18_encoding)

# ################################################################################################################################

    def test_should_return_errors_passed(self) -> 'None':
        """ Config should_return_errors=True reaches the route.
        """
        wrapper = self.make_wrapper(should_return_errors=True)

        wrapper._init_impl()

        self.assertTrue(self.get_only_route_settings().should_return_errors)

# ################################################################################################################################

    def test_max_msg_size_bytes_passed(self) -> 'None':
        """ Config max_msg_size=500, max_msg_size_unit='kb' reaches the route as 512000 bytes.
        """
        wrapper = self.make_wrapper(max_msg_size=500, max_msg_size_unit='kb')

        wrapper._init_impl()

        self.assertEqual(self.get_only_route_settings().max_message_size, 500 * 1024)

# ################################################################################################################################

    def test_should_log_messages_passed(self) -> 'None':
        """ Config should_log_messages=True reaches the route.
        """
        wrapper = self.make_wrapper(should_log_messages=True)

        wrapper._init_impl()

        self.assertTrue(self.get_only_route_settings().should_log_messages)

# ################################################################################################################################

    def test_allowed_networks_passed(self) -> 'None':
        """ The networks a channel limits itself to reach the route as configured.
        """
        wrapper = self.make_wrapper(allowed_networks='10.0.0.0/8, 192.168.1.5')

        wrapper._init_impl()

        networks = [str(one) for one in self.get_only_route_settings().allowed_networks]
        self.assertEqual(networks, ['10.0.0.0/8', '192.168.1.5/32'])

# ################################################################################################################################

    def test_each_channel_gets_its_own_deduplicator(self) -> 'None':
        """ Two channels must not share a memory of what they have already seen, or one would
        silence the other's messages.
        """

        first = self.make_wrapper(name='first', dedup_ttl_value=1, dedup_ttl_unit='hours')
        first._init_impl()

        second = self.make_wrapper(name='second', dedup_ttl_value=1, dedup_ttl_unit='hours')
        second._init_impl()

        routes = _shared_state.router._routes
        self.assertEqual(len(routes), 2)

        self.assertIsNotNone(routes[0].settings.deduplicator)
        self.assertIsNot(routes[0].settings.deduplicator, routes[1].settings.deduplicator)

# ################################################################################################################################

    def test_no_deduplicator_when_not_asked_for(self) -> 'None':
        """ A channel that sets no window remembers nothing and pays for nothing.
        """
        wrapper = self.make_wrapper(dedup_ttl_value=0)

        wrapper._init_impl()

        self.assertIsNone(self.get_only_route_settings().deduplicator)

# ################################################################################################################################
# ################################################################################################################################

class TestListenerWiring(_WiringTestCase):
    """ Tests what the listener itself is started with, as against what each channel brings.
    """

# ################################################################################################################################

    def test_listener_started_once_for_two_channels(self) -> 'None':
        """ The listener is shared, so a second channel joins the one already running rather
        than standing another up.
        """

        first = self.make_wrapper(name='first')
        first._init_impl()

        second = self.make_wrapper(name='second')
        second._init_impl()

        self.mock_server_class.assert_called_once()

# ################################################################################################################################

    def test_the_listener_binds_the_port_the_backend_names(self) -> 'None':
        """ Nothing tells the load balancer where the listener is - its configuration already
        names the port, so the listener has to be the one to match it.
        """

        wrapper = self.make_wrapper(name='first')
        wrapper._init_impl()

        self.assertEqual(_shared_state.internal_port, _test_internal_port)

# ################################################################################################################################

    def test_listener_stops_with_its_last_channel(self) -> 'None':
        """ The listener comes down when the last channel using it goes, and not before.
        """

        first = self.make_wrapper(name='first')
        first._init_impl()

        second = self.make_wrapper(name='second')
        second._init_impl()

        listener = cast_('MagicMock', _shared_state.server)

        first._delete()
        self.assertIsNotNone(_shared_state.server, 'The listener stopped while a channel still used it')

        second._delete()
        self.assertIsNone(_shared_state.server, 'The listener outlived its last channel')

        listener.stop.assert_called_once()

# ################################################################################################################################
# ################################################################################################################################

class TestIsActiveRouting(_WiringTestCase):
    """ Tests for the is_active flag controlling route registration.
    """

# ################################################################################################################################

    def test_inactive_channel_no_route(self) -> 'None':
        """ is_active=False means router.add_route is not called.
        """
        wrapper = self.make_wrapper(is_active=False)

        wrapper._init_impl()

        self.assertFalse(_shared_state.router.has_routes())

# ################################################################################################################################

    def test_active_channel_adds_route(self) -> 'None':
        """ is_active=True means router.add_route is called and route exists.
        """
        wrapper = self.make_wrapper(is_active=True)

        wrapper._init_impl()

        self.assertTrue(_shared_state.router.has_routes())

# ################################################################################################################################

    def test_inactive_then_active(self) -> 'None':
        """ Toggle is_active from False to True via _delete + _init_impl, verify route appears.
        """

        wrapper = self.make_wrapper(is_active=False)

        wrapper._init_impl()
        self.assertFalse(_shared_state.router.has_routes())

        # .. delete it ..
        wrapper._delete()

        # .. re-create as active ..
        wrapper.config.is_active = True
        wrapper._init_impl()

        self.assertTrue(_shared_state.router.has_routes())

# ################################################################################################################################

    def test_active_then_inactive(self) -> 'None':
        """ Toggle is_active from True to False via _delete + _init_impl, verify route is removed.
        """

        wrapper = self.make_wrapper(is_active=True)

        wrapper._init_impl()
        self.assertTrue(_shared_state.router.has_routes())

        # .. delete it ..
        wrapper._delete()

        # .. re-create as inactive ..
        wrapper.config.is_active = False
        wrapper._init_impl()

        self.assertFalse(_shared_state.router.has_routes())

# ################################################################################################################################
# ################################################################################################################################

class TestIsDefaultRouting(_WiringTestCase):
    """ Tests for the is_default flag being passed through to the router.
    """

# ################################################################################################################################

    def test_is_default_passed_true(self) -> 'None':
        """ is_default=True reaches the router as is_default=True on the route.
        """
        wrapper = self.make_wrapper(is_default=True)

        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertTrue(route.is_default)

# ################################################################################################################################

    def test_is_default_passed_false(self) -> 'None':
        """ is_default=False reaches the router as is_default=False on the route.
        """
        wrapper = self.make_wrapper(is_default=False)

        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertFalse(route.is_default)

# ################################################################################################################################

    def test_is_default_toggle(self) -> 'None':
        """ Change is_default from False to True via re-init, verify the router sees the updated value.
        """

        wrapper = self.make_wrapper(is_default=False)

        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertFalse(route.is_default)

        # .. delete and re-create as default ..
        wrapper._delete()
        wrapper.config.is_default = True
        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertTrue(route.is_default)

# ################################################################################################################################
# ################################################################################################################################

class TestRestOnlyMode(_WiringTestCase):
    """ Tests for the rest_only flag skipping the MLLP listener.
    """

# ################################################################################################################################

    def test_rest_only_skips_mllp_server(self) -> 'None':
        """ rest_only=True means the shared MLLP server is not started.
        """
        wrapper = self.make_wrapper(rest_only=True, use_rest=True)

        wrapper._init_impl()

        # .. the MLLP server constructor was never called ..
        self.mock_server_class.assert_not_called()

        # .. no route was registered ..
        self.assertFalse(_shared_state.router.has_routes())

# ################################################################################################################################

    def test_rest_only_false_starts_mllp_server(self) -> 'None':
        """ rest_only=False with use_rest=True still starts the MLLP server normally.
        """
        wrapper = self.make_wrapper(rest_only=False, use_rest=True)

        wrapper._init_impl()

        # .. the MLLP server was started ..
        self.mock_server_class.assert_called_once()

        # .. route was registered ..
        self.assertTrue(_shared_state.router.has_routes())

# ################################################################################################################################

    def test_rest_only_channel_does_not_hold_the_listener_up(self) -> 'None':
        """ A channel that only has a REST bridge never started the listener, so deleting the
        one channel that did must still bring it down.
        """

        listening = self.make_wrapper(name='listening')
        listening._init_impl()

        rest_only = self.make_wrapper(name='rest-only', rest_only=True, use_rest=True)
        rest_only._init_impl()

        listening._delete()

        self.assertIsNone(_shared_state.server, 'A channel that never used the listener kept it alive')

# ################################################################################################################################
# ################################################################################################################################

class TestRestChannelCleanup(_WiringTestCase):
    """ Tests for the backing REST channel cleanup on MLLP channel delete.
    """

# ################################################################################################################################

    def test_delete_invokes_http_soap_delete(self) -> 'None':
        """ Deleting an MLLP channel with rest_channel_id invokes zato.http-soap.delete.
        """
        wrapper = self.make_wrapper(use_rest=True, rest_channel_id=42)

        # .. init first so the channel is counted ..
        wrapper._init_impl()

        # .. now delete ..
        wrapper._delete()

        # .. verify the server's invoke was called to delete the REST channel ..
        self.get_invoker(wrapper).invoke.assert_called_with('zato.http-soap.delete', {
            'id': 42,
            'cluster_id': 1,
        })

# ################################################################################################################################

    def test_delete_no_rest_channel_no_invoke(self) -> 'None':
        """ Deleting an MLLP channel without rest_channel_id does not invoke zato.http-soap.delete.
        """
        wrapper = self.make_wrapper(use_rest=False, rest_channel_id=0)

        wrapper._init_impl()
        wrapper._delete()

        # .. invoke was only called from _invoke_service context, not for REST cleanup ..
        self.get_invoker(wrapper).invoke.assert_not_called()

# ################################################################################################################################

    def test_delete_leaves_alone_a_rest_channel_already_gone(self) -> 'None':
        """ Every worker holding the channel runs this, so whoever finds the REST channel
        already deleted must not try to delete it a second time.
        """

        wrapper = self.make_wrapper(use_rest=True, rest_channel_id=42)
        wrapper._init_impl()

        # Asking after a channel that is no longer there is what raises
        def _invoke(service_name:'str', request:'object') -> 'object':
            if service_name == 'zato.http-soap.get':
                raise Exception('No such channel')
            return None

        invoker = self.get_invoker(wrapper)
        invoker.invoke.side_effect = _invoke

        wrapper._delete()

        invoked_services = [one.args[0] for one in invoker.invoke.call_args_list]
        self.assertNotIn('zato.http-soap.delete', invoked_services)

# ################################################################################################################################
# ################################################################################################################################
