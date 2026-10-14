# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the database drivers' sockets must be cooperative,
# so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# gevent
from gevent import spawn

# pytest
import pytest

# Zato
from common import report_progress_forever, setup_perf_logging, Log_File_Path
from perf import install_interrupt_handler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator

    progressgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def progress_reporting() -> 'progressgen':
    """ Sends the backend's per-operation logs to the log file for the whole session
    and prints a console progress line once per interval, with the disk-space stop.
    """
    counters = setup_perf_logging()
    install_interrupt_handler()
    reporter = spawn(report_progress_forever, counters)

    print(f'Backend logs go to {Log_File_Path}', flush=True)
    yield

    reporter.kill()

# ################################################################################################################################
# ################################################################################################################################
