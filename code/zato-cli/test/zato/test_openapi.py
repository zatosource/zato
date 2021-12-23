# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from traceback import format_exc

from unittest import main, TestCase

# sh
import sh
from sh import ErrorReturnCode

# Zato
from zato.common.test.config import TestConfig
from zato.common.test import rand_string, rand_unicode

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sh import RunningCommand
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

template = """

channel_plain_http:

  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/enmasse1/{test_suffix}
    params_pri: channel-params-over-msg
    sec_def: zato-no-security
    service: pub.zato.ping
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/enmasse1/{test_suffix}

  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/enmasse2/{test_suffix}
    params_pri: channel-params-over-msg
    sec_def: zato-no-security
    service: pub.zato.ping
    service_name: pub.zato.ping
    transport: plain_http
    url_path: /test/enmasse2/{test_suffix}

zato_generic_connection:
    - address: ws://localhost:12345
      cache_expiry: 0
      has_auto_reconnect: true
      is_active: true
      is_channel: true
      is_internal: false
      is_outconn: false
      is_zato: true
      name: test.enmasse.{test_suffix}
      on_connect_service_name: pub.zato.ping
      on_message_service_name: pub.zato.ping
      pool_size: 1
      sec_use_rbac: false
      security_def: ZATO_NONE
      subscription_list:
      type_: outconn-wsx
"""

# ################################################################################################################################
# ################################################################################################################################

class APISpecTestCase(TestCase):

# ################################################################################################################################

    def _warn_on_error(self, stdout:'any_', stderr:'any_', has_exception:'bool'=True) -> 'None':

        if has_exception:
            logger.warning(format_exc())

        logger.warning('stdout -> %r', stdout)
        logger.warning('stderr -> %r', stderr)

# ################################################################################################################################

    def _assert_command_line_result(self, out:'RunningCommand', file_path:'str') -> 'None':

        self.assertEqual(out.exit_code, 0)

        # This is the information returned to user
        expected = 'Output saved to '+ file_path + '\n'

        # This is stdout that the command returned
        stdout = out.stdout.decode('utf8')
        stderr = out.stderr.decode('utf8')

        # Make sure the expected information is in stdout
        if expected not in stdout:
            self._warn_on_error(stdout, stderr, has_exception=False)
            msg = 'Could not find {!r} in {!r}'
            self.fail(msg.format(expected, stdout))

# ################################################################################################################################

    def _invoke_command(self, file_path:'str', require_ok:'bool'=True) -> 'RunningCommand':

        # A shortcut
        command = sh.zato # type: ignore

        # Invoke enmasse ..
        out = command('openapi', TestConfig.server_location,
            '--exclude', '""', '--include', 'helpers.dataclass-service',
            '--file', file_path,
            '--verbose')

        # .. if told to, make sure there was no error in stdout/stderr ..
        if require_ok:
            self._assert_command_line_result(out, file_path)

        return out

# ################################################################################################################################

    def test_apispec(self) -> 'None':

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = 'zato-test-' + test_suffix + '.yaml'
        file_path = os.path.join(tmp_dir, file_name)

        try:
            # Invoke openapi to create a definition ..
            self._invoke_command(file_path)

        except ErrorReturnCode as e:

            stdout = e.stdout # type: bytes
            stdout = stdout.decode('utf8') # type: ignore
            stderr = e.stderr

            self._warn_on_error(stdout, stderr)
            self.fail('Caught an exception while invoking openapi')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
