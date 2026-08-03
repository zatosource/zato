# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import TestCase

# Zato
from zato.common.defaults import http_plain_server_port
from zato.common.hl7.mllp.haproxy import Env_Port_Name, Internal_Port_Base, resolve_internal_port

# ################################################################################################################################
# ################################################################################################################################

# The configuration the load balancer ships with, which is where the other end of this port lives
_config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..', '..',
    'zato-common', 'src', 'zato', 'common', 'pubsub', 'server', 'haproxy.cfg',
)

# ################################################################################################################################
# ################################################################################################################################

class TestResolveInternalPort(TestCase):
    """ The listener's port has to follow from the server's own identity, because a port that were
    picked at runtime would leave the load balancer needing to be told about it every time.
    """

# ################################################################################################################################

    def test_first_server_gets_the_base_port(self) -> 'None':
        """ The first server in a cluster sits at the base of the range.
        """
        self.assertEqual(resolve_internal_port(http_plain_server_port), Internal_Port_Base)

# ################################################################################################################################

    def test_each_server_keeps_its_distance_from_the_first(self) -> 'None':
        """ A server sits as far above the base as its own port does above the first server's.
        """
        self.assertEqual(resolve_internal_port(http_plain_server_port + 3), Internal_Port_Base + 3)

# ################################################################################################################################

    def test_the_same_server_always_resolves_the_same_port(self) -> 'None':
        """ Asking twice gives the same answer, which is the whole point of not picking one.
        """
        first = resolve_internal_port(http_plain_server_port + 1)
        second = resolve_internal_port(http_plain_server_port + 1)

        self.assertEqual(first, second)

# ################################################################################################################################

    def test_an_explicit_port_wins(self) -> 'None':
        """ A port named outright is used as it stands.
        """

        os.environ[Env_Port_Name] = '24680'

        try:
            self.assertEqual(resolve_internal_port(http_plain_server_port), 24680)
        finally:
            del os.environ[Env_Port_Name]

# ################################################################################################################################
# ################################################################################################################################

class TestBackendPointsAtTheListener(TestCase):
    """ The load balancer's MLLP backend is a plain line in a file that nothing rewrites, so the
    only thing holding it to the listener is that both are named the same way.
    """

    def read_config(self) -> 'str':
        with open(_config_path) as config_file:
            return config_file.read()

# ################################################################################################################################

    def test_the_backend_names_the_listener_port(self) -> 'None':
        """ A backend pointing anywhere else would accept every sender and then hang up on it.
        """

        expected = f'server server1 127.0.0.1:${{{Env_Port_Name}}}'
        self.assertIn(expected, self.read_config())

# ################################################################################################################################

    def test_the_backend_asks_for_the_sender_to_be_announced(self) -> 'None':
        """ Without this the listener would have no idea who is calling, since every connection
        would appear to come from the load balancer itself.
        """

        prefix = f'server server1 127.0.0.1:${{{Env_Port_Name}}}'
        config_text = self.read_config()
        line = next(one for one in config_text.splitlines() if one.strip().startswith(prefix))

        self.assertIn('send-proxy-v2-ssl-cn', line)

# ################################################################################################################################
# ################################################################################################################################
