# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
import sys
from logging import getLogger
from tempfile import mkstemp
from time import time, sleep

# Sarge
from sarge import run as sarge_run, shell_format

# Python 2/3 compatibility
from six import PY2

# Zato
from zato.common.api import CLI_ARG_SEP

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################

# This is for convenience of switching to a newer version of sarge in the future. Newer versions use async_ instead of async.
async_keyword = 'async_' if PY2 else 'async_'

# ################################################################################################################################

import platform
system = platform.system()
is_windows = 'windows' in system.lower()

# ################################################################################################################################

def get_executable():
    """ Returns the wrapper which buildout uses for executing Zato commands,
    the one with all the dependencies added to PYTHONPATH.
    """
    if is_windows:
        return os.path.join(os.path.dirname(sys.executable), 'python.exe')
    return os.path.join(os.path.dirname(sys.executable), 'py')

# ################################################################################################################################

class _StdErr(object):

    # Some log messages (like the ones produced by PyKafka) go to stderr but they are not really errors,
    # in which case we need to ignore them.
    ignored = [
        'Could not load pykafka.rdkafka extension.'
    ]

    def __init__(self, path, timeout):
        self.path = path
        self.timeout = timeout

# ################################################################################################################################

    def wait_for_error(self):
        now = time()

        while time() - now < self.timeout:
            sleep(0.1)
            _stderr = open(self.path)
            _err = _stderr.read()
            if _err and (not self.should_ignore(_err)):
                return _err
            else:
                _stderr.close()

# ################################################################################################################################

    def should_ignore(self, err):
        for item in self.ignored:
            if err.endswith(item):
                return True

# ################################################################################################################################

def start_process(component_name, executable, run_in_fg, cli_options, extra_cli_options='', on_keyboard_interrupt=None,
        failed_to_start_err=-100, extra_options=None, stderr_path=None, stdin_data=None, async_keyword=async_keyword):
    """ Starts a new process from a given Python path, either in background or foreground (run_in_fg).
    """
    stderr_path = stderr_path or mkstemp('-zato-start-{}.txt'.format(component_name.replace(' ','')))[1]

    stdout_redirect = ''
    stderr_redirect = ''
    if not is_windows:
        if not run_in_fg:
            stdout_redirect = '1> /dev/null'
        stderr_redirect = '2> {}'.format(stderr_path)

    program = '{} {} {} {}'.format(executable, extra_cli_options, stdout_redirect, stderr_redirect)

    try:
        _stderr = _StdErr(stderr_path, stderr_sleep_fg if run_in_fg else stderr_sleep_bg)

        run_kwargs = {
            async_keyword: False if run_in_fg else True,
        }

        # Do not send input if it does not really exist because it prevents pdb from attaching to a service's stdin
        if stdin_data:
            run_kwargs['input'] = stdin_data

        sarge_run(program, **run_kwargs)

        # Wait a moment for any potential errors
        _err = _stderr.wait_for_error()
        if _err:
            if 'Could not load pykafka.rdkafka extension.' not in _err:
                logger.warn('Stderr received from program `%s` e:`%s`, kw:`%s`', program, _err, run_kwargs)
                sys.exit(failed_to_start_err)

    except KeyboardInterrupt:
        if on_keyboard_interrupt:
            on_keyboard_interrupt()
        sys.exit(0)

# ################################################################################################################################

def start_python_process(component_name, run_in_fg, py_path, program_dir, on_keyboard_interrupt=None, failed_to_start_err=-100,
        extra_options=None, stderr_path=None, stdin_data=None):
    """ Starts a new process from a given Python path, either in background or foreground (run_in_fg).
    """
    options = {
        'fg': run_in_fg,
    }
    if extra_options:
        options.update(extra_options)

    options = CLI_ARG_SEP.join('{}={}'.format(k, v) for k, v in options.items())

    py_path_option = shell_format('-m {0}', py_path)
    program_dir_option = shell_format('{0}', program_dir) if program_dir else ''

    extra_cli_options = '{} {} {}'.format(py_path_option, program_dir_option, options)

    extra_cli_options = '{} '.format(py_path_option)
    if program_dir_option:
        extra_cli_options += '{} '.format(program_dir_option)
    extra_cli_options += '{}'.format(options)

    return start_process(component_name, get_executable(), run_in_fg, None, extra_cli_options, on_keyboard_interrupt,
        failed_to_start_err, extra_options, stderr_path, stdin_data)

# ################################################################################################################################
