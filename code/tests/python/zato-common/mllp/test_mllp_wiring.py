# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.server.generic.api.channel_hl7_mllp import ChannelHL7MLLPWrapper, _shared_state

# ################################################################################################################################
# ################################################################################################################################

def _make_config(**overrides:'object') -> 'MagicMock':
    """ Builds a mock Bunch-like config object with all MLLP channel fields populated.
    """

    defaults = {
        'name': 'test-mllp-channel',
        'service': 'test.hl7.mllp.echo',
        'is_active': True,
        'username': '',
        'username_pretty': '',

        # Protocol fields
        'start_seq': '0b',
        'end_seq': '1c0d',
        'recv_timeout': 30000,
        'max_msg_size': 2,
        'max_msg_size_unit': 'mb',
        'default_character_encoding': 'utf-8',

        # Quirks
        'normalize_line_endings': True,
        'repair_truncated_msh': True,
        'split_concatenated_messages': True,
        'force_standard_delimiters': True,
        'use_msh18_encoding': True,

        # Logging
        'should_log_messages': False,
        'should_return_errors': False,

        # Deduplication
        'dedup_ttl_value': 0,
        'dedup_ttl_unit': '',

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
    _shared_state.channel_count = 0
    _shared_state.internal_port = 0
    _shared_state.haproxy_config_path = ''

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

class TestServerWiring(TestCase):
    """ Tests that _ensure_shared_server_started passes all config fields to HL7MLLPServer.
    """

    def setUp(self) -> 'None':
        _reset_shared_state()

    def tearDown(self) -> 'None':
        _reset_shared_state()

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_recv_timeout_conversion(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Config recv_timeout=250 (milliseconds) is passed as 0.25 seconds.
        """
        config = _make_config(recv_timeout=250)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._ensure_shared_server_started()

        _, kwargs = mock_server_class.call_args
        self.assertAlmostEqual(kwargs['receive_timeout'], 0.25)

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_encoding_passed(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Config default_character_encoding='iso-8859-1' reaches the server constructor.
        """
        config = _make_config(default_character_encoding='iso-8859-1')

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._ensure_shared_server_started()

        _, kwargs = mock_server_class.call_args
        self.assertEqual(kwargs['default_character_encoding'], 'iso-8859-1')

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_quirks_all_off(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ All 5 quirks set to False reach the server constructor as False.
        """
        config = _make_config(
            normalize_line_endings=False,
            repair_truncated_msh=False,
            split_concatenated_messages=False,
            force_standard_delimiters=False,
            use_msh18_encoding=False,
        )

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._ensure_shared_server_started()

        _, kwargs = mock_server_class.call_args
        self.assertFalse(kwargs['should_normalize_line_endings'])
        self.assertFalse(kwargs['should_repair_truncated_msh'])
        self.assertFalse(kwargs['should_split_concatenated_messages'])
        self.assertFalse(kwargs['should_force_standard_delimiters'])
        self.assertFalse(kwargs['should_use_msh18_encoding'])

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_should_return_errors_passed(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Config should_return_errors=True reaches the server constructor.
        """
        config = _make_config(should_return_errors=True)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._ensure_shared_server_started()

        _, kwargs = mock_server_class.call_args
        self.assertTrue(kwargs['should_return_errors'])

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_max_msg_size_bytes_passed(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Config max_msg_size=500, max_msg_size_unit='kb' reaches the server as 512000 bytes.
        """
        config = _make_config(max_msg_size=500, max_msg_size_unit='kb')

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._ensure_shared_server_started()

        _, kwargs = mock_server_class.call_args
        self.assertEqual(kwargs['max_message_size'], 500 * 1024)

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_should_log_messages_passed(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Config should_log_messages=True reaches the server constructor.
        """
        config = _make_config(should_log_messages=True)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._ensure_shared_server_started()

        _, kwargs = mock_server_class.call_args
        self.assertTrue(kwargs['should_log_messages'])

# ################################################################################################################################
# ################################################################################################################################

class TestIsActiveRouting(TestCase):
    """ Tests for the is_active flag controlling route registration.
    """

    def setUp(self) -> 'None':
        _reset_shared_state()

    def tearDown(self) -> 'None':
        _reset_shared_state()

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_inactive_channel_no_route(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ is_active=False means router.add_route is not called.
        """
        config = _make_config(is_active=False)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()

        self.assertFalse(_shared_state.router.has_routes())

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_active_channel_adds_route(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ is_active=True means router.add_route is called and route exists.
        """
        config = _make_config(is_active=True)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()

        self.assertTrue(_shared_state.router.has_routes())

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_inactive_then_active(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Toggle is_active from False to True via _delete + _init_impl, verify route appears.
        """

        # Create inactive channel ..
        config = _make_config(is_active=False)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()
        self.assertFalse(_shared_state.router.has_routes())

        # .. delete it ..
        wrapper._delete()

        # .. re-create as active ..
        config.is_active = True
        wrapper._init_impl()

        self.assertTrue(_shared_state.router.has_routes())

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_active_then_inactive(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Toggle is_active from True to False via _delete + _init_impl, verify route is removed.
        """

        # Create active channel ..
        config = _make_config(is_active=True)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()
        self.assertTrue(_shared_state.router.has_routes())

        # .. delete it ..
        wrapper._delete()

        # .. re-create as inactive ..
        config.is_active = False
        wrapper._init_impl()

        self.assertFalse(_shared_state.router.has_routes())

# ################################################################################################################################
# ################################################################################################################################

class TestIsDefaultRouting(TestCase):
    """ Tests for the is_default flag being passed through to the router.
    """

    def setUp(self) -> 'None':
        _reset_shared_state()

    def tearDown(self) -> 'None':
        _reset_shared_state()

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_is_default_passed_true(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ is_default=True reaches the router as is_default=True on the route.
        """
        config = _make_config(is_default=True)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertTrue(route.is_default)

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_is_default_passed_false(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ is_default=False reaches the router as is_default=False on the route.
        """
        config = _make_config(is_default=False)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertFalse(route.is_default)

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_is_default_toggle(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Change is_default from False to True via re-init, verify the router sees the updated value.
        """

        # Create non-default channel ..
        config = _make_config(is_default=False)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertFalse(route.is_default)

        # .. delete and re-create as default ..
        wrapper._delete()
        config.is_default = True
        wrapper._init_impl()

        route = _shared_state.router._routes[0]
        self.assertTrue(route.is_default)

# ################################################################################################################################
# ################################################################################################################################

class TestRestOnlyMode(TestCase):
    """ Tests for the rest_only flag skipping the MLLP listener.
    """

    def setUp(self) -> 'None':
        _reset_shared_state()

    def tearDown(self) -> 'None':
        _reset_shared_state()

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_rest_only_skips_mllp_server(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ rest_only=True means the shared MLLP server is not started.
        """
        config = _make_config(rest_only=True, use_rest=True)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()

        # .. the MLLP server constructor was never called ..
        mock_server_class.assert_not_called()

        # .. no route was registered ..
        self.assertFalse(_shared_state.router.has_routes())

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_rest_only_false_starts_mllp_server(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ rest_only=False with use_rest=True still starts the MLLP server normally.
        """
        config = _make_config(rest_only=False, use_rest=True)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()

        # .. the MLLP server was started ..
        mock_server_class.assert_called_once()

        # .. route was registered ..
        self.assertTrue(_shared_state.router.has_routes())

# ################################################################################################################################
# ################################################################################################################################

class TestRestChannelCleanup(TestCase):
    """ Tests for the backing REST channel cleanup on MLLP channel delete.
    """

    def setUp(self) -> 'None':
        _reset_shared_state()

    def tearDown(self) -> 'None':
        _reset_shared_state()

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_delete_invokes_http_soap_delete(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Deleting an MLLP channel with rest_channel_id invokes zato.http-soap.delete.
        """
        config = _make_config(use_rest=True, rest_channel_id=42)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        # .. init first so channel_count is incremented ..
        wrapper._init_impl()

        # .. now delete ..
        wrapper._delete()

        # .. verify the server's invoke was called to delete the REST channel ..
        wrapper.server.invoke.assert_called_with('zato.http-soap.delete', {
            'id': 42,
            'cluster_id': 1,
        })

# ################################################################################################################################

    @patch('zato.server.generic.api.channel_hl7_mllp.reload_haproxy')
    @patch('zato.server.generic.api.channel_hl7_mllp.update_mllp_backend_port')
    @patch('zato.server.generic.api.channel_hl7_mllp.find_haproxy_config', return_value='/test/haproxy.cfg')
    @patch('zato.server.generic.api.channel_hl7_mllp.spawn_greenlet')
    @patch('zato.server.generic.api.channel_hl7_mllp.resolve_internal_port', return_value=19000)
    @patch('zato.server.generic.api.channel_hl7_mllp.HL7MLLPServer')
    def test_delete_no_rest_channel_no_invoke(
        self,
        mock_server_class:'MagicMock',
        mock_resolve_port:'MagicMock',
        mock_spawn:'MagicMock',
        mock_find_haproxy:'MagicMock',
        mock_update_port:'MagicMock',
        mock_reload:'MagicMock',
        ) -> 'None':
        """ Deleting an MLLP channel without rest_channel_id does not invoke zato.http-soap.delete.
        """
        config = _make_config(use_rest=False, rest_channel_id=0)

        wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)
        wrapper.config = config
        wrapper.server = MagicMock()

        wrapper._init_impl()
        wrapper._delete()

        # .. invoke was only called from _invoke_service context, not for REST cleanup ..
        wrapper.server.invoke.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################
