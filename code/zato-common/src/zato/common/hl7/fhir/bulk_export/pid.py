# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

# The pid file that says which process works on a job
Pid_File_Name = 'program.pid'

# ################################################################################################################################
# ################################################################################################################################

def is_process_alive(pid:'int') -> 'bool':
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

# ################################################################################################################################

def read_pid_file(job_dir:'str') -> 'int':
    """ Returns the pid recorded for a job, or 0 when there is none.
    """
    path = os.path.join(job_dir, Pid_File_Name)

    if not os.path.exists(path):
        return 0

    with open(path) as file:
        data = file.read().strip()

    if data.isdigit():
        out = int(data)
    else:
        out = 0

    return out

# ################################################################################################################################

def write_pid_file(job_dir:'str', pid:'int') -> 'None':
    os.makedirs(job_dir, exist_ok=True)
    path = os.path.join(job_dir, Pid_File_Name)

    with open(path, 'w') as file:
        _ = file.write(str(pid))

# ################################################################################################################################

def is_job_running(job_dir:'str') -> 'bool':
    """ Whether a process other than this one is alive and working on the job.
    """
    pid = read_pid_file(job_dir)

    if not pid:
        return False

    if pid == os.getpid():
        return False

    out = is_process_alive(pid)
    return out

# ################################################################################################################################

def acquire_pid_file(job_dir:'str') -> 'bool':
    """ Claims the job for this process, unless another process that is still alive has it.
    """
    if is_job_running(job_dir):
        return False

    write_pid_file(job_dir, os.getpid())
    return True

# ################################################################################################################################
# ################################################################################################################################
