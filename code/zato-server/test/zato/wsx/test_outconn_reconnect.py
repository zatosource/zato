# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from time import sleep
from traceback import format_exc

from unittest import main

# Zato
from zato.common.test import rand_string, rand_unicode
from zato.common.test.config import TestConfig
from zato.common.test.enmasse_ import BaseEnmasseTestCase
from zato.common.util.cli import get_zato_sh_command
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

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
      name: test.outconn.WSXOutconnReconnectTestCase.{test_suffix}
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

"""

# ################################################################################################################################
# ################################################################################################################################

class WSXOutconnReconnectTestCase(BaseEnmasseTestCase):

    def _delete(self, command_name:'str', conn_type:'str', test_suffix:'str') -> 'None':

        # A shortcut
        command = get_zato_sh_command()

        # Build the name of the connection to delete
        conn_name = f'test.{conn_type}.WSXOutconnReconnectTestCase.{test_suffix}'

        # Invoke the delete command ..
        out = command(
            command_name,
            '--path', TestConfig.server_location,
            '--name', conn_name
        )

        # .. and make sure there was no error in stdout/stderr ..
        self._assert_command_line_result(out)

    def _delete_channel(self, test_suffix:'str') -> 'None':
        self._delete('delete-wsx-channel', 'channel', test_suffix)

    def _delete_outconn(self, test_suffix:'str') -> 'None':
        self._delete('delete-wsx-outconn', 'outconn', test_suffix)

# ################################################################################################################################

    def _save_enmasse_file(self, template:'str', conn_type:'str', test_suffix:'str') -> 'str':

        tmp_dir = gettempdir()

        file_name = f'zato-{conn_type}-{test_suffix}.yaml'
        config_path = os.path.join(tmp_dir, file_name)

        data = template.format(test_suffix=test_suffix)

        f = open_w(config_path)
        f.write(data)
        f.close()

        return config_path

# ################################################################################################################################

    def _save_enmasse_channel_file(self, test_suffix:'str') -> 'str':
        config_path = self._save_enmasse_file(channel_template, 'WSXOutconnReconnectTestCase-channel', test_suffix)
        return config_path

# ################################################################################################################################

    def _save_enmasse_outconn_file(self, test_suffix:'str') -> 'str':
        config_path = self._save_enmasse_file(outconn_template, 'WSXOutconnReconnectTestCase-outconn', test_suffix)
        return config_path

# ################################################################################################################################

    def test_outconn_reconnect(self) -> 'None':

        # A unique ID for our test run
        test_suffix = rand_unicode() + '.' + rand_string()

        try:

            # Prepare a config file for the channel ..
            channel_config_file = self._save_enmasse_channel_file(test_suffix)

            # .. now, for the outgoing connection ..
            outconn_config_file = self._save_enmasse_outconn_file(test_suffix)

            # .. create the channel ..
            self.invoke_enmasse(channel_config_file)

            # .. create the outgoing connection ..
            self.invoke_enmasse(outconn_config_file)

            # .. now, delete the channel ..
            self._delete_channel(test_suffix)

            # .. create the channel back ..
            self.invoke_enmasse(channel_config_file)

            # .. wait a few seconds to make sure that the outgoing connection
            # .. has enough time to reconnect ..
            sleep(6)

            # .. and confirm that it did.

        except Exception:
            self.fail('Caught an exception -> {}'.format(format_exc()))

        finally:
            self._delete_channel(test_suffix)
            self._delete_outconn(test_suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
