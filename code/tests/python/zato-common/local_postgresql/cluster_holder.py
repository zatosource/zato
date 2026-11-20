# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A process that starts a local PostgreSQL cluster, writes its directory, its ports and the PIDs of its postmasters
# to its standard output as one line of JSON, and holds the cluster until it is killed.

# stdlib
import json
import os
import sys

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.local_postgresql import start_local_cluster
from zato.common.test.pubsub_database import get_container_settings, PubSubDatabase, PubSubDBMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

# ################################################################################################################################
# ################################################################################################################################

def _read_postmaster_pid(data_dir:'str') -> 'int':
    """ Returns the PID of the postmaster of a data directory.
    """
    pid_path = os.path.join(data_dir, 'postmaster.pid')

    with open(pid_path) as pid_file:
        first_line = pid_file.readline()

    out = int(first_line)
    return out

# ################################################################################################################################

def main() -> 'None':
    """ Starts the cluster and reports it.
    """
    password = 'pubsub.' + CryptoManager.generate_hex_string()

    database = PubSubDatabase(mode=PubSubDBMode.PostgreSQL_Local)
    settings = get_container_settings(database, None)

    cluster = start_local_cluster('zato_pubsub', password, 'zato_pubsub', settings)

    pids:'intlist' = []

    for instance in (cluster.primary, cluster.standby):
        pid = _read_postmaster_pid(instance.data_dir)
        pids.append(pid)

    report = {
        'name': cluster.reservation.name,
        'base_dir': cluster.base_dir,
        'ports': [cluster.primary.port, cluster.standby.port],
        'pids': pids,
    }

    data = json.dumps(report)
    _ = sys.stdout.write(data + '\n')
    sys.stdout.flush()

    # The cluster is held until the test kills this process.
    _ = sys.stdin.read()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
