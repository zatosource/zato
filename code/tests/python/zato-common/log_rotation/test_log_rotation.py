# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# PyYAML
import yaml

# Zato
from zato.common.util.log_rotation import LogRotator, ModuleCtx, use_worker_handlers, WorkerFileHandler
from zato.common.util.logging_ import get_logging_conf_contents

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import intset, list_, strlist

    intset = intset
    Path = Path
    strlist = strlist

    handlerlist = list_[WorkerFileHandler]

# ################################################################################################################################
# ################################################################################################################################

# The size limit of the files of the tests, and how many backups each one keeps
_max_bytes = 200
_backup_count = 5

# A record that fills a file above its limit
_large_record = 'x' * _max_bytes

# The slot of the worker that the tests stand for
_slot = 0

# ################################################################################################################################
# ################################################################################################################################

class _Broadcast:
    """ Stands for the hub of the arbiter, recording each rotation and returning the slot of the one worker.
    """
    def __init__(self) -> 'None':
        self.rotation_ids:'list_[int]' = []

    def __call__(self, rotation_id:'int') -> 'intset':
        self.rotation_ids.append(rotation_id)

        out = {_slot}
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_handler(path:'str') -> 'WorkerFileHandler':
    out = WorkerFileHandler(path, maxBytes=_max_bytes, backupCount=_backup_count, encoding='utf8')
    out.setFormatter(logging.Formatter('%(message)s'))
    return out

# ################################################################################################################################

def _write(handler:'WorkerFileHandler', message:'str') -> 'None':
    record = logging.makeLogRecord({'msg': message, 'levelno': logging.INFO, 'levelname': 'INFO'})
    _ = handler.handle(record)

# ################################################################################################################################

def _read_lines(path:'str') -> 'strlist':
    with open(path, encoding='utf8') as log_file:
        out = log_file.read().splitlines()

    return out

# ################################################################################################################################

def _close(handlers:'handlerlist') -> 'None':
    for handler in handlers:
        handler.close()

# ################################################################################################################################
# ################################################################################################################################

def test_the_rotating_handlers_of_the_server_configuration_are_replaced() -> 'None':
    config = yaml.safe_load(get_logging_conf_contents())

    use_worker_handlers(config)

    # Every handler of a file appends to it without renaming it ..
    for handler_config in config['handlers'].values():
        if 'filename' in handler_config:
            assert handler_config['class'] == ModuleCtx.Worker_Handler_Class

    # .. and the other handlers are left as they are.
    assert config['handlers']['stdout']['class'] == 'logging.StreamHandler'

# ################################################################################################################################

def test_a_worker_handler_never_renames_its_file(tmp_path:'Path') -> 'None':
    path = str(tmp_path / 'server.log')
    handler = _new_handler(path)

    for _ in range(3):
        _write(handler, _large_record)

    # The file grew past its limit and has no backup
    assert os.path.getsize(path) > _max_bytes * 2
    assert os.listdir(tmp_path) == ['server.log']

    _close([handler])

# ################################################################################################################################

def test_the_arbiter_renames_a_full_file_and_writes_to_the_new_one(tmp_path:'Path') -> 'None':
    path = str(tmp_path / 'server.log')

    # The arbiter and a worker forked from it each hold a handler of the file ..
    arbiter_handler = _new_handler(path)
    worker_handler = _new_handler(path)

    broadcast = _Broadcast()
    rotator = LogRotator([arbiter_handler], broadcast)

    # .. a file below its limit is not renamed ..
    _write(worker_handler, 'worker-1')
    assert not rotator.rotate_due()

    # .. one that reached it is renamed and the worker is asked to reopen it ..
    _write(worker_handler, _large_record)
    assert rotator.rotate_due()
    assert broadcast.rotation_ids == [1]

    # .. the arbiter writes to the new file at once, while the worker writes to the renamed one until it reopens ..
    _write(arbiter_handler, 'arbiter-1')
    _write(worker_handler, 'worker-2')

    assert _read_lines(path) == ['arbiter-1']
    assert _read_lines(f'{path}.1') == ['worker-1', _large_record, 'worker-2']

    # .. and after its reopen the worker writes to the new file as well.
    worker_handler.reopen()
    _write(worker_handler, 'worker-3')

    assert _read_lines(path) == ['arbiter-1', 'worker-3']

    _close([arbiter_handler, worker_handler])

# ################################################################################################################################

def test_no_file_is_renamed_again_before_the_worker_acknowledged(tmp_path:'Path') -> 'None':
    path = str(tmp_path / 'server.log')

    arbiter_handler = _new_handler(path)
    broadcast = _Broadcast()
    rotator = LogRotator([arbiter_handler], broadcast)

    _write(arbiter_handler, _large_record)
    assert rotator.rotate_due()

    # The new file reaches its limit, but the worker has not acknowledged the rotation ..
    _write(arbiter_handler, _large_record)
    assert not rotator.rotate_due()

    # .. an acknowledgement of an earlier rotation changes nothing ..
    rotator.on_reopened(_slot, 0)
    assert not rotator.rotate_due()

    # .. and the acknowledgement of this one permits the next rotation.
    rotator.on_reopened(_slot, 1)
    assert rotator.rotate_due()
    assert broadcast.rotation_ids == [1, 2]

    # A worker that terminated before its acknowledgement permits the next rotation as well.
    _write(arbiter_handler, _large_record)
    rotator.on_process_exit(_slot)

    assert rotator.rotate_due()
    assert broadcast.rotation_ids == [1, 2, 3]
    assert sorted(os.listdir(tmp_path)) == ['server.log', 'server.log.1', 'server.log.2', 'server.log.3']

    _close([arbiter_handler])

# ################################################################################################################################
# ################################################################################################################################
