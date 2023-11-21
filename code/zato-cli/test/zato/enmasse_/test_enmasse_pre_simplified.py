# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from unittest import main

# Bunch
from bunch import Bunch

# sh
from sh import RunningCommand

# Zato
from zato.common.test import rand_string, rand_unicode
from zato.common.test.config import TestConfig
from zato.common.test.enmasse_ import BaseEnmasseTestCase
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

template1 = """

channel_plain_http:
  - connection: channel
    is_active: true
    is_internal: false
    merge_url_params_req: true
    name: /test/enmasse1/{test_suffix}
    params_pri: channel -params-over-msg
    sec_def: zato-no-security
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
      # These are taken from generic.connection.py -> extra_secret_keys
      oauth2_access_token: null
      consumer_key: null
      consumer_secret: null

def_sec:
  - name: "Test Basic Auth {test_suffix}"
    is_active: true
    type: basic_auth
    username: "MyUser {test_suffix}"
    password: "MyPassword"
    realm: "My Realm"

email_smtp:
  - name: {smtp_config.name}
    host: {smtp_config.host}
    is_active: true
    is_debug: false
    mode: starttls
    port: 587
    timeout: 300
    username: {smtp_config.username}
    password: {smtp_config.password}
    ping_address: {smtp_config.ping_address}

web_socket:
    - address: "ws://0.0.0.0:10203/api/{test_suffix}"
      data_format: "json"
      id: 1
      is_active: true
      is_audit_log_received_active: false
      is_audit_log_sent_active: false
      is_internal: false
      max_bytes_per_message_received: null
      max_bytes_per_message_sent: null
      max_len_messages_received: null
      max_len_messages_sent: null
      name: "wsx.enmasse.{test_suffix}"
      new_token_wait_time: 5
      opaque1: '{{"max_bytes_per_message_sent":null,"max_bytes_per_message_received":null,"ping_interval":30,"extra_properties":null,"is_audit_log_received_active":false,"max_len_messages_received":null,"pings_missed_threshold":2,"max_len_messages_sent":null,"security":null,"is_audit_log_sent_active":false,"service_name":"pub.zato.ping"}}'
      ping_interval: 30
      pings_missed_threshold: 2
      sec_def: "zato-no-security"
      sec_type: null
      security_id: null
      service: "pub.zato.ping"
      service_name: "pub.zato.ping"
      token_ttl: 3600
"""

# ################################################################################################################################
# ################################################################################################################################

template2 = """

security:
  - name: Test Basic Auth Simple
    username: "MyUser {test_suffix}"
    password: "MyPassword"
    type: basic_auth
    realm: "My Realm"

  - name: Test Basic Auth Simple.2
    username: "MyUser {test_suffix}.2"
    type: basic_auth
    realm: "My Realm"

channel_rest:

  - name: name: /test/enmasse1/simple/{test_suffix}
    service: pub.zato.ping
    url_path: /test/enmasse1/simple/{test_suffix}

outgoing_rest:

  - name: Outgoing Rest Enmasse {test_suffix}
    host: https://example.com
    url_path: /enmasse/simple/{test_suffix}

  - name: Outgoing Rest Enmasse {test_suffix}.2
    host: https://example.com
    url_path: /enmasse/simple/{test_suffix}.2
    data_format: form

outgoing_ldap:

  - name: Enmasse LDAP {test_suffix}
    username: 'CN=example.ldap,OU=example01,OU=Example,OU=Groups,DC=example,DC=corp'
    auth_type: NTLM
    server_list: 127.0.0.1:389
    password: {test_suffix}
"""

# ################################################################################################################################
# ################################################################################################################################

class EnmasseTestCase(BaseEnmasseTestCase):

# ################################################################################################################################

    def get_smtp_config(self) -> 'Bunch':
        out = Bunch()

        out.name         = os.environ.get('Zato_Test_Enmasse_SMTP_Name')
        out.host         = os.environ.get('Zato_Test_Enmasse_SMTP_Host')
        out.username     = os.environ.get('Zato_Test_Enmasse_SMTP_Username')
        out.password     = os.environ.get('Zato_Test_Enmasse_SMTP_Password')
        out.ping_address = os.environ.get('Zato_Test_Enmasse_SMTP_Ping_Address')

        return out

# ################################################################################################################################

    def _cleanup(self, test_suffix:'str') -> 'None':

        # Zato
        from zato.common.util.cli import get_zato_sh_command

        # A shortcut
        command = get_zato_sh_command()

        # Build the name of the connection to delete
        conn_name = f'test.enmasse.{test_suffix}'

        # Invoke the delete command ..
        out:'RunningCommand' = command(
            'delete-wsx-outconn',
            '--path', TestConfig.server_location,
            '--name', conn_name
        )

        # .. and make sure there was no error in stdout/stderr ..
        self._assert_command_line_result(out)

# ################################################################################################################################

    def _test_enmasse_ok(self, template:'str') -> 'None':

        # sh
        from sh import ErrorReturnCode

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = 'zato-enmasse-' + test_suffix + '.yaml'
        config_path = os.path.join(tmp_dir, file_name)

        smtp_config = self.get_smtp_config()

        data = template1.format(test_suffix=test_suffix, smtp_config=smtp_config)

        f = open_w(config_path)
        _ = f.write(data)
        f.close()

        try:
            # Invoke enmasse to create objects ..
            _ = self._invoke_command(config_path)

            # .. now invoke it again to edit them in place.
            _ = self._invoke_command(config_path)

        except ErrorReturnCode as e:
            stdout:'bytes' = e.stdout # type: bytes
            stdout = stdout.decode('utf8') # type: ignore
            stderr:'str' = e.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception while invoking enmasse; stdout -> {stdout}')

        finally:
            self._cleanup(test_suffix)

# ################################################################################################################################

    def test_enmasse_ok(self) -> 'None':
        self._test_enmasse_ok(template1)

# ################################################################################################################################

    def test_enmasse_simple_ok(self) -> 'None':
        self._test_enmasse_ok(template2)

# ################################################################################################################################

    def test_enmasse_service_does_not_exit(self) -> 'None':

        # We are going to wait that many seconds for enmasse to complete
        start = datetime.utcnow()
        missing_wait_time = 3

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = 'zato-enmasse-' + test_suffix + '.yaml'
        config_path = os.path.join(tmp_dir, file_name)

        smtp_config = self.get_smtp_config()

        # Note that we replace pub.zato.ping with a service that certainly does not exist
        data = template1.replace('pub.zato.ping', 'zato-enmasse-service-does-not-exit')
        data = data.format(test_suffix=test_suffix, smtp_config=smtp_config)

        f = open_w(config_path)
        _ = f.write(data)
        f.close()

        # Invoke enmasse to create objects (which will block for missing_wait_time seconds) ..
        _ = self._invoke_command(config_path, require_ok=False)

        # .. now, make sure that we actually had to wait that many seconds ..
        now = datetime.utcnow()
        delta = now - start

        # .. the whole test should have taken longer than what we waited for in enmasse .
        if not delta.total_seconds() > missing_wait_time:
            msg = f'Total time should be bigger than {missing_wait_time} (missing_wait_time) instead of {delta}'
            self.fail(msg)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()


# ################################################################################################################################
