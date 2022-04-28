# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent.monkey import patch_all
patch_all()

# stdlib
import os
from tempfile import gettempdir

# gevent
from gevent import sleep

# Zato
from zato.common.util.api import spawn_greenlet
from zato.common.util.file_system import fs_safe_now
from zato.distlock import LockManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strset

# ################################################################################################################################
# ################################################################################################################################

class Const:

    LockType = 'fcntl'

    class NamePattern:
        Directory = 'zato-ipc-{run_id}'
        ToArbiter = 'to-arbiter-{pid}.txt'
        ToPID = 'to-process-{pid}.txt'
        ResponseFrom = 'from-process-{pid}-{cid}.json'

# ################################################################################################################################
# ################################################################################################################################

class IPCArbiter:

    pids: 'strset'
    run_id: 'str'
    full_dir_name: 'str'

    arbiter_pid: 'str'
    ipc_group_id: 'str'
    lock_manager: 'LockManager'

    def __init__(
        self,
        arbiter_pid,  # type: str
        ipc_group_id, # type: str
    ) -> 'None':

        self.arbiter_pid = arbiter_pid
        self.ipc_group_id = ipc_group_id

        self.pids = set() # type: strset
        self.lock_manager = LockManager(Const.LockType, 'zato-ipc-ns')
        self.keep_running = True

# ################################################################################################################################

    def add_pid(self, pid:'str') -> 'None':
        self.pids.add(pid)

# ################################################################################################################################

    def stop(self) -> 'None':
        self.keep_running = False

# ################################################################################################################################

    def set_up(self) -> 'str':

        # This is unique enough ..
        run_id = fs_safe_now()

        # .. we store our data in a temporary directory ..
        tmp_dir = gettempdir()

        # .. build a full name for that run of the arbiter ..
        dir_name = Const.NamePattern.Directory.format(run_id=run_id)
        full_dir_name = os.path.join(tmp_dir, dir_name)

        # .. prepare the directory that the data will be in ..
        os.makedirs(full_dir_name)

        # .. store the config for our own use ..
        self.run_id = run_id
        self.full_dir_name = full_dir_name

        # .. and return the run_id to our caller so that it can be passed to other layers.
        return run_id

# ################################################################################################################################

    def send_to_pid(self, pid:'str'):

        # Take both run_id and PID into account to ensure that the name is unique.
        lock_id = '{}-{}'.format(self.run_id, pid)

        # We can build it upfront here, before we attempt to obtain a lock.
        to_pid_file_name = Const.NamePattern.ToPID.format(pid=pid)
        to_pid_file_name_full = os.path.join(self.full_dir_name, to_pid_file_name)

        with self.lock_manager(lock_id):
            f = open(to_pid_file_name_full, 'a')
            f.write('aaa\n')
            f.close()

            print(111, 'Sent', f.name)

# ################################################################################################################################

    def send_to_all_pids(self):

        for pid in self.pids:
            self.send_to_pid(pid)

# ################################################################################################################################

    def run_forever(self):

        # Prepare all the context and configuration ..
        self.set_up()

        # .. and keep running until stopped.
        while self.keep_running:
            sleep(1)
            print('Arbiter', self.arbiter_pid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    ip_group_id = 'abc'

    arbiter_pid = '6666'
    client_pids = ['7777', '8888']

    ipc_arbiter = IPCArbiter(arbiter_pid, ip_group_id)

    for pid in client_pids:
        ipc_arbiter.add_pid(pid)

    spawn_greenlet(ipc_arbiter.run_forever)

    ipc_arbiter.send_to_all_pids()

    while True:
        sleep(0.1)

# ################################################################################################################################
# ################################################################################################################################
