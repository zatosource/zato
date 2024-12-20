# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import BAD_REQUEST
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from traceback import format_exc
from unittest import main, TestCase

# openapi-spec-validator
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

# requests-openapi
import requests_openapi

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
    from requests import Response
    from sh import RunningCommand
    from zato.common.typing_ import any_, anydict
    Response = Response
    anydict = anydict

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

        # Zato
        from zato.common.util.cli import get_zato_sh_command

        # A shortcut
        command = get_zato_sh_command() # type: ignore

        # Invoke enmasse ..
        out:'any_' = command('openapi', TestConfig.server_location,
            '--exclude', '""', '--include', 'helpers.dataclass-service',
            '--file', file_path,
            '--verbose')

        # .. if told to, make sure there was no error in stdout/stderr ..
        if require_ok:
            self._assert_command_line_result(out, file_path)

        return out

# ################################################################################################################################

    def test_openapi(self) -> 'None':

        if not os.environ.get('ZATO_TEST_OPENAPI'):
            return

        # sh
        from sh import ErrorReturnCode

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = 'zato-test-' + test_suffix + '.yaml'
        file_path = os.path.join(tmp_dir, file_name)

        try:
            # Invoke openapi to create a definition ..
            _ = self._invoke_command(file_path)

            # .. read it back ..
            f = open_r(file_path)
            data = f.read()
            f.close()

            # .. run our assertions ..
            run_common_apispec_assertions(self, data, with_all_paths=False)

            # .. validate it once more using an external library ..
            spec_dict, _ = read_from_filename(file_path)
            validate_spec(spec_dict)

            # .. and triple-check now by invoking the endpoint based on the spec generated ..

            client = requests_openapi.Client()
            client.load_spec_from_file(file_path)

            # Note that we provide no request here
            response = client.post__zato_api_invoke_helpers_dataclass_service() # type: Response
            json_result = response.json() # type: anydict

            # The response and JSON result will point to a 400 error because
            # the underlying client that we use does not accept JSON request messages.
            # Yet, it still a useful test because we know that the operation did exist
            # and the server did correctly reject a call without a correct input.
            self.assertEqual(response.status_code, BAD_REQUEST)

            self.assertEqual(json_result['result'],  'Error')
            self.assertEqual(json_result['details'], 'Invalid input')
            self.assertIsInstance(json_result['cid'], str)
            self.assertGreaterEqual(len(json_result['cid']), 20)

        except ErrorReturnCode as e:

            stdout = e.stdout # type: ignore
            stdout = stdout.decode('utf8') # type: ignore
            stderr = e.stderr # type: ignore

            self._warn_on_error(stdout, stderr)
            self.fail('Caught an exception while invoking openapi')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
