# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import main

# Zato
from zato.common.test.unittest_pubsub_requests import PubSubRESTServerBaseTestCase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerTestCase(PubSubRESTServerBaseTestCase):
    """ Test cases for the pub/sub REST server.
    """

# ################################################################################################################################

    def _run_enmasse(self) -> 'None':
        """ Run enmasse with the config path.
        """
        # sh
        from sh import ErrorReturnCode

        # Zato
        from zato.common.util.cli import get_zato_sh_command
        from zato.common.test.config import TestConfig

        # Set environment variable to avoid requiring server
        import os
        os.environ['Zato_Needs_Config_Reload'] = 'False'

        try:
            # Get the command
            command = get_zato_sh_command()

            # Invoke enmasse with the config path
            out = command('enmasse', TestConfig.server_location, '--import', '--input', self.config_path, '--verbose') # type: ignore

            # Log the output
            stdout = out.stdout.decode('utf8')
            stderr = out.stderr.decode('utf8') if out.stderr else ''
            
            logger.info(f'Enmasse stdout: {stdout}')
            if stderr:
                logger.info(f'Enmasse stderr: {stderr}')

            # Check for successful import
            self.assertEqual(out.exit_code, 0)

        except ErrorReturnCode as e:
            stdout = e.stdout.decode('utf8')
            stderr = e.stderr

            logger.error(f'Enmasse failed - stdout: {stdout}')
            logger.error(f'Enmasse failed - stderr: {stderr}')
            self.fail(f'Caught an exception while invoking enmasse; stdout -> {stdout}')

# ################################################################################################################################

    def test_full_path(self) -> 'None':
        """ Test full path with enmasse configuration.
        """
        # Skip auto-unsubscribe for this test
        self.skip_auto_unsubscribe = True

        # Run enmasse
        self._run_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
