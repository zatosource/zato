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
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sh import RunningCommand

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
    - address2: ws://localhost:12345
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

class CommandLineTestCase(TestCase):

# ################################################################################################################################

    def _assert_command_line_result(self, out:'RunningCommand') -> 'None':

        self.assertEqual(out.exit_code, 0)

        stdout = out.stdout.decode('utf8')
        stderr = out.stdout.decode('utf8')

        if 'error' in stdout:
            logger.warning(format_exc())
            logger.warning('stdout -> %s', stdout)
            logger.warning('stderr -> %s', stderr)

            self.fail('Found an error in stdout while invoking enmasse')

        if 'error' in stderr:
            logger.warning(format_exc())
            logger.warning('stdout -> %s', stdout)
            logger.warning('stderr -> %s', stderr)

            self.fail('Found an error in stderr while invoking enmasse')

# ################################################################################################################################

    def _invoke_enmasse(self, config_path:'str') -> 'None':

        # A shortcut
        command = sh.zato # type: ignore

        # Invoke enmasse ..
        out = command('enmasse', TestConfig.server_location,
            '--import', '--input', config_path, '--replace-odb-objects', '--verbose')

        # .. make sure there was no error in stdout/stderr ..
        self._assert_command_line_result(out)

# ################################################################################################################################

    def test_command_line(self) -> 'None':

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = 'zato-enmasse-' + test_suffix + '.yaml'
        config_path = os.path.join(tmp_dir, file_name)

        data = template.format(test_suffix=test_suffix)

        f = open_w(config_path)
        f.write(data)
        f.close()

        try:
            # Invoke enmasse to create objects ..
            self._invoke_enmasse(config_path)

            # .. now invoke it again to edit them in place.
            self._invoke_enmasse(config_path)

        except ErrorReturnCode as e:
            stdout = e.stdout # type: bytes
            stdout = stdout.decode('utf8') # type: ignore
            stderr = e.stderr

            logger.warning(format_exc())
            logger.warning('stdout -> %s', stdout)
            logger.warning('stderr -> %s', stderr)

            self.fail('Caught an exception while invoking enmasse')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
