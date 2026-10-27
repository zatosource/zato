# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.common.webapp.server import serve

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_env_host = 'Zato_Test_Web_App_Host'
_env_port = 'Zato_Test_Web_App_Port'

_default_host = '127.0.0.1'
_default_port = '8088'

# The thread count the API portal asks for
_portal_thread_count = 32

# ################################################################################################################################
# ################################################################################################################################

class ServeThreadsTestCase(TestCase):
    """ An application may ask gunicorn for threaded workers, and every other one runs in a single thread.
    """

# ################################################################################################################################

    def _serve(self, **kwargs:'int') -> 'anydict':
        """ Serves an application with gunicorn mocked out and returns the options gunicorn received.
        """
        with patch('zato.common.webapp.server.WebAppServer') as web_app_server:
            serve(MagicMock(), 'the test application', _env_host, _env_port, _default_host, _default_port, **kwargs)

        call = web_app_server.call_args
        out = call.args[1]

        return out

# ################################################################################################################################

    def test_the_default_is_one_thread(self) -> 'None':
        options = self._serve()
        self.assertEqual(options['threads'], 1)

# ################################################################################################################################

    def test_an_application_asks_for_threads(self) -> 'None':
        options = self._serve(thread_count=_portal_thread_count)
        self.assertEqual(options['threads'], _portal_thread_count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
