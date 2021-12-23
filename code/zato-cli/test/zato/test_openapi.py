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
from zato.common.test.apispec_ import run_common_apispec_assertions
from zato.common.test.config import TestConfig
from zato.common.test import rand_string, rand_unicode
from zato.common.util.open_ import open_r

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

            # .. read it back ..
            f = open_r(file_path)
            data = f.read()
            f.close()

            run_common_apispec_assertions(self, data, with_all_paths=False)

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
