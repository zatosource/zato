# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import platform
import stat
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from tempfile import TemporaryDirectory
from threading import Thread
from unittest import main, TestCase

# Zato
from zato.common.api import On_Prem_Gateway
from zato.common.util import on_prem_gateway

# ################################################################################################################################
# ################################################################################################################################

_Installed_Version = '4.1.aaaaaaa'
_Latest_Version = '4.1.bbbbbbb'

_Architecture = {'x86_64': 'amd64', 'aarch64': 'arm64'}[platform.machine()]

# A binary stands in for the gateway by reporting its version the way the gateway does.
_Binary_Template = """#!/bin/sh
echo "zato-on-prem-gateway {version}"
"""

# ################################################################################################################################
# ################################################################################################################################

class _ReleaseHandler(BaseHTTPRequestHandler):
    """ Serves the two addresses of a release page - the redirect of the latest release to its tag,
    and the download of an asset of that release.
    """
    latest_version = _Latest_Version

    def do_HEAD(self) -> 'None':

        if self.path == '/releases/latest':
            self.send_response(302)
            self.send_header('Location', '/releases/tag/' + self.latest_version)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()

    def do_GET(self) -> 'None':

        expected_path = f'/releases/download/{self.latest_version}/zato-on-prem-gateway-linux-{_Architecture}'

        if self.path != expected_path:
            self.send_response(404)
            self.end_headers()
            return

        body = _Binary_Template.format(version=self.latest_version).encode('utf8')

        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        _ = self.wfile.write(body)

    def log_message(self, *args:'object') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class UpdateBinaryTestCase(TestCase):

    def setUp(self) -> 'None':

        self.temp_dir = TemporaryDirectory()
        self.binary_path = os.path.join(self.temp_dir.name, 'zato-on-prem-gateway')

        with open(self.binary_path, 'w') as binary_file:
            _ = binary_file.write(_Binary_Template.format(version=_Installed_Version))

        os.chmod(self.binary_path, stat.S_IRWXU)

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), _ReleaseHandler)
        self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        address = 'http://127.0.0.1:{}'.format(self.server.server_address[1])

        self.original = (
            On_Prem_Gateway.Update.Binary_Path,
            On_Prem_Gateway.Update.Latest_URL,
            On_Prem_Gateway.Update.Download_URL,
        )

        On_Prem_Gateway.Update.Binary_Path = self.binary_path
        On_Prem_Gateway.Update.Latest_URL = address + '/releases/latest'
        On_Prem_Gateway.Update.Download_URL = address + '/releases/download/{version}/zato-on-prem-gateway-linux-{architecture}'

    def tearDown(self) -> 'None':

        binary_path, latest_url, download_url = self.original

        On_Prem_Gateway.Update.Binary_Path = binary_path
        On_Prem_Gateway.Update.Latest_URL = latest_url
        On_Prem_Gateway.Update.Download_URL = download_url

        self.server.shutdown()
        self.server.server_close()
        self.temp_dir.cleanup()

# ################################################################################################################################

    def test_a_newer_release_replaces_the_binary(self) -> 'None':

        is_updated = on_prem_gateway.update_binary()

        self.assertTrue(is_updated)
        self.assertEqual(on_prem_gateway.get_installed_version(), _Latest_Version)
        self.assertFalse(os.path.exists(self.binary_path + '.new'))

# ################################################################################################################################

    def test_the_latest_release_leaves_the_binary_in_place(self) -> 'None':

        _ = on_prem_gateway.update_binary()
        is_updated = on_prem_gateway.update_binary()

        self.assertFalse(is_updated)
        self.assertEqual(on_prem_gateway.get_installed_version(), _Latest_Version)

# ################################################################################################################################

    def test_the_latest_version_is_the_tag_of_the_redirect(self) -> 'None':
        self.assertEqual(on_prem_gateway.get_latest_version(), _Latest_Version)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
