# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import basicConfig, getLogger, WARN
from traceback import format_exc

from unittest import TestCase

# Zato
from zato.common.test.config import TestConfig

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

class BaseEnmasseTestCase(TestCase):

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

    def invoke_enmasse(self, config_path:'str', require_ok:'bool'=True, missing_wait_time:'int'=1) -> 'RunningCommand':

        # Zato
        from zato.common.util.cli import get_zato_sh_command

        # A shortcut
        command = get_zato_sh_command()

        # Invoke enmasse ..
        out:'RunningCommand' = command('enmasse', TestConfig.server_location,
            '--import',
            '--input', config_path,
            '--replace',
            '--verbose',
            '--missing-wait-time', missing_wait_time
        )

        # .. if told to, make sure there was no error in stdout/3stderr ..
        if require_ok:
            self._assert_command_line_result(out)

        return out

# ################################################################################################################################
