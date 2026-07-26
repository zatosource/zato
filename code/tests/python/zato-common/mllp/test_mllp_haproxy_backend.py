# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
from unittest import TestCase

# Zato
from zato.common.defaults import http_plain_server_port
from zato.common.hl7.mllp.haproxy import (
    ensure_mllp_backend_server,
    Env_Port_Name,
    Internal_Port_Base,
    resolve_internal_port,
    Servers_Block_End,
    Servers_Block_Start,
)

# ################################################################################################################################
# ################################################################################################################################

# A configuration with the marker the generated server lines go between, as the real one has
_config_template = f"""
backend mllp_backend
    mode tcp
    timeout server 7d
    {Servers_Block_Start}
    {Servers_Block_End}
"""

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

class TestBackendServerLine(TestCase):
    """ Every server writes its own line into the one configuration file they share, so what
    matters is that a server can add or correct its own without touching anyone else's.
    """

    def setUp(self) -> 'None':

        self.tmp_dir = tempfile.mkdtemp(prefix='mllp-haproxy-')
        self.config_path = os.path.join(self.tmp_dir, 'haproxy.cfg')

        with open(self.config_path, 'w') as config_file:
            _ = config_file.write(_config_template)

    def tearDown(self) -> 'None':
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

# ################################################################################################################################

    def read_config(self) -> 'str':
        with open(self.config_path) as config_file:
            return config_file.read()

# ################################################################################################################################

    def get_server_lines(self) -> 'list[str]':
        """ Returns the generated server lines, which is everything between the markers.
        """

        config_text = self.read_config()

        start = config_text.index(Servers_Block_Start) + len(Servers_Block_Start)
        end = config_text.index(Servers_Block_End)

        out = [one.strip() for one in config_text[start:end].splitlines() if one.strip()]
        return out

# ################################################################################################################################

    def test_a_server_writes_its_own_line(self) -> 'None':
        """ A server that has started puts itself where the load balancer will look for it.
        """

        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31312)

        lines = self.get_server_lines()

        self.assertEqual(len(lines), 1)
        self.assertIn('127.0.0.1:31312', lines[0])

# ################################################################################################################################

    def test_the_line_asks_for_the_sender_to_be_announced(self) -> 'None':
        """ Without this the listener would have no idea who is calling, since every connection
        would appear to come from the load balancer itself.
        """

        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31312)

        self.assertIn('send-proxy-v2-ssl-cn', self.get_server_lines()[0])

# ################################################################################################################################

    def test_writing_the_same_line_twice_leaves_one(self) -> 'None':
        """ A server that restarts must correct its own line rather than add a second.
        """

        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31312)
        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31312)

        self.assertEqual(len(self.get_server_lines()), 1)

# ################################################################################################################################

    def test_a_server_that_moved_corrects_its_own_line(self) -> 'None':
        """ A server whose port has changed replaces what it said before, and says it only once.
        """

        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31312)
        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31399)

        lines = self.get_server_lines()

        self.assertEqual(len(lines), 1)
        self.assertIn('127.0.0.1:31399', lines[0])
        self.assertNotIn('31312', lines[0])

# ################################################################################################################################

    def test_one_server_leaves_another_alone(self) -> 'None':
        """ Several servers share the file, so writing a line is not rewriting the block.
        """

        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31312)
        _ = ensure_mllp_backend_server(self.config_path, 'server2', 31313)

        lines = self.get_server_lines()

        self.assertEqual(len(lines), 2)

        addresses = sorted(one.split()[2] for one in lines)
        self.assertEqual(addresses, ['127.0.0.1:31312', '127.0.0.1:31313'])

# ################################################################################################################################

    def test_the_rest_of_the_configuration_is_left_as_it_was(self) -> 'None':
        """ Only the block between the markers is the server's to write.
        """

        _ = ensure_mllp_backend_server(self.config_path, 'server1', 31312)

        config_text = self.read_config()

        self.assertIn('backend mllp_backend', config_text)
        self.assertIn('timeout server 7d', config_text)
        self.assertIn('mode tcp', config_text)

# ################################################################################################################################
# ################################################################################################################################
