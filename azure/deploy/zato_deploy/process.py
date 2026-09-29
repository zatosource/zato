# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess

# Zato
from zato_deploy.common import StageFailed, strlist, strstrdict
from zato_deploy.state import Progress

# ################################################################################################################################
# ################################################################################################################################

def run_logged(progress:'Progress', command:'strlist', extra_env:'strstrdict | None'=None) -> 'None':
    """ Runs a command with each line of its output going to the log, and raises StageFailed with its last line if it fails.
    """
    env = dict(os.environ)

    if extra_env:
        env.update(extra_env)

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace', env=env)

    last_line = ''

    # Each line is logged the moment it appears ..
    if process.stdout:
        for line in process.stdout:
            line = line.rstrip()
            if line:
                progress.log(line)
                last_line = line

    exit_code = process.wait()

    # .. and the last one usually says why the command failed, if it did.
    if exit_code != 0:
        if not last_line:
            last_line = f'{command[0]} exited with code {exit_code}'
        raise StageFailed(last_line)

# ################################################################################################################################
# ################################################################################################################################
