# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from logging import getLogger
from tempfile import mkstemp
from time import time, sleep

# Sarge
from sarge import run as sarge_run, shell_format

# Zato
try:
    from zato.common.api import CLI_ARG_SEP
except ImportError:
    CLI_ARG_SEP = 'Zato_Zato_Zato' # type: ignore

try:
    from zato.common.util.open_ import open_r
except ImportError:
    default_encoding = 'utf8'

    def open_r(path:'str', encoding:'str'=default_encoding) -> 'textio_':
        return open(path, 'r', encoding=encoding)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, textio_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################

# This is for convenience of switching to a newer version of sarge in the future. Newer versions use async_ instead of async.
async_keyword = 'async_'

# ################################################################################################################################

# These messages may be returned by 'zato start' from underlying libraries
# but they do not indicate a genuine error.
stderr_ignore = [
    'pykafka.rdkafka',
    'Auto-created primary key used when not defining a primary key type',
    'Linux distribution found',
]

# ################################################################################################################################

import platform
system = platform.system()
is_windows = 'windows' in system.lower()

# ################################################################################################################################

def get_executable() -> 'str':
    """ Returns the wrapper which pip uses for executing Zato commands,
    the one with all the dependencies added to PYTHONPATH.
    """
    if is_windows:
        return os.path.join(os.path.dirname(sys.executable), 'python.exe')

    return os.path.join(os.path.dirname(sys.executable), 'py')

# ################################################################################################################################

class _StdErr:

    # Some log messages (like the ones produced by PyKafka) go to stderr but they are not really errors,
    # in which case we need to ignore them.
    ignored = [
        'Could not load pykafka.rdkafka extension.'
    ]

    def __init__(self, path:'str', timeout:'float') -> 'None':
        self.path = path
        self.timeout = timeout

# ################################################################################################################################

    def wait_for_error(self) -> 'None':
        now = time()

        while time() - now < self.timeout:
            sleep(0.1)
            _stderr = open_r(self.path)
            _err = _stderr.read()
            if _err and (not self.should_ignore(_err)):
                return _err
            else:
                _stderr.close()

# ################################################################################################################################

    def should_ignore(self, err:'str') -> 'bool':
        for item in self.ignored:
            if err.endswith(item):
                return True
        else:
            return False

# ################################################################################################################################

def start_process(
        component_name:'str',
        executable:'str',
        run_in_fg:'bool',
        cli_options:'str | None',
        extra_cli_options:'str'='',
        on_keyboard_interrupt:'any_'=None,
        failed_to_start_err:'int'=-100,
        extra_options:'strdict | None'=None,
        stderr_path:'str | None'=None,
        stdin_data:'str | None'=None,
        async_keyword:'str'=async_keyword
    ) -> 'int':
    """ Starts a new process from a given Python path, either in background or foreground (run_in_fg).
    """
    stderr_path = stderr_path or mkstemp('-zato-start-{}.txt'.format(component_name.replace(' ','')))[1]

    stdout_redirect = ''
    stderr_redirect = ''

    # This is the exit code as it will be returned by sarge
    exit_code = 0

    # We always run in foreground under Windows
    if is_windows:
        run_in_fg = True
    else:
        if not run_in_fg:
            stdout_redirect = '1> /dev/null'
        stderr_redirect = '2> {}'.format(stderr_path)

    program = '{} {} {} {}'.format(executable, extra_cli_options, stdout_redirect, stderr_redirect)

    try:
        _stderr = _StdErr(stderr_path, stderr_sleep_fg if run_in_fg else stderr_sleep_bg)

        run_kwargs:'strdict' = {
            async_keyword: False if run_in_fg else True,
        }

        # Do not send input if it does not really exist because it prevents pdb from attaching to a service's stdin
        if stdin_data:
            run_kwargs['input'] = stdin_data

        p = sarge_run(program, **run_kwargs)

        # Wait a moment for any potential errors
        _err = _stderr.wait_for_error()
        if _err:
            should_be_ignored = False
            for item in stderr_ignore:
                if item in _err:
                    should_be_ignored = True
                    break
            if not should_be_ignored:
                logger.warning('Stderr received from program `%s` e:`%s`, kw:`%s`', program, _err, run_kwargs)
                sys.exit(failed_to_start_err)

        # Update the exit code ..
        exit_code = p.returncode

    except KeyboardInterrupt:
        if on_keyboard_interrupt:
            on_keyboard_interrupt()
        sys.exit(0)

    finally:
        # We can now return the exit code to our caller
        return exit_code # type: ignore

# ################################################################################################################################

def start_python_process(
        component_name:'str',
        run_in_fg:'bool',
        py_path:'str',
        program_dir:'str',
        on_keyboard_interrupt:'any_'=None,
        failed_to_start_err:'int'=-100,
        extra_options:'strdict | None'=None,
        stderr_path:'str | None'=None,
        stdin_data:'str | None'=None
    ) -> 'int':
    """ Starts a new process from a given Python path, either in background or foreground (run_in_fg).
    """
    options:'strdict' = {
        'fg': run_in_fg,
    }
    if extra_options:
        options.update(extra_options)

    options = CLI_ARG_SEP.join('{}={}'.format(k, v) for k, v in options.items()) # type: ignore

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
