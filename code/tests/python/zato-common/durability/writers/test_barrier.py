# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
from uuid import uuid4

# Zato
from zato.common.common_db.schema import shared_object_table
from zato.common.db_env.engine import execute_write
from zato.common.test.durability.barrier import replicated_environment
from zato.common.test.durability.disk import get_disk_dir
from zato.common.test.zato_database import file_database_engine
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the database, whose path is short enough for the socket of the barrier
    Directory_Name = 'barrier-writes'

    # The type of the shared object whose insert changes a row
    Object_Type = 'durability-barrier'

# ################################################################################################################################
# ################################################################################################################################

def test_barrier_on_schema_and_row() -> 'None':
    """ The creation of the schema of a replicated Zato database, whose statements SQLite commits outside
    a transaction, and a serialized write of a row return only after a barrier request has completed.
    """
    directory = get_disk_dir(ModuleCtx.Directory_Name)
    shutil.rmtree(directory)
    os.makedirs(directory)

    with replicated_environment(directory) as barrier:

        before = barrier.request_count

        with file_database_engine(directory) as engine:

            assert barrier.request_count > before, 'The creation of the schema returned before the barrier'

            insert = shared_object_table.insert().values(
                object_type=ModuleCtx.Object_Type,
                name=uuid4().hex,
                data='{}',
                version=1,
                last_updated=utcnow(),
            )

            before = barrier.request_count
            _ = execute_write(engine, insert)
            assert barrier.request_count > before, 'The change of the row returned before the barrier'

# ################################################################################################################################
# ################################################################################################################################
