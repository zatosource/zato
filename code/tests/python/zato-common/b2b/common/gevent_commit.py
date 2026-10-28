# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import json
import os
from shutil import rmtree
from tempfile import mkdtemp

# gevent
from gevent import sleep, spawn
from gevent.monkey import get_original

# SQLAlchemy
from sqlalchemy import create_engine, event as sa_event

# Zato
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_write_path import new_identity, new_stored_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# How long the commit is held back in the thread that runs it, in seconds.
_commit_seconds = 0.5

# How long the greenlet sleeps between two ticks, in seconds.
_tick_seconds = 0.01

# How many ticks prove that the event loop ran during the commit.
_min_ticks = 20

_real_sleep = get_original('time', 'sleep')
_get_ident = get_original('threading', 'get_ident')

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    directory = mkdtemp(prefix='zato-b2b-gevent-')
    path = os.path.join(directory, 'b2b.db')

    engine = create_engine(f'sqlite:///{path}')
    writer = GroupCommitWriter(engine, interval_ms=0)
    store = MessageStore(writer)

    state:'stranydict' = {
        'commit_thread': 0,
        'in_commit': False,
        'ticks_during_commit': 0,
    }

    def on_commit(conn:'any_') -> 'None':
        state['commit_thread'] = _get_ident()
        state['in_commit'] = True
        _real_sleep(_commit_seconds)
        state['in_commit'] = False

    def tick() -> 'None':
        while True:
            sleep(_tick_seconds)
            if state['in_commit']:
                state['ticks_during_commit'] += 1

    sa_event.listen(engine, 'commit', on_commit)
    _ = spawn(tick)

    is_claimed = store.claim(new_identity('message-1'), new_stored_message())

    report = {
        'is_claimed': is_claimed,
        'main_thread': _get_ident(),
        'commit_thread': state['commit_thread'],
        'ticks_during_commit': state['ticks_during_commit'],
        'min_ticks': _min_ticks,
    }

    writer.stop()
    engine.dispose()
    rmtree(directory, ignore_errors=True)

    print(json.dumps(report))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
