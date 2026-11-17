# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil

# Zato
from zato.common.test.durability.barrier import replicated_environment
from zato.common.test.direct_sql.seed import seed_autocommit_connection
from zato.common.test.durability.disk import get_disk_dir
from zato.common.test.zato_database import file_database_engine

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the database, whose path is short enough for the socket of the barrier
    Directory_Name = 'barrier-writes'

    # The statements that change the schema and a row outside a transaction
    Create_Table = 'create table durability_barrier (value integer)'
    Insert_Row = 'insert into durability_barrier (value) values (1)'

# ################################################################################################################################
# ################################################################################################################################

def test_barrier_outside_transaction() -> 'None':
    """ A statement that changes the schema and a statement that changes a row, each committing on its own
    outside a transaction of the replicated Zato database, return only after a barrier request has completed.
    """
    directory = get_disk_dir(ModuleCtx.Directory_Name)
    shutil.rmtree(directory)
    os.makedirs(directory)

    with replicated_environment(directory) as barrier:
        with file_database_engine(directory) as engine, seed_autocommit_connection(engine) as connection:

            before = barrier.request_count
            _ = connection.exec_driver_sql(ModuleCtx.Create_Table)
            assert barrier.request_count > before, 'The change of the schema returned before the barrier'

            before = barrier.request_count
            _ = connection.exec_driver_sql(ModuleCtx.Insert_Row)
            assert barrier.request_count > before, 'The change of the row returned before the barrier'

# ################################################################################################################################
# ################################################################################################################################
