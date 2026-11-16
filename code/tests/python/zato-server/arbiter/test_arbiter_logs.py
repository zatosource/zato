# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import re
import sys
from multiprocessing import get_context

# gevent
import gevent

# Zato
from arbiter_common import new_config, Probe, ProcessUnderTest, Region_Config, stop_arbiter, wait_until, Writes_Metric
from zato.common.util.log_rotation import WorkerFileHandler
from zato.server.arbiter import Arbiter
from zato_ipc_core.zato_ipc_core import SharedRegion
from zato_server_core.zato_server_core import init_rest_log, log_rest_line

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from re import Pattern
    from zato.common.typing_ import intlist, set_, strlist
    from zato.server.arbiter_config import WorkerContext

    intlist = intlist
    Path = Path
    Pattern = Pattern
    strlist = strlist
    WorkerContext = WorkerContext

    strset = set_[str]

# ################################################################################################################################
# ################################################################################################################################

_context = get_context('fork')

# The files that every process of the test appends to, their size limit, and enough backups to keep every record
_log_name = 'server.log'
_rest_log_name = 'rest.log'
_max_bytes = 20_000
_backup_count = 1000

# A writer of zato_server_core opened without a limit appends to its file and never renames it
_native_no_limit = 0

# The format of every record, and the logger through which the worker writes its own
_format = '%(process)d %(name)s %(message)s'
_logger_name = 'zato_rotation_test'

# How many records the worker writes, the padding that makes each one longer, and how often the worker yields
_record_count = 2000
_padding = 'p' * 64
_records_per_yield = 20
_yield_time = 0.001

# How many renames of each file the test requires at least
_rotations_min = 3

# A record of the worker, which ends with the padding at the end of its line, and any record of the arbiter or of the worker
_worker_record = re.compile(r'^\d+ ' + _logger_name + r' seq=(\d+) ' + _padding + '$')
_any_record = re.compile(r'^\d+ [\w.]+ .+$')

# A line of the worker in the REST log, as log_rest_line formats it
_rest_record = re.compile(r'^[\d-]+ [\d:,]+ - INFO - \d+:Dummy - zato_rest:0 - seq=(\d+) ' + _padding + '$')

# How long the test waits for the worker to write its records, in seconds
_write_timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

def _write_records(probe:'Probe') -> 'None':
    """ Writes the numbered records of the worker to both files, yielding so that the worker applies the commands of the arbiter.
    """
    logger = logging.getLogger(_logger_name)

    for index in range(_record_count):
        logger.info('seq=%d %s', index, _padding)
        _ = log_rest_line(f'seq={index} {_padding}')

        if index % _records_per_yield == 0:
            gevent.sleep(_yield_time)

    probe.add(Writes_Metric, 1)

# ################################################################################################################################

def _run_arbiter(region:'SharedRegion', probe:'Probe', log_dir:'str', tmp_dir:'str') -> 'None':
    """ Configures the log file in the arbiter before its worker is forked, as main.py does, and runs the arbiter,
    which renames the REST log that the worker opens after its fork.
    """
    log_path = os.path.join(log_dir, _log_name)
    rest_log_path = os.path.join(log_dir, _rest_log_name)

    handler = WorkerFileHandler(log_path, maxBytes=_max_bytes, backupCount=_backup_count, encoding='utf8')
    handler.setFormatter(logging.Formatter(_format))

    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    def worker_main(ctx:'WorkerContext') -> 'None':
        init_rest_log(rest_log_path, _native_no_limit)

        worker = ProcessUnderTest(region, probe, ctx, True)
        worker.report_ready()

        _ = gevent.spawn(_write_records, probe)
        worker.serve()

    config = new_config(tmp_dir)
    config.native_log_files = [rest_log_path]
    config.native_log_max_bytes = _max_bytes
    config.native_log_backup_count = _backup_count

    arbiter = Arbiter(region, worker_main, config)
    exit_code = arbiter.run()

    sys.exit(exit_code)

# ################################################################################################################################

def _get_log_files(log_dir:'str', log_name:'str') -> 'strlist':
    out:'strlist' = []

    for name in os.listdir(log_dir):
        if name.startswith(log_name):
            path = os.path.join(log_dir, name)
            out.append(path)

    return out

# ################################################################################################################################

def _check_records(paths:'strlist', worker_record:'Pattern[str]', any_record:'Pattern[str]') -> 'None':
    """ Verifies that the files hold every record of the worker once and whole, and that the worker followed the renames.
    """
    # The file was renamed several times ..
    assert len(paths) > _rotations_min

    seqs:'intlist' = []
    files:'strset' = set()

    for path in paths:
        with open(path, encoding='utf8') as log_file:
            content = log_file.read()

        # .. every file ends with a whole record, other than one that the arbiter created at its last rename
        # and that no process wrote to afterwards ..
        if content:
            assert content.endswith('\n')

        for line in content.splitlines():

            # .. every line is one whole record ..
            assert any_record.match(line), line

            if match := worker_record.match(line):
                seq = int(match.group(1))

                seqs.append(seq)
                files.add(path)

    # .. each record of the worker is in exactly one file ..
    assert sorted(seqs) == list(range(_record_count))

    # .. and the worker followed the renames, writing to more than one file.
    assert len(files) > 1

# ################################################################################################################################
# ################################################################################################################################

def test_records_of_the_worker_survive_rotations_whole_and_once(tmp_path:'Path') -> 'None':
    region = SharedRegion(Region_Config)
    probe = Probe()

    log_dir = tmp_path / 'logs'
    tmp_dir = tmp_path / 'tmp'

    log_dir.mkdir()
    tmp_dir.mkdir()

    # The worker writes its records while the arbiter renames the files ..
    arbiter = _context.Process(target=_run_arbiter, args=(region, probe, str(log_dir), str(tmp_dir)))
    arbiter.start()

    try:
        assert wait_until(probe.reached, (Writes_Metric, 1), _write_timeout)
        stop_arbiter(arbiter, [probe.worker_pid()], str(tmp_dir))

    finally:
        if arbiter.is_alive():
            arbiter.kill()

    # .. the Python handlers and the REST log writer of zato_server_core each kept every record once and whole.
    _check_records(_get_log_files(str(log_dir), _log_name), _worker_record, _any_record)
    _check_records(_get_log_files(str(log_dir), _rest_log_name), _rest_record, _rest_record)

# ################################################################################################################################
# ################################################################################################################################
