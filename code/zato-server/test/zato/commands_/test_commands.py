# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.test import CommandLineServiceTestCase

# ################################################################################################################################
# ################################################################################################################################

class ServiceCommandsTestCase(CommandLineServiceTestCase):

    def test_service_commands(self) -> 'None':

        # Test service to execute
        service_name = 'commands1.commands-service'

        # Run the test now
        self.run_zato_test(service_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

# stdlib
import os
from datetime import datetime
from logging import getLogger
from tempfile import gettempdir
from unittest import TestCase

# Zato
from zato.common.typing_ import cast_
from zato.common.util.open_ import open_w
from zato.common.test import rand_csv, rand_string
from zato.server.commands import CommandResult, Config
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CommandsService(Service):

    class SimpleIO:
        output = CommandResult

    class _CommandsServiceTestCase(TestCase):

        def __init__(self, service:'Service') -> 'None':
            super().__init__()
            self.service = service

# ################################################################################################################################

        def _test_impl(
            self,
            *,
            cid:'str'       = '',
            data:'str'      = '',
            stdin:'str'     = '',
            command:'str'   = '',
            timeout:'float' = Config.Timeout,
            encoding:'str'  = Config.Encoding,
            callback:'any_' = None,
            replace_char:'str'  = Config.ReplaceChar,
            is_multiline:'bool' = False,
            ) -> 'None':

            # Local aliases
            tmp_dir = gettempdir()

            # Test data that we will expect to read back from a test file
            data = data or rand_csv()
            len_data = len(data)

            # If we use the default timeout, it actually means that we do not want to have any
            if timeout == Config.Timeout:
                timeout = cast_('float', None)

            # Where our test data is
            test_file_name = rand_string(prefix='commands-test_invoke_core') + '.txt'
            full_path = os.path.join(tmp_dir, test_file_name)

            # Log useful details
            logger.info('Saving test data `%s` to file `%s`', data, full_path)

            # Populate the file with test data
            with open_w(full_path) as f:
                f.write(data)

            # Read the file back
            command = f'cat {full_path}'

            # Prepend new lines if the command is multiline
            if is_multiline:

                # Let's add two lines in front of the actual command
                line1 = 'cd {} \\ \n'.format(tmp_dir)
                line2 = 'cd {} \\ \n'.format(tmp_dir)
                command = line1 + line2 + command

            # If we have a timeout on input, let's sleep for more than that
            # before running the command. We use an integer instead of a smaller number like 1.1
            # because whether the sleep time is considered a float or integer is up to the underlying shell.
            # To stay on the safe side, it is an integer in our test.
            if timeout:
                sleep_time = timeout * 2
                prefix = f'sleep {sleep_time}'
                command = prefix + ' && ' + command

            # To check that results contain correct timestamps
            now_before_test = datetime.utcnow()

            # Invoke the commands to get the result
            result = self.service.commands.invoke(
                command,
                cid=cid,
                timeout=timeout,
                callback=callback,
                stdin=stdin,
                replace_char=replace_char,
                encoding=encoding,
            )

            logger.info('Result received -> %s', result)

            # To check that results contain correct timestamps
            now_after_test = datetime.utcnow()

            # .. and run the actual tests now ..

            self.assertEqual(result.timeout, timeout)

            if timeout:
                self.assertEqual(result.exit_code, -1)
                self.assertFalse(result.is_ok)
                self.assertFalse(result.is_async)
                self.assertTrue(result.is_timeout)

                expected_timeout_msg = f'Command \'{command}\' timed out after {timeout} sec.'
                self.assertEqual(result.timeout_msg, expected_timeout_msg)

                self.assertEqual(result.stdin,  '')
                self.assertEqual(result.stderr, '')
                self.assertEqual(result.stdout, '')

                self.assertEqual(result.len_stderr_bytes, 0)
                self.assertEqual(result.len_stderr_human, '')

                self.assertEqual(result.len_stdout_bytes, 0)
                self.assertEqual(result.len_stdout_human, '')

            else:
                self.assertEqual(result.exit_code, 0)
                self.assertTrue(result.is_ok)
                self.assertFalse(result.is_async)
                self.assertFalse(result.is_timeout)
                self.assertEqual(result.timeout_msg, '')

                self.assertEqual(result.stdin,  stdin)
                self.assertEqual(result.stderr, '')
                self.assertEqual(result.stdout, data)

                self.assertEqual(result.len_stderr_bytes, 0)
                self.assertEqual(result.len_stderr_human, '0 Bytes')

                self.assertEqual(result.len_stdout_bytes, len_data)
                self.assertEqual(result.len_stdout_human, '{} Bytes'.format(len_data))

            if cid:
                self.assertEqual(result.cid, cid)
            else:
                self.assertTrue(result.cid.startswith('zcmd'))


            self.assertEqual(result.encoding,     encoding)
            self.assertEqual(result.replace_char, replace_char)

            self.assertIsInstance(result.total_time_sec, float)

            start_time_as_iso = result.start_time.isoformat()
            end_time_as_iso   = result.end_time.isoformat()

            self.assertEqual(result.start_time_iso, start_time_as_iso)
            self.assertEqual(result.end_time_iso,   end_time_as_iso)

            self.assertLess(result.start_time, result.end_time)

            self.assertLess(now_before_test, result.start_time)
            self.assertLess(now_before_test, result.end_time)

            self.assertGreater(now_after_test, result.start_time)
            self.assertGreater(now_after_test, result.end_time)

# ################################################################################################################################

        def test_invoke_core(self):

            # This is the same as the core test
            self._test_impl()

# ################################################################################################################################

        def test_invoke_multiline(self):
            self._test_impl(is_multiline=True)

# ################################################################################################################################

        def test_invoke_with_timeout(self):
            self._test_impl(timeout=1)

# ################################################################################################################################

        def test_invoke_with_own_cid(self):
            self._test_impl(cid='abcdef')

# ################################################################################################################################

        def test_invoke_with_encoding(self):
            self._test_impl(encoding='ascii')

# ################################################################################################################################

        def test_invoke_with_replace_char(self):
            self._test_impl(replace_char='?')

# ################################################################################################################################

        def test_invoke_with_stdin(self):
            self._test_impl(stdin='hello')

# ################################################################################################################################

        def test_invoke_with_callback_function(self):
            pass

# ################################################################################################################################

        def test_invoke_with_callback_service_class(self):
            pass

# ################################################################################################################################

        def test_invoke_with_callback_service_name(self):
            pass

# ################################################################################################################################

        def test_invoke_with_callback_topic_name(self):
            pass

# ################################################################################################################################

        def test_invoke_async_core(self):
            pass

# ################################################################################################################################

    def _on_command_completed(self, result:'CommandResult') -> 'None':
        result
        result

# ################################################################################################################################

    def handle(self):

        # Build and run the test suite
        test_suite = self._CommandsServiceTestCase(self)
        test_suite

        #
        # Sync invoke
        #
        test_suite.test_invoke_core()
        test_suite.test_invoke_multiline()
        test_suite.test_invoke_with_timeout()
        test_suite.test_invoke_with_own_cid()
        test_suite.test_invoke_with_encoding()
        test_suite.test_invoke_with_replace_char()
        test_suite.test_invoke_with_stdin()
        # test_suite.test_invoke_with_callback_function()
        # test_suite.test_invoke_with_callback_service_class()
        # test_suite.test_invoke_with_callback_service_name()
        # test_suite.test_invoke_with_callback_topic_name()

        #
        # Async invoke
        #
        # self.test_invoke_async_core()

        """
        # command = 'rm -rf /tmp/abc && mkdir /tmp/abc && cd /tmp/abc && git clone https://github.com/zatosource/zato'
        """
        command = """
        whoami && \
            uname \
                -a
        """

        """
        result = self.commands.invoke(command, callback=self._on_command_completed)
        self.logger.info(result)
        """

        self.response.payload = 'OK'

# ################################################################################################################################
# ################################################################################################################################
'''
