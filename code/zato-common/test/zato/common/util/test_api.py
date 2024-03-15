# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from pathlib import Path
from unittest import main, TestCase
from uuid import uuid4

# Zato
from zato.common.util.file_system import resolve_path

# ################################################################################################################################
# ################################################################################################################################

class UtilAPITestCase(TestCase):

    def test_resolve_path_home_directory(self):

        # Local aliases
        suffix = '/test/abc'
        home_dir = Path.home().as_posix()

        # Before expansion ..
        path = '~' + suffix

        # .. what we expect to receive after expansion ..
        expected = home_dir + suffix # type: ignore

        # .. do resolve it ..
        resolved = resolve_path(path)

        # .. and confirm that it was resolved correctly.
        self.assertEqual(resolved, expected)

# ################################################################################################################################

    def test_resolve_path_env_variable_start(self):

        # Local aliases
        env_01_name = 'Zato_Test_Env_01'

        # Skip this test if there are no test environment variables in this system
        if not (env_01 := os.environ.get('Zato_Test_Env_01')):
            return

        # Local aliases
        prefix = '/hello'
        suffix = '/test/abc'

        # Before expansion ..
        path = prefix + '$' + env_01_name + suffix

        # .. what we expect to receive after expansion ..
        expected = prefix + env_01 + suffix # type: ignore

        # .. do resolve it ..
        resolved = resolve_path(path)

        # .. and confirm that it was resolved correctly.
        self.assertEqual(resolved, expected)

# ################################################################################################################################

    def test_resolve_path_env_variable_middle(self):

        # Local aliases
        env_02_name = 'Zato_Test_Env_02'

        # Skip this test if there are no test environment variables in this system
        if not (env_02 := os.environ.get('Zato_Test_Env_02')):
            return

        # Local aliases
        prefix = '/hello/'
        suffix = '/test/abc'

        # Before expansion ..
        path = prefix + '$' + env_02_name + suffix

        # .. what we expect to receive after expansion ..
        expected = prefix + env_02 + suffix # type: ignore

        # .. do resolve it ..
        resolved = resolve_path(path)

        # .. and confirm that it was resolved correctly.
        self.assertEqual(resolved, expected)

# ################################################################################################################################

    def test_resolve_path_env_variable_end(self):

        # Local aliases
        env_03_name = 'Zato_Test_Env_03'

        # Skip this test if there are no test environment variables in this system
        if not (env_03 := os.environ.get('Zato_Test_Env_03')):
            return

        # Local aliases
        prefix = '/hello/'

        # Before expansion ..
        path = prefix + '$' + env_03_name

        # .. what we expect to receive after expansion ..
        expected = prefix + env_03 # type: ignore

        # .. do resolve it ..
        resolved = resolve_path(path)

        # .. and confirm that it was resolved correctly.
        self.assertEqual(resolved, expected)

# ################################################################################################################################

    def test_resolve_path_multiple_env_variables(self):

        # Local aliases
        env_01_name = 'Zato_Test_Env_01'
        env_02_name = 'Zato_Test_Env_02'
        env_03_name = 'Zato_Test_Env_03'

        # Skip this test if there are no test environment variables in this system

        if not (env_01 := os.environ.get('Zato_Test_Env_01')):
            return

        if not (env_02 := os.environ.get('Zato_Test_Env_02')):
            return

        if not (env_03 := os.environ.get('Zato_Test_Env_03')):
            return

        # Local aliases
        prefix = '/hello/'

        # Before expansion ..
        path = prefix + '$' + env_01_name + '/' + '$' + env_02_name + '/' + '$' + env_03_name

        # .. what we expect to receive after expansion ..
        expected = prefix + env_01 + '/' + env_02 + '/' + env_03 # type: ignore

        # .. do resolve it ..
        resolved = resolve_path(path)

        # .. and confirm that it was resolved correctly.
        self.assertEqual(resolved, expected)

# ################################################################################################################################

    def test_resolve_path_missing_env_variable(self):

        # Local aliases
        random = uuid4().hex

        # Such an environment variable will not exist
        env_missing = 'Zato_Test_Env_' + random

        # Before expansion ..
        path = '/hello/' + '$' + env_missing

        # .. on output, we expect the same path ..
        expected = path

        # .. do resolve it ..
        resolved = resolve_path(path)

        # .. and confirm that it was resolved correctly.
        self.assertEqual(resolved, expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
