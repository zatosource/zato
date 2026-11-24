# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A process of its own that publishes one message to the SQLite file of a scenario when its parent signals it.
# No arbiter binds it to the write queue of the file, so its write competes with those of the parent for the lock of the file.

# stdlib
import sys

# Zato
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What each line that the parent reads begins with
    Line_Prefix = 'pubsub.backend.test.concurrent-publisher:'

    # The line that says that the backend is ready to publish
    Ready = 'ready'

    # The outcome of a publication that was stored
    Published = 'published'

# ################################################################################################################################
# ################################################################################################################################

def _send(value:'str') -> 'None':
    """ Writes one line to the parent.
    """
    line = f'{ModuleCtx.Line_Prefix}{value}\n'

    _ = sys.stdout.write(line)
    _ = sys.stdout.flush()

# ################################################################################################################################

def main() -> 'None':
    """ Publishes one message once the parent signals it and reports the outcome of the publication,
    the name of the class of its exception if it failed.
    """
    topic_name = sys.argv[1]
    data       = sys.argv[2]
    msg_id     = sys.argv[3]

    backend = SQLPubSubBackend(audit_log=new_test_audit_log())

    # The parent learns that the backend is ready ..
    _send(ModuleCtx.Ready)

    # .. and signals the publication with one line ..
    _ = sys.stdin.readline()

    try:
        _ = backend.publish(topic_name, data, msg_id=msg_id)
    except Exception as e:
        outcome = e.__class__.__name__
    else:
        outcome = ModuleCtx.Published

    # .. whose outcome it reads afterwards.
    _send(outcome)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
