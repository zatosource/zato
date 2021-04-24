# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import warnings
from logging import getLogger
from unittest import TestCase

# Zato
from zato.common.api import Testing
from zato.common.util.cli import delete_pidfile as cli_delete_pidfile
from zato.common.util.proc import start_python_process

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_test')

# ################################################################################################################################
# ################################################################################################################################

class ZatoTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def delete_pidfile(self, component_dir):
        # type: (str) -> None
        def impl():
            return cli_delete_pidfile(logger, component_dir)
        return impl

    def test_create_customer(self):

        print()
        print(111, self)
        print()

        #server = ParallelServer()
        #server.api.channel.rest.get('aaa')

        component_dir = ''

        start_kwargs = {
            'component_name': 'test.server',
            'run_in_fg': True,
            'py_path': 'zato.server.main',
            'program_dir': component_dir,
            'on_keyboard_interrupt': self.delete_pidfile(component_dir),
            'failed_to_start_err': Testing.SysErrorCode.FailedToStart,
            'extra_options': {'sync_internal': False, 'secret_key': '', 'stderr_path': None},
            'stderr_path': None,
            'stdin_data': '',
            'should_sys_exit': False,
        }

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', ResourceWarning)
            start_python_process(**start_kwargs)

# ################################################################################################################################
# ################################################################################################################################
