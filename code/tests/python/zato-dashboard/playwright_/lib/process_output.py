# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
import threading
import time

# Zato
from zato.common.test.conftest_base_pubsub import Expected_Record_Marker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import subprocess
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The first line of a log record of a streamed process - each other line continues the record before it, e.g. a traceback
    Record_Start_Pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ')

    # A process that has no readiness line to look for
    No_Ready_Marker = ''

    # The name of the thread that streams the server's output, the same for a restarted server,
    # so that the check for threads left behind by a test sees a replacement rather than a new thread
    Server_Thread_Name = 'stream_output SERVER'

# ################################################################################################################################
# ################################################################################################################################

def stream_output(
    process:'subprocess.Popen',
    label:'str',
    time_reference:'float',
    ready_marker:'str',
    ready_event:'threading.Event',
    expected_records:'list[str]',
    ) -> 'None':
    """ Streams subprocess stdout to the test console with timing information, signalling
    the given event once the process prints the line that says it is ready. A record that contains
    any of the expected records on its first line is marked as provoked deliberately by a test,
    together with each line that continues it, such as its traceback.
    """
    is_expected = False
    stdout:'any_' = process.stdout

    for line in iter(stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        elapsed = time.monotonic() - time_reference

        if ModuleCtx.Record_Start_Pattern.match(text):
            is_expected = any(record in text for record in expected_records)

        # The output is printed rather than logged, because the targets run with log_cli_level=WARNING
        if is_expected:
            print(f'[{label} {elapsed:6.1f}s] {Expected_Record_Marker} {text}', flush=True)
        else:
            print(f'[{label} {elapsed:6.1f}s] {text}', flush=True)

        # An empty marker means this process has no readiness line to wait for
        if ready_marker and ready_marker in text:
            ready_event.set()

# ################################################################################################################################

def start_streaming(
    process:'subprocess.Popen',
    label:'str',
    expected_records:'list[str]',
    thread_name:'str',
    ) -> 'threading.Thread':
    """ Streams the output of a process that has no readiness line, timed from now, in a thread of its own.
    """
    thread = threading.Thread(
        target=stream_output,
        args=(process, label, time.monotonic(), ModuleCtx.No_Ready_Marker, threading.Event(), expected_records),
        name=thread_name,
        daemon=True,
    )
    thread.start()

    return thread

# ################################################################################################################################
# ################################################################################################################################
