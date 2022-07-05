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
from sh import ErrorReturnCode

# Zato
from zato.common.test.config import TestConfig
from zato.common.test import rand_string, rand_unicode
from zato.common.util.cli import get_zato_sh_command
from zato.common.util.open_ import open_w

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

outconn_template = """

zato_generic_connection:
    - address: ws://localhost:22099
      cache_expiry: 0
      has_auto_reconnect: true
      is_active: true
      is_channel: true
      is_internal: false
      is_outconn: false
      is_zato: true
      name: test.enmasse.{test_suffix}
      pool_size: 1
      sec_use_rbac: false
      security_def: ZATO_NONE
      subscription_list:
      type_: outconn-wsx
"""

channel_template = """

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

class EnmasseTestCase(TestCase):

# ################################################################################################################################

    def _warn_on_error(self, stdout:'any_', stderr:'any_') -> 'None':
        logger.warning(format_exc())
        logger.warning('stdout -> %s', stdout)
        logger.warning('stderr -> %s', stderr)

# ################################################################################################################################

    def _assert_command_line_result(self, out:'RunningCommand') -> 'None':

        self.assertEqual(out.exit_code, 0)

        stdout = out.stdout.decode('utf8')
        stderr = out.stderr.decode('utf8')

        if 'error' in stdout:
            self._warn_on_error(stdout, stderr)
            self.fail('Found an error in stdout while invoking enmasse')

        if 'error' in stderr:
            self._warn_on_error(stdout, stderr)
            self.fail('Found an error in stderr while invoking enmasse')

# ################################################################################################################################

    def _invoke_command(self, config_path:'str', require_ok:'bool'=True) -> 'RunningCommand':

        # A shortcut
        command = get_zato_sh_command()

        # Invoke enmasse ..
        out = command('enmasse', TestConfig.server_location,
            '--import', '--input', config_path, '--replace-odb-objects', '--verbose')

        # .. if told to, make sure there was no error in stdout/stderr ..
        if require_ok:
            self._assert_command_line_result(out)

        return out

# ################################################################################################################################

    def _cleanup(self, test_suffix:'str') -> 'None':

        # A shortcut
        command = get_zato_sh_command()

        # Build the name of the connection to delete
        conn_name = f'test.enmasse.{test_suffix}'

        # Invoke the delete command ..
        out = command(
            'delete-wsx-outconn',
            '--path', TestConfig.server_location,
            '--name', conn_name
        )

        # .. and make sure there was no error in stdout/stderr ..
        self._assert_command_line_result(out)

# ################################################################################################################################

    def _save_enmasse_file(self, template:'str', conn_type:'str', test_suffix:'str') -> 'None':

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = f'zato-enmasse-{conn_type}-{test_suffix}.yaml'
        config_path = os.path.join(tmp_dir, file_name)

        data = template.format(test_suffix=test_suffix)

        f = open_w(config_path)
        f.write(data)
        f.close()

# ################################################################################################################################

    def _save_enmasse_channel_file(self, test_suffix:'str') -> 'None':
        self._save_enmasse_file(channel_template, 'channel', test_suffix)

# ################################################################################################################################

    def _save_enmasse_outconn_file(self, test_suffix:'str') -> 'None':
        self._save_enmasse_file(outconn_template, 'outconn', test_suffix)

# ################################################################################################################################

    def _get_enmasse_config_path(self, conn_type:'str', test_suffix:'str') -> 'str':
        pass

# ################################################################################################################################

    def test_outconn_reconnect(self) -> 'None':

        try:
            # Create the outgoing connection ..
            self._invoke_command(config_path)

            # .. create a channel ..

            # .. now, delete the channel ..

            # .. create the channel back ..

            # .. confirm that the outgoin connection reconnected ..

            # .. and run the cleanup procedure.

        except Exception:
            self.fail('Caught an exception -> {}'.format(format_exc()))

        finally:
            self._cleanup(test_suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
