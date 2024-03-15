# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
from zato.common.test.enmasse_.base import BaseEnmasseTestCase
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.test.enmasse_._template_complex_02 import template_complex_02
from zato.common.test.enmasse_._template_complex_03 import template_complex_03
from zato.common.test.enmasse_._template_complex_04 import template_complex_04
from zato.common.test.enmasse_._template_complex_05 import template_complex_05
from zato.common.test.enmasse_._template_simple_01 import template_simple_01
from zato.common.test.enmasse_._template_simple_02 import template_simple_02
from zato.common.test.enmasse_._template_simple_03 import template_simple_03
from zato.common.test.enmasse_._template_simple_04 import template_simple_04
from zato.common.test.enmasse_._template_simple_05 import template_simple_05
from zato.common.test.enmasse_._template_simple_06 import template_simple_06
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseTestCase(BaseEnmasseTestCase):

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

    def _test_enmasse_ok(self, test_name:'str', template:'str') -> 'None':

        # sh
        from sh import ErrorReturnCode

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = 'zato-enmasse-' + test_suffix + '.yaml'
        config_path = os.path.join(tmp_dir, file_name)

        smtp_config = self.get_smtp_config()

        data = template.format(test_suffix=test_suffix, smtp_config=smtp_config)

        f = open_w(config_path)
        _ = f.write(data)
        f.close()

        try:
            # Invoke enmasse to create objects ..
            _ = self.invoke_enmasse(config_path)

            # .. now invoke it again to edit them in place.
            _ = self.invoke_enmasse(config_path)

        except ErrorReturnCode as e:
            stdout:'bytes' = e.stdout # type: bytes
            stdout = stdout.decode('utf8') # type: ignore
            stderr:'str' = e.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception while invoking enmasse; stdout -> {stdout}')

        finally:
            self._cleanup(test_suffix)

# ################################################################################################################################

    def test_enmasse_complex_ok_01(self) -> 'None':
        self._test_enmasse_ok('complex_ok_01', template_complex_01)

# ################################################################################################################################

    def test_enmasse_complex_ok_02(self) -> 'None':
        self._test_enmasse_ok('complex_ok_02', template_complex_02)

# ################################################################################################################################

    def test_enmasse_complex_ok_03(self) -> 'None':
        self._test_enmasse_ok('complex_ok_03', template_complex_03)

# ################################################################################################################################

    def test_enmasse_complex_ok_04(self) -> 'None':
        self._test_enmasse_ok('complex_ok_04', template_complex_04)

# ################################################################################################################################

    def test_enmasse_complex_ok_05(self) -> 'None':
        self._test_enmasse_ok('complex_ok_05', template_complex_05)

# ################################################################################################################################

    def test_enmasse_simple_ok_01(self) -> 'None':
        self._test_enmasse_ok('simple_ok_01', template_simple_01)

# ################################################################################################################################

    def test_enmasse_simple_ok_02(self) -> 'None':
        self._test_enmasse_ok('simple_ok_02', template_simple_02)

# ################################################################################################################################

    def test_enmasse_simple_ok_03(self) -> 'None':
        self._test_enmasse_ok('simple_ok_03', template_simple_03)

# ################################################################################################################################

    def test_enmasse_simple_ok_04(self) -> 'None':
        self._test_enmasse_ok('simple_ok_04', template_simple_04)

# ################################################################################################################################

    def test_enmasse_simple_ok_05(self) -> 'None':
        self._test_enmasse_ok('simple_ok_05', template_simple_05)

# ################################################################################################################################

    def test_enmasse_simple_ok_06(self) -> 'None':
        self._test_enmasse_ok('simple_ok_06', template_simple_06)

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
        data = template_complex_01.replace('pub.zato.ping', 'zato-enmasse-service-does-not-exit')
        data = data.format(test_suffix=test_suffix, smtp_config=smtp_config)

        f = open_w(config_path)
        _ = f.write(data)
        f.close()

        # Invoke enmasse to create objects (which will block for missing_wait_time seconds) ..
        _ = self.invoke_enmasse(config_path, require_ok=False, missing_wait_time=missing_wait_time)

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
