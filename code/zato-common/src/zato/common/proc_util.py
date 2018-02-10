# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from logging import getLogger
from tempfile import mkstemp
from time import time, sleep

# Sarge
from sarge import run as sarge_run

# Zato
from zato.common import CLI_ARG_SEP

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################

def get_executable():
    """ Returns the wrapper which buildout uses for executing Zato commands,
    the one with all the dependencies added to PYTHONPATH.
    """
    return os.path.join(os.path.dirname(sys.executable), 'py')

# ################################################################################################################################

class _StdErr(object):
    def __init__(self, path, timeout):
        self.path = path
        self.timeout = timeout

    def wait_for_error(self):
        now = time()

        while time() - now < self.timeout:
            sleep(0.02)
            _stderr = open(self.path)
            _err = _stderr.read()
            if _err:
                return _err
            else:
                _stderr.close()

# ################################################################################################################################

def start_python_process(run_in_fg, py_path, name, program_dir, on_keyboard_interrupt=None, failed_to_start_err=-100,
    extra_options=None, stderr_path=None, stdin_data=None):
    """ Starts a new process from a given Python path, either in background or foreground (run_in_fg).
    """
    stderr_path = stderr_path or mkstemp('-zato-start-{}.txt'.format(name.replace(' ','')))[1]
    stdout_redirect = '' if run_in_fg else '1> /dev/null'
    stderr_redirect = '2> {}'.format(stderr_path)

    options = {
        'fg': run_in_fg,
    }
    if extra_options:
        options.update(extra_options)

    options = CLI_ARG_SEP.join('{}={}'.format(k, v) for k, v in options.items())

    program = '{} -m {} {} {} {} {}'.format(get_executable(), py_path, program_dir, options, stdout_redirect, stderr_redirect)

    try:
        _stderr = _StdErr(stderr_path, stderr_sleep_fg if run_in_fg else stderr_sleep_bg)
        sarge_run(program, async=False if run_in_fg else True, input=stdin_data)

        # Wait a moment for any potential errors
        _err = _stderr.wait_for_error()
        if _err:
            logger.warn(_err)
            sys.exit(failed_to_start_err)

    except KeyboardInterrupt:
        if on_keyboard_interrupt:
            on_keyboard_interrupt()
        sys.exit(0)

# ################################################################################################################################
