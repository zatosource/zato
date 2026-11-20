# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A server that takes the Zato database over on the database that its variables select, opens a transaction that
# its generation guard confirms with the row of the active server locked for share, prints one line of JSON with
# its process identifier and the process identifier of its session in PostgreSQL, and holds the transaction open
# until its standard input is closed.

# stdlib
import json
import os
import sys

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

# The process identifier of the session of the transaction
_backend_pid_query = text('SELECT pg_backend_pid()')

# A read that locks rows, before which the generation guard locks the row of the active server for share
_locking_read_query = text('SELECT msg_id FROM pubsub_message LIMIT 1 FOR SHARE')

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Takes the database over and holds a guarded transaction open until standard input is closed.
    """
    backend = SQLPubSubBackend(audit_log=new_test_audit_log())
    backend.take_over()

    engine = backend.engine

    with engine.connect() as connection:

        # The transaction confirms the generation with its first statement ..
        transaction = connection.begin()
        backend_pid = connection.execute(_backend_pid_query).scalar_one()

        # .. and locks the row of the active server with the first one that locks rows ..
        _ = connection.execute(_locking_read_query).all()

        report = {
            'pid': os.getpid(),
            'backend_pid': backend_pid,
        }

        line = json.dumps(report)
        print(line, flush=True)

        # .. which it holds until the test lets it go.
        _ = sys.stdin.read()
        transaction.rollback()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
