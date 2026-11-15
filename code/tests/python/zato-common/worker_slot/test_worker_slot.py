# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import traceback
from io import StringIO
from multiprocessing import get_context

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.worker_slot import get_worker_slot, ModuleCtx as WorkerSlotCtx, set_worker_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The slot that the forked process of the test records
    Slot = 2

    Logger_Name = 'zato.test.worker_slot'
    Log_Format = '%(worker_slot)s %(message)s'

    # How long the test waits for its forked process, in seconds
    Join_Timeout = 30.0

# ################################################################################################################################
# ################################################################################################################################

def _new_attrs(audit_log:'AuditLog', attrs:'dict[str, str]') -> 'dict[str, object]':
    pending = audit_log.new_pending_event('test', 'test.event', 'test-object', attrs=attrs)

    out = pending.attrs
    return out

# ################################################################################################################################

def _check_in_worker(output_path:'str') -> 'None':
    """ Confirms in a process of its own, because the slot belongs to the whole process, what the slot changes.
    """
    exit_code = 1

    try:
        logger = logging.getLogger(ModuleCtx.Logger_Name)
        audit_log = AuditLog('test-server')
        attrs = {'customer_id': 'CUST-001'}

        # Before the slot is recorded, neither the records nor the events name one ..
        assert get_worker_slot() is None
        assert WorkerSlotCtx.Attr_Name not in logger.makeRecord(logger.name, logging.INFO, '', 0, '', (), None).__dict__
        assert _new_attrs(audit_log, attrs) == {'customer_id': 'CUST-001'}

        set_worker_slot(ModuleCtx.Slot)

        # .. afterwards, each record names it, including in a formatted line ..
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter(ModuleCtx.Log_Format))

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        logger.info('Order received')

        # .. and each audit event names it, in a dict of its own.
        event_attrs = _new_attrs(audit_log, attrs)

        with open(output_path, 'w') as output:
            _ = output.write(stream.getvalue())
            _ = output.write(repr(sorted(event_attrs.items())) + '\n')
            _ = output.write(repr(attrs) + '\n')

        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_the_records_and_events_of_a_worker_name_its_slot(tmp_path:'Path') -> 'None':
    output_path = str(tmp_path / 'output')

    context = get_context('fork')

    process = context.Process(target=_check_in_worker, args=(output_path,))
    process.start()
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

    with open(output_path) as output:
        lines = output.read().splitlines()

    assert lines == [
        f'{ModuleCtx.Slot} Order received',
        repr([('customer_id', 'CUST-001'), (WorkerSlotCtx.Attr_Name, ModuleCtx.Slot)]),
        repr({'customer_id': 'CUST-001'}),
    ]

    # The process of the test itself is not a worker
    assert get_worker_slot() is None

# ################################################################################################################################
# ################################################################################################################################
