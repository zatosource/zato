# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The takeover of a pub/sub database by another server, which raises the generation through the startup of its backend.

# stdlib
import os
import tempfile

# Zato
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.pubsub_database import pubsub_db_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variables that give the other server a generation file and an engine of its own
    Env_Generation_File = 'Zato_Database_Generation_File'
    Env_Pool_Size = 'Zato_Database_Pool_Size'

    # The prefix of the directory of the generation file of the other server
    Work_Dir_Prefix = 'zato_takeover_'

    # The name of the generation file of the other server
    Generation_File_Name = 'generation'

# ################################################################################################################################
# ################################################################################################################################

def take_over_as_another_server(env:'strstrdict', pool_size:'int') -> 'SQLPubSubBackend':
    """ Starts the backend of another server on the database that the variables select, with a generation file
    and an engine of its own, which takes the database over the way the startup of that server does.
    The pool size gives the other server an engine of its own, since engines are cached by their settings.
    """
    work_dir = tempfile.mkdtemp(prefix=ModuleCtx.Work_Dir_Prefix)

    server_env = dict(env)
    server_env[ModuleCtx.Env_Generation_File] = os.path.join(work_dir, ModuleCtx.Generation_File_Name)
    server_env[ModuleCtx.Env_Pool_Size] = str(pool_size)

    # The backend resolves its engine on first access, which happens here while the variables select the engine
    # that its guard is installed on.
    with pubsub_db_env(server_env):
        out = SQLPubSubBackend(audit_log=new_test_audit_log())
        out.take_over()
        _ = out.engine

    return out

# ################################################################################################################################
# ################################################################################################################################
